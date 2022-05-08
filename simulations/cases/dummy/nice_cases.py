import matplotlib.pyplot as plt

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation
from fides.model.peer import PeerInfo
from fides.utils.logger import Logger
from simulations.model import FidesSetup
from simulations.peer import LocalSlipsTIDb, ConfidentCorrectPeer, MaliciousPeer, UncertainPeer, ConfidentIncorrectPeer, \
    SampleBehavior
from simulations.setup import build_config
from simulations.time_environment import TimeEnvironment
from simulations.utils import Click
from tests.load_fides import get_fides_stream

logger = Logger(__name__)


def plot_correct_malicious_local_compare():
    targets = {"google.com": 1}
    ti_db = LocalSlipsTIDb(target_baseline=targets, behavior=SampleBehavior(score_mean=0.8,
                                                                            score_deviation=0.2,
                                                                            confidence_mean=0.8,
                                                                            confidence_deviation=0.2))

    config = build_config(FidesSetup(
        default_reputation=0,
        pretrusted_peers=[],
        # evaluation_strategy=LocalCompareTIEvaluation(),
        evaluation_strategy=MaxConfidenceTIEvaluation(),
        # evaluation_strategy=DistanceBasedTIEvaluation(),
        # evaluation_strategy=ThresholdTIEvaluation(),
        service_history_max_size=100,
        ti_aggregation_strategy=AverageConfidenceTIAggregation()
        # ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=StdevFromScoreTIAggregation()
    ))
    fides, stream, ti = get_fides_stream(config=config, ti_db=ti_db)

    other_peers = [
        # ConfidentCorrectPeer(PeerInfo("PRE-TRUSTED", [])),
        ConfidentCorrectPeer(PeerInfo("CORRECT", []), fides.config.service_history_max_size,
                             fides.config.recommendations.peers_max_count),
        UncertainPeer(PeerInfo("UNCERTAIN", []), fides.config.service_history_max_size,
                      fides.config.recommendations.peers_max_count),
        ConfidentIncorrectPeer(PeerInfo("INCORRECT", []), fides.config.service_history_max_size,
                               fides.config.recommendations.peers_max_count),
        MaliciousPeer(PeerInfo("MALICIOUS", []), fides.config.service_history_max_size,
                      fides.config.recommendations.peers_max_count, list(targets.keys()), epoch_starts_lying=50),
    ]
    env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

    peer_trust_history = {}

    def update_trust_history(click: Click):
        peer_trust_history[click] = {}
        # peer_trust_history[click]["PRE-TRUSTED"] = fides.trust_db.get_peer_trust_data("PRE-TRUSTED").service_trust
        peer_trust_history[click]["CORRECT"] = fides.trust_db.get_peer_trust_data("CORRECT").service_trust
        peer_trust_history[click]["MALICIOUS"] = fides.trust_db.get_peer_trust_data("MALICIOUS").service_trust
        peer_trust_history[click]["UNCERTAIN"] = fides.trust_db.get_peer_trust_data("UNCERTAIN").service_trust
        peer_trust_history[click]["INCORRECT"] = fides.trust_db.get_peer_trust_data("INCORRECT").service_trust
        peer_trust_history[click]["s-google.com"] = ti_db.get_for("google.com").score
        peer_trust_history[click]["c-google.com"] = ti_db.get_for("google.com").confidence

    env.run(fides.config.service_history_max_size * 2, epoch_callback=update_trust_history)

    peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
    peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)

    logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")

    scale = list(peer_trust_history.keys())
    # pretrustedt_progress = [click_data["PRE-TRUSTED"] for click_data in peer_trust_history.values()]
    correct_progress = [click_data["CORRECT"] for click_data in peer_trust_history.values()]
    malicious_progress = [click_data["MALICIOUS"] for click_data in peer_trust_history.values()]
    uncertain_progress = [click_data["UNCERTAIN"] for click_data in peer_trust_history.values()]
    incorrect_progress = [click_data["INCORRECT"] for click_data in peer_trust_history.values()]
    target_score = [click_data["s-google.com"] for click_data in peer_trust_history.values()]
    target_confidence = [click_data["c-google.com"] for click_data in peer_trust_history.values()]

    # plt.plot(scale, pretrustedt_progress, label='Pre-trusted Peer')
    plt.plot(scale, correct_progress, label='Correct Peer')
    plt.plot(scale, malicious_progress, label='Malicious Peer')
    plt.plot(scale, uncertain_progress, label='Uncertain Peer')
    plt.plot(scale, incorrect_progress, label='Incorrect Peer')
    # plt.plot(scale, target_score, label='Target Score')
    # plt.plot(scale, target_confidence, label='Target Confidence')

    plt.xlabel('Clicks')
    plt.ylabel('Service Trust')
    plt.title(f'{type(config.interaction_evaluation_strategy).__name__} strategy')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    plot_correct_malicious_local_compare()
