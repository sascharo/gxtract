# GroundX Tools for GXtract

GXtract provides a suite of tools for interacting with the GroundX platform. These tools allow you to leverage GroundX's capabilities for document search, querying, and understanding semantic objects directly through the MCP server.

To use these tools, the `GROUNDX_API_KEY` must be configured either via the `--groundx-api-key` CLI argument or the `GROUNDX_API_KEY` environment variable.

## Available Tools

### 1. `groundx/searchDocuments`

Searches for documents within your GroundX projects based on a query string.

**Parameters:**

*   `query` (string, required): The search query.
*   `projectId` (string, optional): The ID of a specific GroundX project to search within. If not provided, searches across all accessible projects.
*   `bucketId` (string, optional): The ID of a specific bucket within the project to search.
*   `groupId` (string, optional): The ID of a specific group to search within.
*   `filter` (object, optional): Additional filters to apply to the search.
*   `limit` (integer, optional): The maximum number of search results to return.

**Returns:**

A list of search result objects, where each object contains:
*   `documentId` (string): The document ID.
*   `documentName` (string): The document name or title.
*   `projectId` (string): The ID of the project containing the document.
*   `bucketId` (string): The ID of the bucket containing the document.
*   `score` (float): A relevance score for the search result.
*   `snippet` (string): A text snippet from the document showing relevant content.
*   Other metadata as provided by the GroundX API.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "groundx/searchDocuments",
  "params": {
    "query": "climate change impact on agriculture",
    "limit": 5
  },
  "id": "search-req-001"
}
```

### 2. `groundx/queryDocument`

Asks a specific question about a particular document stored in GroundX.

**Parameters:**

*   `documentId` (string, required): The ID of the document to query.
*   `query` (string, required): The question to ask about the document.
*   `projectId` (string, optional): The ID of the GroundX project containing the document.
*   `bucketId` (string, optional): The ID of the bucket containing the document.

**Returns:**

An object containing:
*   `answer` (string): The answer to the query based on the document content.
*   `sourceReferences` (array): References to specific parts of the document supporting the answer.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "groundx/queryDocument",
  "params": {
    "documentId": "doc-123abc",
    "query": "What are the main findings of this research paper?",
    "projectId": "proj-456def"
  },
  "id": "query-req-001"
}
```

### 3. `groundx/explainSemanticObject`

Provides an explanation for a semantic object (e.g., a figure, table, or diagram) within a document stored in GroundX.

**Parameters:**

*   `documentId` (string, required): The ID of the document containing the semantic object.
*   `semanticObjectId` (string, required): The ID of the semantic object to explain.
*   `projectId` (string, optional): The ID of the GroundX project containing the document.
*   `bucketId` (string, optional): The ID of the bucket containing the document.

**Returns:**

An object containing:
*   `explanation` (string): A detailed explanation of the semantic object.
*   `type` (string): The type of semantic object (e.g., "figure", "table").
*   `title` (string, optional): The title of the semantic object if available.
*   `caption` (string, optional): The caption of the semantic object if available.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "groundx/explainSemanticObject",
  "params": {
    "documentId": "doc-123abc",
    "semanticObjectId": "figure-2",
    "projectId": "proj-456def"
  },
  "id": "explain-req-001"
}
```

## Notes

*   All GroundX tool methods require the GroundX API key to be configured.
*   Error responses will follow the JSON-RPC 2.0 format for errors, with additional details in the `error.data` field where applicable.
*   The tools use the internal cache managed by `cache.py` to optimize GroundX API usage when retrieving project and bucket information.
