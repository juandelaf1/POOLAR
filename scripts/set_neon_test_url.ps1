# Configura POOLAR_TEST_POSTGRES_URL en poolar/.env SIN mostrar la clave en chat.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\set_neon_test_url.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root ".env"
$url = Read-Host "Pega aqui la URL de conexion Neon (se guardara solo en .env local)".Trim()
if (-not $url -or $url -notmatch '^postgres(ql)?(\+psycopg2)?://') {
  throw "No parece una URL Postgres valida."
}
if ($url -notmatch 'sslmode=') { $url = $url + ($(if ($url -match '\?') { '&' } else { '?' })) + 'sslmode=require' }
if ($url -match '^postgres(ql)?://' -and $url -notmatch '\+psycopg2') {
  $url = $url -replace '^postgresql://','postgresql+psycopg2://' -replace '^postgres://','postgresql+psycopg2://'
}
$lines = @()
if (Test-Path $envFile) { $lines = Get-Content $envFile }
$lines = $lines | Where-Object { $_ -notmatch '^POOLAR_TEST_POSTGRES_URL\s*=' }
$lines += "POOLAR_TEST_POSTGRES_URL=$url"
Set-Content -Path $envFile -Value $lines -Encoding UTF8
Write-Host "OK. Guardado POOLAR_TEST_POSTGRES_URL en .env (local). Ahora dime 'listo' en el chat."