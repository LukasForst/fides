from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

import numpy as np

from fides.model.aliases import Target, Score
from fides.model.peer import PeerInfo
from fides.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from fides.persistance.threat_intelligence import ThreatIntelligenceDatabase
from simulations.utils import Click


@dataclass
class SampleBehavior:
    score_mean: float
    score_deviation: float

    confidence_mean: float
    confidence_deviation: float

    def sample_score(self, mean_shift: float = 1.0) -> float:
        generated = np.random.normal(mean_shift * self.score_mean, self.score_deviation)
        if generated < -1:
            return -1
        elif generated > 1:
            return 1
        return generated

    def sample_confidence(self) -> float:
        generated = np.random.normal(self.confidence_mean, self.confidence_deviation)
        if generated < 0:
            return 0
        elif generated > 1:
            return 1
        return generated


class LocalSlipsTIDb(ThreatIntelligenceDatabase):

    def __init__(self,
                 target_baseline: Dict[Target, Score] = None,
                 behavior: SampleBehavior = SampleBehavior(score_mean=0.9,
                                                           score_deviation=0.1,
                                                           confidence_mean=0.9,
                                                           confidence_deviation=0.1),
                 ):
        self._behavior = behavior
        self._target_baseline = target_baseline if target_baseline else {}

    def get_for(self, target: Target) -> Optional[SlipsThreatIntelligence]:
        baseline = self._target_baseline[target]
        if baseline is not None:
            score = self._behavior.sample_score()
            confidence = self._behavior.sample_confidence()
            return SlipsThreatIntelligence(score=score, confidence=confidence, target=target)
        return None


class PeerBehavior(Enum):
    # being behaviors
    CONFIDENT_CORRECT = 'CONFIDENT_CORRECT',
    UNCERTAIN_PEER = 'UNCERTAIN_PEER',
    CONFIDENT_INCORRECT = 'CONFIDENT_INCORRECT',
    # malicious behavior
    MALICIOUS_PEER = 'MALICIOUS_PEER'


class Peer:
    def __init__(self,
                 peer_info: PeerInfo,
                 network_joining_epoch: Click,
                 label: PeerBehavior,
                 sample_base: SampleBehavior
                 ):
        self.peer_info = peer_info
        self.label = label
        self.network_joining_epoch = network_joining_epoch

        self._sample_base = sample_base

    def provide_ti(self, epoch: Click, target: Target, baseline: float) -> Optional[ThreatIntelligence]:
        if epoch >= self.network_joining_epoch:
            return self._provide_ti(epoch, target, baseline)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        raise NotImplemented()


class ConfidentCorrectPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = SampleBehavior(score_mean=0.9,
                                                              score_deviation=0.1,
                                                              confidence_mean=0.9,
                                                              confidence_deviation=0.1)
                 ):
        super().__init__(peer_info, network_joining_epoch, PeerBehavior.CONFIDENT_CORRECT, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self._sample_base.sample_score(baseline)
        confidence = self._sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)


class UncertainPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = SampleBehavior(score_mean=0.0,
                                                              score_deviation=0.8,
                                                              confidence_mean=0.3,
                                                              confidence_deviation=0.2)
                 ):
        super().__init__(peer_info, network_joining_epoch, PeerBehavior.UNCERTAIN_PEER, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self._sample_base.sample_score()
        confidence = self._sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)


class ConfidentIncorrectPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = SampleBehavior(score_mean=0.8,
                                                              score_deviation=0.2,
                                                              confidence_mean=0.8,
                                                              confidence_deviation=0.2)
                 ):
        super().__init__(peer_info, network_joining_epoch, PeerBehavior.CONFIDENT_INCORRECT, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self._sample_base.sample_score(-baseline)
        confidence = self._sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)


class MaliciousPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 network_joining_epoch: Click,
                 lying_about_targets: List[Target],
                 epoch_starts_lying: Click,
                 sample_base: SampleBehavior = SampleBehavior(score_mean=0.9,
                                                              score_deviation=0.1,
                                                              confidence_mean=0.9,
                                                              confidence_deviation=0.1)

                 ):
        self._lying_about_targets = lying_about_targets
        self._epoch_starts_lying = epoch_starts_lying
        super().__init__(peer_info, network_joining_epoch, PeerBehavior.MALICIOUS_PEER, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        shift = baseline
        if epoch >= self._epoch_starts_lying and target in self._lying_about_targets:
            shift = -baseline

        score = self._sample_base.sample_score(shift)
        confidence = self._sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)
