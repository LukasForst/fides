import matplotlib.pyplot as plt

from fides.evaluation.ti_aggregation import PeerReport, AverageConfidenceTIAggregation
from fides.model.aliases import PeerId
from fides.model.peer import PeerInfo
from fides.model.peer_trust_data import PeerTrustData
from fides.model.threat_intelligence import ThreatIntelligence


def _peer_trust(peer_id: PeerId, service_trust: float) -> PeerTrustData:
    return PeerTrustData(
        PeerInfo(peer_id, []),
        False,
        service_trust=service_trust,
        reputation=0,
        recommendation_trust=0,
        competence_belief=0,
        integrity_belief=0,
        initial_reputation_provided_by_count=0,
        service_history=[],
        recommendation_history=[]
    )


def get_data():
    size = 10
    confidences = [1.0 for _ in range(size)]
    # confidences = [i / 10 for i in range(size)]
    trusts = [i / 10 for i in range(size)]
    # trusts = [1.0] * len(confidences)
    # trusts = confidences.copy()
    trusts.reverse()
    data = []
    for trust, confidence in zip(trusts, confidences):
        # for trust, confidence in itertools.product(trusts, confidences):
        reports = [
            PeerReport(
                report_ti=ThreatIntelligence(score=1.0, confidence=1.0),
                reporter_trust=_peer_trust("#1", service_trust=1.0)
            ),
            PeerReport(
                report_ti=ThreatIntelligence(score=1.0, confidence=confidence),
                reporter_trust=_peer_trust("#2", service_trust=trust)
            )
        ]
        aggregated = AverageConfidenceTIAggregation().assemble_peer_opinion(reports)
        data.append({'t': trust, 'c': confidence, 'as': aggregated.score, 'ac': aggregated.confidence})
    return data


def plot2():
    scale = [i / 10 for i in range(10)]

    d = get_data()
    trusts = [e['t'] for e in d]
    confidences = [e['c'] for e in d]
    aggregated_scores = [e['as'] for e in d]
    aggregated_confidences = [e['ac'] for e in d]

    print(d)
    plt.plot(scale, aggregated_confidences, label='Aggregated Confidence')
    plt.plot(scale, aggregated_scores, label='Aggregated Score')
    plt.plot(scale, confidences, label='Confidence')
    plt.plot(scale, trusts, label='Trust')

    plt.legend()
    plt.show()


if __name__ == '__main__':
    plot2()
