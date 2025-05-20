# Installation

This guide will walk you through installing GXtract and its dependencies.

## Prerequisites

*   **Python 3.12.10** or later.
*   **UV (Python Package Manager)**: Version 0.7.6 or as specified in `pyproject.toml`. If you don\'t have UV, you can install it by following the instructions on the [official UV website](https://github.com/astral-sh/uv).
*   **Git** (for cloning the repository).

## Installation Steps

1.  **Clone the Repository (if applicable):**
    If you have access to the GXtract source code repository, clone it to your local machine:
    ```bash
    git clone <repository_url> gxtract
    cd gxtract
    ```
    If you are installing from a distributed package, skip this step.

2.  **Create a Virtual Environment and Install Dependencies using UV:**
    Navigate to the project root directory (where `pyproject.toml` is located) and run:
    ```bash
    uv venv
    uv pip install -e . # For editable install if developing
    # or
    # uv pip install . # For a standard install
    ```
    This command will:
    *   Create a Python virtual environment (typically in a `.venv` folder).
    *   Install GXtract and all its dependencies as specified in `pyproject.toml` and `uv.lock`.

3.  **Activate the Virtual Environment:**
    *   On Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   On macOS/Linux (bash/zsh):
        ```bash
        source .venv/bin/activate
        ```

4.  **Verify Installation:**
    Once the virtual environment is activated, you can verify the installation by checking the GXtract version or running the help command:
    ```bash
    gxtract --version
    gxtract --help
    ```
    This should display the installed version of GXtract and the available command-line options.

## Next Steps

With GXtract installed, you can proceed to the [Configuration](./configuration.md) section to learn how to set up the server and its tools.
