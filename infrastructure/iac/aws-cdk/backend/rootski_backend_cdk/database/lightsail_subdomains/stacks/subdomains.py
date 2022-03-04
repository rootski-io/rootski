"""A stack for mapping multiple subdomains to an IP address."""

from enum import Enum
from pathlib import Path
from typing import List

from aws_cdk import aws_route53 as route53
from aws_cdk import core as cdk

THIS_DIR = Path(__file__).parent


class StackOutputs(str, Enum):
    """Stack outputs for a subdomain stack."""

    @staticmethod
    def get_subdomain_output_key(stack_name: str, subdomain: str) -> Path:
        """Get the stack output key for a subdomain in a subdomain stack."""
        return f"{stack_name}RootskiSubdomain{subdomain}"


class ContextVars(str, Enum):
    """Context vars to be passed as CLI arguments for the Subdomain stack."""

    # pylint: disable=invalid-name
    rootski_lightsail_intance_static_ip = "RootskiLightsailInstanceStaticIp"


class Subdomains(cdk.Stack):
    """A Lightsail instance with a static IP used to host the backend database."""

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        backend_public_ip: str,
        subdomains: List[str],
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        for subdomain in subdomains:
            self.create_subdomain(subdomain=subdomain, backend_public_ip=backend_public_ip)

    def create_subdomain(self, subdomain: str, backend_public_ip: str):
        """Add a subdomain and output mapping to the provided public IP.

        :param subdomain: subdomain in ``<subdomain>.rootski.io``
        :param backend_public_ip: IP address which the subdomain should map to
        """
        route53.RecordSet(
            self,
            id=f"{subdomain}-record",
            record_type=route53.RecordType.A,
            zone=route53.HostedZone.from_lookup(
                self,
                id=f"HostedZone-{subdomain}",
                domain_name="rootski.io",
            ),
            record_name=f"{subdomain}.rootski.io",
            target=route53.RecordTarget.from_ip_addresses(backend_public_ip),
        )

        cdk.CfnOutput(
            self,
            id=StackOutputs.get_subdomain_output_key(stack_name=self.stack_name, subdomain=subdomain),
            value=f"{subdomain}.rootski.io",
            description=f"Map {subdomain}.rootski.io to {backend_public_ip}",
            export_name=StackOutputs.get_subdomain_output_key(stack_name=self.stack_name, subdomain=subdomain),
        )
