"""
VPC Endpoint for SSM.

Context: We need the rootski database to be secure.
We do not want people in the outside world to be able to access
the backend database at all. To achieve this, we will set the security group
rules on the database to only accept traffic from IP addresses local to
the AWS Lightsail VPC where the database is running.

The rootski REST API runs inside of AWS Lambda. We need the rootksi
lambda function to be able to reach the backend database over the network.
This means that the rootski Lambda will need to be on the same network as
the rootski database and have a local IP address for that network.
This way, the lambda function will be able to access the database.

To achieve this, we manually created a VPC peering connection from
the Lightsail VPC to the rootski AWS account (us-west-2) "Default VPC".
We now deploy the lambda function into the Default VPC, so the lambda
is on the same network!

Problem: If you deploy a lambda function into a VPC, it loses internet access
unless the VPC has an "internet gateway" AKA an EC2 instance that costs ~$33.50/mo.
That... is not an option for us. The issue is that the rootski lambda function needs
to access at least three services:

1. Lightsail instance with the rootski database
2. AWS SSM Parameter store
3. AWS Cognito

(1) is taken care of. (3) is the subject of another construct. (2) is addressed
here. For each EC2-related AWS service such as DynamoDB, SSM, API Gateway, etc., you
have the option to turn on a "VPC Endpoint" which an endpoint that libraries such as
``boto3`` can hit without leaving a VPC. In this way, our lambda function *will* be
able to access SSM. Yaaaay!
"""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class SsmVpcEndpoint(Construct):
    """Create a VPC Endpoint in the Default VPC for SSM."""

    def __init__(self, scope: cdk.Stack, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        #: Default VPC in the region this construct is deployed in.
        self.default_vpc = ec2.Vpc.from_lookup(
            self, construct_id + "Vpc-Endpoint-Default-VPC", vpc_name="Default VPC"
        )

        #: Security Group restricting access to the SSM VPC Endpoint; in this case, all services are allowed
        self.ssm_endpoint_security_group = ec2.SecurityGroup(
            self,
            construct_id + "SSM-VPC-Endpoint-SG",
            allow_all_outbound=True,
            vpc=self.default_vpc,
            description="Allow any service to hit the internal SSM endpoint.",
        )
        self.ssm_endpoint_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.all_tcp(), description="Enable all inbound traffic"
        )

        #: VPC Endpoint for SSM allowing services in any ``Default VPC`` subnet to access SSM without leaving the VPC
        self.ssm_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            construct_id + "SSM-VPC-Endpoint",
            # enable the DNS in the subnets to resolve the endpoint FQDN to the IP of the AWS service
            private_dns_enabled=True,
            vpc=self.default_vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            # the default VPC only has one subnet per AZ, so this will make the private SSM endpoint available in every subnet
            subnets=ec2.SubnetSelection(one_per_az=True),
            security_groups=[self.ssm_endpoint_security_group],
        )
