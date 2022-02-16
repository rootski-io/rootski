#!xonsh

#
# Usage: ./apply.sh <ip_address>
#

from pathlib import Path
import json

#####################
# --- Constants --- #
#####################

THIS_DIR: Path = Path(__file__).parent
TF_STATE_JSON_FPATH = (THIS_DIR / "../../terraform/rootski-backend/terraform.tfstate").resolve()
ROOTSKI_FRONTEND_STACK_NAME = "Rootski-Front-End-CF"

CF_TEMPLATE_NAME = "subdomain.yml"
CF_TEMPLATE_FPATH: Path = THIS_DIR / CF_TEMPLATE_NAME

STACK_NAME_TEMPLATE = "Rootski-{subdomain}-Subdomain-CF"
# this stack exports the hosted zone
AWS_REGION = "us-west-2"
# this is not a valid IP for us, it is meant to be a placeholder
# to be updated later by our dynamic DNS script
ON_PREM_IP_ADDRESS = "10.0.0.1"
CF_CONSOLE_URL = f"https://us-west-2.console.aws.amazon.com/cloudformation/home?region={AWS_REGION}#/stacks?filteringStatus=active&filteringText=&viewNested=true&hideStacks=false"


# echo "[rootski] Error: no EC2 ip address provided"
print("[rootski] Usage: ./apply.sh [ip address]")
print("[rootski] Since :ip address: was not provided, getting it from ")
# if an EC2 ip address is not provided, get it from the terraform state
print("[rootski] Since :ip address: was not provided, getting it from $TF_STATE_PATH")

tf_json_txt: str = Path.read_text(TF_STATE_JSON_FPATH)
tf_json: dict = json.loads(tf_json_txt)
ec2_ip_address = tf_json["outputs"]["rootski_public_ip"]["value"]
print("[rootski] Using IP Address $EC2_IP_ADDRESS from terraform.tfstate file")

subdomains = [
    ("api", ec2_ip_address),
    ("traefik", ec2_ip_address),
    ("docker", ec2_ip_address),
    ("dbadmin", ec2_ip_address),
    ("on-prem", ON_PREM_IP_ADDRESS),
]

for subdomain, ip in subdomains:
    stack_name: str = STACK_NAME_TEMPLATE.format(subdomain=subdomain)
    template_fpath = f"file://{CF_TEMPLATE_FPATH}"
    aws cloudformation create-stack \
        --stack-name @(stack_name) \
        --template-body @(template_fpath) \
        --parameters \
            ParameterKey="RootskiFrontEndStackName",ParameterValue=@(ROOTSKI_FRONTEND_STACK_NAME) \
            ParameterKey="Subdomain",ParameterValue=@(subdomain) \
            ParameterKey="PublicIP",ParameterValue=@(ip) \
        --region @(AWS_REGION) \
        --profile rootski | cat
    print(f"[rootski] Successfully issued apply command for \n\tSubdomain: {subdomain}\n\tPublicIP: {ip}")

print(f"[rootski] Click here to go to the CloudFormation console:\n\t{CF_CONSOLE_URL}")
