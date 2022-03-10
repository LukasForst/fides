from typing import Dict, Tuple

from fides.evaluation.service.interaction import Satisfaction, Weight, SatisfactionLevels
from fides.messaging.model import PeerIntelligenceResponse
from fides.model.aliases import PeerId
from fides.model.peer_trust_data import PeerTrustData, TrustMatrix
from fides.model.threat_intelligence import SlipsThreatIntelligence


class TIEvaluation:
    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        """Evaluate interaction with all peers that gave intelligence responses."""
        raise NotImplemented('Use implementation rather then interface!')

    @staticmethod
    def _assert_keys(responses: Dict[PeerId, PeerIntelligenceResponse], trust_matrix: TrustMatrix):
        assert trust_matrix.keys() == responses.keys()


class EvenTIEvaluation(TIEvaluation):
    """Basic implementation for the TI evaluation, all responses are evaluated the same.
    This implementation corresponds with Salinity botnet.
    """

    def __init__(self, **kwargs):
        self.__kwargs = kwargs

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        return {p.peer_id: (p, SatisfactionLevels.Ok, Weight.INTELLIGENCE_DATA_REPORT) for p in
                trust_matrix.values()}


class DistanceBasedTIEvaluation(TIEvaluation):
    """Implementation that takes distance from the aggregated result and uses it as a penalisation."""

    def __init__(self, **kwargs):
        self.__kwargs = kwargs

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        satisfactions = {
            peer_id: self.__satisfaction(
                aggregated_score=aggregated_ti.score,
                aggregated_confidence=aggregated_ti.confidence,
                report_score=ti.intelligence.score,
                report_confidence=ti.intelligence.confidence
            )
            for peer_id, ti in responses.items()
        }

        return {p.peer_id: (p, satisfactions[p.peer_id], Weight.INTELLIGENCE_DATA_REPORT) for p in
                trust_matrix.values()}

    @staticmethod
    def __satisfaction(aggregated_score: float,
                       aggregated_confidence: float,
                       report_score: float,
                       report_confidence: float) -> Satisfaction:
        return (1 - (abs(aggregated_score - report_score) / 2) * report_confidence) * aggregated_confidence


class ThresholdTIEvaluation(TIEvaluation):
    """Employs DistanceBasedTIEvaluation when the confidence of the decision
    is higher than given threshold. Otherwise, it uses even evaluation.
    """

    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        self.__threshold = kwargs.get('threshold', 0.5)
        self.__even = EvenTIEvaluation()
        self.__distance = DistanceBasedTIEvaluation()

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        return self.__distance.evaluate(aggregated_ti, responses, trust_matrix) \
            if self.__threshold <= aggregated_ti.confidence \
            else self.__even.evaluate(aggregated_ti, responses, trust_matrix)


EvaluationStrategy = {
    'even': EvenTIEvaluation,
    'distance': DistanceBasedTIEvaluation,
    'threshold': ThresholdTIEvaluation
}
