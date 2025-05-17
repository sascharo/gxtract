"""
GroundX Tools for the MCP Server.

These tools provide access to search documents, query documents, and explain semantic objects within
the GroundX platform, enabling AI assistance with scientific papers and technical documentation.
"""

import logging
import os
from typing import Any, TypedDict

import groundx

from gxtract.cache import get_cached_projects

# Configure logging
logger = logging.getLogger(__name__)

# GroundX API key from environment
GROUNDX_API_KEY = os.environ.get("GROUNDX_API_KEY")


# Type definitions for request/response parameters
class SearchDocumentsParams(TypedDict, total=False):
    """Parameters for searching documents in GroundX."""

    query: str
    projectId: str | None
    bucketId: str | None
    groupId: str | None
    filter: dict[str, Any] | None
    limit: int | None


class SearchDocumentsReturn(TypedDict):
    """Return type for search documents."""

    results: list[dict[str, Any]]
    total: int


class QueryDocumentParams(TypedDict, total=False):
    """Parameters for querying a specific document."""

    documentId: str
    query: str
    projectId: str | None
    bucketId: str | None


class QueryDocumentReturn(TypedDict):
    """Return type for document query."""

    answer: str
    documentInfo: dict[str, Any]
    confidence: float


class ExplainSemanticObjectParams(TypedDict, total=False):
    """Parameters for explaining a semantic object within a document."""

    documentId: str
    semanticObjectId: str
    projectId: str | None
    bucketId: str | None


class ExplainSemanticObjectReturn(TypedDict):
    """Return type for semantic object explanation."""

    explanation: str
    objectType: str
    objectInfo: dict[str, Any]


# Type definitions and handler functions for list cached resources and refresh cached resources
# are imported from cache_management.py


