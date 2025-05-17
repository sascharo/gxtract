# PowerShell script to interact with GXtract using FastMCP Inspector

param(
    [string]$ServerUrl = "http://localhost:8080" # Default if GXtract is running HTTP on port 8080
)

# Ensure FastMCP is installed or accessible
# This script assumes `fastmcp-inspector` is in the PATH or in the current environment.

Write-Host "Attempting to launch FastMCP Inspector for GXtract at $ServerUrl ..."
Write-Host "If GXtract is running with --transport stdio, this inspector won\'t connect directly."
Write-Host "Ensure GXtract is running with --transport http and accessible at the specified URL."
Write-Host "You might need to install fastmcp separately if not in the same venv: uv pip install fastmcp"

fastmcp-inspector --url $ServerUrl

if ($LASTEXITCODE -ne 0) {
    Write-Error "FastMCP Inspector exited with error code $LASTEXITCODE. Ensure fastmcp-inspector is installed and GXtract HTTP server is running at $ServerUrl."
}
else {
    Write-Host "FastMCP Inspector closed."
}
