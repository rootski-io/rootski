# from aws_cdk import (
#     Stack,
# )
# import aws_cdk as cdk
# from constructs import Construct

# from aws_cdk import aws_ecs as ecs
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_iam as iam
# from aws_cdk import aws_batch_alpha as batch

# # class BatchJobStack(Stack):

# #     def __init__(self, scope: Construct, construct_id: str, ecs_cluster_arn: str, **kwargs) -> None:
# #         super().__init__(scope, construct_id, **kwargs)

# #         default_vpc = ec2.Vpc.from_lookup(self, "default-vpc", vpc_name="Default VPC")
        
# #         batch.ComputeEnvironment(
# #             self,
# #             "BatchComputeEnvironment",
# #             compute_resources=batch.ComputeResources(

# #             )
#         )
        
#         # Create ComputeEnvironment
#         # batch.ComputeEnvironment(self, "ComputeEnvironment", props?: ComputeEnvironmentProps)
        