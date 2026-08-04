variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix for tagged resources."
  type        = string
  default     = "task-manager"
}

variable "instance_type" {
  description = "EC2 instance size."
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Existing EC2 key pair name for SSH access."
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH (lock this to your IP)."
  type        = string
  default     = "0.0.0.0/0"
}

variable "repo_url" {
  description = "Public Git URL cloned and run on the instance."
  type        = string
}

variable "django_secret_key" {
  description = "Django SECRET_KEY for the deployed app."
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "Database password for the deployed app."
  type        = string
  sensitive   = true
}

variable "allowed_hosts" {
  description = "DJANGO_ALLOWED_HOSTS value (comma-separated)."
  type        = string
  default     = "*"
}
