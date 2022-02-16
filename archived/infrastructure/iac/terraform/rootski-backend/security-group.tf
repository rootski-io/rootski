resource "aws_security_group" "rootski" {
  name        = "rootski_security_group"
  description = "Allows traffic in and out of the ec2 instance."
  vpc_id      = aws_default_vpc.default.id # declared in main.tf
}

resource "aws_security_group_rule" "allow_nfs_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "NFS"
  from_port   = 2049
  to_port     = 2049
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_traefik_dashboard_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "traefik UI"
  from_port   = 8080
  to_port     = 8080
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_all_outbound" {
  type              = "egress"
  security_group_id = aws_security_group.rootski.id

  description = "all"
  from_port   = 0
  to_port     = 65535
  protocol    = "-1"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_ssh_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "SSH"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_http_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "HTTP"
  from_port   = 80
  to_port     = 80
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_https_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "HTTPS"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_rootski_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "SSH"
  from_port   = 3333
  to_port     = 3333
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
resource "aws_security_group_rule" "allow_postgres_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.rootski.id

  description = "SSH"
  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = [var.allowed_ips_cidr]
}
