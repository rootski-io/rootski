from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lightsail as lightsail
)
from constructs import Construct
from rootski_cdk.common.constants import 

from rootski_backend_cdk.common.constants import TAGS

class VpnStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # iam user with SSM access
        # lightsail instance with that user in the ~/.aws/credentials

    cfn_instance = lightsail.CfnInstance(self, "MyCfnInstance",
        blueprint_id="blueprintId",
        bundle_id="bundleId",
        instance_name="instanceName",

        # the properties below are optional
        add_ons=[lightsail.CfnInstance.AddOnProperty(
            add_on_type="addOnType",

            # the properties below are optional
            auto_snapshot_add_on_request=lightsail.CfnInstance.AutoSnapshotAddOnProperty(
                snapshot_time_of_day="snapshotTimeOfDay"
            ),
            status="status"
        )],
        availability_zone="availabilityZone",
        hardware=lightsail.CfnInstance.HardwareProperty(
            cpu_count=123,
            disks=[lightsail.CfnInstance.DiskProperty(
                disk_name="diskName",
                path="path",

                # the properties below are optional
                attached_to="attachedTo",
                attachment_state="attachmentState",
                iops=123,
                is_system_disk=False,
                size_in_gb="sizeInGb"
            )],
            ram_size_in_gb=123
        ),
        key_pair_name="keyPairName",
        networking=lightsail.CfnInstance.NetworkingProperty(
            ports=[lightsail.CfnInstance.PortProperty(
                access_direction="accessDirection",
                access_from="accessFrom",
                access_type="accessType",
                cidr_list_aliases=["cidrListAliases"],
                cidrs=["cidrs"],
                common_name="commonName",
                from_port=123,
                ipv6_cidrs=["ipv6Cidrs"],
                protocol="protocol",
                to_port=123
            )],

            # the properties below are optional
            monthly_transfer=123
        ),
        tags=[CfnTag(
            key="name",
            value="rootski"),
            CfnTag(key='',
            )
        )],
        user_data="userData"
    )
