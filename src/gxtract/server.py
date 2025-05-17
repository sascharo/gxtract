"""Core server logic for initializing and running the FastMCP server."""

import logging

import fastmcp  # Ensure fastmcp is imported
from fastmcp import FastMCP

from .config import ServerConfig
from .tools import (
    get_all_tool_definitions_for_discovery,
)  # Correctly import the function that returns all tool definitions

logger = logging.getLogger(__name__)

# Global server configuration that can be accessed by tools
server_config = None
# logger.info(f"Using FastMCP version: {fastmcp.__version__}") # Moved from here


def run_server(config: ServerConfig) -> None:  # Changed to synchronous
    """
    Initializes and runs the MCP server based on the provided configuration.
    Lets KeyboardInterrupt propagate to the caller (main.py) for handling.
    """
    logger.info(f"Using FastMCP version: {fastmcp.__version__}")  # Moved to here
    # Store VS Code settings in globals that can be accessed by tool handlers
    global server_config
    server_config = config

    # Log if we're running in VS Code mode
    if config.is_vscode:
        logger.info("Running in VS Code integration mode")
        if config.default_bucket_id:
            logger.info(f"Using default bucket ID: {config.default_bucket_id}")

    # Instantiate FastMCP server. The name can be configured later if needed.
    mcp_server = FastMCP(name="GXtract")

    # Discover and register tools
    logger.info("Starting tool discovery and registration...")
    try:
        tool_definition_list = get_all_tool_definitions_for_discovery()
    except Exception as e:
        logger.error(f"Critical error during tool discovery or loading: {e}", exc_info=True)
        tool_definition_list = []

    if not tool_definition_list:
        logger.warning("No tools found or loaded. Server will run without any registered tools.")
    else:
        for tool_def_dict in tool_definition_list:
            tool_module_name = tool_def_dict.get("name")
            # tool_module_description = tool_def_dict.get("description") # Tool level description

            if not tool_module_name:
                logger.warning(f"Skipping tool definition due to missing 'name': {tool_def_dict}")
                continue

            for method_spec in tool_def_dict.get("methods", []):
                handler_fn = method_spec.get("handler")
                method_basename = method_spec.get("name")
                method_description = method_spec.get("description")
                # Parameters and returns schema are defined in the tool_def_dict
                # but FastMCP.add_tool likely infers them from the handler_fn's type hints.
                # We pass the handler, its full name, and its description.

                if not (callable(handler_fn) and method_basename):
                    logger.warning(
                        f"Skipping method in tool '{tool_module_name}' due to missing handler or name: {method_spec}"
                    )
                    continue

                full_mcp_method_name = f"{tool_module_name}_{method_basename}"

                try:
                    mcp_server.add_tool(
                        fn=handler_fn,  # The callable handler function
                        name=full_mcp_method_name,  # Full MCP name, e.g., "example_echo"
                        description=method_description,  # Description of the method
                    )
                    logger.info(f"Successfully registered method: {full_mcp_method_name}")
                except Exception as e:
                    logger.error(
                        f"Failed to register method: {full_mcp_method_name} from tool {tool_module_name}. Error: {e}",
                        exc_info=True,
                    )
        logger.info(
            f"Tool registration completed. {len(tool_definition_list)} tool definition(s) processed."
        )  # The mcp_server.run() call is blocking and handles its own async event loop.
    # It's also responsible for handling KeyboardInterrupt to initiate shutdown.
    # We will let KeyboardInterrupt propagate from it to be handled in main.py.
    try:
        if config.transport == "stdio":
            logger.info("Starting server with STDIO transport.")
            # transport="stdio" is the default for .run() if no transport is specified
            mcp_server.run()
        elif config.transport == "http":
            logger.info(f"Starting server with HTTP (SSE) transport on http://{config.host}:{config.port}.")
            mcp_server.run(transport="sse", host=config.host, port=config.port)
        else:
            # This case should ideally be caught by argparse in main.py
            logger.error(f"Unsupported transport: {config.transport}. This should not happen.")
            # Consider raising an error or exiting if this path is reached.
            return
    except Exception as e:
        # Catch other exceptions to log them before they propagate to main.py
        # KeyboardInterrupt will bypass this and be caught by the outer handler in main.py
        if not isinstance(e, KeyboardInterrupt):
            logger.exception(f"An unexpected error occurred within mcp_server.run(): {e}")
        raise  # Re-raise all exceptions, including KeyboardInterrupt if it somehow lands here
    finally:
        # Removing the log line that was causing "I/O operation on closed file" error
        # logger.info("run_server function in server.py has finished its execution path.")
        pass  # Finally block still useful if other cleanup were needed in future
