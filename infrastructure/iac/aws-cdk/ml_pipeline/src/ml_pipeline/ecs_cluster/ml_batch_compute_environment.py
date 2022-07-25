from aws_cdk import (
    Stack,
)
import aws_cdk as cdk
from constructs import Construct

from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_batch_alpha as batch

from pathlib import Path

THIS_DIR = Path(__file__).parent

class MlBatchComputeEnvironment(Stack):
    """
    
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        default_vpc = ec2.Vpc.from_lookup(self, "default-vpc", vpc_name="Default VPC")

        # Compute Environment
        batch_compute_environment = batch.ComputeEnvironment(
            self,
            "MlComputeEnvironment",
            managed=False,
            # compute_resources=batch.ComputeResources(
            #     vpc=default_vpc,
            #     compute_resources_tags = [cdk.CfnTag(key="app", value="rootski"), cdk.CfnTag(key="created", value="hackathon")],
            #     image=,
            #     instance_role= "ecsInstanceRole" # arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole 
            # )
        )
        
        # Job Queue
        job_queue = batch.JobQueue(
            self, 
            "JobQueue",
            compute_environments=[batch.JobQueueComputeEnvironment(
                compute_environment=batch_compute_environment, # Defines a collection of compute resources to handle assigned batch jobs
                order=1 # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment) 
            )]
        )

        job_definiton = batch.JobDefinition(
            self,
            "TestJobDefinition",
            container=batch.JobDefinitionContainer(
                # self,
                # "TestJobDefinitionContainer",
                image=ecs.ContainerImage.from_asset(
                    directory=str(THIS_DIR / "../../../resources/test_batch_image/"),
                ),
                log_configuration=batch.LogConfiguration(
                    log_driver=batch.LogDriver.AWSLOGS,
                )

            )
        )


        # role for creating the ECS activation for registering the on-prem instance with the 
        instance_iam_role = iam.Role(self, 'EcsAnywhereInstanceRole',
            role_name="EcsAnywhereInstanceRole",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_managed_policy_arn(self, "EcsAnywhereEC2Policy", "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"),
            ]
        )

        # Create Outputs
        cdk.CfnOutput(self, "RegisterExternalInstance",
            description="Create an Systems Manager activation pair",
            value=f"aws ssm create-activation --iam-role {instance_iam_role.role_name}",
            export_name="1-RegisterExternalInstance",
        )

        cdk.CfnOutput(self, "DownloadInstallationScript",
            description="On your VM, download installation script",
            value='curl -o "ecs-anywhere-install.sh" "https://amazon-ecs-agent-packages-preview.s3.us-east-1.amazonaws.com/ecs-anywhere-install.sh" && sudo chmod +x ecs-anywhere-install.sh',
            export_name="2-DownloadInstallationScript",
        )

        cdk.CfnOutput(self, "ExecuteScript",
            description="Run installation script on VM",
            value=f"sudo ./ecs-anywhere-install.sh  --region {self.region} --cluster $CLUSTER_NAME --activation-id $ACTIVATION_ID --activation-code $ACTIVATION_CODE",
            export_name="3-ExecuteInstallationScript",
        )