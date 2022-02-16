output "terraform_state_bucket_arn" {
  value = aws_s3_bucket.terraform_remote_state.arn
}

output "terraform_locks_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}
