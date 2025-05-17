"""Handles server configuration from CLI arguments and environment variables."""

import argparse
import os
from dataclasses import dataclass, field
from typing import Literal

# Define literal types for choices to improve type checking
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["text", "json"]
TransportChoice = Literal["stdio", "http"]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
DEFAULT_LOG_LEVEL: LogLevel = "INFO"
DEFAULT_LOG_FORMAT: LogFormat = "text"
DEFAULT_TRANSPORT: TransportChoice = "http"


@dataclass
class ServerConfig:
    """Holds all server configuration settings."""

    transport: TransportChoice = DEFAULT_TRANSPORT
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    log_level: LogLevel = DEFAULT_LOG_LEVEL
    log_format: LogFormat = (
        DEFAULT_LOG_FORMAT  # Add other tool-specific configurations here as needed, e.g., from os.environ
    )
    groundx_api_key: str | None = None
    disable_cache: bool = False  # Whether to disable the metadata cache
    fail_on_cache_init_error: bool = False  # Whether to exit if cache initialization fails

    # VS Code specific options
    is_vscode: bool = False  # Whether the server is running in VS Code
    default_bucket_id: str | None = None  # Default bucket ID to use when none is provided
    friendly_errors: bool = True  # Whether to use VS Code friendly error messages

    # Store the original args for reference if needed
    cli_args: argparse.Namespace = field(default_factory=argparse.Namespace, repr=False)


def load_configuration(args: argparse.Namespace) -> ServerConfig:
    """
    Loads configuration, prioritizing CLI arguments over environment variables,
    and then defaults.
    """
    # Start with defaults
    config = ServerConfig()

    # Apply environment variables first
    env_log_level = os.getenv("MCP_LOG_LEVEL")
    if env_log_level and env_log_level.upper() in get_args(LogLevel):
        config.log_level = env_log_level.upper()  # type: ignore

    env_log_format = os.getenv("MCP_LOG_FORMAT")
    if env_log_format and env_log_format.lower() in get_args(LogFormat):
        config.log_format = env_log_format.lower()  # type: ignore    # Cache control from environment variables
    if os.getenv("GROUNDX_DISABLE_CACHE", "").lower() in ("true", "yes", "1"):
        config.disable_cache = True

    if os.getenv("GROUNDX_FAIL_ON_CACHE_INIT_ERROR", "").lower() in ("true", "yes", "1"):
        config.fail_on_cache_init_error = True

    # Override with CLI arguments if they were provided
    # For transport, it's marked as required in PRD, so args.transport should exist.
    if hasattr(args, "transport") and args.transport is not None:
        config.transport = args.transport

    if hasattr(args, "host") and args.host is not None:
        config.host = args.host
    elif config.transport == "http" and args.host is None:  # Ensure host is set if http and not provided
        config.host = DEFAULT_HOST

    if hasattr(args, "port") and args.port is not None:
        config.port = args.port
    elif config.transport == "http" and args.port is None:  # Ensure port is set if http and not provided
        config.port = DEFAULT_PORT

    if hasattr(args, "log_level") and args.log_level is not None:
        config.log_level = args.log_level

    if hasattr(args, "log_format") and args.log_format is not None:
        config.log_format = args.log_format

    # Handle boolean flags from CLI to override environment variables
    if hasattr(args, "disable_cache"):
        config.disable_cache = args.disable_cache

    if hasattr(args, "fail_on_cache_init_error"):
        config.fail_on_cache_init_error = args.fail_on_cache_init_error

    # Load tool-specific configurations from environment variables
    config.groundx_api_key = os.getenv("GROUNDX_API_KEY")

    # Load VS Code specific configurations
    config.is_vscode = os.getenv("MCP_VSCODE_INTEGRATION", "").lower() == "true"
    config.default_bucket_id = os.getenv("GROUNDX_DEFAULT_BUCKET_ID")

    # Override friendly_errors if explicitly set
    if os.getenv("GROUNDX_FRIENDLY_ERRORS", "").lower() in ("false", "no", "0"):
        config.friendly_errors = False

    # Check if we're running from VS Code based on environment variables
    # VS Code sets VSCODE_PID or VSCODE_CWD when running extensions
    if os.getenv("VSCODE_PID") or os.getenv("VSCODE_CWD"):
        config.is_vscode = True

    # Override with CLI arguments
    if hasattr(args, "vscode") and args.vscode:
        config.is_vscode = True

    if hasattr(args, "default_bucket_id") and args.default_bucket_id:
        config.default_bucket_id = args.default_bucket_id

    config.cli_args = args  # Store the parsed args
    return config


# Helper to get Literal values for argparse choices if needed elsewhere
def get_args(literal_type: object) -> tuple[str, ...]:
    """Extracts arguments from a Literal type."""
    return getattr(literal_type, "__args__", ())
