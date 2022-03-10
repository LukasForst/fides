# This file, class and computational algorithm was inspired by Draliii's implementation of Trust Model for local
# network peer-to-peer module for Slips
# https://github.com/draliii/StratosphereLinuxIPS/blob/ac854a8e18ff2acef558036fa3c8cc764bbf2323/modules/p2ptrust/trust/trust_model.py
from dataclasses import dataclass
from typing import List, Optional

from fides.model.configuration import TrustModelConfiguration
from fides.model.peer_trust_data import PeerTrustData
from fides.model.threat_intelligence import ThreatIntelligence


@dataclass
class PeerReport:
    report_ti: ThreatIntelligence
    """Threat intelligence report."""

    reporter_trust: PeerTrustData
    """How much does Slips trust the reporter."""

    reporter_ti: Optional[ThreatIntelligence]
    """Threat intelligence that Slips has about the reporter."""


class TIAggregation:

    def __init__(self, config: TrustModelConfiguration):
        self.__peer_trust_weight = config.peer_trust_weight

    def compute_peer_trust(self, reporter_trust: PeerTrustData, reporter_ti: Optional[ThreatIntelligence]) -> float:
        """
        Compute the opinion value from a peer by multiplying his report data and his reputation.

        score: score by slips for the peer's IP address
        confidence: confidence by slips for the peer's IP address

        :param reporter_trust: trust value for the peer
        :param reporter_ti threat intelligence about the peer from Slips
        :return: The trust we should put in the report given by this peer
        """
        if reporter_ti is not None:
            return ((reporter_trust.service_trust * self.__peer_trust_weight) + (
                        reporter_ti.score * reporter_ti.confidence)) / 2
        else:
            return reporter_trust.service_trust

    @staticmethod
    def normalize_peer_reputations(peers: List[float]) -> List[float]:
        """
        Normalize peer reputation

        A list of peer reputations is scaled so that the reputations sum to one, while keeping the hierarchy.

        :param peers: a list of peer reputations
        :return: weighted trust value
        """

        # move trust values from [-1, 1] to [0, 1]
        normalized_trust = [(t + 1) / 2 for t in peers]

        normalize_net_trust_sum = sum(normalized_trust)

        weighted_trust = [nt / normalize_net_trust_sum for nt in normalized_trust]
        return weighted_trust

    def assemble_peer_opinion(self, data: List[PeerReport]) -> ThreatIntelligence:
        """
        Assemble reports given by all peers and compute the overall network opinion.

        The opinion is computed by using data from the database, which is a list of values: [report_score,
        report_confidence, reporter_reliability, reporter_score, reporter_confidence]. The reputation value for a peer
        is computed, then normalized across all peers, and the reports are multiplied by this value. The average peer
        reputation, final score and final confidence is returned

        :param data: a list of peers and their reports, in the format given by TrustDB.get_opinion_on_ip()
        :return: average peer reputation, final score and final confidence
        """

        reports = []
        reporters = []

        for d in data:
            reports.append(d.report_ti)
            reporters.append(self.compute_peer_trust(d.reporter_trust, d.reporter_ti))

        weighted_reporters = self.normalize_peer_reputations(reporters)

        combined_score = sum([r.score * w for r, w, in zip(reports, weighted_reporters)])
        combined_confidence = sum([max(0.0, r.confidence * w) for r, w, in zip(reports, reporters)]) / len(reporters)

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)
