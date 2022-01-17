import dataclasses
from math import sqrt
from statistics import mean
from typing import List

from global_p2p.model.service_history import ServiceHistory
from global_p2p.model.trust_data import TrustData


def update_service_trust(trust: TrustData) -> TrustData:
    """
    Computes and updates TrustData.service_trust - st_ij - based on the given data.

    This function should be called whenever there's new service interaction record added
    to the interaction history.

    Does not modify given trust values directly, returns new object - however, this
    method does not create new collections as they're not being modified, they're simply copied.

    :param trust: trust data to be reevaluated
    :return: new trust object with fresh service_trust, competence_belief and integrity_belief
    """

    fading_factor = compute_fading_factor(trust.service_history)
    competence_belief = compute_competence_belief(trust.service_history, fading_factor)
    integrity_belief = compute_integrity_belief(trust.service_history, fading_factor, competence_belief)
    discount_factor = compute_discount_factor(trust.service_history)

    history_factor = trust.service_history_size / trust.configuration.service_history_max_size

    # (sh_ij / sh_max) * (cb_ij -0.5 * ib_ij) -> where -0.5 is discount factor
    service_trust_own_experience = history_factor * (competence_belief + discount_factor * integrity_belief)
    # (1 - (sh_ij / sh_max)) * r_ij
    service_trust_reputation = (1 - history_factor) * trust.reputation
    # and now add both parts together
    service_trust = service_trust_own_experience + service_trust_reputation

    updated_trust = dataclasses.replace(trust,
                                        service_trust=service_trust,
                                        competence_belief=competence_belief,
                                        integrity_belief=integrity_belief
                                        )

    return updated_trust


def compute_fading_factor(service_history: ServiceHistory) -> List[float]:
    """
    Computes fading factor for each record in service history.

    In model's notation f^k_ij where "k" is index in service history.

    :param service_history: history for which should be fading factor generated
    :return: ordered list of fading factors, index of fading factor matches record in ServiceHistory
    """
    # TODO: this might be time based in the future
    # f^k_ij = k / sh_ij
    # where 1 <= k <= sh_ij
    history_size = len(service_history)
    return [i / history_size for i, _ in enumerate(service_history, start=1)]


def compute_competence_belief(service_history: ServiceHistory, fading_factor: List[float]) -> float:
    """
    Computes competence belief - cb_ij.

    :param service_history: history for peer j
    :param fading_factor: fading factors for given history
    :return: competence belief for given data
    """
    assert len(service_history) == len(fading_factor), "Service history must have same length as fading factors."

    normalisation = sum([service.weight * fading for service, fading in zip(service_history, fading_factor)])
    belief = sum([service.satisfaction * service.weight * fading
                  for service, fading
                  in zip(service_history, fading_factor)])

    return belief / normalisation


def compute_integrity_belief(service_history: ServiceHistory,
                             fading_factor: List[float],
                             competence_belief: float) -> float:
    """
    Computes integrity belief - ib_ij.

    :param competence_belief: competence belief for given service history and fading factor
    :param service_history: history for peer j
    :param fading_factor: fading factors for given history
    :return: integrity belief for given data
    """
    assert len(service_history) == len(fading_factor), "Service history must have same length as fading factors."

    history_size = len(service_history)
    weight_mean = mean([service.weight for service in service_history])
    fading_mean = mean(fading_factor)

    sat = sum([(service.satisfaction * weight_mean * fading_mean - competence_belief) ** 2
               for service
               in service_history])

    return sqrt(sat / history_size)


# noinspection PyUnusedLocal
# might be used in the future
def compute_discount_factor(service_history: ServiceHistory) -> float:
    """
    Computes discount factor used for `competence + (discount) * integrity` to lower
    the expectations of current peer for future interaction.

    :param service_history: history for peer j
    :return: discount factor for integrity
    """
    # arbitrary value -1/2 explained in the paper
    return -0.5
