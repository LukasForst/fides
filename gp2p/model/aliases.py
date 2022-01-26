from ctypes import Union

IP = str
"""IPv4, IPv6 in string representation."""

Domain = str
"""Host Name, Domain."""

PeerId = str
"""String representation of peer's public key. """

OrganisationId = str
"""String representation of organisation ID."""

Target = Union[IP, Domain]
"""Intelligence Target - domain or IP."""
