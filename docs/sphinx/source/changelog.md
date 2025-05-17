# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-05-17

### Added

*   Initial release of GXtract.
*   Core MCP server functionality based on FastMCP v2.
*   Support for STDIO and HTTP transports.
*   GroundX integration tools:
    *   `groundx/searchDocuments`
    *   `groundx/queryDocument`
    *   `groundx/explainSemanticObject`
*   Cache management tools:
    *   `cache/refreshMetadataCache`
    *   `cache/getCacheStatistics`
    *   `cache/listCachedResources`
    *   `cache/refreshCachedResources`
*   Configuration via CLI arguments and environment variables.
    *   Secure API key management through environment variables and VS Code's secure storage.
    *   Logging with configurable levels and formats (text, JSON).
    *   GroundX metadata caching with TTL and periodic refresh.
    *   Sphinx documentation with documentation on cache management, API key security, and troubleshooting.
    *   GitHub Actions workflow for building and publishing documentation to GitHub Pages.
    *   `pyproject.toml` for UV-based dependency management.
*   Ruff for linting and formatting, MyPy for type checking.
*   GPLv3 License.

### Changed

*   N/A (Initial Release)

### Fixed

*   N/A (Initial Release)
