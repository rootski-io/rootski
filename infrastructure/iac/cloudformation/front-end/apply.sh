#!/bin/bash

STACK_NAME="Rootski-Front-End-CF"
REGION="us-west-2"

echo $(aws cloudformation create-stack --stack-name "$STACK_NAME" \
  --template-body file://./static-website.yml \
  --parameters ParameterKey="DomainName",ParameterValue="$DOMAIN_NAME" \
               ParameterKey="FullDomainName",ParameterValue="$FULL_DOMAIN_NAME" \
               ParameterKey="AcmCertificateArn",ParameterValue="$ACM_CERTIFICATE_ARN" \
  --profile dev-global \
  --region "$REGION")
echo "[rootski] Successfully issued apply command"
