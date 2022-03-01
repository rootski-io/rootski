from enum import Enum
from pathlib import Path

from jinja2 import Template

from aws_cdk import core as cdk
from aws_cdk import aws_lightsail as lightsail

from rootski_backend_cdk.common.constants import TAGS

THIS_DIR = Path(__file__).parent
RESOURCES_DIR = THIS_DIR / "resources"
USER_DATA_TEMPLATE_FPATH = RESOURCES_DIR / "user-data.template.sh"


class StackOutputs(str, Enum):
    static_ip = "StaticIp"
    ssh_key_pair_name = "SshKeyPairName"
    lightsail_admin_username = "LightsailAdminUsername"


class ContextVars(str, Enum):
    iam_access_key_id = "iam_access_key_id"
    iam_access_key = "iam_access_key"


def render_user_data_script(iam_access_key_id: str, iam_access_key: str) -> str:
    """
    Render the user-data.template.sh script inserting the IAM credentials for the Lightsail instance.

    :param iam_access_key_id: key_id with programmatic access that will be present in the user-data.sh script
    :param iam_access_key: same as above but the actual key
    """
    user_data_template = Template(USER_DATA_TEMPLATE_FPATH.read_text())
    return user_data_template.render(
        {
            "AWS_ACCESS_KEY_ID": iam_access_key_id,
            "AWS_SECRET_ACCESS_KEY": iam_access_key,
        }
    )


class LightsailInstanceStack(cdk.Stack):
    """
    A Lightsail instance with a static IP used to host the backend database.
    """

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        iam_access_key_id: str,
        iam_access_key: str,
        **kwargs,
    ):
        """
        :param iam_access_key_id: key_id with programmatic access that will be present in the user-data.sh script
        :param iam_access_key: same as above but the actual key

        The IAM key and key id are used to access the S3 bucket where database backups are kept.
        """
        super().__init__(scope, construct_id, **kwargs)

        instance = lightsail.CfnInstance(
            self,
            id="Rootski-DB-Lightsail-Instance",
            # specifying the instance name prevents CDK from being able to destroy this resource
            # if we update the stack (for example, if we want to change the instance size
            # which would require destroying the existing instance and creating a new one).
            # However, this is a required parameter :(
            instance_name="Rootski-DB-Lightsail-Instance",
            key_pair_name="rootski.id_rsa",
            availability_zone="us-west-2a",
            tags=TAGS,
            networking=lightsail.CfnInstance.NetworkingProperty(
                ports=[
                    lightsail.CfnInstance.PortProperty(
                        access_direction="inbound",
                        cidrs=["172.0.0.0/8"],
                        common_name="SSH",
                        from_port=22,
                        protocol="tcp",
                        to_port=22,
                    ),
                    lightsail.CfnInstance.PortProperty(
                        access_direction="inbound",
                        cidrs=["172.0.0.0/8"],
                        common_name="Postgres",
                        from_port=8000,
                        protocol="tcp",
                        to_port=8000,
                    ),
                    # traefik
                    lightsail.CfnInstance.PortProperty(
                        access_direction="inbound",
                        cidrs=["172.0.0.0/8"],
                        common_name="Postgres",
                        from_port=80,
                        protocol="tcp",
                        to_port=80,
                    ),
                    lightsail.CfnInstance.PortProperty(
                        access_direction="inbound",
                        cidrs=["172.0.0.0/8"],
                        common_name="Postgres",
                        from_port=5432,
                        protocol="tcp",
                        to_port=5432,
                    ),
                    lightsail.CfnInstance.PortProperty(
                        access_direction="inbound",
                        cidrs=["172.0.0.0/8"],
                        common_name="Postgres",
                        from_port=3333,
                        protocol="tcp",
                        to_port=3333,
                    ),
                    lightsail.CfnInstance.PortProperty(
                        access_direction="outbound",
                        cidrs=["0.0.0.0/0"],
                        common_name="All Outbound Traffic",
                        from_port=0,
                        protocol="all",
                        to_port=65535,
                    ),
                ]
            ),
            # found using 'aws lightsail get-blueprints --profile rootski'
            blueprint_id="amazon_linux_2",
            # found using 'aws lightsail get-bundles --profile rootski'
            bundle_id="micro_2_0",
            user_data=render_user_data_script(
                iam_access_key_id=iam_access_key_id, iam_access_key=iam_access_key
            ),
        )

        # free as long as the instance is running
        self.static_ip = lightsail.CfnStaticIp(
            self,
            id="Rootski-DB-Lightsail-StaticIp",
            static_ip_name="Rootski-DB-Lightsail-StaticIp",
            attached_to=instance.ref,
        )

        cdk.CfnOutput(
            scope=self,
            id=StackOutputs.static_ip.value,
            value=self.static_ip.attr_ip_address,
            description="IP address of the rootski db Lightsail instance",
            export_name=StackOutputs.static_ip.value,
        )
        cdk.CfnOutput(
            scope=self,
            id=StackOutputs.ssh_key_pair_name.value,
            value=instance.attr_ssh_key_name,
            description="RSA key pair used to SSH into the db instance.",
            export_name=StackOutputs.ssh_key_pair_name.value,
        )
        cdk.CfnOutput(
            scope=self,
            id=StackOutputs.lightsail_admin_username.value,
            value=instance.attr_user_name,
            description="IP address of the rootski db Lightsail instance",
            export_name=StackOutputs.lightsail_admin_username.value,
        )
