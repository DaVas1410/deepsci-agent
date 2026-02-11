# DeepSci Agent

A CLI-based research agent for deep literature research on physics topics using local AI models.

## Overview

DeepSci Agent is an interactive command-line tool that helps researchers explore and synthesize physics literature from multiple sources including arXiv, PubMed, Google Scholar, academic journals, books, and forums. It uses local TinyML models for AI-powered research assistance without API costs.

## Features

- 🔍 **Multi-source search**: arXiv (2M papers) + PubMed (35M papers)
- 📊 **Citation metrics**: Counts, rankings, and influential citations from Semantic Scholar
- 💬 **Interactive chatbot**: Natural language interface in your terminal
- 🤖 **Local AI summaries**: Uses TinyLlama (1.1B) for paper analysis - 100% offline!
- 📚 **Smart ranking**: Automatic sorting by citation count
- 🎯 **Source selection**: Search specific sources or all at once
- 🌟 **Impact metrics**: Influential citations marked with ⭐
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
- *"find papers on quantum entanglement"* - Searches all sources
- *"search arxiv:dark matter"* - Search only arXiv
- *"search pubmed:brain imaging"* - Search only PubMed  
- *"show 1"* - View paper details
- *"summarize 1"* - Get AI-powered summary
- *"citations off"* - Disable citations for faster searches
- *"help"* - Show all commands

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

## Data Sources

- **arXiv**: 2M+ physics, math, and CS papers
- **PubMed**: 35M+ biomedical and biophysics papers  
- **Semantic Scholar**: Citation metrics for 200M+ papers

## Requirements

- Python 3.10+
- 8GB+ RAM (for local LLM inference)
- ~5GB disk space (for models and cache)
- Internet (for searching sources; AI works offline after model download)

## Example Session

```bash
You: search quantum entanglement

✓ Found 10 papers from arXiv
✓ Found 5 papers from PubMed

Found 15 papers (ranked by citations)
╭───┬────────────────────────────┬───────────┬──────┬────────────┬────────╮
│ # │ Title                      │ Authors   │ Year │ Citations  │ Source │
├───┼────────────────────────────┼───────────┼──────┼────────────┼────────┤
│ 1 │ Entanglement dynamics...   │ Potter et.│ 2021 │ 847 (23⭐) │ ARXIV  │
│ 2 │ Quantum Networks...        │ Smith et. │ 2020 │ 234        │ PUBMED │
╰───┴────────────────────────────┴───────────┴──────┴────────────┴────────╯

You: show 1
[Displays full abstract and details]

You: summarize 1
🤖 Generating AI summary...
[AI provides concise summary and key findings]
```

## Data Sources (Detailed)

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
