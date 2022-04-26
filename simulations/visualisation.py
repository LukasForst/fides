from typing import Dict

import matplotlib.pyplot as plt

from fides.model.aliases import Target, PeerId
from fides.model.threat_intelligence import SlipsThreatIntelligence
from simulations.utils import Click


def plot_simulation_result(
        title: str,
        peer_trust_history: Dict[Click, Dict[PeerId, float]],
        targets_history: Dict[Click, Dict[Target, SlipsThreatIntelligence]]):
    time_scale = list(peer_trust_history.keys())

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle(title)

    service_trust_plt = axs[0]
    service_trust_plt.set_title('Service Trust')
    service_trust_plt.set_xlabel('Clicks')
    service_trust_plt.set_ylabel('Service Trust')
    service_trust_plt.set_ylim([0, 1])

    service_trust_progress = [peer_trust_history[click] for click in time_scale]

    other_peers = set()
    for time in service_trust_progress:
        other_peers.update(time.keys())
    other_peers = list(other_peers)
    other_peers.sort()
    for peer_id in other_peers:
        service_trust_plt.plot(time_scale, [c[peer_id] for c in service_trust_progress],
                               label=peer_id)

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
    targets = set()
    for time in target_progress:
        targets.update(time.keys())
    targets = list(targets)
    targets.sort()

    for target in targets:
        score_plt.plot(time_scale, [c[target].score for c in target_progress], label=target)
        confidence_plt.plot(time_scale, [c[target].confidence for c in target_progress], label=target)

    score_plt.legend(loc=(1.04, 0), borderaxespad=0)
    confidence_plt.legend(loc=(1.04, 0), borderaxespad=0)

    plt.subplots_adjust(right=0.7)
    plt.show()
