# GXtract Architecture

This document outlines the architecture of the GXtract MCP server.

## System Overview

The high-level architecture of GXtract illustrates how different components interact:

```{mermaid}
graph TB
    subgraph "Client"
        VSC[VS Code / Editor]
    end

    subgraph "GXtract MCP Server"
        MCP[MCP Interface<br>stdio/http]
        Server[GXtract Server]
        Cache[Metadata Cache]
        Tools[Tool Implementations]
    end

    subgraph "External Services"
        GXAPI[GroundX API]
    end

    VSC -->|MCP Protocol| MCP
    MCP --> Server
    Server --> Tools
    Tools -->|Query| GXAPI
    Tools -->|Read/Write| Cache
    Cache -.->|Refresh| GXAPI
```

### Detailed Component View

For a more detailed look at how the components interact internally:

```{mermaid}
flowchart TD
    CLI[CLI Entry Point<br>main.py] --> Config[Config<br>config.py]
    CLI --> ServerInit[Server Initialization<br>server.py]
    Config --> ServerInit
    
    ServerInit --> FastMCP[FastMCP<br>Instance]
    ServerInit --> Transport[Transport<br>stdio/http]
    ServerInit --> ToolRegistry[Tool<br>Registration]
    
    subgraph "Tool Modules"
        GroundX[GroundX Tools<br>groundx.py]
        CacheMgmt[Cache Management<br>cache_management.py]
        OtherTools[Other Tools<br>...]
    end
    
    ToolRegistry --> GroundX
    ToolRegistry --> CacheMgmt
    ToolRegistry --> OtherTools
    
    GroundX --> CacheModule[Cache<br>cache.py]
    CacheMgmt --> CacheModule
    
    CacheModule --> GXClient[GroundX Client<br>groundx SDK]
    GroundX --> GXClient
    
    Transport --> FastMCP
    FastMCP --> ToolRegistry
    
    GXClient -->|API Calls| GXAPI[GroundX API]
```

The diagram above shows the main components of the GXtract system:

1. **Client Layer**: VS Code or other compatible editors that communicate with GXtract
2. **MCP Interface**: Handles MCP protocol communication (via stdio or HTTP)
3. **GXtract Server**: Core server component managing tool registration and requests
4. **Tools**: Specialized implementations for various GroundX operations
5. **Cache**: In-memory storage for GroundX metadata to improve performance
6. **GroundX API**: External service providing document understanding capabilities

## Core Components

GXtract is built upon several key components and libraries:

1.  **Python 3.12:** The core programming language.
2.  **FastMCP v2:** A Python library providing the foundation for creating MCP servers. GXtract uses `FastMCP` to handle MCP communication (JSON-RPC 2.0) and tool registration.
    *   **Transports:** FastMCP supports different transport layers. GXtract allows selection between:
        *   `StdioTransport`: Communication over standard input/output, typically used for direct integration with client applications like VS Code extensions.
        *   `HttpTransport`: Communication over HTTP, with Server-Sent Events (SSE) for streaming responses. This allows GXtract to act as a web server accessible over a network.
3.  **`asyncio`:** Python's library for asynchronous programming. GXtract is heavily asynchronous to ensure high performance and responsiveness, especially for I/O-bound operations like network requests to GroundX or file system access.
4.  **UV:** The package manager used for dependency management and virtual environments, configured via `pyproject.toml`.
5.  **GroundX Python SDK (`groundx`):** The official Python library for interacting with the GroundX API. Tools within GXtract use this SDK to perform actions like searching documents, querying, and explaining semantic objects.

## Project Structure Overview

(Refer to the [Development Guide](./development.md) for a detailed file structure.)

The main application logic resides in the `src/gxtract` directory:

*   **`main.py`:**
    *   Parses command-line arguments (using `argparse`).
    *   Loads configuration settings from environment variables and CLI arguments (managed by `config.py`).
    *   Initializes the logging system.
    *   Creates an instance of `FastMCP` from the `fastmcp` library.
    *   Selects and configures the appropriate MCP transport (`StdioTransport` or `HttpTransport`).
    *   Starts the server and manages its lifecycle, including the periodic cache refresh task.
*   **`server.py`:**
    *   Defines the `run_server` function which instantiates `FastMCP`.
    *   Handles discovery and registration of all available MCP tools (e.g., GroundX tools, cache management tools) with the server instance.
    *   Uses the tool discovery mechanism from `tools/__init__.py` to dynamically load all tool modules.
    *   Tool methods are typically defined in separate modules within the `tools/` directory.
