from unittest import TestCase

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import ThresholdTIEvaluation, LocalCompareTIEvaluation
from fides.model.peer import PeerInfo
from fides.utils.logger import Logger
from simulations.model import FidesSetup, PreTrustedPeer
from simulations.peer import ConfidentCorrectPeer, SampleBehavior, LocalSlipsTIDb, ConfidentIncorrectPeer, \
    UncertainPeer, MaliciousPeer
from simulations.setup import build_config
from simulations.time_environment import TimeEnvironment
from simulations.utils import Click
from tests.load_fides import get_fides_stream

logger = Logger(__name__)


class TestBasicSimulationWithOneTypeOfPeer(TestCase):

    def test_run_basic_simulation_perfect_behavior(self):
        fides, stream, ti = get_fides_stream()
        perfect_behavior = SampleBehavior(1, 0, 1, 0)
        other_peers = [
            # ConfidentCorrectPeer(PeerInfo("#1", []), sample_base=perfect_behavior),
            # ConfidentCorrectPeer(PeerInfo("#2", []), sample_base=perfect_behavior),
            ConfidentCorrectPeer(PeerInfo("#1", []), fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
            ConfidentCorrectPeer(PeerInfo("#2", []), fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
        ]
        targets = {"google.com": 1, "microsoft.com": 1}
        env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

        env.run(fides.config.service_history_max_size)

        peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
        peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)

        logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")

    def test_with_overriden_config(self):
        ppeer = PeerInfo("#1", [])
        config = build_config(FidesSetup(
            default_reputation=0.5,
            pretrusted_peers=[PreTrustedPeer(ppeer.id, 0.9)],
            evaluation_strategy=ThresholdTIEvaluation(threshold=0.7),
            ti_aggregation_strategy=AverageConfidenceTIAggregation()
        ))
        fides, stream, ti = get_fides_stream(config=config)

        other_peers = [
            ConfidentCorrectPeer(ppeer, fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
            ConfidentCorrectPeer(PeerInfo("#2", []), fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
        ]
        targets = {"google.com": 1, "microsoft.com": 1}
        env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

        env.run(fides.config.service_history_max_size)

        peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
        peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)

        logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")

    def test_with_overriden_config_and_local_ti_db(self):
        targets = {"google.com": 1, "microsoft.com": 1}
        ti_db = LocalSlipsTIDb(target_baseline=targets)

        ppeer = PeerInfo("PRE-TRUSTED", [])
        config = build_config(FidesSetup(
            default_reputation=0.5,
            pretrusted_peers=[PreTrustedPeer(ppeer.id, 0.9)],
            evaluation_strategy=LocalCompareTIEvaluation(),
            ti_aggregation_strategy=AverageConfidenceTIAggregation()
        ))
        fides, stream, ti = get_fides_stream(config=config, ti_db=ti_db)

        other_peers = [
            ConfidentCorrectPeer(ppeer, fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
            ConfidentCorrectPeer(PeerInfo("CORRECT", []), fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
            UncertainPeer(PeerInfo("UNCERTAIN", []), fides.config.service_history_max_size,
                          fides.config.recommendations.peers_max_count),
            ConfidentIncorrectPeer(PeerInfo("INCORRECT", []), fides.config.service_history_max_size,
                                   fides.config.recommendations.peers_max_count),
        ]
        env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

        env.run(fides.config.service_history_max_size)

        peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
        peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)
        peer3 = fides.trust_db.get_peer_trust_data(other_peers[2].peer_info)
        peer4 = fides.trust_db.get_peer_trust_data(other_peers[3].peer_info)

        logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")

    def test_see_difference_honest_malicious(self):
        targets = {"google.com": 1}
        ti_db = LocalSlipsTIDb(target_baseline=targets)

        config = build_config(FidesSetup(
            default_reputation=0,
            pretrusted_peers=[],
            evaluation_strategy=LocalCompareTIEvaluation(),
            service_history_max_size=100,
            ti_aggregation_strategy=AverageConfidenceTIAggregation()
        ))
        fides, stream, ti = get_fides_stream(config=config, ti_db=ti_db)

        other_peers = [
            ConfidentCorrectPeer(PeerInfo("CORRECT", []), fides.config.service_history_max_size,
                                 fides.config.recommendations.peers_max_count),
            MaliciousPeer(PeerInfo("MALICIOUS", []),
                          fides.config.service_history_max_size,
                          fides.config.recommendations.peers_max_count, list(targets.keys()), epoch_starts_lying=50),
        ]
        env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

        peer_trust_history = {}

        def update_trust_history(click: Click):
            peer_trust_history[click] = {}
            peer_trust_history[click]["CORRECT"] = fides.trust_db.get_peer_trust_data("CORRECT").service_trust
            peer_trust_history[click]["MALICIOUS"] = fides.trust_db.get_peer_trust_data("MALICIOUS").service_trust
            peer_trust_history[click]["google.com"] = ti_db.get_for("google.com").score

        env.run(fides.config.service_history_max_size, epoch_callback=update_trust_history)

        peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
        peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)

        logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")
