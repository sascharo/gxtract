# Development Guide for GXtract

This guide provides information for developers looking to contribute to GXtract, create new tools, or understand its internal workings.

## Prerequisites

*   All prerequisites listed in the [Installation Guide](./installation.md).
*   Familiarity with Python 3.12, `asyncio`, and type hinting.
*   Understanding of the Model Context Protocol (MCP).
*   Knowledge of the FastMCP v2 library is highly recommended.

## Project Structure {#project-structure}

The GXtract project follows a standard Python package structure:

```
gxtract/
├── docs/                  # Sphinx documentation sources
├── examples/              # Example scripts and usage scenarios (to be added)
├── scripts/               # Utility scripts (e.g., for running, testing)
├── src/
│   └── gxtract/           # Main source code for the gxtract package
│       ├── __init__.py
│       ├── main.py        # CLI entry point and server setup
│       ├── server.py      # Core FastMCP server logic and tool registration
│       ├── config.py      # Configuration handling (env vars, CLI args)
│       ├── cache.py       # GroundX metadata caching logic
│       ├── direct_api.py  # Direct (non-MCP) GroundX API interactions (if any)
│       └── tools/         # MCP tool implementations
│           ├── __init__.py
│           ├── groundx.py # Tools for GroundX interaction
│           ├── cache_management.py # Tools for cache management
│           └── _example.py  # Example tool (skipped by default)
├── tests/                 # Unit and integration tests (to be added)
├── .gitignore
├── LICENSE.md
├── pyproject.toml         # Project metadata, dependencies (for UV)
├── README.md
└── uv.lock                # Pinned versions of dependencies
```

## Setting up a Development Environment

