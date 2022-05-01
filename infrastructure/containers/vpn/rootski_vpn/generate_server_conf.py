"""Standalone shell script for generating the secrets and configuration file for the wireguard server."""

import json
from pathlib import Path
from textwrap import dedent
from typing import Dict, List

import boto3


def main():
    """Genereate files for the server configuration, server private key, and server public key."""
    key_pairs: List[dict] = fetch_key_pairs_from_ssm(
        key_pairs_ssm_prefix="/rootski/wireguard-vpn/key-pair-for-ip", aws_region="us-west-2"
    )
    generate_wireguard_server_configuration_file(
        key_pairs=key_pairs,
        server_conf_fpath=Path("/etc/wireguard/wg0.conf"),
    )
    generate_wireguard_server_private_key_file(
        key_pairs=key_pairs,
        server_key_fpath=Path("/etc/wireguard/server.key"),
    )
    generate_wireguard_server_public_key_file(
        key_pairs=key_pairs,
        server_pub_fpath=Path("/etc/wireguard/server.pub"),
    )


def fetch_key_pairs_from_ssm(
    key_pairs_ssm_prefix: str,
    aws_region: str,
) -> List[dict]:
    """
    Retrieve the deserialized VPN key-pair data from ssm.

    :param key_pairs_ssm_prefix: The hierarchy for the parameter, which is the parameter name except for the last part of the parameter. See :py:func:`fetch_all_ssm_parameters_with_prefix`
    :param aws_region: The AWS region where the key-pairs are stored in ssm
    :return: The deserialized VPN key-pair data from ssm. See footski_vpn.wireguard_keygen_utils
    """
    key_pair_params: List[dict] = fetch_all_ssm_parameters_with_prefix(
        path_prefix=key_pairs_ssm_prefix,
        aws_region=aws_region,
    )
    key_pairs: List[dict] = deserialize_key_pair_ssm_parameters(key_pair_parameters=key_pair_params)

    return key_pairs


def generate_wireguard_server_configuration_file(
    key_pairs: List[dict],
    server_conf_fpath: Path = Path("/etc/wireguard/wg0.conf"),
):
    """
    Generate the wireguard server configruation file.

    :param key_pairs: List of key-pair data
    :param server_conf_fpath: Path object representing the filepath to write the server configuration to
    """
    key_pairs_sorted_by_ip_address: List[dict] = sort_key_pairs_by_ip_address(key_pairs=key_pairs)

    # generate the text for the [Interface] section
    server_key_pair = key_pairs_sorted_by_ip_address[0]
    interface_section = generate_wireguard_interface(server_private_key=server_key_pair["private_key"])

    # generate the text for each [Peer] section
    peer_sections = [
        generate_wireguard_peer(
            peer_public_key=key_pair["public_key"],
            ip_address=key_pair["private_ip_address_on_vpn_network"],
            owner_username=key_pair["owner_name"],
        )
        for key_pair in key_pairs_sorted_by_ip_address[1:]
    ]

    # combine the sections into a single string
    sections: List[str] = [interface_section, *peer_sections]
    server_conf_contents: str = "\n\n".join(sections)

    # write the contents to the server configuration file on disk
    server_conf_fpath.write_text(server_conf_contents, encoding="utf-8")


def generate_wireguard_server_private_key_file(
    key_pairs: List[dict],
    server_key_fpath: Path = Path("/etc/wireguard/server.key"),
):
    """
    Generate the wireguard server.key file.

    :param key_pairs: List of key-pair data
    :param server_conf_fpath: Path object representing the filepath to write the server.key file to
    """
    server_key_fpath.write_text(key_pairs[0]["private_key"], encoding="utf8")


def generate_wireguard_server_public_key_file(
    key_pairs: List[dict],
    server_pub_fpath: Path = Path("/etc/wireguard/server.pub"),
):
    """
    Generate the wireguard server.pub file.

    :param key_pairs: List of key-pair data
    :param server_conf_fpath: Path object representing the filepath to write the server.pub file to
    """
    server_pub_fpath.write_text(key_pairs[0]["public_key"], encoding="utf8")


def generate_wireguard_interface(server_private_key: str) -> str:
    """
    Generate the interface for a wireguard server configuration file wg0.conf.

    :param server_private_key: The private key of the wireguard VPN server
    :return interface: A string representing the [Interface] section of the wireguard configuration file
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
    :return peer: A string representing a [Peer] section of the wireguard configuration file
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


def fetch_all_ssm_parameters_with_prefix(path_prefix: str, aws_region: str) -> List[dict]:
    """
    Retrieve all key-pair aws ssm pararmters using a given prefix.

    The aws parameters are retrieved using the boto3 SSM client, and the structure of the key_pair_parameters are found in the following URL.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameters_by_path

    :param path_prefix: The hierarchy for the parameter, which is the parameter name except for the last part of the parameter
    :param aws_region: The aws region where the key-pair data is stored in ssm
    :return: The aws key-pair ssm paramters
    """
    # prepare an iterator to fetch the key pairs in batches
    ssm_client = boto3.client("ssm", region_name=aws_region)
    paginator = ssm_client.get_paginator("get_parameters_by_path")
    response_iterator = paginator.paginate(Path=path_prefix)

    # fetch all pages of parameters from SSM
    pages: List[str, List[dict]] = [page["Parameters"] for page in response_iterator]
    # flatten the list of lists to a single list of parameter dicts
    parameters: List[dict] = sum(pages, [])

    return parameters


def deserialize_key_pair_ssm_parameters(key_pair_parameters: List[str]) -> List[Dict[str, str]]:
    """
    Deserialize the aws key-pair ssm parameters.

    :param key_pair_parameters: The key-pair aws pararmeters. See :py:func:`fetch_all_ssm_parameters_with_prefix`
    :return: The VPN key-pair data. See rootski_vpn.wireguard_keygen_utils.
    """
    deserialized_key_pairs: List[Dict[str, str]] = [
        json.loads(ssm_parameter["Value"]) for ssm_parameter in key_pair_parameters
    ]

    return deserialized_key_pairs


def sort_key_pairs_by_ip_address(key_pairs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sort the key pairs by IP address so the keys are sequentially ordered.

    :param key_pairs: The VPN key-pair data to be sorted by ip-address
    :return sorted_key_pairs: The sorted key-pair data sequentially organized
    """

    def by_ip_address(key_pair_data: dict) -> List[int]:
        """Return the IP address of a key pair in a form that is sortable."""
        numerical_representation_of_ip: List[int] = [
            int(bit) for bit in key_pair_data["private_ip_address_on_vpn_network"].split(".")
        ]
        return numerical_representation_of_ip

    sorted_key_pairs: List[Dict[str, str]] = sorted(key_pairs, key=by_ip_address)
    return sorted_key_pairs


if __name__ == "__main__":
    main()
