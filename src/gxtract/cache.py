"""
Cache for GroundX metadata, such as projects and buckets.

This module provides an in-memory cache for frequently accessed GroundX
metadata to reduce API calls and improve performance. The cache is populated
on server startup and can be refreshed periodically or manually.
"""

import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import TypedDict  # Removed unused Any

import groundx

logger = logging.getLogger(__name__)

GROUNDX_API_KEY = os.environ.get("GROUNDX_API_KEY")


class BucketDetail(TypedDict):
    """Structure for cached bucket details."""

    id: str
    name: str


class ProjectDetail(TypedDict):
    """Structure for cached project details."""

    id: str
    name: str
    buckets: list[BucketDetail]


class CacheStatistics(TypedDict):
    """Structure for tracking cache performance metrics."""

    hits: int
    misses: int
    last_hit_time: str | None
    last_miss_time: str | None
    last_refresh_time: str | None
    refresh_count: int
    refresh_success_count: int
    refresh_failure_count: int


class GroundXMetadataCache(TypedDict):
    """Structure for the GroundX metadata cache."""

    projects: list[ProjectDetail]
    last_refreshed: str | None  # ISO 8601 timestamp
    statistics: CacheStatistics


# Initialize the global cache
groundx_metadata_cache: GroundXMetadataCache = {
    "projects": [],
    "last_refreshed": None,
    "statistics": {
        "hits": 0,
        "misses": 0,
        "last_hit_time": None,
        "last_miss_time": None,
        "last_refresh_time": None,
        "refresh_count": 0,
        "refresh_success_count": 0,
        "refresh_failure_count": 0,
    },
}


def _record_cache_hit() -> None:
    """Record a cache hit in the statistics."""
    stats = groundx_metadata_cache["statistics"]
    stats["hits"] += 1
    stats["last_hit_time"] = datetime.now(UTC).isoformat()


def _record_cache_miss() -> None:
    """Record a cache miss in the statistics."""
    stats = groundx_metadata_cache["statistics"]
    stats["misses"] += 1
    stats["last_miss_time"] = datetime.now(UTC).isoformat()


def get_cache_statistics() -> dict:
    """
    Returns the current cache statistics.

    Returns:
        Dict: A dictionary containing cache hit/miss counts and other statistics.
    """
    stats = groundx_metadata_cache["statistics"].copy()
    # Calculate hit rate if there were any lookups
    total_lookups = stats["hits"] + stats["misses"]
    hit_rate = stats["hits"] / total_lookups if total_lookups > 0 else 0
    stats["hit_rate"] = round(hit_rate * 100, 2)  # As percentage

    # Calculate success rate for refreshes
    total_refreshes = stats["refresh_count"]
    refresh_success_rate = stats["refresh_success_count"] / total_refreshes if total_refreshes > 0 else 0
    stats["refresh_success_rate"] = round(refresh_success_rate * 100, 2)  # As percentage

    return stats


async def refresh_groundx_metadata_cache() -> bool:
    """
    Refreshes the GroundX metadata cache by fetching projects and their buckets.

    Returns:
        bool: True if the cache was refreshed successfully, False otherwise.
    """
    global groundx_metadata_cache
    # Update statistics
    groundx_metadata_cache["statistics"]["refresh_count"] += 1

    if not GROUNDX_API_KEY:
        logger.error("GROUNDX_API_KEY not set. Cannot refresh GroundX metadata cache.")
        groundx_metadata_cache["statistics"]["refresh_failure_count"] += 1
        return False

    client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)
    logger.info("Attempting to refresh GroundX metadata cache...")

    try:
        new_projects_data: list[ProjectDetail] = []
        groups_response = await client.groups.list()

        # Add debug info about the response structure
        logger.debug(f"GroundX API response type: {type(groups_response)}")
        logger.debug(f"Response attributes: {dir(groups_response)}")
        if hasattr(groups_response, "__dict__"):
            logger.debug(f"Response __dict__: {groups_response.__dict__}")

        if hasattr(groups_response, "groups") and groups_response.groups:
            # More debug info about the groups
            logger.debug(f"Found {len(groups_response.groups)} groups")
            logger.debug(f"First group type: {type(groups_response.groups[0]) if groups_response.groups else 'None'}")
            if groups_response.groups:
                logger.debug(f"First group attributes: {dir(groups_response.groups[0])}")

            for group in groups_response.groups:
                project_id = str(group.id)
                project_name = group.name
                logger.debug(f"Fetching buckets for project: {project_name} (ID: {project_id})")

                # Debug if buckets are available
                if hasattr(group, "buckets"):
                    logger.debug(f"Group has 'buckets' attribute. Value type: {type(group.buckets)}")
                    if group.buckets:
                        logger.debug(f"Found {len(group.buckets)} buckets in project {project_name}")
                    else:
                        logger.debug(f"'buckets' is empty for project {project_name}")
                else:
                    logger.debug(
                        f"Group object does not have a 'buckets' attribute. Available attributes: {dir(group)}"
                    )

                current_project_buckets: list[BucketDetail] = []

                # Strategy 1: Check if buckets are directly available on the group object
                if hasattr(group, "buckets") and group.buckets:
                    logger.debug(f"Using buckets directly from group attribute for project {project_name}")
                    for bucket_in_group in group.buckets:
                        current_project_buckets.append({"id": str(bucket_in_group.id), "name": bucket_in_group.name})

                # Strategy 2: If no buckets found directly, try to fetch them explicitly with the buckets API
                else:
                    try:
                        logger.info(
                            f"Attempting to fetch buckets separately for project {project_name} (ID: {project_id})"
                        )
                        if hasattr(client, "buckets") and hasattr(client.buckets, "list"):
                            buckets_response = await client.buckets.list(project_id=project_id)

                            if hasattr(buckets_response, "buckets") and buckets_response.buckets:
                                logger.debug(f"Successfully fetched {len(buckets_response.buckets)} buckets separately")
                                for bucket in buckets_response.buckets:
                                    current_project_buckets.append({"id": str(bucket.id), "name": bucket.name})
                            else:
                                logger.warning(f"No buckets found in separate API call for project {project_name}")
                        else:
                            logger.warning("Client does not support separate bucket listing API")
                    except Exception as e:
                        logger.warning(f"Error fetching buckets separately for project {project_name}: {e!s}")

                new_projects_data.append(
                    {
                        "id": project_id,
                        "name": project_name,
                        "buckets": current_project_buckets,
                    }
                )

            groundx_metadata_cache["projects"] = new_projects_data
            groundx_metadata_cache["last_refreshed"] = datetime.now(UTC).isoformat()
            logger.info(f"GroundX metadata cache refreshed successfully. Found {len(new_projects_data)} projects.")
            stats = groundx_metadata_cache["statistics"]
            stats["refresh_count"] += 1
            stats["refresh_success_count"] += 1
            stats["last_refresh_time"] = datetime.now(UTC).isoformat()
            return True

        logger.warning("No projects (groups) found or 'groups' attribute missing in API response.")
        groundx_metadata_cache["projects"] = []
        groundx_metadata_cache["last_refreshed"] = datetime.now(UTC).isoformat()
        stats = groundx_metadata_cache["statistics"]
        stats["refresh_count"] += 1
        stats["refresh_failure_count"] += 1
        stats["last_refresh_time"] = datetime.now(UTC).isoformat()
        return False

    except Exception as e:
        logger.error(f"Error refreshing GroundX metadata cache: {e!s}", exc_info=True)
        stats = groundx_metadata_cache["statistics"]
        stats["refresh_count"] += 1
        stats["refresh_failure_count"] += 1
        stats["last_refresh_time"] = datetime.now(UTC).isoformat()
        return False


