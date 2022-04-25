from dataclasses import dataclass
from typing import List

import numpy as np

from fides.model.peer_trust_data import PeerTrustData
from fides.model.threat_intelligence import ThreatIntelligence


@dataclass
class PeerReport:
    report_ti: ThreatIntelligence
    """Threat intelligence report."""

    reporter_trust: PeerTrustData
    """How much does Slips trust the reporter."""


class TIAggregation:

    @staticmethod
    def assemble_peer_opinion(data: List[PeerReport]) -> ThreatIntelligence:
        """
        Assemble reports given by all peers and compute the overall network opinion.

        :param data: a list of peers and their reports, in the format given by TrustDB.get_opinion_on_ip()
        :return: final score and final confidence
        """
        # TODO select a single aggregation function
        return TIAggregation._assemble_peer_opinion_average(data)
        # return TIAggregation._assemble_peer_opinion_weighted(data)
        # return TIAggregation._assemble_peer_opinion_stdev(data)

    @staticmethod
    def _assemble_peer_opinion_average(data: List[PeerReport]) -> ThreatIntelligence:
        reports_ti = [d.report_ti for d in data]
        reporters_trust = [d.reporter_trust.service_trust for d in data]

        normalize_net_trust_sum = sum(reporters_trust)
        weighted_reporters = [trust / normalize_net_trust_sum for trust in reporters_trust]

        combined_score = sum(r.score * w for r, w, in zip(reports_ti, weighted_reporters))
        combined_confidence = sum(r.confidence * w for r, w, in zip(reports_ti, reporters_trust)) / len(reporters_trust)

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)

    @staticmethod
    def _assemble_peer_opinion_weighted(data: List[PeerReport]) -> ThreatIntelligence:
        reports_ti = [d.report_ti for d in data]
        reporters_trust = [d.reporter_trust.service_trust for d in data]

        normalize_net_trust_sum = sum(reporters_trust)
        weighted_reporters = [trust / normalize_net_trust_sum for trust in reporters_trust]

        combined_score = sum(r.score * w for r, w, in zip(reports_ti, weighted_reporters))
        combined_confidence = sum(r.confidence * w for r, w, in zip(reports_ti, weighted_reporters))

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)

    @staticmethod
    def _assemble_peer_opinion_stdev(data: List[PeerReport]) -> ThreatIntelligence:
        reports_ti = [d.report_ti for d in data]
        reporters_trust = [d.reporter_trust.service_trust for d in data]

        normalize_net_trust_sum = sum(reporters_trust)
        weighted_reporters = [trust / normalize_net_trust_sum for trust in reporters_trust]

        merged_score = [r.score * r.confidence * w for r, w, in zip(reports_ti, weighted_reporters)]
        combined_score = sum(merged_score)
        combined_confidence = 1 - np.std(merged_score)

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)
