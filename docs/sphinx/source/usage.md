# Using GXtract

Once GXtract is installed and configured, you can start the server and interact with it using an MCP client. This guide covers basic usage scenarios.

## Starting the Server

Navigate to your project directory where GXtract is installed (and activate the virtual environment if you haven\'t already).

**Using STDIO Transport (Default):**

This is common for direct integration with tools like VS Code extensions.

```bash
gxtract --groundx-api-key YOUR_API_KEY_HERE
```

Or, if `GROUNDX_API_KEY` is set as an environment variable:

```bash
gxtract
```

The server will start and listen for MCP messages on standard input/output.

**Using HTTP Transport:**

This runs GXtract as an HTTP server, which can be useful for testing or if your client communicates over HTTP.

```bash
gxtract --transport http --port 8000 --groundx-api-key YOUR_API_KEY_HERE
```

Or, with environment variables:

```bash
$env:GXTRACT_TRANSPORT="http" # PowerShell
$env:GXTRACT_PORT="8000"      # PowerShell
# export GXTRACT_TRANSPORT="http" # bash/zsh
# export GXTRACT_PORT="8000"      # bash/zsh
gxtract
```

The server will start and be accessible at `http://localhost:8000` (or the configured port).

## Secure API Key Management

The GroundX API key is required for GXtract to communicate with the GroundX platform. This key should be handled securely to prevent unauthorized access. There are several options for managing your API key:

### Environment Variables

Setting the API key as an environment variable is the most straightforward approach, especially for development environments:

```powershell
# PowerShell
$env:GROUNDX_API_KEY = "your-api-key-here"

# Or to set it permanently for your user
[Environment]::SetEnvironmentVariable("GROUNDX_API_KEY", "your-api-key-here", "User")
```

```bash
# Bash/Zsh
export GROUNDX_API_KEY="your-api-key-here"

# Or add to your .bashrc/.zshrc for persistence
echo 'export GROUNDX_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### VS Code Secure Storage

VS Code can securely store your API key in your system's credential manager (Windows Credential Manager, macOS Keychain, etc.):

1. **Configure the input in `settings.json`**:

```json
"inputs": [
    {
        "type": "promptString",
        "id": "groundx-api-key",
        "description": "GroundX API Key",
        "password": true
    }
]
```

2. **Reference the input in your MCP server configuration**:

```json
"env": {
    "GROUNDX_API_KEY": "${input:groundx-api-key}"
}
```

3. **First Use**: VS Code will prompt you for the API key the first time it starts the server, then store it securely.

This approach is especially recommended for shared workstations or when you don't want to store the key in your environment variables.

### Security Best Practices

- Never commit your API key to version control
- Rotate your API key periodically
- Use the most secure method available for your environment
- Limit API key permissions to only what is needed for your use case
- For production deployments, consider using a secrets management system

## Interacting with GXtract (MCP Client)

You will need an MCP client to send requests to GXtract and receive responses. Examples include:

*   **VS Code with an MCP Extension:** Configure the extension to point to your `gxtract` executable and provide necessary arguments.
*   **Command-Line MCP Clients:** Tools like `mcp-cli` or custom scripts can be used to send JSON-RPC messages compliant with MCP.
*   **FastMCP v2 Inspector:** The FastMCP library provides an inspector tool that can connect to an MCP server (especially useful for HTTP transport) to explore available tools and send requests. See the [FastMCP documentation](https://context7.com/jlowin/fastmcp) for details on its inspector.

### Example MCP Request (Conceptual)

An MCP client would send a JSON-RPC request. For example, to use the `groundx/searchDocuments` tool:

```json
{
  "jsonrpc": "2.0",
  "method": "groundx/searchDocuments",
  "params": {
    "query": "machine learning architectures for natural language processing",
    "n_results": 5
  },
  "id": "request-123"
}
```

GXtract would process this request and return a JSON-RPC response:

```json
{
  "jsonrpc": "2.0",
  "result": [
    { "id": "doc1", "title": "Paper A", "score": 0.9 },
    { "id": "doc2", "title": "Paper B", "score": 0.85 }
    // ... other results
  ],
  "id": "request-123"
}
```

(The actual structure of `params` and `result` depends on the specific tool\'s definition.)

## Available Tools

GXtract comes with a set of pre-built tools, primarily for interacting with GroundX.

*   **`groundx/searchDocuments`**: Searches for documents in GroundX.
*   **`groundx/queryDocument`**: Asks specific questions about a document in GroundX.
*   **`groundx/explainSemanticObject`**: Explains semantic objects (diagrams, tables) within a document.
*   **`cache/getCacheStatistics`**: Retrieves statistics about the local GroundX metadata cache.
*   **`cache/listCachedResources`**: Lists projects and buckets currently in the cache.
*   **`cache/refreshMetadataCache`**: Manually triggers a refresh of the GroundX metadata cache.
*   **`cache/refreshCachedResources`**: Another way to manually refresh the GroundX projects and buckets cache.

Refer to the [Tools documentation](./tools_docs/groundx.md) and [./tools_docs/cache_management.md](./tools_docs/cache_management.md) for detailed information on each tool, including their parameters and expected responses.

## Logging

GXtract logs its operations, which can be helpful for debugging and monitoring. The log level and format can be configured as described in the [Configuration](./configuration.md) section.

*   **Log Levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
*   **Log Formats:** `text` (human-readable), `json` (structured, for machine processing).

By default, logs are printed to standard error.

## Stopping the Server

*   **STDIO Transport:** Send an EOF (End-of-File) signal to the server\'s standard input (e.g., `Ctrl+D` in Linux/macOS terminals, `Ctrl+Z` then Enter in Windows Command Prompt if the client doesn\'t handle shutdown gracefully). If launched by VS Code, closing VS Code or the MCP session usually handles this.
*   **HTTP Transport:** Press `Ctrl+C` in the terminal where the server is running.

## Cache Management

GXtract maintains an in-memory cache of metadata from your GroundX account (projects and buckets) to improve performance and reduce API calls. This section explains how to manage this cache effectively.

### Cache Population

The cache is automatically populated when the GXtract server starts. If this initial population fails (for example, due to connectivity issues or API key problems), the server will still start, but it will log warning messages. You can manually populate the cache later using the refresh tools.

### When to Refresh the Cache

You should manually refresh the cache in the following situations:

1. After creating new projects or buckets in your GroundX account
2. If you see warnings about cache population failures in the logs
3. If tools that require project or bucket information aren't working correctly

### Refreshing the Cache

#### Using an MCP Client (e.g., VS Code)

If you're using VS Code with MCP support:

1. Open the MCP chat interface
2. Use the appropriate mention for your GXtract server (e.g., `@GXtract`)
3. Request a cache refresh:
   ```
   @GXtract please refresh the GroundX metadata cache
   ```

#### Using Direct JSON-RPC (for HTTP Transport)

If you're using GXtract with HTTP transport, you can make a direct JSON-RPC call:

```bash
curl -X POST http://localhost:8080/jsonrpc -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "method": "cache/refreshMetadataCache",
  "params": {},
  "id": "request-1"
}'
```

### Checking Cache Status

You can check the status of the cache using the `cache/getCacheStatistics` tool, which provides information about cache hits, misses, and refresh history. You can also list the currently cached projects and buckets with `cache/listCachedResources`.

### Common Issues

- **Empty Cache**: If the cache is empty after startup, check your API key and network connectivity, then try a manual refresh.
- **Missing Projects**: If recently created projects aren't appearing, refresh the cache to update it with the latest data.
- **Connection Issues**: If cache refresh fails with connectivity errors, verify your network connection and the status of the GroundX API.

For more detailed information about cache management, see [Cache Management Tools](./tools_docs/cache_management.md).

## Next Steps

*   Explore the detailed documentation for each [Tool](./tools_docs/groundx.md).
*   If you plan to develop custom tools or contribute to GXtract, see the [Development](./development.md) guide.
