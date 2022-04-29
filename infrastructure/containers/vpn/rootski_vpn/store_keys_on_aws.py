"""Generates a number of keypairs and pushes them to AWS SSM."""

import json

import boto3
import wireguard_make_keys as wgkeys

# os.environ["AWS_PROFILE"] = "rootski"
# this is the max number of keys without going over 4096 characters


# vpn_key_data = wgkeys.generate_n_keypairs(NUMBER_OF_KEYS)
# rootski_wireguard_keypairs = {
#     "notes": "The first 10 keys and ip addresses 10.0.0.1-10.0.0.10 are reserved. Do not assign those when onboarding new contributors.",
#     "key_pairs": vpn_key_data,
# }
NUMBER_OF_KEYS = 15
rootski_wireguard_keypair_data = wgkeys.generate_n_keypairs(number_of_keys=NUMBER_OF_KEYS)


ssm_client = boto3.client("ssm", region_name="us-west-2")

for i in range(NUMBER_OF_KEYS):
    ip_address = rootski_wireguard_keypair_data[i]["private_ip_address_on_vpn_network"]

    new_string_parameter = ssm_client.put_parameter(
        Name=f"/rootski/wireguard_vpn/key-pair_for_ip/{ip_address}",
        Description="WireGuard Key Data",
        Value=json.dumps(rootski_wireguard_keypair_data[i], indent=4),
        Type="String",
        Overwrite=False,
        Tier="Standard",
        DataType="text",
    )
