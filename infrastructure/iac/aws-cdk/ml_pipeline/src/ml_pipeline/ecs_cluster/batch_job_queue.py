# from aws_cdk import (
#     Stack,
# )
# import aws_cdk as cdk
# from constructs import Construct

# from aws_cdk import aws_ecs as ecs
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_iam as iam
# from aws_cdk import aws_batch_alpha as batch

# job_queue = batch.JobQueue(self, "JobQueue",
#     compute_environments=[batch.JobQueueComputeEnvironment(
#         # Defines a collection of compute resources to handle assigned batch jobs
#         compute_environment=compute_environment,
        
#         # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment)
#         order=1
#     )
#     ]
# )