async def search_documents_handler(params: SearchDocumentsParams) -> SearchDocumentsReturn:
    """
    Searches for documents across a GroundX Project, Bucket, or Group based on a natural language query.

    This tool is useful for finding relevant scientific papers, technical documentation, and other
    document types based on architectural patterns, algorithms, or specific technologies.
    """
    # Try to import server configuration for VS Code settings if available
    default_bucket_id = None
    friendly_errors = True
    is_vscode = False

    # Check if we're running in VS Code environment
    import sys

    module_path = "gxtract.server"
    if module_path in sys.modules:
        try:
            server_config = sys.modules[module_path].server_config
            if server_config:
                default_bucket_id = server_config.default_bucket_id
                friendly_errors = server_config.friendly_errors
                is_vscode = server_config.is_vscode
        except (AttributeError, KeyError):
            logger.debug("Server config not accessible, using defaults")
    else:
        logger.debug("Server module not loaded, using defaults")

    if not GROUNDX_API_KEY:
        error_msg = (
            "GROUNDX_API_KEY environment variable not set. Please set this variable with your "
            "GroundX API key from https://dashboard.groundx.ai/"
        )
        if friendly_errors and is_vscode:
            error_msg += (
                "\n\nIn VS Code: Add this to your settings.json:\n"
                '"terminal.integrated.env.windows": {\n'
                '    "GROUNDX_API_KEY": "your-api-key-here"\n'
                "}\n"
            )
        raise ValueError(error_msg) from None

    # Initialize GroundX async client with API key
    client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)

    # Extract parameters
    query = params["query"]
    project_id = params.get("projectId")
    bucket_id = params.get("bucketId") or default_bucket_id  # Use default if not provided
    group_id = params.get("groupId")
    filter_query = params.get("filter")
    limit = params.get(
        "limit", 5
    )  # Default to 5 results    # Validate project_id and bucket_id against cache with API fallback
    from gxtract.cache import get_cached_bucket_by_id, get_cached_project_by_id
    from gxtract.direct_api import get_bucket_by_id_direct, get_project_by_id_direct

    validation_warning = None
    if project_id or bucket_id:
        projects = await get_cached_projects()
        if project_id:
            project = await get_cached_project_by_id(project_id)
            if not project:
                # Cache miss - try direct API call
                logger.info(f"Project ID '{project_id}' not found in cache. Trying direct API call.")
                project = await get_project_by_id_direct(project_id)
                if not project:
                    validation_warning = (
                        f"Warning: Project ID '{project_id}' not found in cache or via direct API. "
                        f"This might be an invalid project ID."
                    )
                    logger.warning(validation_warning)

            if bucket_id and project_id:
                bucket = await get_cached_bucket_by_id(project_id, bucket_id)
                if not bucket:
                    # Cache miss - try direct API call
                    logger.info(f"Bucket ID '{bucket_id}' not found in cache. Trying direct API call.")
                    bucket = await get_bucket_by_id_direct(project_id, bucket_id)
                    if not bucket:
                        validation_warning = (
                            f"Warning: Bucket ID '{bucket_id}' not found in project '{project_id}' "
                            f"in cache or via direct API. This might be an invalid bucket ID."
                        )
                        logger.warning(validation_warning)
            elif bucket_id:
                # If only bucket_id is provided, check across all projects
                found = False
                for project in projects:
                    for cached_bucket in project["buckets"]:
                        if cached_bucket["id"] == bucket_id:
                            found = True
                            project_id = project["id"]  # Set the project_id based on found bucket
                            break
                    if found:
                        break

                if not found:
                    # Try direct API without project ID (less efficient)
                    logger.info(
                        f"Bucket ID '{bucket_id}' not found in cache. "
                        f"Please provide a project ID for better performance."
                    )
                    validation_warning = (
                        f"Warning: Bucket ID '{bucket_id}' not found in any project in cache. "
                        f"Please specify a project ID for more accurate validation."
                    )
                    logger.warning(validation_warning)
    logger.info(
        f"Searching GroundX documents with query: '{query}' "
        f"(project: {project_id}, bucket: {bucket_id}, group: {group_id}, limit: {limit})"
    )  # Call GroundX search API
    try:
        # The search module is accessed through the client
        search_params = {"query": query, "n": limit}  # The id parameter is required for content() method
        # Add optional params if provided
        if not project_id and not bucket_id and not group_id:
            raise ValueError(
                "At least one of projectId, bucketId, or groupId must be provided for searching documents."
            )

        # Set the search ID based on priority: project, bucket, group
        # Try using direct numeric IDs rather than prefixed strings
        if project_id:
            try:
                search_id = int(project_id)
            except ValueError:
                search_id = project_id
        elif bucket_id:
            try:
                search_id = int(bucket_id)
            except ValueError:
                search_id = bucket_id
        elif group_id:
            try:
                search_id = int(group_id)
            except ValueError:
                search_id = group_id

        if filter_query:
            search_params["filter"] = filter_query  # Call the content method for searching with required id parameter
        search_results = await client.search.content(
            search_id, **search_params
        )  # SearchResponse is a structured object, not a dictionary
        # Access the 'results' through the search attribute
        results_objects = getattr(search_results.search, "results", []) or []
        total_results = len(results_objects)
        logger.info(
            f"Search returned {total_results} results"
        )  # Convert the Pydantic model objects to dictionaries for consistent interface
        results = []
        for result in results_objects:
            # Initialize result dictionary with common fields
            result_dict = {
                "documentId": getattr(result, "document_id", None),
                "score": getattr(result, "score", None),
            }

            # Extract text content with fallbacks
            text_content = (
                getattr(result, "content", None) or getattr(result, "text", None) or getattr(result, "summary", None)
            )
            result_dict["summary"] = text_content

            # Get document title with fallbacks
            result_dict["title"] = getattr(result, "title", None) or getattr(result, "name", None)

            # Get document metadata
            result_dict["documentType"] = getattr(result, "document_type", None)
            result_dict["sourceUrl"] = getattr(result, "source_url", None)

            # Add additional fields that might be useful
            search_data = getattr(result, "search_data", {})
            if search_data and isinstance(search_data, dict):
                # Extract useful metadata from search_data
                for key in ["title", "summary", "content", "type", "authors", "date"]:
                    if key in search_data and not result_dict.get(key):
                        result_dict[key] = search_data[key]

            # Convert result object to dict if possible to capture any other fields
            try:
                # Try to get all properties if object supports it
                obj_dict = result.dict() if hasattr(result, "dict") else {}
                for key, value in obj_dict.items():
                    if key not in result_dict and value is not None:
                        snake_to_camel = "".join(
                            word.capitalize() if i > 0 else word for i, word in enumerate(key.split("_"))
                        )
                        result_dict[snake_to_camel] = value
            except (AttributeError, TypeError):
                pass

            results.append(result_dict)

        return {"results": results, "total": total_results}
    except Exception as e:
        logger.error(f"Error searching documents: {e!s}", exc_info=True)
        raise ValueError(f"Failed to search documents: {e!s}") from e


