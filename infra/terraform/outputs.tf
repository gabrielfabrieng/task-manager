output "public_ip" {
  description = "Public IP of the app instance."
  value       = aws_eip.app.public_ip
}

output "app_url" {
  description = "URL to open once bootstrap finishes (a few minutes)."
  value       = "http://${aws_eip.app.public_ip}"
}
