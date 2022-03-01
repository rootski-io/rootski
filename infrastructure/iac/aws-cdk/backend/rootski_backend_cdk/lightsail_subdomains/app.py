#!/usr/bin/env python3

from aws_cdk import core as cdk

from rootski_backend_cdk.lightsail_subdomains.stacks.subdomains import ContextVars, Subdomains

app = cdk.App()

# TODO - get the environment information from main.py somehow
environment = cdk.Environment(
    account="091910621680",
    region="us-west-2",
)


Subdomains(
    app,
    "Rootski-Subdomains-Stack-cdk",
    subdomains=["docker", "traefik", "database", "lightsail", "backend"],
    backend_public_ip=app.node.try_get_context(ContextVars.rootski_lightsail_intance_static_ip.value),
    env=environment,
)

app.synth()
