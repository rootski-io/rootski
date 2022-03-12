# ⭐️ Get access to AWS

## Project Context

rootski runs in AWS. If you are working exclusively on the frontend and backend code, you
won't need access to AWS.

If you want to help with DevOps, MLOps, and application monitoring, Infrastructure as Code,
or Continuous Delivery, you will need AWS access.

Even if you aren't working on the technical side of rootski, you may need some level of AWS
access. If customers are having issues with the product due to downtime or code errors,
we will eventually have dashboards in place to help diagnose these and plan work to resolve
the issues. Product Managers and "Site Reliability Engineers" and anyone who cares
will need access to see these.

Find resources for this in the `Onboarding` page of the knowledge base.

## Project Requirements

1. Ask in `#onboarding-and-training` in slack to create an IAM user for you in AWS.

2. Get an AWS access key and secret key for your user from Eric.

3. Log in and set your password.

4. Download the AWS CLI version 2.

5. Run `aws configure --profile rootski` and copy/paste your credentials into the terminal when prompted.

6. Validate your setup by running `aws sts get-caller-identity --profile rootski` and getting a successful response.
