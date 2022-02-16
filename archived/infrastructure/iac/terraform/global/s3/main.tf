terraform {
  backend "local" {
    path = "./.terraform/terraform.tfstate"
  }
}

# terraform {
#   backend "s3" {
#     key = "global/s3/terraform.tfstate"
#     # other backend properties come from global/backend/backend.hcl
#     # you can incorporate these into the "terraform init" process by running
#     # terraform init -backend-config=/path/to/global/s3/backend.hcl
#     # terragrunt can provide a better way to do this... but 3rd party tools
#   }
# }


provider "aws" {
  region  = "us-west-2" # doesn't matter since s3 buckets are global
  profile = "personal"
}

# store terraform state
resource "aws_s3_bucket" "terraform_remote_state" {
  bucket = "rootski-terraform-remote-state"

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true # protect data stores from being deleted
  }

  # all data written to the s3 bucket will be encrypted
  # this makes it safer to have secrets in the remote state file
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# provide terraform state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "rootski-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
