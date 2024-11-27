# Basic Factory

AI-assisted software development workflow tools.

## Overview

Basic Factory provides tools for integrating AI assistants (like Claude) into software development workflows via GitHub. It enables AI assistants to:

- Create and manage branches
- Commit changes
- Create pull requests
- Run and monitor GitHub Actions
- Participate in code review

## Github
For the GitHub token, you'll need to:

Go to GitHub Settings → Developer Settings → Personal Access Tokens
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens


Create a new token with 'repo' scope
We can use this for both direct API calls and for GitHub Actions

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


# MCP quickstart
https://modelcontextprotocol.io/quickstart

Claude Desktop config json
/Users/phernandez/Library/Application Support/Claude/claude_desktop_config.json

logs-dir:
/Users/phernandez/Library/Logs/Claude

- mcp-server-sqlite.log 
- mcp.log

To test changes efficiently:

- Configuration changes: Restart Claude Desktop
- Server code changes: Use Command-R to reload
- Quick iteration: Use Inspector during development
  - https://modelcontextprotocol.io/docs/tools/inspector

eg. 
```bash
npx @modelcontextprotocol/inspector uvx mcp-server-sqlite --db-path /Users/phernandez/dev/basicmachines/mcp-quickstart/test.db
```

## tools 
Inspector: https://modelcontextprotocol.io/docs/tools/inspector
Debugger: https://modelcontextprotocol.io/docs/tools/debugging

## MCP Services 

### filesystem
language: ts
repo_url: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

### memory knowledge graph
language: ts
repo_url: https://github.com/modelcontextprotocol/servers/tree/main/src/memory

```markdown
Follow these steps for each interaction:

1. User Identification:
   - You should assume that you are interacting with default_user
   - If you have not identified default_user, proactively try to do so.

2. Memory Retrieval:
   - Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph
   - Always refer to your knowledge graph as your "memory"

3. Memory
   - While conversing with the user, be attentive to any new information that falls into these categories:
     a) Basic Identity (age, gender, location, job title, education level, etc.)
     b) Behaviors (interests, habits, etc.)
     c) Preferences (communication style, preferred language, etc.)
     d) Goals (goals, targets, aspirations, etc.)
     e) Relationships (personal and professional relationships up to 3 degrees of separation)

4. Memory Update:
   - If any new information was gathered during the interaction, update your memory as follows:
     a) Create entities for recurring organizations, people, and significant events
     b) Connect them to the current entities using relations
     b) Store facts about them as observations
```


### git 
git: python 
repo_url: https://github.com/modelcontextprotocol/servers/tree/main/src/git

```    
"git": {
      "command": "uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "/Users/phernandez/dev/basicmachines/basic-factory"
      ]
    },
```
```bash
npx @modelcontextprotocol/inspector uvx mcp-server-git --repository /Users/phernandez/dev/basicmachines/basic-factory
```

### github
language: ts
repo_url: https://github.com/modelcontextprotocol/servers/tree/main/src/github

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
      }
    }
  }
}
```

inspector
```bash
npx -y @modelcontextprotocol/inspector npx  @modelcontextprotocol/server-github
```
set env var:

"GITHUB_PERSONAL_ACCESS_TOKEN": <.env file>

### fetch: web -> markdown 
language: python
repo_url: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-fetch 
```

## Notes:
Update claude config
/Users/phernandez/Library/Application Support/Claude/claude_desktop_config.json


## logs
```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```


# MCP Filesystem Tools - Working Notes

## Tool Capabilities
1. **Directory Operations**
   - `create_directory`: Creates new directories, including nested paths
   - `list_directory`: Shows files and directories with [FILE] and [DIR] prefixes
   
2. **File Operations**
   - `write_file`: Creates or overwrites files with content
   - `read_file`: Retrieves file contents
   - `move_file`: Relocates files between directories
   - `get_file_info`: Provides metadata (size, dates, permissions)
   - `search_files`: Finds files matching patterns (note: case sensitivity varies)

