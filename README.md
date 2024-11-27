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

3. **Git Tool Limitations**
   - Missing `git push` functionality
   - Local operations only (add, commit, branch)
   - No remote repository management
   - Branch operations require extra verification

4. **GitHub Tool Limitations**
   - No PR comment functionality
   - No issue comments
   - `push_files` requires existing remote branch
   - PR creation returns merge_commit_sha errors
   - Limited repository management options
   - No direct comment or review features