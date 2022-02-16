#!/bin/bash

REGION="us-west-2"

echo $(aws cloudformation create-stack --stack-name Rootski-API-Gateway-Lambda-CF --profile personal \
  --template-body file://./api-gateway-for-ssm.yml \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM)
echo "[rootski] Successfully issued apply command"
