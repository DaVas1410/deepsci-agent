# 🔬 DeepSci Agent

**Your AI-powered physics research assistant in the terminal**

A CLI-based research agent for deep literature research on physics topics using local AI models and semantic search. Built with a GitHub Copilot-style interface for researchers who live in the terminal.

## ✨ Features

### 🔍 **Smart Literature Search**
- Search 2M+ physics papers from arXiv
- Citation metrics from Semantic Scholar (200M+ papers)
- Automatic ranking by citation count & influence
- Influential citations marked with ⭐

### 🧠 **Semantic Discovery** (NEW!)
- **Vector search** powered by sentence-transformers
- Build a personal research library with ChromaDB
- Find similar papers by meaning, not keywords
- Discover hidden connections in your research

### 🤖 **Local AI Analysis**
- TinyLlama (1.1B) for paper summaries - 100% offline!
- Extract key findings automatically
- No API costs, no token limits
- Privacy-first: your research stays local

### ⚡ **Fast & Efficient**
- Parallel citation fetching (3-5 seconds for 10 papers)
- Persistent vector database
- Semantic search across thousands of papers in milliseconds
- Clean, beautiful terminal UI with Rich

### 💬 **Natural Interface**
- Chat-like experience in your terminal
- Natural language commands: *"find papers on quantum entanglement"*
- Interactive mode with command history
- Markdown rendering for paper details

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/DaVas1410/deepsci-agent.git
cd deepsci-agent

# Create conda environment
conda create -n deep_sci python=3.10 -y
conda activate deep_sci

# Install dependencies
pip install -r requirements.txt

# Start the interactive agent
python -m deepsci.cli.main interactive
```

**First run:** TinyLlama model (669MB) downloads automatically. This only happens once!

## 💡 Usage Examples

### Interactive Mode (Recommended)

```bash
python -m deepsci.cli.main interactive
```

**Basic Search & Discovery:**
```
You: search quantum entanglement
✓ Found 10 papers from arXiv

You: show 1
[Full paper details with abstract]

You: summarize 1
🤖 AI Summary: This paper explores quantum entanglement...
```

**Build Your Research Library:**
```
You: search string theory
You: save 1 2 3
✓ Saved 3 papers to library

You: library stats
📚 Your Research Library
Total Papers: 3
```

**Semantic Discovery:**
```
You: library search dark matter implications
🔍 Searching your library (25 papers)
✓ Found 5 relevant papers
[Papers semantically related to your query]

You: similar to 1
Finding papers similar to: String Theory in AdS/CFT...
✓ Found 3 similar papers in library
```

### Natural Language Commands

The agent understands natural language:
- *"find papers on black holes"*
- *"what about quantum gravity?"*
- *"show me paper 3"*
- *"save papers 1 2 and 5"*

### Command Reference

| Command | Description |
|---------|-------------|
| `search <query>` | Search arXiv with citation rankings |
| `show <number>` | View paper details |
| `save <numbers>` | Save papers to library (e.g., "save 1 2 3") |
| `library search <query>` | Semantic search in your saved papers |
| `similar to <number>` | Find papers similar to one from results |
| `summarize <number>` | Get AI summary (requires AI) |
| `library stats` | Show library statistics |
| `help` | Show all commands |
| `exit` | Exit the chat |

### CLI Options

```bash
# Start without AI (faster, no summaries)
python -m deepsci.cli.main interactive --no-ai

# Direct search from command line
python -m deepsci.cli.main search "quantum mechanics" --limit 5

# Get help
python -m deepsci.cli.main --help
```

## 🧠 How It Works

### Vector Search & Semantic Discovery

DeepSci uses **embeddings** to understand paper meaning, not just keywords:

```
Traditional Search:          Vector Search (DeepSci):
"quantum entanglement"   →   "quantum entanglement"
  ↓                            ↓
Finds: Papers with           Finds: Papers about:
exact words only             • EPR paradox ✓
                             • Bell's theorem ✓
                             • Quantum teleportation ✓
                             • Non-locality ✓
```

**Technology:**
- **Embeddings:** all-MiniLM-L6-v2 (384 dimensions)
- **Vector DB:** ChromaDB with HNSW indexing
- **Speed:** Search 10,000 papers in ~0.5 seconds
- **Storage:** Persistent, survives restarts

📖 **Learn more:** See `docs/VECTOR_SEARCH_EXPLAINED.md` for detailed explanation

### Citation Metrics

Powered by Semantic Scholar API:
- **Citation count:** Total paper citations
- **Influential citations (⭐):** Highly cited by important papers
- **Parallel fetching:** 5 concurrent workers for 5x speedup

### Local AI

- **Model:** TinyLlama 1.1B Chat (Q4_K_M quantized)
- **Size:** 669MB (one-time download)
- **Speed:** ~2-5 seconds per summary on CPU
- **Privacy:** 100% local, no data sent to external APIs

## Requirements

- Python 3.10+
- 8GB+ RAM (for local LLM inference)
- ~5GB disk space (for models and cache)
- Internet (for searching sources; AI works offline after model download)

## 📊 Example Session

```bash
$ python -m deepsci.cli.main interactive

╔═══════════════════════════════════════ DeepSci Agent ════════════════════════════════════════╗
║                           🔬 Welcome to DeepSci Agent v0.1.0                                 ║
║                                                                                              ║
║ Your AI-powered physics research assistant. I can help you:                                  ║
║                                                                                              ║
║ • Search arXiv for physics papers with citation metrics                                      ║
║ • Summarize research papers and extract key findings 🤖                                      ║
║ • Rank papers by citation impact and influence                                               ║
║ • Build a semantic research library with vector search                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

