from typing import Dict, List, Literal
import boto3


def get_stack_outputs(stack_name: str, region="us-west-2") -> Dict[str, str]:
    """
    :return: stack outputs in this form:

        .. code-block:: json

            {
                "output-key-1": "output-value-1",
                "output-key-2": "output-value-2",
            }
    """
    cf = boto3.client("cloudformation", region_name=region)
    r = cf.describe_stacks(StackName=stack_name)

    (stack,) = r["Stacks"]
    outputs: List[Dict[Literal["OutputKey", "OutputValue"], str]] = stack["Outputs"]

    result: Dict[str, str] = {o["OutputKey"]: o["OutputValue"] for o in outputs}

    return result
