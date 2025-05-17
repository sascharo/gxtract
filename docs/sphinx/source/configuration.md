# Configuration

GXtract can be configured using command-line arguments and environment variables. Environment variables take precedence over default values, and command-line arguments take precedence over environment variables.

## Command-Line Arguments

When starting the GXtract server, you can use the following command-line arguments. Run `gxtract --help` to see the most up-to-date list.

*   `--transport {stdio|http}`: Specifies the MCP transport protocol to use. (Default: `stdio`)
    *   `stdio`: Uses standard input/output for communication, suitable for direct integration with clients like VS Code extensions.
    *   `http`: Runs an HTTP server (with Server-Sent Events for streaming), accessible via a specified port.
*   `--port PORT`: The port number to use when `--transport` is `http`. (Default: `8080`)
*   `--log-level {DEBUG|INFO|WARNING|ERROR|CRITICAL}`: Sets the logging level for the server. (Default: `INFO`)
*   `--log-format {text|json}`: Sets the log output format. (Default: `text`)
*   `--cache-ttl SECONDS`: Time-to-live in seconds for the GroundX metadata cache. After this duration, the cache will be refreshed. (Default: `3600` seconds = 1 hour)
*   `--groundx-api-key KEY`: Your GroundX API key. **Required** for GroundX tools to function.
*   `--groundx-base-url URL`: The base URL for the GroundX API. (Optional, defaults to the standard GroundX API endpoint).

**Example:**
```bash
gxtract --transport http --port 8000 --log-level DEBUG --groundx-api-key YOUR_API_KEY_HERE
```

## Environment Variables

GXtract can also be configured using the following environment variables:

*   `GXTRACT_TRANSPORT`: Equivalent to `--transport`. (e.g., `stdio` or `http`)
*   `GXTRACT_PORT`: Equivalent to `--port`. (e.g., `8080`)
*   `GXTRACT_LOG_LEVEL`: Equivalent to `--log-level`. (e.g., `DEBUG`)
*   `GXTRACT_LOG_FORMAT`: Equivalent to `--log-format`. (e.g., `json`)
*   `GXTRACT_CACHE_TTL`: Equivalent to `--cache-ttl`. (e.g., `1800` for 30 minutes)
*   `GROUNDX_API_KEY`: Equivalent to `--groundx-api-key`. **Required**.
*   `GROUNDX_BASE_URL`: Equivalent to `--groundx-base-url`.

**Example (PowerShell):**
```powershell
$env:GROUNDX_API_KEY = "YOUR_API_KEY_HERE"
$env:GXTRACT_LOG_LEVEL = "DEBUG"
gxtract
```

**Example (bash/zsh):**
```bash
export GROUNDX_API_KEY="YOUR_API_KEY_HERE"
export GXTRACT_LOG_LEVEL="DEBUG"
gxtract
```

## Tool-Specific Configuration

Some tools might have their own specific configuration needs. These are typically handled via environment variables or by passing parameters during tool invocation.

*   **GroundX Tools:** Primarily require the `GROUNDX_API_KEY`. The `groundx-base-url` can be set if you need to target a different GroundX API endpoint (e.g., for testing or a private instance).

## VS Code Integration

When using GXtract with the VS Code MCP extension, you\'ll configure the server path and arguments within VS Code\'s `settings.json`. Refer to the [README.md](../../../README.md) for an example configuration (see the "Quick Start: VS Code Integration" section).

Ensure that the `GROUNDX_API_KEY` is available in the environment where VS Code launches the GXtract server. This might mean setting it globally, in your shell profile, or within VS Code\'s integrated terminal environment if it inherits it.

## Next Steps

After configuring GXtract, you can learn more about [Using GXtract](./usage.md)
