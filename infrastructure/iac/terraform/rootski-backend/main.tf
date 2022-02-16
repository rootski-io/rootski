provider "aws" {
  region  = "us-west-2" # doesn't matter since s3 buckets are global
  profile = "personal"
}

# this version/backend block was causing issues with the terraform state version; commenting it out fixes it
# terraform {
#   required_version = ">= 0.13"
#   backend "local" {
#     path = "./.terraform/terraform.tfstate"
#   }
# }

# this resource "adopts" the default VPC as a resource rather than creating it
resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}

# IAM Role
resource "aws_iam_role" "rootski_role" {
  name = "RootskiBackendRole"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
            "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy" "rootskiPolicy" {
  name = "rootskiPolicy"
  role = aws_iam_role.rootski_role.id

  # this policy grants all cloudformation and route53 access... yep
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "cloudformation:*"
        ],
        "Effect": "Allow",
        "Resource": "*"
      },
      {
        "Action": [
          "route53:*"
        ],
        "Effect": "Allow",
        "Resource": "*"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy" "route53_traefik_letsencrypt_dnschallege_provider_policy" {
  name = "route53_traefik_letsencrypt_dnschallege_provider_policy"
  role = aws_iam_role.rootski_role.id

  # this policy grants permissions to alter route53 record sets
  # and list hosted zones; this will enable the traefik container
  # running on the EC2 instance to answer the LetsEncrypt DNS Challenge
  policy = <<-EOF
  {
   "Version": "2012-10-17",
   "Statement": [
       {
           "Sid": "",
           "Effect": "Allow",
           "Action": [
               "route53:GetChange",
               "route53:ChangeResourceRecordSets",
               "route53:ListResourceRecordSets"
           ],
           "Resource": [
               "arn:aws:route53:::hostedzone/*",
               "arn:aws:route53:::change/*"
           ]
       },
       {
           "Sid": "",
           "Effect": "Allow",
           "Action": "route53:ListHostedZonesByName",
           "Resource": "*"
       }
    ]
  }
  EOF
}


# grant rootski role full ec2 access
resource "aws_iam_role_policy_attachment" "ec2_full_access" {
  role       = aws_iam_role.rootski_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

# grant rootski role full ssm access
resource "aws_iam_role_policy_attachment" "ssm_full_access" {
  role       = aws_iam_role.rootski_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}


# If you use the AWS Management Console to create a role for Amazon EC2,
# the console automatically creates an instance profile and gives it the same name as the role.
# When you then use the Amazon EC2 console to launch an instance with an IAM role,
# you can select a role to associate with the instance.
# In the console, the list that's displayed is actually a list of instance profile names.
# The console does not create an instance profile for a role that is not associated with Amazon EC2.
resource "aws_iam_instance_profile" "rootski_iam_profile" {
  # use this command to delete it:
  # aws iam delete-instance-profile --profile personal --instance-profile-name RootskiEC2InstanceProfile
  name = "RootskiEC2InstanceProfile"
  role = aws_iam_role.rootski_role.name
}

data "aws_region" "current_region" {}
data "template_file" "user_data" {
  template = file("${path.module}/user-data.sh")
  vars = {
    ROOTSKI_FILE_SYSTEM_ID = var.efs_id
    AWS_REGION             = data.aws_region.current_region.name
  }
}

# Fantastic spot instance terraform documentation:
# https://www.terraform.io/docs/providers/aws/r/spot_instance_request.html
resource "aws_spot_instance_request" "rootski_spot_request" {
  spot_price                      = var.spot_price
  instance_type                   = var.ec2_size
  spot_type                       = "persistent" # "one-time"
  instance_interruption_behaviour = "terminate"  # optional (setting this to "terminate" is the default behavior)

  # Terraform will wait 10m for the request to complete
  # when set, the spot_instance_id will be accessible which
  # we can use to auto-associate the elastic ip
  wait_for_fulfillment = "true"

  # ec2 config
  ami                  = var.ami_id
  key_name             = var.key_name
  user_data            = data.template_file.user_data.rendered
  security_groups      = [aws_security_group.rootski.name]
  iam_instance_profile = aws_iam_instance_profile.rootski_iam_profile.name

  # configure the default storage device (/dev/xvda1--defaults to 8gb)
  # TIP: use 'df -h' on the server to check the % disk usage of all devices
  root_block_device {
    delete_on_termination = true
    volume_size = 20 # gigabytes
    volume_type = "gp3" # $0.08/GB/mo
  }

  tags = {
    Name = "rootski_spot_request"
  }
}
