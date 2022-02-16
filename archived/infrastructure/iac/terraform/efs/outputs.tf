output "efs_id" {
  description = "AWS id of the EFS to be used for rootski. Format: fs-xxxxxxx"
  value       = aws_efs_file_system.efs.id
}