async def query_document_handler(params: QueryDocumentParams) -> QueryDocumentReturn:
    """
    Queries a specific document with a natural language question.

    This tool allows for extracting precise implementation details, methodologies,
    or data points from scientific papers or technical documentation.
    """
    # Try to import server configuration for VS Code settings if available
    default_bucket_id = None
    friendly_errors = True
    is_vscode = False

    # Check if we're running in VS Code environment
    import sys

    module_path = "gxtract.server"
    if module_path in sys.modules:
        try:
            server_config = sys.modules[module_path].server_config
            if server_config:
                default_bucket_id = server_config.default_bucket_id
                friendly_errors = server_config.friendly_errors
                is_vscode = server_config.is_vscode
        except (AttributeError, KeyError):
            logger.debug("Server config not accessible, using defaults")
    else:
        logger.debug("Server module not loaded, using defaults")

    if not GROUNDX_API_KEY:
        error_msg = (
            "GROUNDX_API_KEY environment variable not set. Please set this variable with your "
            "GroundX API key from https://dashboard.groundx.ai/"
        )
        if friendly_errors and is_vscode:
            error_msg += (
                "\n\nIn VS Code: Add this to your settings.json:\n"
                '"terminal.integrated.env.windows": {\n'
                '    "GROUNDX_API_KEY": "your-api-key-here"\n'
                "}\n\n"
                "Or run with default bucket ID:\n"
                '"gxtract": {\n'
                '    "command": "uv",\n'
                '    "args": [\n'
                '        "run", "python", "-m", "gxtract",\n'
                '        "--transport", "stdio",\n'
                '        "--vscode",\n'
                '        "--default-bucket-id", "your-bucket-id"\n'
                "    ]\n"
                "}"
            )
        raise ValueError(error_msg) from None

    # Initialize GroundX async client with API key
    client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)

    # Extract parameters
    document_id = params["documentId"]
    query = params["query"]
    project_id = params.get("projectId")
    bucket_id = params.get("bucketId") or default_bucket_id  # Use default bucket ID if none provided

    # Validate project_id and bucket_id against cache if available
    from gxtract.cache import get_cached_bucket_by_id, get_cached_project_by_id
    # from gxtract.direct_api import get_bucket_by_id_direct, get_project_by_id_direct

    validation_warning = None
    if project_id or bucket_id:
        projects = await get_cached_projects()
        if projects:  # Only validate if we have cache data
            if project_id:
                project = await get_cached_project_by_id(project_id)
                if not project:
                    validation_warning = (
                        f"Warning: Project ID '{project_id}' not found in cache. "
                        f"This might be due to an outdated cache or invalid ID."
                    )
                    logger.warning(validation_warning)

            if bucket_id and project_id:
                bucket = await get_cached_bucket_by_id(project_id, bucket_id)
                if not bucket:
                    validation_warning = (
                        f"Warning: Bucket ID '{bucket_id}' not found in project '{project_id}' cache. "
                        f"This might be due to an outdated cache or invalid ID."
                    )
                    logger.warning(validation_warning)
            elif bucket_id:
                # If only bucket_id is provided, check across all projects
                found = False
                for project in projects:
                    for cached_bucket in project["buckets"]:
                        if cached_bucket["id"] == bucket_id:
                            found = True
                            break
                    if found:
                        break

                if not found and projects:  # Only warn if we have projects but didn't find the bucket
                    validation_warning = (
                        f"Warning: Bucket ID '{bucket_id}' not found in any project's cache. "
                        f"This might be due to an outdated cache or invalid ID."
                    )
                    logger.warning(validation_warning)

    logger.info(f"Querying document {document_id} with: '{query}' (bucket: {bucket_id})")

    # Since query_document doesn't exist directly, we'll implement a workaround using search.content
    # with document_id filter to focus the search on only the target document
    try:
        # Step 1: Prepare a document-specific search
        # Note: We include the document_id in the query string rather than as a separate filter
        # parameter because the GroundX API doesn't accept a separate filter parameter
        search_params = {
            "query": f"{query} document_id:{document_id}",  # Include document filter in the query
            "n": 5,  # Limit to top 5 most relevant chunks
        }

        # Set the search ID based on bucket_id since we're searching in a bucket
        search_id = None
        if bucket_id:
            try:
                search_id = int(bucket_id)
            except ValueError:
                search_id = bucket_id
        elif project_id:
            try:
                search_id = int(project_id)
            except ValueError:
                search_id = project_id

        # Execute the search against the bucket to find relevant parts of the document
        if search_id:
            search_results = await client.search.content(search_id, **search_params)
            results_objects = getattr(search_results.search, "results", []) or []

            if not results_objects:
                logger.warning(f"No results found for document {document_id} with query '{query}'")
                if friendly_errors and is_vscode:
                    return {
                        "answer": f"No information found in this document about '{query}'.\n\n"
                        "Tips for VS Code users:\n"
                        "1. Try a more specific query using terms that appear in the document\n"
                        "2. Make sure you're using a valid document ID\n"
                        "3. Check that your bucket ID contains this document",
                        "documentInfo": {"documentId": document_id},
                        "confidence": 0.0,
                    }

                return {
                    "answer": f"No information found in this document about '{query}'.",
                    "documentInfo": {"documentId": document_id},
                    "confidence": 0.0,
                }

            # Step 2: Extract and combine the most relevant content chunks
            contents = []
            max_score = 0
            doc_info = {}

            # Log what fields are available in results for debugging
            if results_objects:
                available_attrs = dir(results_objects[0])
                logger.debug(f"Available attributes in result object: {available_attrs}")

            for result in results_objects:
                score = getattr(result, "score", 0)
                # Try different attributes that might contain the content
                content = None
                for attr_name in ["content", "text", "summary", "chunk", "value", "data"]:
                    if hasattr(result, attr_name) and getattr(result, attr_name):
                        content = getattr(result, attr_name)
                        logger.debug(f"Found content in attribute: {attr_name}")
                        break

                if not content:
                    # Log full result object for debugging
                    logger.debug(f"No content found in result object: {result}")

                if content:
                    contents.append(content)

                # Keep track of the highest relevance score
                if score > max_score:
                    max_score = score

                # Gather document metadata from the first result
                if not doc_info:
                    doc_info = {
                        "documentId": document_id,
                        "title": getattr(result, "title", None) or getattr(result, "name", None),
                        "documentType": getattr(result, "document_type", None),
                        "sourceUrl": getattr(result, "source_url", None),
                    }

            # Step 3: Form a combined answer from the most relevant chunks
            combined_content = "\n\n".join(contents)  # Debug log to see what kind of content we're getting
            logger.debug(f"Combined content: {combined_content[:200]}...")
            logger.debug(f"Total content length: {len(combined_content)}")
            logger.debug(f"Number of content chunks found: {len(contents)}")

            # Format the content for VS Code display if needed
            if is_vscode and combined_content:
                # Add markdown formatting for better display in VS Code
                combined_content = f"# Document: {doc_info.get('title', 'Unnamed Document')}\n\n{combined_content}"

                # Add source info at the bottom
                if doc_info.get("sourceUrl"):
                    combined_content += (
                        f"\n\n---\nSource: [{doc_info.get('title', 'Document')}]({doc_info.get('sourceUrl')})"
                    )

            # If we have content but it's not meaningful, provide a helpful message
            if not combined_content or combined_content.strip() == "":
                # Add a more detailed explanation
                combined_content = (
                    f"Found the document, but couldn't extract specific information about '{query}'. "
                    f"Try a more specific question focused on what's visible in the document. "
                )

                # Add VS Code specific suggestions
                if friendly_errors and is_vscode:
                    combined_content += (
                        "\n\nTips for better results in VS Code:\n"
                        "1. Use specific terminology that appears in the document\n"
                        "2. Reference specific sections, figures, or tables if you know them\n"
                        "3. Break complex questions into simpler queries"
                    )

            # Normalize confidence based on max score (0-1 scale)
            normalized_confidence = min(max_score / 1000, 1.0)

            return {
                "answer": combined_content,
                "documentInfo": doc_info,
                "confidence": normalized_confidence,
            }

        # No search_id means no bucket_id was provided or found in defaults
        err_msg = "Cannot query document without specifying a bucket ID."
        if friendly_errors and is_vscode:
            err_msg += (
                "\n\nIn VS Code settings.json, add:\n"
                '"terminal.integrated.env.windows": {\n'
                '    "GROUNDX_DEFAULT_BUCKET_ID": "your-bucket-id"\n'
                "}\n\n"
                "Or specify the bucket ID directly in your query."
            )

        logger.error("Cannot query document without a bucket ID")
        return {
            "answer": err_msg,
            "documentInfo": {"documentId": document_id},
            "confidence": 0.0,
        }

    except Exception as e:
        logger.error(f"Error querying document: {e!s}", exc_info=True)

        # Provide more helpful error message for VS Code users
        if friendly_errors and is_vscode:
            error_msg = f"Failed to query document: {e!s}\n\n"
            error_msg += (
                "Common solutions for VS Code users:\n"
                "1. Check that your GROUNDX_API_KEY is correct\n"
                "2. Verify that the document ID exists in the specified bucket\n"
                "3. Try a simpler query with fewer special characters"
            )
            raise ValueError(error_msg) from e

        raise ValueError(f"Failed to query document: {e!s}") from e


