import aws_cdk as core
import aws_cdk.assertions as assertions

from ml_pipeline.ml_pipeline_stack import MlPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ml_pipeline/ml_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MlPipelineStack(app, "ml-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
