# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-31

### Added
- Initial release of OpenClaw Memory Manager
- **Token Counter** (`token_counter.py`)
  - Count tokens using tiktoken (cl100k_base encoding)
  - Support for text input and JSON files
  - Threshold checking with exit codes
  - Warning levels: OK, MEDIUM, HIGH, CRITICAL
- **Streaming Compressor** (`compressor.py`)
  - Summarize old messages using Claude Haiku
  - Keep recent N messages verbatim
  - Batch processing for large histories
  - Dry-run mode for testing
- **Budget Tracker** (`budget_tracker.py`)
  - Track costs per session and daily
  - Model pricing for Claude 3/4 family
  - Budget alerts
  - Usage logging to JSON
- **Dashboard** (`dashboard_server.py` + `index.html`)
  - Real-time metrics display
  - Context usage visualization
  - Cost tracking
  - Compression stats
- **Clawdbot/Moltbot Integration**
  - Standard SKILL.md format
  - Mandatory rules for subagent spawning
  - Priority loading configuration

### Documentation
- README with before/after diagrams (Mermaid)
- SKILL.md with usage instructions
- Installation guide

## [Unreleased]

### Planned
- WebSocket support for real-time dashboard updates
- Integration with Clawdbot hooks for automatic compression
- Prometheus metrics export
- Multi-agent session tracking
