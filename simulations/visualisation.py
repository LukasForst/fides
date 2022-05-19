import dataclasses
from typing import Optional, Dict, List, Any, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker

from simulations.environment import SimulationResult
from simulations.evaluation import HardnessEvaluationMatrix
from simulations.peer import PeerBehavior


@dataclasses.dataclass
class HardnessPlotParams:
    matrix: HardnessEvaluationMatrix
    y_label: str
    plot_level_one_line: bool = False
    moving_mean_window: int = 1
    scatter_instead_of_plot: bool = False


def plot_hardness_evaluation_all(
        hardness_matrices: Union[HardnessPlotParams, List[HardnessPlotParams]],
        save_output: Optional[str] = None,
        title: Optional[str] = 'Performance of each interaction evaluation function'
):
    hardness_matrices = hardness_matrices if type(hardness_matrices) is list else [hardness_matrices]
    all_used_ti_evaluations = {label.split('|')[0] for label in hardness_matrices[0].matrix.keys()}
    all_used_ti_evaluations = sorted(list(all_used_ti_evaluations))

    fig, axs = plt.subplots(len(all_used_ti_evaluations), len(hardness_matrices),
                            figsize=(7 * len(hardness_matrices), round(6.25 * len(all_used_ti_evaluations))),
                            squeeze=False
                            )
    use_fig_legend = len(axs) != 1
    if title is not None:
        fig.suptitle(title, fontsize=22)

    for idx, hardness_plot in enumerate(hardness_matrices):
        axes = {ti_evaluation: axs[i, idx] for i, ti_evaluation in enumerate(all_used_ti_evaluations)}
        plot_hardness_evaluation(hardness_plot.matrix, axes, hardness_plot.y_label, hardness_plot.plot_level_one_line,
                                 hardness_plot.moving_mean_window, hardness_plot.scatter_instead_of_plot,
                                 plot_legend=not use_fig_legend)

    if use_fig_legend:
        lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
        handles, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        final_handles, final_labels = [], []
        for h, l in zip(handles, labels):
            if l in final_labels:
                continue
            final_handles.append(h)
            final_labels.append(l)

        final_labels, final_handles = zip(*sorted(zip(final_labels, final_handles), key=lambda t: t[0]))
        fig.legend(final_handles, final_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95))

    plt.subplots_adjust(left=0.1,
                        right=0.97,
                        top=0.85,
                        bottom=0.05,
                        wspace=0.3,
                        hspace=0.3)

    if save_output is not None:
        plt.savefig(save_output)
    else:
        plt.show()


def plot_hardness_evaluation(
        matrix: HardnessEvaluationMatrix,
        axes: Dict[str, Any],
        y_label: str,
        plot_level_one_line: bool = False,
        moving_mean_window: int = 2,
        scatter_instead_of_plot: bool = False,
        plot_legend: bool = False
):
    global_max_y = max(max(data.values()) for data in matrix.values())
    global_max_x = max(max(data.keys()) for data in matrix.values())
    global_min_x = min(min(data.keys()) for data in matrix.values())
    x_offset = (global_max_x - global_min_x) / 20
    x_lim = [global_max_x + x_offset, global_min_x - x_offset]
    sorted_labels = sorted(matrix.keys())
    for idx, label in enumerate(sorted_labels):
        data = matrix[label]
        evaluation, aggregation, initial_trust = label.split('|')
        ax = axes[evaluation]

        sorted_keys = sorted(list(data.keys()), reverse=False)
        values = [data[i] for i in sorted_keys]

        if scatter_instead_of_plot:
            ax.scatter(sorted_keys, values, label=f'{aggregation}, {initial_trust}')
        else:
            ax.plot(sorted_keys, moving_average(values, window=moving_mean_window),
                    label=f'{aggregation}, {initial_trust}')

        if 'Correct Peers in Network' in y_label:
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.set_title(f'{y_label}')
        else:
            ax.set_title(f'{evaluation} - {y_label}')

        ax.set_xlabel('Environment Hardness')
        ax.set_ylabel(y_label)
        ax.set_xlim(x_lim)
        if plot_level_one_line:
            ax.set_ylim([0, 2])
        else:
            y_lim = 100 if global_max_y > 1 else 1
            ax.set_ylim([0, y_lim])
        # this is the case with aggregated trust in network and in that case we need more granularity
        # if sorted_keys[-1] < 20:
        #     ax.set_xticks(np.arange(sorted_keys[0], sorted_keys[-1], 0.5))

        if plot_level_one_line:
            ax.axhline(1.0, color='red', linewidth=1.0)
        if plot_legend:
            handles, labels = ax.get_legend_handles_labels()
            # sort both labels and handles by labels
            labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
            ax.legend(handles, labels)
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)


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
        score_plt.plot(time_scale, [c[target].score for c in target_progress],
                       label=target, alpha=0.4, linewidth=0.5)
        score_plt.plot(time_scale, moving_average([c[target].score for c in target_progress]),
                       label=f'{target} (MM)')

        confidence_plt.plot(time_scale, [c[target].confidence for c in target_progress],
                            label=target, alpha=0.4, linewidth=0.5)
        confidence_plt.plot(moving_average([c[target].confidence for c in target_progress]),
                            label=f'{target} (MM)')

    score_plt.legend(loc=(1.04, 0), borderaxespad=0)
    confidence_plt.legend(loc=(1.04, 0), borderaxespad=0)

    plt.subplots_adjust(left=0.1,
                        right=0.7,
                        top=0.87,
                        bottom=0.03,
                        wspace=0.4,
                        hspace=0.4)
    if save_output:
        plt.savefig(save_output)
    else:
        plt.show()


def moving_average(data, window=10):
    if window <= 1:
        return data
    # small hack to make the graph looks nice at the end
    avg = np.average(data[-window:])
    return np.convolve(data + ([avg] * (window - 1)), np.ones(window) / window, mode='valid')