async def get_cached_projects() -> list[ProjectDetail]:
    """
    Returns the list of cached projects.

    If the cache is empty (possibly because it was disabled), this will still return an empty list.
    The calling code should handle this appropriately.
    """
    # Always return the projects list whether empty or populated
    # We don't count this as a hit or miss since it's just retrieving the whole cache
    return groundx_metadata_cache["projects"]


async def get_cached_project_by_id(project_id: str) -> ProjectDetail | None:
    """
    Returns a specific project from cache by its ID.

    If the cache is disabled, this will return None. The calling code should handle this
    by making a direct API call if needed.
    """
    for project in groundx_metadata_cache["projects"]:
        if project["id"] == project_id:
            _record_cache_hit()
            return project
    _record_cache_miss()
    return None


async def get_cached_bucket_by_id(project_id: str, bucket_id: str) -> BucketDetail | None:
    """
    Returns a specific bucket from cache by its project ID and bucket ID.

    If the cache is disabled, this will return None. The calling code should handle this
    by making a direct API call if needed.
    """
    project = await get_cached_project_by_id(project_id)
    if project:
        for bucket in project["buckets"]:
            if bucket["id"] == bucket_id:
                _record_cache_hit()
                return bucket
    _record_cache_miss()
    return None


if __name__ == "__main__":
    # Set logging level to DEBUG to see more information
    logging.basicConfig(level=logging.DEBUG)

    async def test_cache():
        if "GROUNDX_API_KEY" not in os.environ:
            logger.error("Please set the GROUNDX_API_KEY environment variable to test.")
            return

        logger.info("Attempting initial cache refresh...")
        success = await refresh_groundx_metadata_cache()
        if success:
            # Adjusted long line for logger
            logger.info(f"Cache refreshed. Projects: {len(groundx_metadata_cache['projects'])}")
            if groundx_metadata_cache["projects"]:
                for proj in groundx_metadata_cache["projects"]:
                    logger.info(f"  Project: {proj['name']} (ID: {proj['id']})")
                    for buck in proj["buckets"]:
                        logger.info(f"    Bucket: {buck['name']} (ID: {buck['id']})")
            else:
                logger.info("  No projects found in the cache.")
        else:
            logger.error("Cache refresh failed.")

        # Log cache statistics
        stats = get_cache_statistics()
        logger.info("Cache statistics:")
        logger.info(f"  Hits: {stats['hits']}")
        logger.info(f"  Misses: {stats['misses']}")
        logger.info(f"  Hit rate: {stats['hit_rate']}%")
        logger.info(f"  Refresh count: {stats['refresh_count']}")
        logger.info(f"  Successful refreshes: {stats['refresh_success_count']}")
        logger.info(f"  Failed refreshes: {stats['refresh_failure_count']}")
        logger.info(f"  Last refresh time: {stats['last_refresh_time']}")
        logger.info(f"  Last hit time: {stats['last_hit_time']}")
        logger.info(f"  Last miss time: {stats['last_miss_time']}")

    asyncio.run(test_cache())
