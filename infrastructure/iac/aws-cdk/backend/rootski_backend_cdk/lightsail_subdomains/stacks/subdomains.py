from enum import Enum
from pathlib import Path
from typing import List

from aws_cdk import core as cdk
from aws_cdk import aws_route53 as route53


THIS_DIR = Path(__file__).parent


class StackOutputs(str, Enum):
    @staticmethod
    def get_subdomain_output_key(stack_name: str, subdomain: str) -> Path:
        return f"{stack_name}RootskiSubdomain{subdomain}"


class ContextVars(str, Enum):
    rootski_lightsail_intance_static_ip = "RootskiLightsailInstanceStaticIp"


class Subdomains(cdk.Stack):
    """
    A Lightsail instance with a static IP used to host the backend database.
    """

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        backend_public_ip: str,
        subdomains: List[str],
        **kwargs,
    ):
        """ """
        super().__init__(scope, construct_id, **kwargs)

        for subdomain in subdomains:
            self.create_subdomain(subdomain=subdomain, backend_public_ip=backend_public_ip)

    def create_subdomain(self, subdomain: str, backend_public_ip: str):
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

    #     Type: AWS::Route53::RecordSet
    # Description: Make the traefik dashboard accessible at the site domain name
    # Properties:
    #   HostedZoneName:
    #     Fn::ImportValue: !Sub "${RootskiFrontEndStackName}-HostedZoneName"
    #   Type: A # CNAME
    #   # example: traefik.rootski.io
    #   Name: !Join
    #     - "."
    #     - - !Ref Subdomain
    #       - Fn::ImportValue: !Sub "${RootskiFrontEndStackName}-HostedZoneName"
    #   # "time to live" (seconds); DNS servers will only cache the result of this
    #   # subdomain for this long--setting it longer can reduce queries to route53,
    #   # and therefore save costs. 900 is the default. Shorter times are good for
    #   # development when we change them rapidly. Probably good for DynamicDNS, too :)
    #   TTL: "60"
    #   ResourceRecords:
    #     - !Ref PublicIP
