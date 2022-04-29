"""
Generate a number of wireguard keys using the ``pywgkey`` library.

See the docs: https://pywgkey.readthedocs.io/en/latest/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Type, TypedDict

from pywgkey import WgKey

#: default owner of a key pair if not already assigned to a rootski contributor
DEFAULT__VPN_IP_ADDRESS_OWNER_NAME = "unassigned"
#: max number of IP addresses on our wireguard VPN CIDR range
MAX_ALLOWED_WIREGUARD_KEY_PAIRS = 253


class NumberOfKeysError(Exception):
    """Exception for generating more keys than currently allowed."""


class VpnKeyPairData(TypedDict):
    """
    Storing data for a wireguard Peer configuration.

    There is an example of a peer configuration in the following documentation: https://www.wireguard.com/#cryptokey-routing
    """

    #: RSA public key for a wireguard peer
    public_key: str
    #: RSA private key for a wireguard peer
    private_key: str
    #: contributor or rootski service that reserves this IP address
    owner_name: str
    #: IP address on the local wireguard VPN network reserved for this peer
    private_ip_address_on_vpn_network: str


@dataclass
class KeyPair:
    """Wireguard key pair wrapper."""

    public_key: str
    private_key: str

    @classmethod
    def generate(cls: Type[KeyPair]) -> KeyPair:
        """Generate a KeyPair object."""
        keypair = WgKey()
        return cls(public_key=keypair.pubkey, private_key=keypair.privkey)

    def to_dict(
        self, ip_address: str, owner_name: Optional[str] = None, note: Optional[str] = None
    ) -> VpnKeyPairData:
        """Convert KeyPair keys to a VpnKeyPairData dictionary object."""
        vpn_keypair_data = VpnKeyPairData(
            public_key=self.public_key,
            private_key=self.private_key,
            owner_name=owner_name or DEFAULT__VPN_IP_ADDRESS_OWNER_NAME,
            private_ip_address_on_vpn_network=ip_address,
            note=note,
        )
        return vpn_keypair_data


def generate_n_keypairs(num_keys: int, num_reserved_keys: int = 10) -> List[VpnKeyPairData]:
    """
    Generate ``num_keys`` wireguard keypairs.

    :param num_keys: number of keys to generate
    :param num_reserved_keys: reserve certain IP addresses for rootski
        services e.g. vpn.rootski.io, mlflow.rootski.io, etc.

    :return: a list containing ``num_keys`` :py:class:`KeyPair` object
    """
    if num_keys > MAX_ALLOWED_WIREGUARD_KEY_PAIRS:
        raise NumberOfKeysError("num_keys must be smaller than 254")

    # create key pairs for IP addresses reserved for rootski services
    reserved_key_pairs = [
        KeyPair.generate().to_dict(
            ip_address=f"10.0.0.{i+1}", note="This ip-address is reserved and not available for contributors."
        )
        for i in range(num_reserved_keys)
    ]

    # create key pairs for IP addresses assignable to rootski contributors
    unreserved_key_pairs = [
        KeyPair.generate().to_dict(ip_address=f"10.0.0.{i+1}") for i in range(num_reserved_keys, num_keys)
    ]
    key_pairs = reserved_key_pairs + unreserved_key_pairs

    return key_pairs
