"""
Example MCP Tool: EchoTool
Demonstrates a basic tool with a single method.
"""

import logging
from typing import Any, TypedDict  # Removed Dict and List

logger = logging.getLogger(__name__)


# Define types for method parameters and return values for clarity (optional but good practice)
class EchoParams(TypedDict):
    message: str


class EchoReturn(TypedDict):
    echoed_message: str


async def echo_handler(params: EchoParams) -> EchoReturn:
    """
    Handles the 'echo' method call.
    """
    logger.info(f"ExampleTool: Echo method called with message: '{params['message']}'")
    return {"echoed_message": f"Echo: {params['message']}"}


def get_tool_definition() -> dict[str, Any]:  # Changed Dict to dict
    """
    Returns the MCP tool definition dictionary for this tool.
    """
    tool_definition: dict[str, Any] = {  # Changed Dict to dict
        "name": "example",
        "description": "A simple example tool that echoes messages.",
        "methods": [
            {
                "name": "echo",
                "description": "Echoes back the input message, prefixed with 'Echo: '.",
                "handler": echo_handler,  # Reference to the async handler function
                "parameters": [
                    {
                        "name": "message",
                        "type": "string",  # MCP type
                        "required": True,
                        "description": "The message to be echoed.",
                    }
                ],
                "returns": {
                    # MCP schema for return value. FastMCP might wrap this.
                    # For now, let's define what the handler itself returns.
                    # The actual JSON schema for 'returns' in MCP is usually an object
                    # with properties. Let's assume it's a simple string for now,
                    # or an object containing the string.
                    # Based on FastMCP, it's often a JSON schema.
                    "type": "object",
                    "properties": {"echoed_message": {"type": "string", "description": "The echoed message."}},
                },
            }
        ],
    }
    return tool_definition


logger.info("ExampleTool module loaded.")
