# PowerShell script to run the GXtract MCP Server

param(
    [string]$Transport = $env:GXTRACT_TRANSPORT,
    [string]$Port = $env:GXTRACT_PORT,
    [string]$LogLevel = $env:GXTRACT_LOG_LEVEL,
    [string]$LogFormat = $env:GXTRACT_LOG_FORMAT,
    [string]$CacheTtl = $env:GXTRACT_CACHE_TTL,
    [string]$GroundxApiKey = $env:GROUNDX_API_KEY,
    [string]$GroundxBaseUrl = $env:GROUNDX_BASE_URL
)

# Construct the command with arguments only if they are provided
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path -Path $scriptDir -ChildPath "..\.venv\Scripts\gxtract.exe" # Assuming standard venv structure

if (-not (Test-Path $venvPath)) {
    $venvPath = "gxtract" # Fallback to gxtract in PATH if not found in .venv
    Write-Warning "gxtract.exe not found in .venv, attempting to use gxtract from PATH."
}

$commandArgs = @()

if ($Transport) { $commandArgs += @("--transport", $Transport) }
if ($Port) { $commandArgs += @("--port", $Port) }
if ($LogLevel) { $commandArgs += @("--log-level", $LogLevel) }
if ($LogFormat) { $commandArgs += @("--log-format", $LogFormat) }
if ($CacheTtl) { $commandArgs += @("--cache-ttl", $CacheTtl) }
if ($GroundxApiKey) { $commandArgs += @("--groundx-api-key", $GroundxApiKey) }
if ($GroundxBaseUrl) { $commandArgs += @("--groundx-base-url", $GroundxBaseUrl) }

Write-Host "Starting GXtract server..."
Write-Host "Command: $venvPath $commandArgs"

# Execute the command
& $venvPath $commandArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "GXtract server exited with error code $LASTEXITCODE"
}
else {
    Write-Host "GXtract server finished."
}
