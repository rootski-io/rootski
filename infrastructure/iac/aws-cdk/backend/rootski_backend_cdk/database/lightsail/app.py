"""
App that creates a lightsail instance and static IP address mapping to it.

.. note::

    Eric recommends *never* putting node.try_get_context() calls inside of a stack.
    Hiding those calls inside of a stack makes it very unintuitive to figure out what inputs
    you need to actually create a stack. Instead, write stacks and constructs assuming any
    required inputs will be passed as arguments to the constructor. Make the calls to try_get_context
    in the app.py.

    In each stack/construct, use a dataclass, enum, or constants to define actual string constants
    used for ContextVars (inputs) and Cloudformation Outputs (outputs).
"""

import aws_cdk as cdk
from rootski_backend_cdk.database.lightsail.stacks.lightsail_instance import ContextVars, LightsailInstanceStack

if __name__ == "__main__":
    app = cdk.App()

    environment = cdk.Environment(
        account="091910621680",
        region="us-west-2",
    )

    lightsail_stack = LightsailInstanceStack(
        app,
        "Rootski-Database-Stack-cdk",
        iam_access_key_id=app.node.try_get_context(ContextVars.iam_access_key_id.value),
        iam_access_key=app.node.try_get_context(ContextVars.iam_access_key.value),
    )

    app.synth()