async def explain_semantic_object_handler(params: ExplainSemanticObjectParams) -> ExplainSemanticObjectReturn:
    """
    Provides explanations for semantic objects (figures, tables, diagrams, etc.) within documents.

    This tool is vital for understanding complex visual or structured representations in scientific
    papers and technical documentation, such as architectural diagrams or result tables.
    """
    if not GROUNDX_API_KEY:
        raise ValueError(
            "GROUNDX_API_KEY environment variable not set. Please set this variable with your "
            "GroundX API key from https://dashboard.groundx.ai/"
        ) from None

    # Initialize GroundX async client with API key
    client = groundx.AsyncGroundX(api_key=GROUNDX_API_KEY)

    # Extract parameters
    document_id = params["documentId"]
    semantic_object_id = params["semanticObjectId"]
    project_id = params.get("projectId")
    bucket_id = params.get("bucketId")

    # Validate project_id and bucket_id against cache with API fallback
    from gxtract.cache import get_cached_bucket_by_id, get_cached_project_by_id
    from gxtract.direct_api import get_bucket_by_id_direct, get_project_by_id_direct

    validation_warning = None
    if project_id or bucket_id:
        projects = await get_cached_projects()
        if project_id:
            project = await get_cached_project_by_id(project_id)
            if not project:
                # Cache miss - try direct API call
                logger.info(f"Project ID '{project_id}' not found in cache. Trying direct API call.")
                project = await get_project_by_id_direct(project_id)
                if not project:
                    validation_warning = (
                        f"Warning: Project ID '{project_id}' not found in cache or via direct API. "
                        f"This might be an invalid project ID."
                    )
                    logger.warning(validation_warning)

            if bucket_id and project_id:
                bucket = await get_cached_bucket_by_id(project_id, bucket_id)
                if not bucket:
                    # Cache miss - try direct API call
                    logger.info(f"Bucket ID '{bucket_id}' not found in cache. Trying direct API call.")
                    bucket = await get_bucket_by_id_direct(project_id, bucket_id)
                    if not bucket:
                        validation_warning = (
                            f"Warning: Bucket ID '{bucket_id}' not found in project '{project_id}' "
                            f"in cache or via direct API. This might be an invalid bucket ID."
                        )
                        logger.warning(validation_warning)
            elif bucket_id:
                # If only bucket_id is provided, check across all projects
                found = False
                for project in projects:
                    for cached_bucket in project["buckets"]:
                        if cached_bucket["id"] == bucket_id:
                            found = True
                            project_id = project["id"]  # Set the project_id based on found bucket
                            break
                    if found:
                        break

                if not found:
                    # Try direct API without project ID (less efficient)
                    logger.info(
                        f"Bucket ID '{bucket_id}' not found in cache. "
                        f"Please provide a project ID for better performance."
                    )
                    validation_warning = (
                        f"Warning: Bucket ID '{bucket_id}' not found in any project in cache. "
                        f"Please specify a project ID for more accurate validation."
                    )
                    logger.warning(validation_warning)
    logger.info(
        f"Explaining semantic object {semantic_object_id} in document {document_id} "
        f"(project: {project_id}, bucket: {bucket_id})"
    )

    # Call GroundX explain API
    try:
        explain_params = {"document_id": document_id, "semantic_object_id": semantic_object_id}

        if project_id:
            explain_params["project_id"] = project_id
        if bucket_id:
            explain_params["bucket_id"] = bucket_id

        # Documents client API call for explaining a semantic object
        explanation_result = await client.documents.explain_semantic_object(**explain_params)

        logger.info("Semantic object explanation completed successfully")

        return {
            "explanation": explanation_result.get("explanation", ""),
            "objectType": explanation_result.get("objectType", "unknown"),
            "objectInfo": explanation_result.get("objectInfo", {}),
        }
    except Exception as e:
        logger.error(f"Error explaining semantic object: {e!s}", exc_info=True)
        raise ValueError(f"Failed to explain semantic object: {e!s}") from e


