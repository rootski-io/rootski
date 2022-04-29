"""We need to bulk read the parameters and upload the parameters as individual strings to AWS."""


import json
from pathlib import Path
from textwrap import dedent
from typing import List

import boto3


def generate_wireguard_interface(server_private_key: str) -> str:
    """
    Generate the interface for a wireguard server configuration file wg0.conf.

    :param server_private_key: _description_
    """
    interface = dedent(
        f"""\
    [Interface]
    Address = 10.0.0.1/24
    ListenPort = 51820
    PrivateKey = {server_private_key}
    PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

    """
    )

    return interface


def generate_wireguard_peer(peer_public_key: str, ip_address: str, owner_username: str) -> str:
    """
    Generate a peer for a wireguard server configuration file wg0.conf.

    :param peer_public_key: The public key for a peer's rsa key-pair
    :return: _description_
    """
    peer = dedent(
        f"""\
    [Peer]
    # Username = {owner_username}
    PublicKey = {peer_public_key}
    AllowedIPs = {ip_address}/32

    """
    )

    return peer


# Connect to AWS SSM and retrieve key-pairs
# os.environ["AWS_PROFILE"] = "rootski"
ssm_client = boto3.client("ssm", region_name="us-west-2")
paginator = ssm_client.get_paginator("get_parameters_by_path")

response_iterator = paginator.paginate(Path="/rootski/wireguard_vpn/key-pair_for_ip")

parameters = []
for page in response_iterator:
    for entry in page["Parameters"]:
        parameters.append(entry)


key_data = []
for param in parameters:
    key_pair_data = json.loads(param["Value"])
    key_data.append(key_pair_data)


def sort_key(data: dict) -> List[int]:
    """Sort a list of key_data dictionaries by their ip_address."""
    numerical_representation_of_ip: List[int] = [
        int(bit) for bit in data["private_ip_address_on_vpn_network"].split(".")
    ]
    return numerical_representation_of_ip


sorted_key_data = sorted(key_data, key=sort_key)


# Generate the configuration file
server_conf_filepath = Path("/etc/wireguard/wg0.conf", encoding="utf8")

server_conf_filepath.write_text(
    generate_wireguard_interface(sorted_key_data[0]["private_key"]), encoding="utf8"
)

filepath = server_conf_filepath.open("a", encoding="utf8")

for i in range(1, len(sorted_key_data)):  # First 10 keys are resevered for services
    filepath.write(
        generate_wireguard_peer(
            sorted_key_data[i]["public_key"],
            sorted_key_data[i]["private_ip_address_on_vpn_network"],
            sorted_key_data[i]["owner_name"],
        ),
        encoding="utf8",
    )

# Store server private key
server_private_key_filepath = Path("/etc/wireguard/server.key", encoding="utf8")
server_private_key_filepath.write_text(sorted_key_data[0]["private_key"], encoding="utf8")

# Store server public key
server_public_key_filepath = Path("/etc/wireguard/server.pub", encoding="utf8")
server_public_key_filepath.write_text(sorted_key_data[0]["public_key"], encoding="utf8")