1.  **Clone the repository** (if you haven\'t already).
2.  **Navigate to the project root.**
3.  **Create and activate a virtual environment using UV:**
    ```bash
    uv venv
    # On Windows (PowerShell)
    .venv\Scripts\Activate.ps1
    # On macOS/Linux
    source .venv/bin/activate
    ```
4.  **Install in editable mode with development dependencies:**
    UV uses dependency groups defined in `pyproject.toml`. Ensure you have a `[project.optional-dependencies]` group for development, e.g., `dev`.

    In `pyproject.toml`:
    ```toml
    [project.optional-dependencies]
    dev = ["ruff", "mypy", "pytest", "sphinx", "furo", "myst-parser", "sphinx-copybutton"]
    ```

    Then install:
    ```bash
    uv pip install -e ".[dev]"
    ```

## Coding Standards and Linting

GXtract uses Ruff for linting, formatting, and import sorting, and MyPy for static type checking.

*   **Ruff:** Configuration is in `pyproject.toml` under `[tool.ruff]`.
    *   To format code: `ruff format .`
    *   To check for linting issues: `ruff check .`
    *   To fix automatically fixable issues: `ruff check . --fix`
*   **MyPy:** Configuration can be in `pyproject.toml` under `[tool.mypy]` or in a `mypy.ini` file.
    *   To run type checking: `mypy src/gxtract`

It\'s recommended to integrate these tools into your IDE or use pre-commit hooks.

## Running Tests (To Be Implemented)

Tests will be implemented using `pytest`.

*   Place tests in the `tests/` directory.
*   Test file names should start with `test_` (e.g., `test_cache.py`).
*   Test function names should start with `test_`.

To run tests (once implemented):
```bash
pytest
```

## Building Documentation

Documentation is built using Sphinx.

1.  **Navigate to the `docs/sphinx/` directory:**
    ```bash
    cd docs/sphinx
    ```
2.  **Build the HTML documentation:**
    ```bash
    sphinx-build -b html source build/html
    ```
    (On Windows, you might use `make.bat html` if a `make.bat` is provided, or execute the `sphinx-build` command directly).

    The output will be in `docs/sphinx/build/html/`.

## Creating a New Tool

1.  **Create a new Python file** in the `src/gxtract/tools/` directory (e.g., `my_new_tool.py`).
2.  **Define your tool class or functions.** Tool methods must be `async def`.
3.  **Structure methods clearly.** Use the `tool_name/method_name` convention for MCP methods.
4.  **Import and register your tool** in `src/gxtract/server.py` within the `setup_tools` async function.
    ```python
    # In server.py
    from .tools import my_new_tool # Assuming my_new_tool.py contains functions or a class

    async def setup_tools(server: FastMCP, config: AppConfig):
        # ... other tools ...
        # Each tool module should provide a get_tool_definition function
        # that returns a dictionary with the tool's name, description, and methods
        await server.add_tool(my_new_tool.get_tool_definition())
    ```
5.  **Add configuration** for your tool in `src/gxtract/config.py` if needed, and handle it in `main.py` and your tool.
6.  **Write docstrings** for your tool and its methods. These can be used by Sphinx for API documentation.
7.  **Add documentation** for your tool in `docs/sphinx/source/tools_docs/` (e.g., `my_new_tool.md`) and link it in `docs/sphinx/source/index.md`.
8.  **Write tests** for your tool in the `tests/` directory.

## Versioning and Changelog

*   GXtract follows Semantic Versioning (SemVer 2.0.0).
*   Update `CHANGELOG.md` with any significant changes for each new version.
*   Update the `version` in `pyproject.toml`.

## Submitting Contributions (If Applicable)

If contributing to a shared repository:

1.  Create a new branch for your feature or bug fix.
2.  Make your changes, adhering to coding standards.
3.  Ensure all tests pass.
4.  Update documentation and changelog as necessary.
5.  Submit a pull request.

## Key Modules

*   `main.py`: Handles CLI parsing, configuration loading, server instantiation, and startup.
*   `server.py`: Defines the `FastMCP` instance and is responsible for registering all tools.
*   `config.py`: Defines the `AppConfig` data structure and loads configuration from environment variables and CLI arguments.
*   `cache.py`: Implements the caching logic for GroundX metadata, including TTL and periodic refresh.
*   `tools/`: Contains individual modules for each tool or group of related tools.

## Dependency Management

GXtract uses UV for dependency management, with dependencies declared in `pyproject.toml` and locked versions in `uv.lock`. This approach ensures reproducible builds across different development environments.

### The uv.lock File

The `uv.lock` file is an important part of the repository that ensures consistency:

- It specifies exact versions of all direct and transitive dependencies
- It is committed to the repository to ensure everyone uses the same dependency versions
- It prevents "works on my machine" issues and helps with CI/CD reproducibility

### Working with Dependencies

When making changes to dependencies:

1. **Adding a new dependency**:
   - Add the dependency to the appropriate section in `pyproject.toml`
   - Run `uv pip compile pyproject.toml -o uv.lock` to update the lockfile with the new dependency
   - Run `uv sync` to install the dependencies
   - Commit both the updated `pyproject.toml` and `uv.lock` files

2. **Updating a dependency**:
   - Update the version specifier in `pyproject.toml`
   - Run `uv pip compile pyproject.toml -o uv.lock --upgrade` to refresh the lockfile with the new versions
   - Run `uv sync` to install the updated dependencies
   - Test thoroughly to ensure the updated dependency doesn't break anything
   - Commit both files

3. **Resolving conflicts**:
   - If you encounter dependency conflicts, you may need to adjust version constraints
   - Use `uv pip list --not-required` to see transitive dependencies
   - Consider using compatibility releases (e.g., `~=1.2.3` instead of `>=1.2.3`)
   
The goal is to maintain a balance between keeping dependencies up-to-date (for features and security) and ensuring stability.

## Further Reading

*   [FastMCP v2 Documentation](https://context7.com/jlowin/fastmcp)
*   [GroundX Python SDK](https://context7.com/eyelevelai/groundx-python)
*   [Model Context Protocol Specification](https://microsoft.github.io/model-context-protocol/)
