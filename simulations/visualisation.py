from typing import Optional

import matplotlib.pyplot as plt

from simulations.environment import SimulationResult
from simulations.peer import PeerBehavior


def plot_simulation_result(
        result: SimulationResult,
        title_override: Optional[str] = None,
        save_output: Optional[str] = None
):
    time_scale = list(result.peer_trust_history.keys())

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))
    title = title_override if title_override else \
        f'ID: {result.simulation_id}\n' + \
        f'History Size: {result.simulation_config.service_history_size}\n' + \
        f'Interaction Evaluation: {type(result.simulation_config.evaluation_strategy).__name__}\n' + \
        f'TI Aggregation: {type(result.simulation_config.ti_aggregation_strategy).__name__}\n' + \
        f'Local Slips is {result.simulation_config.local_slips_acts_as.name}\n' + \
        f'There\'re {result.simulation_config.pre_trusted_peers_count} pre-trusted peers\n' + \
        f'Peers had initial reputation of {result.simulation_config.initial_reputation}'
    fig.suptitle(title)

    def plot_peers_lie_since(ax):
        if result.simulation_config.peers_distribution[PeerBehavior.MALICIOUS_PEER] != 0:
            ax.axvline(x=result.simulation_config.malicious_peers_lie_since, color='black', ls='--', lw=1,
                       label='Malicious Peers Lie')

    service_trust_plt = axs[0]
    plot_peers_lie_since(service_trust_plt)
    service_trust_plt.set_title('Service Trust')
    service_trust_plt.set_xlabel('Clicks')
    service_trust_plt.set_ylabel('Service Trust')
    service_trust_plt.set_ylim([0, 1])

    service_trust_progress = [result.peer_trust_history[click] for click in time_scale]

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
    plot_peers_lie_since(score_plt)
    score_plt.set_title('Target Score')
    score_plt.set_xlabel('Clicks')
    score_plt.set_ylabel('Score')
    score_plt.set_ylim([-1, 1])

    score_plt.axhline(0.0, color='red', linewidth=5.0)

    confidence_plt = axs[2]
    plot_peers_lie_since(confidence_plt)
    confidence_plt.set_title('Target Confidence')
    confidence_plt.set_xlabel('Clicks')
    confidence_plt.set_ylabel('Confidence')
    confidence_plt.set_ylim([0, 1])

    target_progress = [result.targets_history[click] for click in time_scale]
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

    plt.subplots_adjust(left=0.1,
                        right=0.7,
                        top=0.88,
                        bottom=0.03,
                        wspace=0.4,
                        hspace=0.4)
    if save_output is not None:
        plt.savefig(save_output)
    else:
        plt.show()
