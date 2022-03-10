from typing import Dict, Tuple, Callable, Optional

from fides.evaluation.service.interaction import Satisfaction, Weight, SatisfactionLevels
from fides.messaging.model import PeerIntelligenceResponse
from fides.model.aliases import PeerId, Target
from fides.model.peer_trust_data import PeerTrustData, TrustMatrix
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.utils.logger import Logger

logger = Logger(__name__)


class TIEvaluation:
    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix,
                 **kwargs,
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
        self.__satisfaction = kwargs.get('satisfaction', SatisfactionLevels.Ok)

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix,
                 **kwargs,
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        return {p.peer_id: (p, self.__satisfaction, Weight.INTELLIGENCE_DATA_REPORT) for p in
                trust_matrix.values()}


class DistanceBasedTIEvaluation(TIEvaluation):
    """Implementation that takes distance from the aggregated result and uses it as a penalisation."""

    def __init__(self, **kwargs):
        self.__kwargs = kwargs

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix,
                 **kwargs,
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)
        return self._build_evaluation(
            baseline_score=aggregated_ti.score,
            baseline_confidence=aggregated_ti.confidence,
            responses=responses,
            trust_matrix=trust_matrix
        )

    def _build_evaluation(
            self,
            baseline_score: float,
            baseline_confidence: float,
            responses: Dict[PeerId, PeerIntelligenceResponse],
            trust_matrix: TrustMatrix,
    ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        satisfactions = {
            peer_id: self._satisfaction(
                baseline_score=baseline_score,
                baseline_confidence=baseline_confidence,
                report_score=ti.intelligence.score,
                report_confidence=ti.intelligence.confidence
            )
            for peer_id, ti in responses.items()
        }

        return {p.peer_id: (p, satisfactions[p.peer_id], Weight.INTELLIGENCE_DATA_REPORT) for p in
                trust_matrix.values()}

    @staticmethod
    def _satisfaction(baseline_score: float,
                      baseline_confidence: float,
                      report_score: float,
                      report_confidence: float) -> Satisfaction:
        return (1 - (abs(baseline_score - report_score) / 2) * report_confidence) * baseline_confidence


class LocalCompareTIEvaluation(DistanceBasedTIEvaluation):
    """This strategy compares received threat intelligence with the threat intelligence from local database.

    Uses the same penalisation system as DistanceBasedTIEvaluation with the difference that as a baseline,
    it does not use aggregated value, but rather local intelligence.

    If it does not find threat intelligence for the target, it falls backs to DistanceBasedTIEvaluation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__default_ti_getter = kwargs.get('default_ti_getter', None)

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix,
                 ti_getter: Optional[Callable[[Target], SlipsThreatIntelligence]] = None,
                 **kwargs,
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        ti_getter = ti_getter if ti_getter else self.__default_ti_getter
        if not ti_getter:
            raise Exception('No Threat Intelligence getter given, ' +
                            'use different evaluation strategy when the local TI is not available!')

        ti = ti_getter(aggregated_ti.target)
        if not ti:
            logger.warn(f'No local threat intelligence found for target {aggregated_ti.target}! ' +
                        'Falling back to DistanceBasedTIEvaluation.')
            ti = aggregated_ti

        return self._build_evaluation(
            baseline_score=ti.score,
            baseline_confidence=ti.confidence,
            responses=responses,
            trust_matrix=trust_matrix
        )


class ThresholdTIEvaluation(TIEvaluation):
    """Employs DistanceBasedTIEvaluation when the confidence of the decision
    is higher than given threshold. Otherwise, it uses even evaluation.
    """

    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        self.__threshold = kwargs.get('threshold', 0.5)
        self.__lower = kwargs.get('lower', EvenTIEvaluation())
        self.__higher = kwargs.get('higher', DistanceBasedTIEvaluation())

    def evaluate(self,
                 aggregated_ti: SlipsThreatIntelligence,
                 responses: Dict[PeerId, PeerIntelligenceResponse],
                 trust_matrix: TrustMatrix,
                 **kwargs,
                 ) -> Dict[PeerId, Tuple[PeerTrustData, Satisfaction, Weight]]:
        super()._assert_keys(responses, trust_matrix)

        return self.__higher.evaluate(aggregated_ti, responses, trust_matrix) \
            if self.__threshold <= aggregated_ti.confidence \
            else self.__lower.evaluate(aggregated_ti, responses, trust_matrix)


EvaluationStrategy = {
    'even': EvenTIEvaluation,
    'distance': DistanceBasedTIEvaluation,
    'localDistance': LocalCompareTIEvaluation,
    'threshold': ThresholdTIEvaluation
}
