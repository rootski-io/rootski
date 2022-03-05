#!/bin/bash

STACK_NAME="Rootski-Docs-Site-CF"
REGION="us-west-2"
DOMAIN_NAME="rootski.io"
FULL_DOMAIN_NAME="docs.rootski.io"
ACM_CERTIFICATE_ARN="arn:aws:acm:us-east-1:091910621680:certificate/71a39faa-9225-4232-85f8-00a86935b1af"

echo $(aws cloudformation create-stack --stack-name "$STACK_NAME" \
  --template-body file://./static-website.yml \
  --parameters ParameterKey="DomainName",ParameterValue="$DOMAIN_NAME" \
               ParameterKey="FullDomainName",ParameterValue="$FULL_DOMAIN_NAME" \
               ParameterKey="AcmCertificateArn",ParameterValue="$ACM_CERTIFICATE_ARN" \
  --profile rootski \
  --region "$REGION")
echo "[rootski] Successfully issued apply command"
