import random
from typing import Dict, List

from fides.model.aliases import Target, Score
from fides.model.peer import PeerInfo
from simulations.peer import PeerBehavior, Peer, ConfidentCorrectPeer, UncertainPeer, ConfidentIncorrectPeer, \
    MaliciousPeer
from simulations.utils import Click


def generate_targets(being: int, malicious: int) -> Dict[Target, Score]:
    being = [(f"BEING #{i}", 1) for i in range(being)]
    malicious = [(f"MALICIOUS #{i}", -1) for i in range(malicious)]

    all_targets = being + malicious

    random.shuffle(all_targets)
    return {target: score for (target, score) in all_targets}


def generate_peers(
        distribution: Dict[PeerBehavior, int],
        malicious_lie_about: List[Target],
        malicious_start_lie_at: Click
) -> List[Peer]:
    peers = []

    for idx, (peer_type, count) in enumerate(distribution.items()):

        if peer_type == PeerBehavior.CONFIDENT_CORRECT:
            p = [ConfidentCorrectPeer(PeerInfo(f"CONFIDENT_CORRECT #{i}", [])) for i in range(count)]
        elif peer_type == PeerBehavior.UNCERTAIN_PEER:
            p = [UncertainPeer(PeerInfo(f" UNCERTAIN_PEER #{i}", [])) for i in range(count)]
        elif peer_type == PeerBehavior.CONFIDENT_INCORRECT:
            p = [ConfidentIncorrectPeer(PeerInfo(f"CONFIDENT_INCORRECT #{i}", [])) for i in range(count)]
        elif peer_type == PeerBehavior.MALICIOUS_PEER:
            p = [MaliciousPeer(
                PeerInfo(f"MALICIOUS_PEER #{i}", []),
                0, malicious_lie_about, malicious_start_lie_at) for i in range(count)]
        else:
            raise ValueError()

        peers.extend(p)

    random.shuffle(peers)
    return peers
