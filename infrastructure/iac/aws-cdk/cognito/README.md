# Cognito CDK by Eric

## Overview

The Rootksi frontend uses the AWS Amplify client library to reach out to
the AWS user pool created by this CDK project to authenticate.

### Identity Providers

To set up Google, Facebook, Amazon, Apple, etc. as "OAuth Identity Providers",
follow the [Amplify documentation](https://docs.amplify.aws/lib/auth/social/q/platform/js)

### Spinning up the Cognito User Pool

This'll do the trick. Just make sure that the `cdk` CLI is installed.

``` bash
# install the needed python packages into a virtual environment
cd infrastructure/aws-cdk/cognito
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run cdk deploy against the desired region
AWS_DEFAULT_REGION="us-west-2" cdk deploy --profile personal
```

**NOTE!!!** You need to hook this up with the front end. After running `cdk deploy ...`,
you'll see several stack outputs. Copy/paste those into the correct JS variables in
`rootski_frontend/src/aws-cognito/auth-utils.tsx`.

### Config File

If you want to set up more OAuth providers (Google, Apple, Facebook, Amazon, etc.) you'll need
to add one `CfnUserPoolIdentityProvider` resource for each in the stack.

Place the OAuth `client_secret` and `client_id` for those in the
`infrastructure/aws-cdk/cognito/src/rootski-oauth-providers.yml` file.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
