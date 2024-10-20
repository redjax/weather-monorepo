# PowerShell script

$containersDir = "containers"
$dockerCmd = "docker compose -f containers/db-messaging.docker-compose.yml --env-file containers/.env up -d"

# Execute the Docker command
try {
    Invoke-Expression $dockerCmd
}
catch {
    Write-Host "Error executing Docker command: $_"
}
