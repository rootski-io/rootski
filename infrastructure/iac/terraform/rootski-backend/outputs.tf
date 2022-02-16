output "rootski_public_ip" {
  value = aws_spot_instance_request.rootski_spot_request.public_ip
}

output "rootski_public_dns" {
  value = aws_spot_instance_request.rootski_spot_request.public_dns
}
