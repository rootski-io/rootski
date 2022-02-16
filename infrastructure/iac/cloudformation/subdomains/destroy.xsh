#!xonsh

STACK_NAME="Rootski-Subdomain-CF"
AWS_REGION="us-west-2"
STACK_NAME_TEMPLATE = "Rootski-{subdomain}-Subdomain-CF"


subdomains = [
    "api",
    "traefik",
    "on-prem",
]

for subdomain in subdomains:
    stack_name: str = STACK_NAME_TEMPLATE.format(subdomain=subdomain)
    aws cloudformation delete-stack \
        --stack-name @(stack_name) \
        --profile rootski \
        --region @(AWS_REGION)
    print(f"[rootski] Successfully issued destroy command for '{stack_name}'")
