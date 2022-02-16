#!/bin/bash

REGION="us-west-2"

echo $(aws cloudformation delete-stack --stack-name Rootski-API-Gateway-Lambda-CF --profile personal --region "$REGION")
echo "[rootski] Successfully issued destroy command"
