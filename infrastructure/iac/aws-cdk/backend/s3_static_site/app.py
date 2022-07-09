"""
App creating a static site for the rootski docs.

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
from s3_static_site.s3_static_site_stack import S3StaticSiteStack

app = cdk.App()

#: parent domain for rootski
ROOTSKI_DOMAIN_NAME = "rootski.io"

#: subdomain for docs site
DOCS_SITE_SUBDOMAIN = "docs"

#: rootski environment with ``us-east-1`` as the region due to ACM limitation
ENVIRONMENT = cdk.Environment(
    account="091910621680",
    # ACM certs used with CloudFront::Distribution have to be in us-east-1
    region="us-east-1",
)

S3StaticSiteStack(
    app,
    "docs-s3-static-site--stack--cdk",
    domain_name=ROOTSKI_DOMAIN_NAME,
    subdomain=DOCS_SITE_SUBDOMAIN,
    env=ENVIRONMENT,
)

app.synth()
