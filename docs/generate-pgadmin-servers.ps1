param(
  [string]$OutputPath = "pgadmin-ldsgrupo1-servers.json",
  [string]$HostName = "localhost",
  [string]$Username = "postgres",
  [string]$Group = "LDS Grupo 1"
)

$servers = @(
  @{ Name = "db-auth";         Port = 15432; MaintenanceDB = "auth_db" },
  @{ Name = "db-usuario";      Port = 15433; MaintenanceDB = "usuario_db" },
  @{ Name = "db-cliente";      Port = 15434; MaintenanceDB = "cliente_db" },
  @{ Name = "db-servico";      Port = 15435; MaintenanceDB = "servico_db" },
  @{ Name = "db-os";           Port = 15436; MaintenanceDB = "os_db" },
  @{ Name = "db-financeiro";   Port = 15437; MaintenanceDB = "financeiro_db" },
  @{ Name = "db-auditoria";    Port = 15438; MaintenanceDB = "auditoria_db" },
  @{ Name = "db-notification"; Port = 15439; MaintenanceDB = "notification_db" }
)

$serverEntries = [ordered]@{}
$index = 1

foreach ($server in $servers) {
  $serverEntries["$index"] = [ordered]@{
    Name = $server.Name
    Group = $Group
    Host = $HostName
    Port = $server.Port
    MaintenanceDB = $server.MaintenanceDB
    Username = $Username
    SSLMode = "prefer"
    ConnectNow = $false
  }

  $index++
}

$payload = [ordered]@{
  Servers = $serverEntries
}

$resolvedOutputPath = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
  $OutputPath
} else {
  Join-Path (Get-Location) $OutputPath
}

$json = $payload | ConvertTo-Json -Depth 5
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($resolvedOutputPath, $json, $utf8NoBom)

Write-Host "Ficheiro gerado: $resolvedOutputPath"
Write-Host "Importe no pgAdmin em Tools > Import/Export Servers > Import."
