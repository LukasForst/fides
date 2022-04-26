import logging
from typing import List, Dict

import matplotlib.pyplot as plt

from fides.evaluation.ti_aggregation import WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import DistanceBasedTIEvaluation
from fides.model.aliases import Target, Score, PeerId
from fides.model.configuration import TrustModelConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistance.threat_intelligence import ThreatIntelligenceDatabase
from simulations.generators import generate_targets, generate_peers
from simulations.peer import LocalSlipsTIDb, PeerBehavior, Peer, behavioral_map
from simulations.time_environment import TimeEnvironment
from simulations.utils import build_config, FidesSetup, Click, PreTrustedPeer
from tests.load_fides import get_fides_stream

logger = logging.getLogger(__name__)


def run_simulation(
        config: TrustModelConfiguration,
        local_ti_db: ThreatIntelligenceDatabase,
        targets: Dict[Target, Score],
        other_peers: List[Peer],
        simulation_time: Click
) -> (Dict[Click, Dict[PeerId, float]], Dict[Click, Dict[Target, SlipsThreatIntelligence]]):
    fides, stream, ti = get_fides_stream(config=config, ti_db=local_ti_db)

    env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

    peer_trust_history: Dict[Click, Dict[PeerId, float]] = {}
    targets_history: Dict[Click, Dict[Target, SlipsThreatIntelligence]] = {}

    def epoch_callback(click: Click):
        peer_trust_history[click] = {}
        targets_history[click] = {}

        for peer in other_peers:
            peer_trust_history[click][peer.peer_info.id] = \
                fides.trust_db.get_peer_trust_data(peer.peer_info.id).service_trust

        for target in targets.keys():
            targets_history[click][target] = ti[target]

    env.run(simulation_time, epoch_callback=epoch_callback)

    return peer_trust_history, targets_history


def plot_correct_malicious_local_compare():
    targets = generate_targets(being=1, malicious=1)
    other_peers = generate_peers(
        distribution={
            PeerBehavior.CONFIDENT_CORRECT: 2,
            PeerBehavior.UNCERTAIN_PEER: 0,
            PeerBehavior.CONFIDENT_INCORRECT: 0,
            PeerBehavior.MALICIOUS_PEER: 1,
        },
        malicious_lie_about=list(targets.keys()),
        malicious_start_lie_at=50
    )

    local_slips_acts_as = PeerBehavior.UNCERTAIN_PEER
    ti_db = LocalSlipsTIDb(
        target_baseline=targets,
        behavior=behavioral_map[local_slips_acts_as]
    )
    pretrusted_peers = 0
    config = build_config(FidesSetup(
        default_reputation=0.0,
        pretrusted_peers=[PreTrustedPeer(p.peer_info.id, 0.95)
                          for p in other_peers if p.label == PeerBehavior.CONFIDENT_CORRECT
                          ][:pretrusted_peers],
        # evaluation_strategy=LocalCompareTIEvaluation(),
        # evaluation_strategy=MaxConfidenceTIEvaluation(),
        evaluation_strategy=DistanceBasedTIEvaluation(),
        # evaluation_strategy=ThresholdTIEvaluation(threshold=0.5),
        # evaluation_strategy=EvenTIEvaluation(),
        # ti_aggregation_strategy=AverageConfidenceTIAggregation(),
        ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=StdevFromScoreTIAggregation(),
        service_history_max_size=100
    ))

    peer_trust_history, targets_history = run_simulation(
        config=config,
        local_ti_db=ti_db,
        targets=targets,
        other_peers=other_peers,
        simulation_time=config.service_history_max_size * 2
    )
    time_scale = list(peer_trust_history.keys())

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle(
        f'{type(config.interaction_evaluation_strategy).__name__} &'
        f'{type(config.ti_aggregation_strategy).__name__}'
    )

    service_trust_plt = axs[0]
    service_trust_plt.set_title('Service Trust')
    service_trust_plt.set_xlabel('Clicks')
    service_trust_plt.set_ylabel('Service Trust')
    service_trust_plt.set_ylim([0, 1])

    service_trust_progress = [peer_trust_history[click] for click in time_scale]
    other_peers.sort(key=lambda x: x.peer_info.id)
    for peer in other_peers:
        service_trust_plt.plot(time_scale, [c[peer.peer_info.id] for c in service_trust_progress],
                               label=peer.peer_info.id)

    service_trust_plt.legend(loc=(1.04, 0), borderaxespad=0)

    score_plt = axs[1]
    score_plt.set_title('Target Score')
    score_plt.set_xlabel('Clicks')
    score_plt.set_ylabel('Score')
    score_plt.set_ylim([-1, 1])

    score_plt.axhline(0.0, color='red', linewidth=5.0)

    confidence_plt = axs[2]
    confidence_plt.set_title('Target Confidence')
    confidence_plt.set_xlabel('Clicks')
    confidence_plt.set_ylabel('Confidence')
    confidence_plt.set_ylim([0, 1])

    target_progress = [targets_history[click] for click in time_scale]
    other_peers.sort(key=lambda x: x.peer_info.id)
    for target in targets:
        score_plt.plot(time_scale, [c[target].score for c in target_progress], label=target)
        confidence_plt.plot(time_scale, [c[target].confidence for c in target_progress], label=target)

    score_plt.legend(loc=(1.04, 0), borderaxespad=0)
    confidence_plt.legend(loc=(1.04, 0), borderaxespad=0)

    plt.subplots_adjust(right=0.7)
    plt.show()


if __name__ == '__main__':
    plot_correct_malicious_local_compare()
