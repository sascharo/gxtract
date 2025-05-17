import argparse
import asyncio
import logging
import sys

from .cache import refresh_groundx_metadata_cache
from .config import (
    DEFAULT_HOST,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PORT,
    DEFAULT_TRANSPORT,
    LogFormat,
    LogLevel,
    ServerConfig,
    TransportChoice,
    get_args,
    load_configuration,
)
from .server import run_server

APP_NAME = "GXtract"

# Logger for this module
logger = logging.getLogger(__name__)


def setup_logging(log_level: LogLevel, log_format: LogFormat) -> None:
    """Configures the root logger based on server configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    if log_format == "json":
        # Basic JSON logging (can be expanded with a library like python-json-logger)
        log_formatter = logging.Formatter(
            """{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}"""
        )
    else:  # Text format
        log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers to avoid duplicate logs if reconfiguring
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add a new stream handler
    stream_handler = logging.StreamHandler(sys.stderr)  # Changed from sys.stdout to sys.stderr
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)

    logger.info(f"Logging configured: Level={log_level}, Format={log_format}")


def cli_entry_point() -> int:
    """
    Command-line interface entry point for the {APP_NAME}.
    Parses arguments, loads configuration, and starts the server.
    """
    parser = argparse.ArgumentParser(description="GroundX MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=get_args(TransportChoice),
        required=False,  # Changed from True to False to allow using the default
        default=DEFAULT_TRANSPORT,  # Use the default transport (now HTTP)
        help=(
            f"Communication transport type. Choices: {{', '.join(get_args(TransportChoice))}}. "  # Adjusted long line
            f"Default: {DEFAULT_TRANSPORT}"
        ),
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,  # Default is handled in load_configuration based on transport
        help=(f"Host address for HTTP transport. Defaults to {DEFAULT_HOST} if transport is http."),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,  # Default is handled in load_configuration based on transport
        help=(f"Port number for HTTP transport. Defaults to {DEFAULT_PORT} if transport is http."),
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=get_args(LogLevel),
        default=None,  # Default is handled in load_configuration
        help=(
            f"Logging level. Choices: {', '.join(get_args(LogLevel))}. "
            f"Overrides MCP_LOG_LEVEL env var. Defaults to {DEFAULT_LOG_LEVEL}."
        ),
    )
    parser.add_argument(
        "--log-format",
        type=str,
        choices=get_args(LogFormat),
        default=None,  # Default is handled in load_configuration
        help=(
            f"Logging output format. Choices: {', '.join(get_args(LogFormat))}. "
            f"Overrides MCP_LOG_FORMAT env var. Defaults to {DEFAULT_LOG_FORMAT}."
        ),
    )
    parser.add_argument(
        "--vscode",
        action="store_true",
        help="Enable VS Code integration mode. Sets friendly error messages and other VS Code optimizations.",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Disable the GroundX metadata cache. All operations will use direct API calls.",
    )
    parser.add_argument(
        "--default-bucket-id",
        type=str,
        default=None,
        help="Default bucket ID to use when none is provided in a query. Overrides GROUNDX_DEFAULT_BUCKET_ID env var.",
    )
    parser.add_argument(
        "--fail-on-cache-init-error",
        action="store_true",
        help="Exit the server if cache initialization fails. By default, the server continues with "
        "direct API fallback.",
    )

    args = None
    try:
        args = parser.parse_args()
    except SystemExit as e:  # Handles --help, invalid arguments from argparse
        # argparse typically prints a message and exits.
        # If we are here, it's likely due to --help or a parsing error.
        # Return the exit code from argparse.
        return e.code

    # If args parsing was successful, proceed to load config and setup logging
    config: ServerConfig = load_configuration(args)
    setup_logging(config.log_level, config.log_format)

    logger.info(f"{APP_NAME} starting with configuration: {config}")

    # Initialize GroundX metadata cache if not disabled
    if not config.disable_cache:
        logger.info("Initializing GroundX metadata cache...")
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            cache_refreshed = loop.run_until_complete(refresh_groundx_metadata_cache())
            if cache_refreshed:
                logger.info("GroundX metadata cache populated successfully.")
            else:
                logger.warning("GroundX metadata cache population failed. Check logs for details.")
                if config.fail_on_cache_init_error:
                    logger.error("Server configured to exit on cache initialization failure. Exiting.")
                    return 1  # Or appropriate error code
        except Exception as e:
            logger.error(f"An error occurred during cache initialization: {e!s}", exc_info=True)
            # Depending on policy, you might want to exit if cache is critical
            # For now, we'll log the error and continue server startup
    else:
        logger.info("GroundX metadata cache disabled. All operations will use direct API calls.")

    try:
        if config.transport == "stdio":
            logger.info("Initializing server with STDIO transport...")
        elif config.transport == "http":
            logger.info(f"HTTP (SSE) transport selected. Server will listen on http://{config.host}:{config.port}")

        run_server(config)  # This is a blocking call. FastMCP.run() handles its own KeyboardInterrupt.

        # This part is reached if run_server completes normally (e.g., if it had a programmed stop condition)
        logger.info(f"{APP_NAME} shut down gracefully.")  # This log might not be reached with Ctrl+C
        return 0
    except KeyboardInterrupt:
        # FastMCP.run() (called within run_server) should have already handled
        # its own shutdown due to KeyboardInterrupt.
        # We simply acknowledge that the main process was interrupted.
        # Attempting to log here is unreliable as stdio streams might be closed.
        # A direct print to stderr is more robust if a message is absolutely needed,
        # but for now, we'll keep it clean and just exit.
        # print(f"\\n{APP_NAME} interrupted by user. Exiting.", file=sys.stderr) # Consider if essential
        return 1  # Indicate shutdown due to interrupt
    except Exception:
        # Catch any other unexpected exceptions from run_server or setup.
        logger.exception(f"An unhandled error occurred in {APP_NAME}.")
        return 1  # Indicate error
    # No 'finally' block here for logging "main process finished" as it's unreliable on KbdInterrupt.


if __name__ == "__main__":
    cli_entry_point()