You: search quantum entanglement

🔍 Searching arXiv for: quantum entanglement

✓ Found 10 papers from arXiv
✓ Fetching citations from Semantic Scholar...

╭───┬────────────────────────────────────────────────────┬─────────────────┬──────┬────────────┬────────╮
│ # │ Title                                              │ Authors         │ Year │ Citations  │ Source │
├───┼────────────────────────────────────────────────────┼─────────────────┼──────┼────────────┼────────┤
│ 1 │ Quantum Entanglement in Many-Body Systems          │ Bennett et al.  │ 2020 │ 847 (23⭐) │ ARXIV  │
│ 2 │ Entanglement Dynamics in Black Holes               │ Hawking et al.  │ 2019 │ 234        │ ARXIV  │
│ 3 │ EPR Paradox Revisited                              │ Einstein et al. │ 2021 │ 156 (5⭐)  │ ARXIV  │
╰───┴────────────────────────────────────────────────────┴─────────────────┴──────┴────────────┴────────╯

Type 'show <number>' to see details | Citations with ⭐ are highly influential

You: save 1 2 3
✓ Saved paper 1: Quantum Entanglement in Many-Body Systems
✓ Saved paper 2: Entanglement Dynamics in Black Holes
✓ Saved paper 3: EPR Paradox Revisited

Library now has 3 papers

You: library search wave functions
🔍 Searching your library (3 papers)
✓ Found 2 relevant papers

[Shows semantically related papers from your library]

You: similar to 1
Finding papers similar to: Quantum Entanglement in Many-Body Systems...
✓ Found 2 similar papers

[Shows papers with similar topics]

You: summarize 1
🤖 Generating AI summary...

This paper explores quantum entanglement in many-body systems, focusing on...
Key Findings:
• Novel approach to measuring entanglement entropy
• Applications to condensed matter physics
• Connections to quantum computing

You: exit
👋 Goodbye! Happy researching!
```

## 📦 Data Sources

| Source | Papers | What It Provides |
|--------|--------|-----------------|
| **arXiv** | 2M+ | Physics, math, CS preprints |
| **Semantic Scholar** | 200M+ | Citation metrics, influence scores |
| **Your Library** | ∞ | Personal semantic research database |

**Note:** PubMed integration was removed (biomedical focus, not physics). Future versions may add Google Scholar, journals, and books.

## 🛠️ Technical Stack

- **Language:** Python 3.10+
- **CLI:** Click + Rich for beautiful terminal UI
- **LLM:** llama-cpp-python (TinyLlama 1.1B)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** ChromaDB with persistent storage
- **APIs:** arxiv, semanticscholar

## ⚙️ Requirements

- **Python:** 3.10 or higher
- **RAM:** 4GB minimum, 8GB+ recommended (for LLM)
- **Disk:** ~2GB (models + cache + library)
- **Internet:** Required for searching; AI works offline after model download

## 📁 Project Structure

```
deepsci-agent/
├── deepsci/                # Main package
│   ├── cli/               # CLI interface & interactive chat
│   │   ├── main.py       # Entry point
│   │   └── interactive.py # Chat interface
│   ├── sources/           # Data source integrations
│   │   ├── arxiv_client.py
│   │   └── citation_client.py
│   ├── llm/               # Local LLM integration
│   │   └── local_llm.py
│   └── search/            # Vector search engine
│       └── vector_store.py
├── docs/                  # Documentation
│   ├── VECTOR_SEARCH_EXPLAINED.md
│   ├── FEATURES.md
│   └── CITATION_METRICS.md
├── data/vectordb/         # Your saved papers (persistent)
├── models/                # Downloaded AI models
├── tests/                 # Unit tests
└── README.md
```

## 🎯 Development Status

**✅ MVP COMPLETE!** All core features are functional:

- ✅ arXiv search with citation metrics
- ✅ Local AI summaries (TinyLlama 1.1B)
- ✅ Vector search & semantic discovery
- ✅ Personal research library
- ✅ Interactive CLI with natural language
- ✅ Parallel citation fetching (5x speedup)
- ✅ Persistent storage

### Roadmap (Optional Enhancements)

- [ ] **Paper comparison** - Side-by-side AI analysis
- [ ] **PDF processing** - Full-text search and analysis
- [ ] **Google Scholar** - Additional citation sources
- [ ] **Export** - Save research to Markdown/PDF
- [ ] **Citation graphs** - Visualize paper relationships
- [ ] **Multi-lingual** - Support for non-English papers

## 📚 Documentation

- **[Vector Search Explained](docs/VECTOR_SEARCH_EXPLAINED.md)** - Deep dive into semantic search
- **[Features Guide](docs/FEATURES.md)** - Complete feature documentation
- **[Citation Metrics](docs/CITATION_METRICS.md)** - Understanding impact scores

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with inspiration from **GitHub Copilot CLI**
- Powered by open-source AI models:
  - [TinyLlama](https://github.com/jzhang38/TinyLlama) by Zhang et al.
  - [Sentence Transformers](https://www.sbert.net/) by UKP Lab
- Data from [arXiv](https://arxiv.org/) and [Semantic Scholar](https://www.semanticscholar.org/)

## 🔗 Links

- **Repository:** https://github.com/DaVas1410/deepsci-agent
- **Issues:** https://github.com/DaVas1410/deepsci-agent/issues
- **Author:** [DaVas1410](https://github.com/DaVas1410)

---

**Made with ❤️ for physics researchers who love the terminal** 🔬⚛️

*"The best search engine is the one that understands what you mean, not just what you say."*
