"""
Utility functions for direct API calls to GroundX.

This module provides functions for making direct API calls to GroundX
when the cache is disabled or when cache lookups fail.
"""

import logging
import os
from typing import Any

import groundx

logger = logging.getLogger(__name__)

GROUNDX_API_KEY = os.environ.get("GROUNDX_API_KEY")


async def get_project_by_id_direct(project_id: str) -> dict[str, Any] | None:
    """
    Fetches a project directly from the GroundX API by its ID.

    Args:
        project_id: The ID of the project to fetch.

    Returns:
        A dictionary with project details if found, None otherwise.
    """
    if not GROUNDX_API_KEY:
        logger.error("GROUNDX_API_KEY not set. Cannot fetch project details.")
        return None

    try:
        client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)
        logger.info(f"Fetching project details directly from API for project ID: {project_id}")

        # Get the group/project directly
        group_response = await client.groups.get(group_id=project_id)

        if group_response:
            # Transform to match cache format
            return {
                "id": str(group_response.id),
                "name": group_response.name,
                "buckets": [],  # Buckets will be fetched separately if needed
            }

        return None
    except Exception as e:
        logger.error(f"Error fetching project details directly: {e!s}")
        return None


async def get_bucket_by_id_direct(project_id: str, bucket_id: str) -> dict[str, str] | None:
    """
    Fetches a bucket directly from the GroundX API by its ID and project ID.

    Args:
        project_id: The ID of the project containing the bucket.
        bucket_id: The ID of the bucket to fetch.

    Returns:
        A dictionary with bucket details if found, None otherwise.
    """
    if not GROUNDX_API_KEY:
        logger.error("GROUNDX_API_KEY not set. Cannot fetch bucket details.")
        return None

    try:
        client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)
        logger.info(f"Fetching bucket details directly from API for bucket ID: {bucket_id}")

        # Get the bucket directly
        bucket_response = await client.buckets.get(bucket_id=bucket_id)

        if bucket_response and str(bucket_response.group_id) == project_id:
            # Transform to match cache format
            return {"id": str(bucket_response.id), "name": bucket_response.name}

        return None
    except Exception as e:
        logger.error(f"Error fetching bucket details directly: {e!s}")
        return None


async def get_all_projects_direct() -> list[dict[str, Any]]:
    """
    Fetches all projects directly from the GroundX API.

    Returns:
        A list of dictionaries with project details.
    """
    if not GROUNDX_API_KEY:
        logger.error("GROUNDX_API_KEY not set. Cannot fetch projects.")
        return []

    try:
        client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)
        logger.info("Fetching all projects directly from API")

        # Get all groups/projects
        groups_response = await client.groups.list()

        if hasattr(groups_response, "groups") and groups_response.groups:
            # Transform to match cache format
            projects = []
            for group in groups_response.groups:
                projects.append(
                    {
                        "id": str(group.id),
                        "name": group.name,
                        "buckets": [],  # Buckets will be fetched separately if needed
                    }
                )
            return projects

        return []
    except Exception as e:
        logger.error(f"Error fetching all projects directly: {e!s}")
        return []
