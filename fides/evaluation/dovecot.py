# This file, class and computational algorithm was inspired by Draliii's implementation of Trust Model for local
# network peer-to-peer module for Slips
# https://github.com/draliii/StratosphereLinuxIPS/blob/ac854a8e18ff2acef558036fa3c8cc764bbf2323/modules/p2ptrust/trust/trust_model.py
from fides.model.threat_intelligence import ThreatIntelligence


class Dovecot:

    # TODO: [!] migrate this class so it uses data structures from Fides

    def __init__(self, reliability_weight: float):
        self.__reliability_weight = reliability_weight

    def compute_peer_trust(self, reliability: float, score: float, confidence: float) -> float:
        """
        Compute the opinion value from a peer by multiplying his report data and his reputation

        :param reliability: trust value for the peer, obtained from the go level
        :param score: score by slips for the peer's IP address
        :param confidence: confidence by slips for the peer's IP address
        :return: The trust we should put in the report given by this peer
        """

        return ((reliability * self.__reliability_weight) + (score * confidence)) / 2

    @staticmethod
    def normalize_peer_reputations(peers: list) -> (float, float, list):
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

    def assemble_peer_opinion(self, data: list) -> ThreatIntelligence:
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

        for peer_report in data:
            report_score, report_confidence, reporter_reliability, reporter_score, reporter_confidence = peer_report
            reports.append((report_score, report_confidence))
            reporters.append(self.compute_peer_trust(reporter_reliability, reporter_score, reporter_confidence))

        weighted_reporters = self.normalize_peer_reputations(reporters)

        combined_score = sum([r[0] * w for r, w, in zip(reports, weighted_reporters)])
        combined_confidence = sum([max(0, r[1] * w) for r, w, in zip(reports, reporters)]) / len(reporters)

        return ThreatIntelligence(score=combined_score, confidence=combined_confidence)
