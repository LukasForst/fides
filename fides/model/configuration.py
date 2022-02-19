from dataclasses import dataclass
from typing import List, Union

import yaml

from fides.model.aliases import OrganisationId, PeerId
from fides.utils.logger import Logger


@dataclass(frozen=True)
class PrivacyLevel:
    name: str
    """Name of the level."""
    value: float
    """Value used for comparison.
    
    0 <= value <= 1
    
    (there can be a case where value > 1 but that means the data won't be ever send)
    """

    def __cmp__(self, other):
        return self.value - other.value


@dataclass(frozen=True)
class PrivacyThreshold:
    level: float
    """For this level (and all levels > this) require peer to have at least this trust."""
    required_trust: float
    """The trust required to obtain data with this level."""


@dataclass(frozen=True)
class TrustedEntity:
    id: Union[PeerId, OrganisationId]
    """Unique identifier for the peer or organisation."""

    name: str
    """Name of the entity."""

    trust: float
    """Initial trust for the entity.

    If, "enforce_trust = false" this value will change during time as the instance has more interactions with
    organisation nodes. If "enforce_trust = true", the trust for all peers from this entity will remain 
    the same. 
    """

    enforce_trust: bool
    """If true, entity nodes will have always initial trust."""

    privacy_level: float
    """What level of data should be shared with this entity."""


@dataclass(frozen=True)
class RecommendationsConfiguration:
    enabled: bool
    """If the recommendation protocol should be executed."""

    only_preconfigured: bool
    """If true, protocol will only ask pre-trusted peers / organisations for recommendations."""

    required_trusted_peers_count: int
    """Require minimal number of trusted connected peers before running recommendations."""

    trusted_peer_threshold: float
    """Minimal trust for trusted peer."""

    peers_max_count: int
    """Maximal count of peers that are asked to give recommendations on a peer.

    In model's notation η_max.
    """

    history_max_size: int
    """Maximal size of Recommendation History.

    In model's notation rh_max.
    """


@dataclass(frozen=True)
class TrustModelConfiguration:
    privacy_levels: List[PrivacyLevel]
    """Privacy levels settings."""

    privacy_thresholds: List[PrivacyThreshold]
    """Thresholds for data filtering."""

    data_default_level: float
    """If some data are not labeled, what value should we use."""

    initial_reputation: float
    """Initial reputation that is assigned for every peer when there's new encounter."""

    service_history_max_size: int
    """Maximal size of Service History.
    
    In model's notation sh_max.
    """

    recommendations: RecommendationsConfiguration
    """Config for recommendations."""

    alert_trust_from_unknown: float
    """How much should we trust an alert that was sent by peer we don't know anything about.

    0 <= alert_trust_from_unknown <= 1
    """

    trusted_peers: List[TrustedEntity]
    """List of preconfigured peers."""

    trusted_organisations: List[TrustedEntity]
    """List of preconfigured organisations."""


def load_configuration(file_path: str) -> TrustModelConfiguration:
    with open(file_path, "r") as stream:
        try:
            return __parse_config(yaml.safe_load(stream))
        except Exception as exc:
            Logger('config_loader').error(f"It was not possible to load file! {exc}.")
            raise exc


def __parse_config(data: dict) -> TrustModelConfiguration:
    return TrustModelConfiguration(
        privacy_levels=[PrivacyLevel(name=level['name'],
                                     value=level['value'])
                        for level in data['privacy']['levels']],
        privacy_thresholds=[PrivacyThreshold(level=threshold['level'],
                                             required_trust=threshold['requiredTrust'])
                            for threshold in data['privacy']['thresholds']],
        data_default_level=data['privacy']['defaultLevel'],
        initial_reputation=data['trust']['service']['initialReputation'],
        service_history_max_size=data['trust']['service']['historyMaxSize'],
        recommendations=RecommendationsConfiguration(
            enabled=data['trust']['recommendations']['enabled'],
            only_preconfigured=data['trust']['recommendations']['useOnlyPreconfigured'],
            required_trusted_peers_count=data['trust']['recommendations']['requiredTrustedPeersCount'],
            trusted_peer_threshold=data['trust']['recommendations']['trustedPeerThreshold'],
            peers_max_count=data['trust']['recommendations']['peersMaxCount'],
            history_max_size=data['trust']['recommendations']['historyMaxSize']
        ),
        alert_trust_from_unknown=data['trust']['alert']['defaultTrust'],
        trusted_peers=[TrustedEntity(id=e['id'],
                                     name=e['name'],
                                     trust=e['trust'],
                                     enforce_trust=e['enforceTrust'],
                                     privacy_level=e['privacyLevel'])
                       for e in data['privacy']['peers']],
        trusted_organisations=[TrustedEntity(id=e['id'],
                                             name=e['name'],
                                             trust=e['trust'],
                                             enforce_trust=e['enforceTrust'],
                                             privacy_level=e['privacyLevel'])
                               for e in data['privacy']['organisations']],
    )