def get_tool_definition() -> dict[str, Any]:
    """
    Returns the MCP tool definition dictionary for GroundX tools.
    """
    return {
        "name": "groundx",
        "description": "Tools for extracting information from documents using GroundX.",
        "methods": [
            {
                "name": "searchDocuments",
                "description": "Searches for documents across a GroundX Project based on a natural language query.",
                "handler": search_documents_handler,
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "required": True,
                        "description": "The natural language query to search for.",
                    },
                    {
                        "name": "projectId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of the GroundX Project to search in.",
                    },
                    {
                        "name": "bucketId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of a specific GroundX Bucket to search in.",
                    },
                    {
                        "name": "groupId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of a specific document group to search in.",
                    },
                    {
                        "name": "filter",
                        "type": "object",
                        "required": False,
                        "description": "A filter to apply to the search results using MongoDB query operators.",
                    },
                    {
                        "name": "limit",
                        "type": "integer",
                        "required": False,
                        "description": "Maximum number of results to return. Default: 5.",
                    },
                ],
                "returns": {
                    "type": "object",
                    "properties": {
                        "results": {"type": "array", "description": "List of document results matching the query."},
                        "total": {"type": "integer", "description": "Total number of results returned."},
                    },
                },
            },
            {
                "name": "queryDocument",
                "description": "Queries a specific document with a natural language question.",
                "handler": query_document_handler,
                "parameters": [
                    {
                        "name": "documentId",
                        "type": "string",
                        "required": True,
                        "description": "The ID of the document to query.",
                    },
                    {
                        "name": "query",
                        "type": "string",
                        "required": True,
                        "description": "The natural language question to ask about the document.",
                    },
                    {
                        "name": "projectId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of the GroundX Project containing the document.",
                    },
                    {
                        "name": "bucketId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of the GroundX Bucket containing the document.",
                    },
                ],
                "returns": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string", "description": "The answer to the query."},
                        "documentInfo": {
                            "type": "object",
                            "description": "Information about the document that was queried.",
                        },
                        "confidence": {"type": "number", "description": "Confidence score for the answer."},
                    },
                },
            },
            {
                "name": "explainSemanticObject",
                "description": "Provides explanations for semantic objects (figures, tables, diagrams) "
                "within documents.",
                "handler": explain_semantic_object_handler,
                "parameters": [
                    {
                        "name": "documentId",
                        "type": "string",
                        "required": True,
                        "description": "The ID of the document containing the semantic object.",
                    },
                    {
                        "name": "semanticObjectId",
                        "type": "string",
                        "required": True,
                        "description": "The ID of the semantic object to explain.",
                    },
                    {
                        "name": "projectId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of the GroundX Project containing the document.",
                    },
                    {
                        "name": "bucketId",
                        "type": "string",
                        "required": False,
                        "description": "The ID of the GroundX Bucket containing the document.",
                    },
                ],
                "returns": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string", "description": "Explanation of the semantic object."},
                        "objectType": {
                            "type": "string",
                            "description": "Type of the semantic object (e.g., figure, table, code).",
                        },
                        "objectInfo": {
                            "type": "object",
                            "description": "Additional information about the semantic object.",
                        },
                    },
                },
            },
        ],
    }


logger.info("GroundX Tools module loaded.")
