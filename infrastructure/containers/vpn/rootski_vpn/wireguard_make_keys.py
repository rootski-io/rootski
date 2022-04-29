"""
Generate a number of wireguard keys using the pywgkey library.

See the docs: https://pywgkey.readthedocs.io/en/latest/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Type, TypedDict

from pywgkey import WgKey

DEFAULT_VPN_IP_ADDRESS_OWNER_NAME = "unassigned"


class NumberOfKeysError(Exception):
    """Exception for generating more keys than currently allowed."""


class VpnKeyPairData(TypedDict):
    """
    Storing data for a wireguard Peer configuration.

    There is an example in the following documentation: https://www.wireguard.com/#cryptokey-routing
    """

    public_key: str
    private_key: str
    owner_name: str
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
            owner_name=owner_name or DEFAULT_VPN_IP_ADDRESS_OWNER_NAME,
            private_ip_address_on_vpn_network=ip_address,
            note=note,
        )
        return vpn_keypair_data


def generate_n_keypairs(number_of_keys: int) -> List[VpnKeyPairData]:
    """
    Generate ``number_of_keys`` wireguard keypairs.

    :param number_of_keys: number of key to generate
    :return: a list containing ``number_of_keys`` :py:class:`KeyPair` object
    """
    if number_of_keys > 253:
        raise NumberOfKeysError("number_of_keys must be smaller than 254")
    key_pairs_reserved = [
        KeyPair.generate().to_dict(
            ip_address=f"10.0.0.{i+1}", note="This ip-address is reserved and not available for contributors."
        )
        for i in range(10)
    ]
    key_pairs_unreserved = [
        KeyPair.generate().to_dict(ip_address=f"10.0.0.{i+1}") for i in range(10, number_of_keys)
    ]
    key_pairs = key_pairs_reserved + key_pairs_unreserved
    return key_pairs
