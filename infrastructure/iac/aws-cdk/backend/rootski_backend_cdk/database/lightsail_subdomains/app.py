"""App that maps several .rootski.io subdomains to the backend lightsail instance."""

from aws_cdk import core as cdk
from rootski_backend_cdk.database.lightsail_subdomains.stacks.subdomains import ContextVars, Subdomains

if __name__ == "__main__":
    app = cdk.App()

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
