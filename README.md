# DeepSci Agent

A CLI-based research agent for deep literature research on physics topics using local AI models.

## Overview

DeepSci Agent is an interactive command-line tool that helps researchers explore and synthesize physics literature from multiple sources including arXiv, PubMed, Google Scholar, academic journals, books, and forums. It uses local TinyML models for AI-powered research assistance without API costs.

## Features

- 🔍 **Multi-source search**: Query arXiv (PubMed, Google Scholar coming soon)
- 💬 **Interactive chatbot**: Natural language interface in your terminal
- 🤖 **Local AI summaries**: Uses TinyLlama (1.1B) for paper analysis - 100% offline!
- 📚 **Paper details**: View abstracts, authors, and metadata
- 🎯 **Smart summarization**: Extract key findings and methodologies
- 🔗 **Citation tracking**: Build and explore citation graphs (coming soon)
- 💾 **No API costs**: Everything runs locally on your machine

## Installation

```bash
# Clone the repository
git clone https://github.com/DaVas1410/deepsci-agent.git
cd deepsci-agent

# Create conda environment
conda create -n deep_sci python=3.10 -y
conda activate deep_sci

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Interactive Chat Mode (Recommended!)

Start the interactive chatbot interface:

```bash
python -m deepsci.cli.main interactive
```

Then just chat naturally:
- *"find papers on quantum entanglement"*
- *"search for dark matter research"*  
- *"show 1"* (to see details of paper #1 from results)
- *"summarize 1"* (to get AI-powered summary - requires model download on first use)
- *"help"* for more commands

### Command-Line Mode

```bash
# Search for papers
python -m deepsci.cli.main search "quantum mechanics" --limit 5

# Start without AI (faster startup)
python -m deepsci.cli.main interactive --no-ai

# Get help
python -m deepsci.cli.main --help
```

### First-Time AI Setup

On first use of AI features, TinyLlama (669MB) will be downloaded automatically. This only happens once!

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
