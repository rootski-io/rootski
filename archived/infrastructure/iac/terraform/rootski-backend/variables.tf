########################################
### ------ REQUIRED VARIABLES ------ ###
########################################

########################################
### ------ OPTIONAL VARIABLES ------ ###
########################################

variable "ec2_size" {
  type        = string
  default     = "m1.large"
  description = "AWS API name for EC2 size e.g. 'm1.large'"
}

variable "spot_price" {
  type        = string
  default     = "0.02"
  description = "Max allowed price for the spot instance bid"
}

variable "key_name" {
  type        = string
  default     = "rootski"
  description = "Name of SSH key pair used to attach to the EC2 instance."
}

variable "ami_id" {
  type        = string
  default     = "ami-0e5b6b6a9f3db6db8" # id of a community made amazon linux 2 AMI
  # default     = "ami-072ee3bebf0e24400" # id of the rootski AMI
  description = "ID of AMI used for running the ec2 instance"
}

variable "allowed_ips_cidr" {
  type        = string
  default     = "0.0.0.0/0"
  description = "Single CIDR block describing all inbound and outbound ip addresses. By default, all IPs are allowed in and out."
}

variable "efs_id" {
  type        = string
  default     = "fs-97ec6392"
  description = "Id of an EFS networked filesystem for the ec2 instance to mount and use. If empty string, an EFS will be created."
}
