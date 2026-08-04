# Terraform — AWS deploy

Provisions a single EC2 instance (Amazon Linux 2023) that installs Docker and
runs the production stack (`docker-compose.prod.yml`) via `user_data`. An
Elastic IP gives it a stable public address. Kept deliberately small — one box,
default VPC — to be reviewable, not a full ECS/RDS platform.

## Architecture choice

| Option | Why not here |
|--------|--------------|
| ECS Fargate + RDS + ALB | Production-correct but heavy for a review; more moving parts than the test warrants |
| **EC2 + Docker Compose** ✅ | Same containers as local; one file to read; cheap; enough to demonstrate IaC |

For a real production system, swap the EC2 box for ECS services, move Postgres to
RDS and Redis to ElastiCache, and put an ALB (with ACM TLS) in front — the app
needs no code change, only settings/env.

## Usage

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # fill in values
terraform init
terraform apply
# wait ~3-5 min for user_data (Docker build) to finish
terraform output app_url
```

## Notes
- `terraform.tfvars`, state files and `.terraform/` are gitignored (contain secrets/state).
- The demo box serves plain HTTP; `DJANGO_SECURE_SSL_REDIRECT` is disabled for it.
  Add TLS (ALB + ACM, or Caddy/Traefik) before any real use.
- Lock `allowed_ssh_cidr` to your IP.
