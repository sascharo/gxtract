"""
Tool discovery and loading utilities for the GXtract.

This module provides functions to automatically find and prepare tool modules
located within the 'tools' package. Each tool module is expected to define
a `get_tool_definition()` function that returns a dictionary describing the
tool, its methods, and their handlers.
"""

import importlib
import logging
import pkgutil
from collections.abc import Callable, Iterator  # Import from collections.abc
from pathlib import Path
from typing import Any  # Dict, List, Tuple removed

logger = logging.getLogger(__name__)


def discover_tools() -> Iterator[tuple[str, Callable[..., Any]]]:  # Changed Tuple to tuple
    """
    Discovers tool modules in this package, loads them, and yields
    tuples of (full_method_name, handler_function) for registration.

    Each tool module is expected to have a `get_tool_definition()` function
    that returns a dictionary with at least "name" (tool name) and "methods".
    "methods" should be a list of dictionaries, each with "name" (method name)
    and "handler" (the callable function).

    Example structure for `get_tool_definition()` in a tool module::

        def get_tool_definition():
            return {
                "name": "mytool",
                "description": "A description of my tool.",
                "methods": [
                    {
                        "name": "mymethod",
                        "description": "A description of my method.",
                        "handler": my_method_handler_function,
                        "parameters": [
                            {"name": "param1", "type": "string", "description": "First param."}
                        ],
                        "returns": {"type": "object", "description": "The result."}
                    }
                ]
            }
    """
    tools_package_path = Path(__file__).parent
    # Use the package name of 'tools' itself for relative imports within this package
    package_import_prefix = __name__  # e.g., "gxtract.tools"

    logger.info(f"Discovering tools in: {tools_package_path} (package import prefix: {package_import_prefix})")

    for _finder, name, _ispkg in pkgutil.iter_modules([str(tools_package_path)]):
        if name == Path(__file__).stem or name.startswith("_"):
            logger.debug(f"Skipping module: {name}")
            continue

        module_full_name = f"{package_import_prefix}.{name}"
        try:
            tool_module = importlib.import_module(module_full_name)
            logger.info(f"Successfully imported tool module: {module_full_name}")

            if not hasattr(tool_module, "get_tool_definition"):
                logger.warning(
                    f"Tool module '{module_full_name}' does not have a 'get_tool_definition' function. Skipping."
                )
                continue

            # Get the tool's definition
            definition_func = tool_module.get_tool_definition  # Direct attribute access
            definition: dict[str, Any] = definition_func()  # Changed Dict to dict

            tool_base_name = definition.get("name")
            if not tool_base_name or not isinstance(tool_base_name, str):
                logger.warning(
                    f"Tool definition from '{module_full_name}' is missing 'name' or it's not a string. Skipping."
                )
                continue

            methods: list[dict[str, Any]] = definition.get("methods", [])  # Changed List and Dict
            if not isinstance(methods, list):
                logger.warning(
                    f"Tool '{tool_base_name}' from '{module_full_name}' has "
                    f"invalid 'methods' format (expected list). Skipping."
                )
                continue

            for method_spec in methods:
                method_name = method_spec.get("name")
                handler_func = method_spec.get("handler")

                if not method_name or not isinstance(method_name, str):
                    logger.warning(
                        f"Method in tool '{tool_base_name}' from '{module_full_name}' "
                        f"is missing 'name' or it's not a string. Skipping method."
                    )
                    continue
                if not handler_func or not callable(handler_func):
                    logger.warning(
                        f"Method '{method_name}' in tool '{tool_base_name}' "
                        f"from '{module_full_name}' is missing 'handler' or "
                        f"it's not callable. Skipping method."
                    )
                    continue  # Construct the full MCP method name with underscores (e.g., "tool_name_method_name")
                full_mcp_method_name = f"{tool_base_name}_{method_name}"
                yield full_mcp_method_name, handler_func
                logger.info(
                    f"Prepared tool for registration: '{full_mcp_method_name}' using handler from '{module_full_name}'"
                )

        except ImportError as e:
            logger.error(f"Failed to import tool module '{module_full_name}': {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Failed to load or process tool module '{name}' (imported as '{module_full_name}'): {e}",
                exc_info=True,
            )


def get_all_tool_definitions_for_discovery() -> list[dict[str, Any]]:  # Changed List and Dict
    """
    Discovers and loads all tool definitions from modules in this package.
    This is primarily for constructing the response for 'mcp/discover',
    although FastMCP typically handles this automatically for registered tools.
    """
    tool_definitions: list[dict[str, Any]] = []  # Changed List and Dict
    tools_package_path = Path(__file__).parent
    package_import_prefix = __name__

    logger.info(f"Gathering all tool definitions for mcp/discover (package import prefix: {package_import_prefix})")

    for _finder, name, _ispkg in pkgutil.iter_modules([str(tools_package_path)]):  # Unused vars prefixed
        if name == Path(__file__).stem or name.startswith("_"):
            continue

        module_full_name = f"{package_import_prefix}.{name}"
        try:
            tool_module = importlib.import_module(module_full_name)
            if hasattr(tool_module, "get_tool_definition"):
                definition_func = tool_module.get_tool_definition  # Direct attribute access
                definition = definition_func()
                tool_definitions.append(definition)
                logger.info(
                    f"Successfully loaded tool definition for discovery: "
                    f"'{definition.get('name', name)}' from '{module_full_name}'."
                )  # Corrected parenthesis
            else:
                logger.warning(
                    f"Tool module '{module_full_name}' lacks 'get_tool_definition' when gathering for mcp/discover."
                )
        except ImportError as e:
            logger.error(f"Failed to import tool module '{module_full_name}' for discovery: {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Error getting tool definition for discovery from '{module_full_name}': {e}",
                exc_info=True,
            )
    return tool_definitions
