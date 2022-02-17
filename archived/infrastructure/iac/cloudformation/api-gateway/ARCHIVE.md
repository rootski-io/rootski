Before the rootski backend fell under the subdomain `api.rootski.io`, the backend
could only be accessed using an IP address.

This CloudFormation template creates
a REST API that invokes a Lambda function that pulls a single parameter value
from AWS Parameter Store. That value was a continually updated IP address
for the current spot instance on the backend server.

This approach is no longer needed. If it were needed, it would be advisable to
recreate the same functionality using AWS CDK or whichever IaC tool
is currently the standard for Rootski.
