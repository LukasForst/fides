import logging
from typing import Dict, Tuple
from unittest import TestCase

from fides.evaluation.ti_evaluation import ThresholdTIEvaluation, TIEvaluation, LocalCompareTIEvaluation
from fides.model.peer import PeerInfo
from simulations.peer import ConfidentCorrectPeer, SampleBehavior, PeerBehavior, LocalSlipsTIDb, ConfidentIncorrectPeer, \
    UncertainPeer
from simulations.time_environment import TimeEnvironment
from simulations.utils import build_config, FidesSetup, PreTrustedPeer
from tests.load_fides import get_fides_stream

logger = logging.getLogger(__name__)


def setup_simulation(
        number_of_other_peers: int,
        percentage_of_pretrusted_trusted_peers: float,  # 0.0 -> 1.0
        network_topology: Dict[PeerBehavior, float],  # behavior to fraction
        targets: Tuple[int, int],  # being, malicious
        gaining_trust_window: int,
        evaluation_strategy: TIEvaluation,

):
    pass


class TestBasicSimulationWithOneTypeOfPeer(TestCase):

    def test_run_basic_simulation_perfect_behavior(self):
        fides, stream, ti = get_fides_stream()
        perfect_behavior = SampleBehavior(1, 0, 1, 0)
        other_peers = [
            # ConfidentCorrectPeer(PeerInfo("#1", []), sample_base=perfect_behavior),
            # ConfidentCorrectPeer(PeerInfo("#2", []), sample_base=perfect_behavior),
            ConfidentCorrectPeer(PeerInfo("#1", [])),
            ConfidentCorrectPeer(PeerInfo("#2", [])),
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
            evaluation_strategy=ThresholdTIEvaluation(threshold=0.7)
        ))
        fides, stream, ti = get_fides_stream(config=config)

        other_peers = [
            ConfidentCorrectPeer(ppeer),
            ConfidentCorrectPeer(PeerInfo("#2", [])),
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
            evaluation_strategy=LocalCompareTIEvaluation()
        ))
        fides, stream, ti = get_fides_stream(config=config, ti_db=ti_db)

        other_peers = [
            ConfidentCorrectPeer(ppeer),
            ConfidentCorrectPeer(PeerInfo("CORRECT", [])),
            UncertainPeer(PeerInfo("UNCERTAIN", [])),
            ConfidentIncorrectPeer(PeerInfo("INCORRECT", [])),
        ]
        env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

        env.run(fides.config.service_history_max_size)

        peer1 = fides.trust_db.get_peer_trust_data(other_peers[0].peer_info)
        peer2 = fides.trust_db.get_peer_trust_data(other_peers[1].peer_info)
        peer3 = fides.trust_db.get_peer_trust_data(other_peers[2].peer_info)
        peer4 = fides.trust_db.get_peer_trust_data(other_peers[3].peer_info)

        logger.info(f"Simulation done - {peer1}, {peer2}, {ti}")
