#!python3
"""Generates a number of keypairs and pushes them to AWS SSM."""

import json
from typing import Dict, List

import boto3
from mypy_boto3_ssm import SSMClient
from wireguard_keygen_utils import generate_n_keypairs


def store_key_pair_on_aws(key_pair_identifier: str, keypair_data: dict, ssm_client: SSMClient):
    """
    Store a keypair on AWS SSM.

    :raises SSM.Client.exceptions.ParameterAlreadyExists: if the keypair already exists

    :param key_pair_identifier: name that uniquely identifies
        the keypair saved in parameter store. It is the last part
        of the SSM parameter path.
    :param keypair_data: dictionary containing the keypair data.
        See :py:class:`wireguard_keygen_utils.VpnKeyPairData` for
        an explanation of the contents.
    """
    ssm_client.put_parameter(
        Name=f"/rootski/wireguard-vpn/key-pair-for-ip/{key_pair_identifier}",
        Description="WireGuard Key Data",
        Value=json.dumps(keypair_data, indent=4),
        Type="String",
        Overwrite=False,
        Tier="Standard",
        DataType="text",
    )


def store_n_key_pairs_on_aws(number_of_keypairs: int):
    """Generate and store a number of keypairs on AWS SSM."""

    ssm_client = boto3.client("ssm", region_name="us-west-2")

    rootski_wireguard_keypair_data_objs: List[Dict[str, str]] = generate_n_keypairs(
        number_of_keys=number_of_keypairs
    )

    # store all keypairs in SSM
    for wireguard_keypaird_data in rootski_wireguard_keypair_data_objs:
        ip_address = wireguard_keypaird_data["private_ip_address_on_vpn_network"]
        store_key_pair_on_aws(
            key_pair_identifier=ip_address, keypair_data=wireguard_keypaird_data, ssm_client=ssm_client
        )


if __name__ == "__main__":

    NUMBER_OF_KEY_PAIRS_TO_GENERATE = 15
    store_n_key_pairs_on_aws(NUMBER_OF_KEY_PAIRS_TO_GENERATE)
