#!/bin/bash

STACK_NAME="Rootski-Front-End-CF"
REGION="us-west-2"

echo $(aws s3 rm s3://www.rootski.io --recursive --profile personal)
echo "[rootski] Successfully issued command to empty the front end bucket"
echo $(aws cloudformation delete-stack --stack-name "$STACK_NAME" --profile personal --region "$REGION")
echo "[rootski] Successfully issued destroy command"
