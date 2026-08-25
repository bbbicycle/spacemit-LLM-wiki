# Project: Spacemit LLM Wiki 重构

## Architecture
- Submodules: `Sources/docs-chip`, `Sources/docs-buildroot`, `Sources/docs-product`, `Sources/docs-ai`, `Sources/docs-ros` -> `https://github.com/spacemit-com/<repo>`
- Knowledge base & Metadata: `Knowledge_Atoms/`, `Evidence/`
- Static Assets: `static/`
- Scripts & Automation: `update_sources.sh`, `双击更新文档.command`, `.github/workflows/sync_sources.yml`
- Verification Tool: `vault_linker_lint.py`
- MCP Server & Cloudflare Deployment: `mcp/`, `mcp-worker/`, `scripts/build_mcp_index.py`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Explorer Exploration | Comprehensive exploration of codebase, git submodules, static assets, lint scripts | none | DONE |
| 2 | M2: Git Submodule Architecture | Clean nested repos, add `.gitmodules` for `Sources/docs-*` to `https://github.com/spacemit-com/` | M1 | DONE |
| 3 | M3: Static Asset & Image Protection | Verify all images in `static/`, fix Markdown relative image paths in `Knowledge_Atoms/` & `Evidence/` | M1 | DONE |
| 4 | M4: Cross-Platform Sync & CI/CD | Upgrade `双击更新文档.command`, create `update_sources.sh`, create `.github/workflows/sync_sources.yml` | M2 | DONE |
| 5 | M5: Documentation & Lint Script | Update `README.md`, enhance and run `vault_linker_lint.py` | M3, M4 | DONE |
| 6 | M6: E2E Integration & Audit | E2E verification, Challenger test suite, Forensic Auditor integrity check | M5 | DONE |
| 7 | M7: Dual-Layer MCP Server | Zero-chunking graph navigation + Sources dynamic fetch on Cloudflare Workers (`mcp.yao1302.xyz`) | M6 | DONE |

## Interface Contracts
- Submodule Remote Command: `git submodule update --remote --merge`
- Lint Runner: `python3 vault_linker_lint.py` (Must validate 6 domains and broken link check)

## Code Layout
- `Sources/` — Submodule targets (docs-chip, docs-buildroot, docs-product, docs-ai, docs-ros)
- `static/` — Static assets (schematics, pinouts, diagrams)
- `Knowledge_Atoms/` & `Evidence/` — Core Markdown Wiki & metadata
- `vault_linker_lint.py` — Lint & link validation script
- `.github/workflows/sync_sources.yml` — GitHub Actions daily sync workflow
- `update_sources.sh` & `双击更新文档.command` — Local sync scripts
- `README.md` — Usage documentation
