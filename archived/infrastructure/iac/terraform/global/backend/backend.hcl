bucket         = "rootski-terraform-remote-state"
region         = "us-east-1"
dynamodb_table = "rootski-terraform-locks"
encrypt        = true # redundant with encryption settings for s3 bucket, but good practice
