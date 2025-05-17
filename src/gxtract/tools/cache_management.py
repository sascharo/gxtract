"""
Cache management tools for the MCP Server.

These tools provide operations for managing the GroundX metadata cache,
such as refreshing the cache manually and retrieving cache statistics.
"""

import logging
from typing import Any, TypedDict

from gxtract.cache import (
    get_cache_statistics,
    groundx_metadata_cache,
    refresh_groundx_metadata_cache,
)

# Configure logging
logger = logging.getLogger(__name__)


# Type definitions for request/response parameters
class RefreshCacheParams(TypedDict, total=False):
    """Parameters for refreshing the cache (empty, no parameters needed)."""

    pass


class RefreshCacheReturn(TypedDict):
    """Return type for refresh cache operation."""

    success: bool
    message: str


class GetCacheStatsParams(TypedDict, total=False):
    """Parameters for getting cache statistics (empty, no parameters needed)."""

    pass


class GetCacheStatsReturn(TypedDict):
    """Return type for get cache statistics operation."""

    statistics: dict


# Type definition for the list cached resources response
class ListCachedResourcesReturn(TypedDict):
    """Return type for list cached resources."""

    projects: list[dict[str, Any]]
    lastRefreshed: str | None


class RefreshCachedResourcesReturn(TypedDict):
    """Return type for refresh cached resources."""

    success: bool
    lastRefreshed: str | None
    projectCount: int


async def refresh_metadata_cache_handler(_params: RefreshCacheParams) -> RefreshCacheReturn:
    """
    Manually refreshes the GroundX metadata cache.

    This tool allows you to refresh the cache when you suspect it might be stale
    or when you want to ensure you have the most up-to-date metadata for your operations.

    Returns:
        A dictionary with success status and a message describing the outcome.
    """
    logger.info("Manual cache refresh requested")

    success = await refresh_groundx_metadata_cache()

    if success:
        message = "Cache refresh completed successfully"
        logger.info(message)
    else:
        message = "Cache refresh failed - check server logs for details"
        logger.warning(message)

    return {"success": success, "message": message}


async def get_cache_statistics_handler(_params: GetCacheStatsParams) -> GetCacheStatsReturn:
    """
    Retrieves statistics about the GroundX metadata cache.

    This tool provides information about cache usage, hit/miss rates, and refresh history.
    It's useful for monitoring cache performance and diagnosing potential issues.

    Returns:
        A dictionary containing cache statistics such as hits, misses, hit rate, and refresh history.
    """
    logger.info("Cache statistics requested")

    stats = get_cache_statistics()

    return {"statistics": stats}


async def list_cached_resources_handler(_: dict[str, Any] | None = None) -> ListCachedResourcesReturn:
    """
    Lists available GroundX projects and buckets from the server's cache.

    This tool allows clients to discover available resources without making direct API calls
    to GroundX, which can be helpful for contextual matching or UI selection interfaces.

    Returns:
        A dictionary with the list of projects (including their buckets) and a timestamp
        indicating when the cache was last refreshed.
    """
    logger.debug("Retrieving cached GroundX resources")

    # Return the cache contents directly
    return {
        "projects": groundx_metadata_cache["projects"],
        "lastRefreshed": groundx_metadata_cache["last_refreshed"],
    }


async def refresh_cached_resources_handler(_: dict[str, Any] | None = None) -> RefreshCachedResourcesReturn:
    """
    Manually refreshes the GroundX projects and buckets cache.

    This tool allows clients to force a refresh of the cache without restarting the server.
    """
    logger.info("Manually refreshing GroundX metadata cache...")

    success = await refresh_groundx_metadata_cache()

    return {
        "success": success,
        "lastRefreshed": groundx_metadata_cache["last_refreshed"],
        "projectCount": len(groundx_metadata_cache["projects"]),
    }


def get_tool_definition() -> dict[str, Any]:
    """
    Returns the tool definition for the cache management tools.

    This function is called by the tool discovery mechanism to register
    the cache management tools with the MCP server.

    Returns:
        A dictionary containing the tool definition.
    """
    return {
        "name": "cache",
        "description": "Tools for managing the GroundX metadata cache",
        "methods": [
            {
                "name": "refreshMetadataCache",
                "description": "Manually refreshes the GroundX metadata cache",
                "handler": refresh_metadata_cache_handler,
                "parameters": {},
                "returns": {
                    "type": "object",
                    "properties": {"success": {"type": "boolean"}, "message": {"type": "string"}},
                },
            },
            {
                "name": "getCacheStatistics",
                "description": "Retrieves statistics about the GroundX metadata cache",
                "handler": get_cache_statistics_handler,
                "parameters": {},
                "returns": {
                    "type": "object",
                    "properties": {
                        "statistics": {
                            "type": "object",
                            "properties": {
                                "hits": {"type": "integer"},
                                "misses": {"type": "integer"},
                                "hit_rate": {"type": "number"},
                                "refresh_count": {"type": "integer"},
                                "refresh_success_count": {"type": "integer"},
                                "refresh_failure_count": {"type": "integer"},
                                "refresh_success_rate": {"type": "number"},
                                "last_refresh_time": {"type": "string"},
                                "last_hit_time": {"type": "string"},
                                "last_miss_time": {"type": "string"},
                            },
                        }
                    },
                },
            },
            {
                "name": "listCachedResources",
                "description": "Lists available GroundX projects and buckets from the server's cache",
                "handler": list_cached_resources_handler,
                "parameters": {},
                "returns": {
                    "type": "object",
                    "properties": {
                        "projects": {"type": "array"},
                        "lastRefreshed": {"type": "string", "nullable": True},
                    },
                },
            },
            {
                "name": "refreshCachedResources",
                "description": "Manually refreshes the GroundX projects and buckets cache",
                "handler": refresh_cached_resources_handler,
                "parameters": {},
                "returns": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "lastRefreshed": {"type": "string", "nullable": True},
                        "projectCount": {"type": "integer"},
                    },
                },
            },
        ],
    }
