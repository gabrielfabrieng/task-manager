terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Latest Amazon Linux 2023 AMI (kept current via SSM public parameter).
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Use the account's default VPC/subnet to keep this example self-contained.
data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "app" {
  name        = "${var.project}-sg"
  description = "Allow HTTP from anywhere and SSH from an allowed CIDR."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Project = var.project }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    repo_url          = var.repo_url
    django_secret_key = var.django_secret_key
    postgres_password = var.postgres_password
    allowed_hosts     = var.allowed_hosts
  })

  tags = { Project = var.project, Name = var.project }
}

resource "aws_eip" "app" {
  instance = aws_instance.app.id
  tags     = { Project = var.project }
}
