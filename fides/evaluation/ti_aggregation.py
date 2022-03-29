from dataclasses import dataclass
from typing import List, Optional

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

    @staticmethod
    def assemble_peer_opinion(data: List[PeerReport]) -> ThreatIntelligence:
        """
        Assemble reports given by all peers and compute the overall network opinion.

        :param data: a list of peers and their reports, in the format given by TrustDB.get_opinion_on_ip()
        :return: final score and final confidence
        """

        reports_ti = [d.report_ti for d in data]
        reporter_trust = [d.reporter_trust.service_trust for d in data]

        normalize_net_trust_sum = sum(reporter_trust)
        weighted_reporters = [nt / normalize_net_trust_sum for nt in reporter_trust]

        combined_score = sum(r.score * w for r, w, in zip(reports_ti, weighted_reporters))
        combined_confidence = sum(r.confidence * w for r, w, in zip(reports_ti, reporter_trust)) / len(reporter_trust)

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)
