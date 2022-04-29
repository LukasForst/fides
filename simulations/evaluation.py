from simulations.environment import SimulationResult


def evaluate(result: SimulationResult) -> float:
    last_click = max(result.targets_history.keys())
    diff = 0
    for target, ti in result.targets_history[last_click].items():
        diff += abs(result.targets_labels[target] - ti.score)
    return diff
