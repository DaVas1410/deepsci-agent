# DeepSci Agent

A CLI-based research agent for deep literature research on physics topics using local AI models.

## Overview

DeepSci Agent is an interactive command-line tool that helps researchers explore and synthesize physics literature from multiple sources including arXiv, PubMed, Google Scholar, academic journals, books, and forums. It uses local TinyML models for AI-powered research assistance without API costs.

## Features (Planned)

- 🔍 **Multi-source search**: Query arXiv, PubMed, Google Scholar, journals, books, and forums
- 🤖 **Local AI**: Uses TinyML models (Llama-based) for offline research assistance
- 📚 **Semantic search**: Vector database for intelligent paper discovery
- 💬 **Interactive CLI**: Terminal interface for natural research workflows
- 📊 **Synthesis**: Automatic summarization and comparison of research papers
- 🔗 **Citation tracking**: Build and explore citation graphs
- 💾 **Session management**: Save and resume research sessions

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/deepsci-agent.git
cd deepsci-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Start interactive mode
python -m deepsci

# Search for papers
deepsci search "quantum entanglement"

# Summarize a paper
deepsci summarize arxiv:2301.12345

# Compare papers
deepsci compare arxiv:2301.12345 arxiv:2302.67890
```

## Requirements

- Python 3.10+
- 8GB+ RAM (for local LLM inference)
- ~5GB disk space (for models and vector database)

## Data Sources

- **arXiv**: Preprint papers in physics and related fields
- **PubMed**: Biomedical and biophysics literature
- **Google Scholar**: Broad academic search
- **Journals**: APS, Nature Physics, Physical Review, etc.
- **Books**: Google Books API for textbooks and references
- **Forums**: PhysicsForums and physics.stackexchange

## Architecture

```
deepsci-agent/
├── deepsci/           # Main package
│   ├── cli/          # CLI interface
│   ├── sources/      # Data source integrations
│   ├── llm/          # Local LLM integration
│   ├── search/       # Vector search engine
│   └── agent/        # Research agent core
├── tests/            # Unit and integration tests
└── docs/             # Documentation
```

## Development Status

🚧 **In Development** - This project is in early stages. Check the project board for current progress.

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with inspiration from GitHub Copilot CLI
- Powered by open-source LLM models and tools
