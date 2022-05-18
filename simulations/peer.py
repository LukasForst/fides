from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

import numpy as np

from fides.model.aliases import Target, Score, PeerId
from fides.model.peer import PeerInfo
from fides.model.recommendation import Recommendation
from fides.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from fides.persistence.threat_intelligence import ThreatIntelligenceDatabase
from fides.utils import bound
from simulations.utils import Click


class PeerBehavior(Enum):
    # benign behaviors
    CONFIDENT_CORRECT = 'CONFIDENT_CORRECT',
    UNCERTAIN_PEER = 'UNCERTAIN_PEER',
    CONFIDENT_INCORRECT = 'CONFIDENT_INCORRECT',
    # malicious behavior
    MALICIOUS_PEER = 'MALICIOUS_PEER'


@dataclass
class SampleBehavior:
    score_mean: float
    score_deviation: float

    confidence_mean: float
    confidence_deviation: float

    def sample_score(self, mean_shift: float = 1.0) -> float:
        generated = np.random.normal(mean_shift * self.score_mean, self.score_deviation)
        return bound(generated, -1, 1)

    def sample_confidence(self) -> float:
        generated = np.random.normal(self.confidence_mean, self.confidence_deviation)
        return bound(generated, 0, 1)


behavioral_map = {
    PeerBehavior.CONFIDENT_CORRECT: SampleBehavior(score_mean=0.9,
                                                   score_deviation=0.1,
                                                   confidence_mean=0.9,
                                                   confidence_deviation=0.1),
    PeerBehavior.UNCERTAIN_PEER: SampleBehavior(score_mean=0.0,
                                                score_deviation=0.8,
                                                confidence_mean=0.3,
                                                confidence_deviation=0.2),
    PeerBehavior.CONFIDENT_INCORRECT: SampleBehavior(score_mean=0.8,
                                                     score_deviation=0.2,
                                                     confidence_mean=0.8,
                                                     confidence_deviation=0.2),
    PeerBehavior.MALICIOUS_PEER: SampleBehavior(score_mean=0.9,
                                                score_deviation=0.1,
                                                confidence_mean=0.9,
                                                confidence_deviation=0.1),
}


class LocalSlipsTIDb(ThreatIntelligenceDatabase):

    def __init__(self,
                 target_baseline: Dict[Target, Score] = None,
                 behavior: SampleBehavior = behavioral_map[PeerBehavior.UNCERTAIN_PEER],
                 ):
        self._behavior = behavior
        self._target_baseline = target_baseline if target_baseline else {}

    def get_for(self, target: Target) -> Optional[SlipsThreatIntelligence]:
        baseline = self._target_baseline[target]
        if baseline is not None:
            score = self._behavior.sample_score(baseline)
            confidence = self._behavior.sample_confidence()
            return SlipsThreatIntelligence(score=score, confidence=confidence, target=target)
        return None


class Peer:
    def __init__(self,
                 peer_info: PeerInfo,
                 service_history_size: int,
                 max_recommenders: int,
                 network_joining_epoch: Click,
                 label: PeerBehavior,
                 sample_base: SampleBehavior
                 ):
        self.peer_info = peer_info
        self.label = label
        self.network_joining_epoch = network_joining_epoch

        self._service_history_size = service_history_size
        self._max_recommenders = max_recommenders
        self.sample_base = sample_base

    def provide_ti(self, epoch: Click, target: Target, baseline: float) -> Optional[ThreatIntelligence]:
        if epoch >= self.network_joining_epoch:
            return self._provide_ti(epoch, target, baseline)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        raise NotImplemented()

    def provide_recommendation(self,
                               epoch: Click,
                               subject: PeerId,
                               peers_baseline_behavior: PeerBehavior) -> Optional[Recommendation]:
        if epoch >= self.network_joining_epoch:
            return self._provide_recommendation(epoch, subject, peers_baseline_behavior)

    def _provide_recommendation(self,
                                epoch: Click,
                                subject: PeerId,
                                peers_baseline_behavior: PeerBehavior) -> Recommendation:
        raise NotImplemented()

    def _sample_service_history_size(self, mean: int, dev: float = None) -> int:
        service_history_size = bound(round(np.random.normal(mean, dev if dev else mean / 4)), 0,
                                     self._service_history_size)
        return service_history_size

    def _sample_reputation_provided_by(self, mean: int, dev: float = None) -> int:
        reputation_provided_by = bound(round(np.random.normal(mean, dev if dev else mean / 4)), 0,
                                       self._max_recommenders)
        return reputation_provided_by


class ConfidentCorrectPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 service_history_size: int,
                 max_recommenders: int,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = behavioral_map[PeerBehavior.CONFIDENT_CORRECT]
                 ):
        super().__init__(peer_info, service_history_size, max_recommenders, network_joining_epoch,
                         PeerBehavior.CONFIDENT_CORRECT, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self.sample_base.sample_score(baseline)
        confidence = self.sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)

    def _provide_recommendation(self,
                                epoch: Click,
                                subject: PeerId,
                                peers_baseline_behavior: PeerBehavior) -> Recommendation:
        shift = -1 if peers_baseline_behavior == PeerBehavior.MALICIOUS_PEER else 1
        sample = behavioral_map[peers_baseline_behavior]
        return Recommendation(
            competence_belief=bound(sample.sample_score(shift), 0, 1),
            integrity_belief=1 - sample.sample_confidence(),
            service_history_size=self._sample_service_history_size(self._service_history_size),
            recommendation=bound(sample.sample_score(), 0, 1),
            initial_reputation_provided_by_count=self._sample_reputation_provided_by(self._max_recommenders)
        )


class UncertainPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 service_history_size: int,
                 max_recommenders: int,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = behavioral_map[PeerBehavior.UNCERTAIN_PEER]
                 ):
        super().__init__(peer_info, service_history_size, max_recommenders, network_joining_epoch,
                         PeerBehavior.UNCERTAIN_PEER, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self.sample_base.sample_score()
        confidence = self.sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)

    def _provide_recommendation(self,
                                epoch: Click,
                                subject: PeerId,
                                peers_baseline_behavior: PeerBehavior) -> Recommendation:
        sample = behavioral_map[peers_baseline_behavior]
        return Recommendation(
            competence_belief=bound(np.random.normal(0.5, 0.5), 0, 1),
            integrity_belief=bound(np.random.normal(0.2, 1), 0, 1),
            service_history_size=self._sample_service_history_size(round(self._service_history_size / 4)),
            recommendation=bound(sample.sample_score(), 0, 1),
            initial_reputation_provided_by_count=self._sample_reputation_provided_by(round(self._max_recommenders / 4))
        )


class ConfidentIncorrectPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 service_history_size: int,
                 max_recommenders: int,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = behavioral_map[PeerBehavior.CONFIDENT_INCORRECT]
                 ):
        super().__init__(peer_info, service_history_size, max_recommenders, network_joining_epoch,
                         PeerBehavior.CONFIDENT_INCORRECT, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        score = self.sample_base.sample_score(-baseline)
        confidence = self.sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)

    def _provide_recommendation(self,
                                epoch: Click,
                                subject: PeerId,
                                peers_baseline_behavior: PeerBehavior) -> Recommendation:
        shift = 1 if peers_baseline_behavior == PeerBehavior.MALICIOUS_PEER else -1
        sample = behavioral_map[peers_baseline_behavior]
        return Recommendation(
            competence_belief=bound(sample.sample_score(shift), 0, 1),
            integrity_belief=1 - sample.sample_confidence(),
            service_history_size=self._sample_service_history_size(self._service_history_size),
            recommendation=bound(sample.sample_score(), 0, 1),
            initial_reputation_provided_by_count=self._sample_reputation_provided_by(self._max_recommenders)
        )


class MaliciousPeer(Peer):
    def __init__(self,
                 peer_info: PeerInfo,
                 service_history_size: int,
                 max_recommenders: int,
                 lying_about_targets: List[Target],
                 epoch_starts_lying: Click,
                 network_joining_epoch: Click = 0,
                 sample_base: SampleBehavior = behavioral_map[PeerBehavior.MALICIOUS_PEER]
                 ):
        self._lying_about_targets = lying_about_targets
        self._epoch_starts_lying = epoch_starts_lying
        super().__init__(peer_info, service_history_size, max_recommenders, network_joining_epoch,
                         PeerBehavior.MALICIOUS_PEER, sample_base)

    def _provide_ti(self, epoch: Click, target: Target, baseline: float) -> ThreatIntelligence:
        shift = baseline
        if epoch >= self._epoch_starts_lying and target in self._lying_about_targets:
            shift = -baseline

        score = self.sample_base.sample_score(shift)
        confidence = self.sample_base.sample_confidence()
        return ThreatIntelligence(score=score, confidence=confidence)

    def _provide_recommendation(self,
                                epoch: Click,
                                subject: PeerId,
                                peers_baseline_behavior: PeerBehavior) -> Recommendation:
        shift = 1 if peers_baseline_behavior == PeerBehavior.MALICIOUS_PEER else -1
        sample = behavioral_map[peers_baseline_behavior]
        return Recommendation(
            competence_belief=bound(sample.sample_score(shift), 0, 1),
            integrity_belief=1 - sample.sample_confidence(),
            service_history_size=self._sample_service_history_size(self._service_history_size,
                                                                   self._service_history_size / 10),
            recommendation=bound(sample.sample_score(), 0, 1),
            initial_reputation_provided_by_count=self._sample_reputation_provided_by(self._max_recommenders,
                                                                                     self._max_recommenders / 10)
        )
