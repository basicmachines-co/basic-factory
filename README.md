# Basic Factory

AI-assisted software development workflow tools.

## Overview

Basic Factory provides tools for integrating AI assistants (like Claude) into software development workflows via GitHub. It enables AI assistants to:

- Create and manage branches
- Commit changes
- Create pull requests
- Run and monitor GitHub Actions
- Participate in code review

## Model Context Protocol (MCP)

Basic Factory uses MCP tools to enable direct integration between Claude and development tools:

- Git operations for branch and commit management
- GitHub integration for PRs and collaboration
- Memory graph for maintaining context
- Filesystem tools for direct file manipulation

### Configuration

Set up MCP servers and tools:

```bash
# Git operations
npx @modelcontextprotocol/inspector uvx mcp-server-git --repository /path/to/repo

# GitHub integration
npx @modelcontextprotocol/inspector npx @modelcontextprotocol/server-github

# Memory & context
npx @modelcontextprotocol/inspector uvx mcp-server-memory

# File operations
npx @modelcontextprotocol/inspector uvx mcp-server-filesystem
```

## Installation

```bash
uv add basic-factory
```

## Development

Set up development environment:

```bash
# Create virtual environment
uv venv
uv sync 

# Install project in editable mode with dev dependencies
uv add --dev --editable .
uv add --dev pytest pytest-cov ruff

source .venv/bin/activate

# Run tests
pytest
```