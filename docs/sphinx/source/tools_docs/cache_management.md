# Cache Management Tools for GXtract

GXtract includes a set of tools for inspecting and managing its internal cache of GroundX metadata. This cache primarily stores information like GroundX Project IDs and their associated Bucket IDs to optimize interactions with the GroundX API by reducing redundant calls.

The cache has a Time-To-Live (TTL) associated with its entries and is refreshed periodically in the background. These tools allow you to monitor its status and manually trigger refreshes if needed.

## Available Tools

### 1. `cache/getCacheStatistics`

Retrieves statistics about the current state of the GroundX metadata cache.

**Parameters:**

*   None.

**Returns:**

An object containing cache statistics, such as:
*   `hits` (integer): The total number of successful cache lookups.
*   `misses` (integer): The total number of cache lookups that didn't find the requested item.
*   `last_hit_time` (string, ISO 8601 format): The timestamp of the last successful cache lookup. `null` if never accessed.
*   `last_miss_time` (string, ISO 8601 format): The timestamp of the last cache miss. `null` if no misses.
*   `last_refresh_time` (string, ISO 8601 format): The timestamp of when the cache was last refreshed. `null` if never refreshed.
*   `refresh_count` (integer): The total number of times the cache refresh has been attempted.
*   `refresh_success_count` (integer): The number of successful cache refresh operations.
*   `refresh_failure_count` (integer): The number of failed cache refresh operations.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "cache/getCacheStatistics",
  "params": {},
  "id": "cache-stats-req-001"
}
```

### 2. `cache/listCachedResources`

Lists the project and bucket resources currently stored in the GroundX metadata cache. This can be useful for debugging or understanding what metadata the server is currently working with.

**Parameters:**

*   None.

**Returns:**

An object containing:
*   `projects` (array): A list of project objects, each containing:
    *   `id` (string): The project ID.
    *   `name` (string): The project name.
    *   `buckets` (array): A list of bucket objects associated with the project, each containing:
        *   `id` (string): The bucket ID.
        *   `name` (string): The bucket name.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "cache/listCachedResources",
  "params": {},
  "id": "list-cache-req-001"
}
```

### 3. `cache/refreshMetadataCache`

Manually triggers a refresh of the GroundX metadata cache. This can be useful if you know that new projects or buckets have been created in GroundX and want the server to recognize them immediately without waiting for the automatic refresh.

**Parameters:**

*   None.

**Returns:**

An object containing:
*   `success` (boolean): Whether the refresh operation was successful.
*   `details` (string, optional): Additional details about the refresh operation, especially if it failed.

**Example MCP Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "cache/refreshMetadataCache",
  "params": {},
  "id": "refresh-cache-req-001"
}
```

### 4. `cache/refreshCachedResources`

An alternative name for `cache/refreshMetadataCache` that may be used for backward compatibility or clarity.

**Parameters and Returns** are identical to `cache/refreshMetadataCache`.

## Notes

The cache is automatically populated when the GXtract server starts and periodically refreshed in the background. However, there are situations where manually refreshing the cache is necessary.

## Troubleshooting Cache Issues

### Common Warning Messages

When using GXtract, you might encounter the following warning messages related to cache operations:

#### 1. "No projects (groups) found or 'groups' attribute missing in API response"

This warning appears when the cache refresh operation did not find any projects in your GroundX account.

**Possible causes:**
- Your API key doesn't have access to any projects
- There are no projects created in your GroundX account yet
- There's an issue with the GroundX API response format
- Network connectivity issues between GXtract and GroundX servers

**Solutions:**
- Verify you have projects created in your GroundX account
- Check your API key permissions
- Ensure there are no network issues preventing access to GroundX
- Try refreshing the cache after resolving these issues

#### 2. "GroundX metadata cache population failed. Check logs for details"

This warning appears during server startup if the initial cache population attempt failed.

**Solutions:**
- Review the full server logs for more detailed error information
- Check your API key is correctly set in the environment variables
- Verify network connectivity to GroundX API endpoints
- Use the manual cache refresh tools described above to retry the operation

### Verifying Cache Status

After refreshing the cache, you can verify its status using the following steps:

1. Call `cache/getCacheStatistics` to check if the cache has been successfully refreshed.
2. Call `cache/listCachedResources` to see what projects and buckets are currently cached.

The `last_refreshed` timestamp in the `listCachedResources` response should be recent, and the `projects` list should contain the expected projects and buckets.

## Using Cache Tools from VS Code MCP Chat Interface

If your version of VS Code supports MCP chat interfaces, you can use the cache tools directly through chat:

1. Open VS Code's chat interface.
2. Begin typing with an @ mention of your MCP server (e.g., `@GXtract`).
3. Enter your command to refresh the cache or get statistics.

Examples:
- `@GXtract please refresh the metadata cache` - This will trigger the `cache/refreshMetadataCache` tool.
- `@GXtract show me the cache statistics` - This will trigger the `cache/getCacheStatistics` tool.
- `@GXtract list the cached resources` - This will trigger the `cache/listCachedResources` tool.

## Differences Between Cache Refresh Tools

GXtract provides two tools for refreshing the cache:

1. `cache/refreshMetadataCache`: The primary tool for refreshing the GroundX metadata cache. It fetches the latest projects and buckets from the GroundX API.

2. `cache/refreshCachedResources`: Functionally equivalent to `refreshMetadataCache`. It's provided as an alternative name for clarity or backward compatibility.

Both tools perform the same operation internally and will refresh the entire cache, including projects and their associated buckets.

## Best Practices

- **After Account Setup**: Always manually refresh the cache after setting up new projects or buckets in your GroundX account to ensure GXtract can immediately use them.
- **Periodic Verification**: Periodically check the cache statistics to ensure the cache is functioning correctly, especially if you encounter unexpected behavior.
- **Before Important Operations**: Consider refreshing the cache before important operations to ensure you're working with the most up-to-date project and bucket information.
