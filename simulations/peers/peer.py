from dataclasses import dataclass

import numpy as np

from fides.model.peer import PeerInfo


@dataclass
class SampleBehavior:
    score_mean: float
    score_deviation: float

    confidence_mean: float
    confidence_deviation: float

    def sample_score(self) -> float:
        generated = np.random.normal(self.score_mean, self.score_deviation)
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


class Peer:
    def __init__(self,
                 peer_info: PeerInfo,
                 label: str,
                 sample_base: SampleBehavior
                 ):
        self._peer_info = peer_info
        self._label = label
        self._sample_base = sample_base
