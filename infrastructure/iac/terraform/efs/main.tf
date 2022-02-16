#
# To import this preexisting resource, I used
# terraform import aws_efs_file_system.efs fs-c154276b
#

provider "aws" {
  region  = "us-west-2"
  profile = "personal"
}

# comment out this block next time you create the efs from scratch; this messes with the .tfstate version
terraform {
  backend "local" {
    path = "./.terraform/terraform.tfstate"
  }
}

# terraform {
#   backend "s3" {
#     key = "prod/data-storage/efs/terraform.tfstate"
#     # be sure to run the following init command from this directory
#     # terraform init -backend-config="../global/backend/backend.hcl"
#   }
# }

resource "aws_efs_file_system" "efs" {
  tags = {
    "project" = "rootksi"
  }
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS" # AFTER_7_DAYS, AFTER_14_DAYS, AFTER_30_DAYS, AFTER_60_DAYS, or AFTER_90_DAYS
  }
}
