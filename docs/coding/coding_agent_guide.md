# CodingAgent Execution Guide & Safety Architecture

## Architecture Overview
`CodingAgent` is a specialized developer agent operating within the Personal AI OS framework.

### Toolchain
- `grep_search`: Codebase symbol & pattern search
- `view_file`: Read-only source code inspection
- `replace_file_content`: Sandboxed patch modification
- `run_command`: Automated unit test execution

### Security Invariants
1. **Read Before Write**: Always inspect source definitions before proposing edits.
2. **Sandbox Isolation**: Modifications are tested in isolation prior to git diff review.
3. **No Direct Remote Push**: Production deployments and git pushes require explicit human approval via `AutonomyGovernor`.