*   **`config.py`:**
    *   Defines the `ServerConfig` dataclass to hold all server configuration (e.g., log level, API keys, transport settings, cache TTL).
    *   Provides logic to load these settings from environment variables and merge them with CLI arguments.
*   **`cache.py`:**
    *   Implements the caching mechanism for GroundX metadata (e.g., project IDs, bucket IDs).
    *   Uses an in-memory dictionary for the cache.
    *   Provides structured data types (`TypedDict`) for cache entries and statistics.
    *   Includes logic for Time-To-Live (TTL) based cache entries and a mechanism to refresh the cache, ensuring data doesn't become too stale while minimizing API calls to GroundX.
*   **`tools/` directory:**
    *   Contains individual Python modules for each logical group of tools.
    *   **`groundx.py`:** Implements tools for interacting with the GroundX API (e.g., `searchDocuments`, `queryDocument`, `explainSemanticObject`). These tools use the `groundx` SDK and interact with the `cache.py` module to retrieve necessary IDs.
    *   **`cache_management.py`:** Implements tools for inspecting and managing the cache (e.g., `getCacheStatistics`, `listCachedResources`, `refreshMetadataCache`).
    *   **`__init__.py`:** Provides functions for discovering and loading tools dynamically.
    *   **`_example.py`:** Contains an example tool implementation that can be used as a template for new tools.

## Workflow

1.  **Server Startup (`main.py`):**
    *   Application starts, CLI arguments are parsed.
    *   Configuration is loaded (environment variables + CLI args).
    *   Logging is initialized.
    *   The GroundX metadata cache is initialized, and an initial population attempt might occur.
    *   A background task for periodic cache refresh is started if configured.
    *   A `FastMCP` instance is created.
    *   Tools are discovered and registered with the server.
    *   The chosen transport (STDIO or HTTP) is initialized and started.
    *   The server begins listening for incoming MCP requests.

2.  **MCP Request Handling (FastMCP & `server.py`):**
    *   The transport layer receives an incoming request (JSON-RPC 2.0 format).
    *   FastMCP parses the request and identifies the target tool method (e.g., `groundx/searchDocuments`).
    *   FastMCP invokes the corresponding registered handler function.

3.  **Tool Execution (e.g., `tools/groundx.py`):**
    *   The tool handler function receives parameters from the request.
    *   It may interact with the `cache.py` to get cached data (like GroundX project/bucket IDs).
    *   It uses the `groundx` Python SDK to make API calls to the GroundX service, using the configured API key.
    *   It processes the response from GroundX.
    *   It returns a result (or an error) that FastMCP will format into a JSON-RPC 2.0 response.

4.  **MCP Response (FastMCP):**
    *   FastMCP sends the JSON-RPC response back to the client via the active transport.

5.  **Cache Refresh (`cache.py`):**
    *   Periodically or upon manual request, the cache refresh function is called.
    *   This function makes API calls to GroundX (e.g., to list projects and buckets) and updates the in-memory cache.
    *   This ensures that tools have access to relatively up-to-date metadata without querying GroundX on every request.

## Type Annotations

GXtract makes extensive use of Python's type annotation features:

*   Using `TypedDict` to define structured response and parameter types
*   Leveraging Python 3.12's pipe operator (`|`) for Union types (e.g., `str | None`)
*   Importing from `collections.abc` instead of `collections` for abstract types
*   Strict type checking with `mypy` to ensure type safety

## Error Handling

*   FastMCP provides mechanisms for returning JSON-RPC errors.
*   Tools should catch exceptions (e.g., from the `groundx` SDK or internal errors) and can return appropriate MCP error responses.
*   Configuration errors (e.g., missing API key) are typically checked at startup, and the server may exit with an informative message.
*   Logging is used to record errors and operational details.

## Scalability and Maintainability

*   **Modularity:** Tools are separated into their own modules, making it easier to add new tools or modify existing ones.
*   **Configuration:** Centralized configuration in `config.py` and `main.py` makes it easy to manage settings.
*   **Asynchronous Design:** Improves scalability by allowing efficient handling of concurrent operations.
*   **Caching:** Reduces load on external services and improves response times for common metadata lookups.
*   **Dependency Management:** UV and `pyproject.toml` ensure reproducible builds and clear dependency tracking.

This architecture aims to provide a robust, performant, and maintainable MCP server for interacting with GroundX and potentially other future services.
