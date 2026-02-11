# 🔬 DeepSci Agent

**Your AI-powered physics research assistant in the terminal**

A comprehensive CLI-based research agent for deep literature research on physics topics. Features local AI models, semantic search, PDF processing, citation network visualization, and intelligent paper comparison. Built for use in the interface for researchers who live in the terminal.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

### 🔍 **Smart Literature Search**
- Search **2M+ physics papers** from arXiv
- Citation metrics from **Semantic Scholar** (200M+ papers)
- **Google Scholar integration** for broader coverage
- Automatic ranking by citation count & influence
- **80-90% citation success rate** with intelligent fallback
- Multi-layered caching (7-day persistence)
- Influential citations marked with ⭐

### 📊 **AI-Powered Paper Comparison**
- **Compare 2-4 papers** with intelligent AI analysis
- Automatic identification of similarities and differences
- Methodological comparisons and research impact assessment
- Reading recommendations based on content analysis
- Formatted comparison tables with citation metrics
- Fallback to rule-based comparison if AI unavailable

### 📄 **PDF Full-Text Processing**
- **Download PDFs** directly from arXiv with smart caching
- **Extract full text** with PyMuPDF (fitz)
- **Section detection** (Abstract, Introduction, Methods, Results, etc.)
- **Full-text search** within PDFs with context highlighting
- Instant access to cached PDFs (0.000s retrieval)

### 🔗 **Citation Network Visualization**
- Build **interactive citation graphs** with NetworkX
- **3 visualization modes:**
  - Interactive HTML (hover, zoom, pan) with pyvis
  - Static publication-quality images with matplotlib
  - Terminal ASCII visualization with Rich
- Identify **seminal papers** by influence score (PageRank)
- Find **citation paths** between papers
- Node sizing by citation count, coloring by year
- Discover research communities and influential works

### 🧠 **Semantic Discovery**
- **Vector search** powered by sentence-transformers
- Build a personal research library with ChromaDB
- Find similar papers by meaning, not keywords
- Discover hidden connections in your research
- Search 10,000 papers in ~0.5 seconds

### 🤖 **Local AI Analysis**
- TinyLlama (1.1B) for paper summaries - **100% offline!**
- Extract key findings automatically
- Compare multiple papers with AI insights
- Proper chat template formatting for quality output
- **No API costs, no token limits**
- **Privacy-first:** your research stays local

### ⚡ **Fast & Efficient**
- Citation fetching with retry logic and exponential backoff
- 7-day persistent caching for citations
- Instant PDF retrieval from cache
- Semantic search across thousands of papers in milliseconds
- Clean, beautiful terminal UI with Rich
- Progress indicators and real-time stats

### 💬 **Natural Interface**
- Chat-like experience in your terminal
- Natural language commands: *"find papers on quantum entanglement"*
- Interactive mode with command history
- Markdown rendering for paper details
- Comprehensive help system
- Error recovery and helpful suggestions

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/DaVas1410/deepsci-agent.git
cd deepsci-agent

# Create conda environment (recommended)
conda create -n deep_sci python=3.10 -y
conda activate deep_sci

# Or use venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the interactive agent
python deepsci_chat.py
```

**First run:** TinyLlama model (638MB) downloads automatically. This only happens once!

## 💡 Usage Examples

### Interactive Mode (Recommended)

```bash
python deepsci_chat.py
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

**Download & Search PDFs:**
```
You: download 1
📄 Downloading PDF: Quantum Entanglement in Many-Body Systems
✓ PDF downloaded: 1706.03762.pdf

You: fulltext 1
📝 Extracting text from PDF...
✓ Extracted 45,230 characters

You: search pdf 1 quantum
🔍 Searching PDF for: 'quantum'
✓ Found 87 matches
```

**Build Citation Networks:**
```
You: graph 1 2 3
🔗 Building citation network for 3 papers...
✓ Graph built: 45 nodes, 128 edges

📊 Citation Network (Terminal View)
[Shows statistics and top papers]

Generate interactive HTML visualization? [Y/n]: y
✓ Interactive graph saved: ./data/graphs/citation_network.html
→ Opening in browser...

You: seminal
🌟 Seminal Papers (Most Influential):
[Shows ranked list of influential papers]

You: path 1 3
✓ Citation path found (4 papers):
  1. Quantum Entanglement... → cites
  2. EPR Paradox Revisited... → cites
  3. Bell's Theorem... → cites
  4. Quantum Teleportation...
```

**Build Your Research Library:**
```
You: search string theory
You: save 1 2 3
✓ Saved 3 papers to library

You: library stats
📚 Your Research Library
Total Papers: 3

You: library search dark matter
🔍 Searching your library (3 papers)
✓ Found 2 relevant papers
[Papers semantically related to your query]

You: similar to 1
Finding papers similar to: String Theory in AdS/CFT...
✓ Found 2 similar papers in library
```

**Compare Papers with AI:**
```
You: search quantum machine learning
✓ Found 10 papers from arXiv

You: compare 1 2 3
🔍 Comparing 3 papers with AI...

╭────────────────────────── Comparison of 3 Papers ──────────────────────────╮
│ 📊 Comparative Analysis                                                    │
│                                                                            │
│ **Similarities:**                                                          │
│ • All three papers focus on quantum-classical hybrid approaches            │
│ • Common emphasis on variational quantum algorithms                        │
│ • Similar experimental validation methodologies                            │
│                                                                            │
│ **Key Differences:**                                                       │
│ • Paper 1 focuses on supervised learning, Paper 2 on reinforcement        │
│ • Paper 3 introduces novel quantum feature maps                            │
│ • Different quantum hardware platforms (IBM vs. Google vs. IonQ)          │
│                                                                            │
│ **Overall Assessment:**                                                    │
│ Papers show convergence on core techniques with divergent applications    │
│                                                                            │
│ **Reading Order:**                                                         │
│ 1. Paper 1 (foundational concepts)                                         │
│ 2. Paper 3 (advanced techniques)                                           │
│ 3. Paper 2 (specialized applications)                                      │
╰────────────────────────────────────────────────────────────────────────────╯

                          Side-by-Side Summary
╭───┬────────────────────────┬──────┬────────────┬──────────────────────╮
│ # │ Title                  │ Year │ Citations  │ Authors              │
├───┼────────────────────────┼──────┼────────────┼──────────────────────┤
│ 1 │ Quantum Comp...        │ 2023 │ 45         │ Smith et al.         │
│ 2 │ Neural Nets...         │ 2023 │ 28         │ White et al.         │
│ 3 │ Hybrid Appr...         │ 2024 │ 12         │ Johnson et al.       │
╰───┴────────────────────────┴──────┴────────────┴──────────────────────╯
```

### Natural Language Commands

The agent understands natural language:
- *"find papers on black holes"*
- *"what about quantum gravity?"*
- *"show me paper 3"*
- *"save papers 1 2 and 5"*
- *"compare the first three papers"*
- *"download pdf for paper 2"*

### Command Reference

#### Search & Discovery
| Command | Description |
|---------|-------------|
| `search <query>` | Search arXiv with citation rankings |
| `show <number>` | View paper details |
| `similar to <number>` | Find papers similar to one from results |
| `library search <query>` | Semantic search in your saved papers |

#### Analysis & AI
| Command | Description |
|---------|-------------|
| `summarize <number>` | Get AI summary (requires AI) |
| `compare <numbers>` | Compare 2-4 papers with AI (e.g., "compare 1 2 3") |

#### PDF Processing
| Command | Description |
|---------|-------------|
| `download <number>` | Download PDF for offline access |
| `fulltext <number>` | Extract and view full text from PDF |
| `search pdf <number> <query>` | Search for text within a PDF |

#### Citation Networks
| Command | Description |
|---------|-------------|
| `graph` | Build citation network for current papers |
| `graph <numbers>` | Build network for specific papers (e.g., "graph 1 2 3") |
| `seminal` | Identify most influential papers in network |
| `path <num1> <num2>` | Find citation path between two papers |

#### Library Management
| Command | Description |
|---------|-------------|
| `save <numbers>` | Save papers to library (e.g., "save 1 2 3") |
| `library stats` | Show library statistics |

#### Settings & Help
| Command | Description |
|---------|-------------|
| `citations on/off` | Enable/disable citation fetching |
| `help` | Show all commands |
| `exit` | Exit the chat |

### CLI Options

```bash
# Start without AI (faster, no summaries)
python deepsci_chat.py --no-ai

# Show version
python deepsci_chat.py --version

# Get help
python deepsci_chat.py --help
```

## 📚 Documentation

**Comprehensive Guides:**
- **[NEW_FEATURES.md](docs/NEW_FEATURES.md)** - Complete guide to Google Scholar & paper comparison
- **[CITATION_FIX.md](CITATION_FIX.md)** - Citation ranking improvements & architecture
- **[PDF_FEATURE.md](PDF_FEATURE.md)** - PDF processing capabilities
- **[QUICKSTART_NEW_FEATURES.md](QUICKSTART_NEW_FEATURES.md)** - Quick reference for new features

## 🧠 How It Works

### Citation Network Visualization

DeepSci builds **interactive citation graphs** to visualize research relationships:

```
Paper A (2020, 500 cites) ─┐
                           ├──→ Paper C (2022, 50 cites)
Paper B (2019, 300 cites) ─┘      ↓
                                Paper D (2023, 10 cites)
```

**Features:**
- **Interactive HTML:** Hover for details, zoom, pan, click to explore
- **Node sizing:** Larger nodes = more citations (log scale)
- **Color coding:** Blue (old) → Teal → Orange → Red (recent)
- **Influence metrics:** PageRank algorithm identifies seminal works
- **Path finding:** Discover how papers are connected through citations

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

### Citation Metrics with Intelligent Fallback

DeepSci uses a **multi-layered approach** for reliable citation data:

```
1. Check Cache (7-day persistence)
   ↓ (if miss)
2. Try Semantic Scholar API (3 retries, exponential backoff)
   ↓ (if fail)
3. Fallback to Google Scholar
   ↓ (if fail)
4. Return 0 with graceful degradation
```

**Result:** 80-90% success rate (up from 20%)

**Metrics Provided:**
- **Citation count:** Total paper citations
- **Influential citations (⭐):** Highly cited by important papers
- **Reference count:** Papers cited by this paper
- **Year & venue:** Publication details
- **Fields of study:** Research categories

### PDF Processing Pipeline

DeepSci provides comprehensive PDF handling:

```
1. Download from arXiv → Smart caching in ./data/pdfs/
2. Extract text with PyMuPDF → High-quality text extraction
3. Detect sections → Abstract, Intro, Methods, Results, etc.
4. Enable search → Full-text search with context
```

**Capabilities:**
- Instant cache retrieval (0.000s for cached PDFs)
- Section-aware extraction
- Context highlighting in search results
- Metadata extraction (pages, size, etc.)

### Local AI

- **Model:** TinyLlama 1.1B Chat (Q4_K_M quantized)
- **Size:** 638MB (one-time download)
- **Speed:** ~2-5 seconds per summary on CPU
- **Privacy:** 100% local, no data sent to external APIs
- **Format:** Proper chat template for quality output

## 📊 Requirements

- **Python:** 3.10 or higher
- **RAM:** 4GB minimum, 8GB+ recommended (for LLM)
- **Disk:** ~3GB (models + cache + library + PDFs)
- **Internet:** Required for searching; AI works offline after model download

## 📊 Example Session

```bash
$ python deepsci_chat.py

╔═══════════════════════════════════════ DeepSci Agent ════════════════════════════════════════╗
║                           🔬 Welcome to DeepSci Agent v0.2.0                                 ║
║                                                                                              ║
║ Your AI-powered physics research assistant. I can help you:                                  ║
║                                                                                              ║
║ • Search arXiv & Google Scholar for physics papers                                           ║
║ • Compare papers with AI-powered analysis                                                    ║
║ • Download & search PDFs with full-text extraction                                           ║
║ • Build interactive citation networks                                                        ║
║ • Summarize papers and extract key findings 🤖                                               ║
║ • Rank papers by citation impact and influence                                               ║
║ • Build a semantic research library with vector search                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

You: search quantum entanglement

🔍 Searching arXiv: quantum entanglement

✓ Found 10 papers from arXiv
✓ Fetching citations...

╭───┬────────────────────────────────────────────────────┬─────────────────┬──────┬────────────┬────────╮
│ # │ Title                                              │ Authors         │ Year │ Citations  │ Source │
├───┼────────────────────────────────────────────────────┼─────────────────┼──────┼────────────┼────────┤
│ 1 │ Quantum Entanglement in Many-Body Systems          │ Bennett et al.  │ 2020 │ 847 (23⭐) │ ARXIV  │
│ 2 │ Entanglement Dynamics in Black Holes               │ Hawking et al.  │ 2019 │ 234        │ ARXIV  │
│ 3 │ EPR Paradox Revisited                              │ Einstein et al. │ 2021 │ 156 (5⭐)  │ ARXIV  │
╰───┴────────────────────────────────────────────────────┴─────────────────┴──────┴────────────┴────────╯

Type 'show <number>' to see details | Citations with ⭐ are highly influential

You: compare 1 2

🔍 Comparing 2 papers with AI...

╭────────────────────────── Comparison of 2 Papers ──────────────────────────╮
│ 📊 Comparative Analysis                                                    │
│                                                                            │
│ **Similarities:**                                                          │
│ Both papers investigate quantum entanglement, with emphasis on many-body  │
│ systems. They share theoretical frameworks and mathematical approaches.   │
│                                                                            │
│ **Key Differences:**                                                       │
│ Paper 1 focuses on condensed matter applications while Paper 2 explores   │
│ black hole physics and thermodynamics. Different experimental methods.    │
╰────────────────────────────────────────────────────────────────────────────╯

You: download 1

📄 Downloading PDF: Quantum Entanglement in Many-Body Systems
✓ PDF downloaded: 2003.05542.pdf (2.1 MB)

You: search pdf 1 entropy

🔍 Searching PDF for: 'entropy'
✓ Found 23 matches

Match 1:
  ...entanglement entropy is a fundamental measure of quantum correlations in many-body systems...

Match 2:
  ...we calculate the von Neumann entropy to quantify the degree of entanglement...

You: graph

🔗 Building citation network for 3 papers...
✓ Graph built: 87 nodes, 234 edges

📊 Citation Network (Terminal View)

Graph Statistics
━━━━━━━━━━━━━━━━━━━━━━━━
Total Papers      87
Citation Links    234
Density          0.031

Top Papers by Citations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Title                              Year  Cites    In-Graph
1  Quantum Entanglement in Many...    2020  847      15
2  Entanglement Dynamics in Bla...    2019  234      8
3  EPR Paradox Revisited              2021  156      5

Generate interactive HTML visualization? [Y/n]: y
✓ Interactive graph saved: ./data/graphs/citation_network.html
→ Opening in browser...

You: seminal

🌟 Seminal Papers (Most Influential):

#  Title                              Year  Citations  Influential  Score
1  Quantum Entanglement in Many...    2020  847        23          8547
2  Foundations of Quantum Mecha...    1997  2341       156         23566
3  Entanglement Dynamics in Bla...    2019  234        8           2420

You: save 1 2 3
✓ Saved paper 1: Quantum Entanglement in Many-Body Systems
✓ Saved paper 2: Entanglement Dynamics in Black Holes
✓ Saved paper 3: EPR Paradox Revisited

Library now has 3 papers

You: library search wave functions
🔍 Searching your library (3 papers)
✓ Found 2 relevant papers

[Shows semantically related papers from your library]

You: exit
👋 Goodbye! Happy researching!
```

## 📦 Data Sources

| Source | Papers | What It Provides |
|--------|--------|-----------------|
| **arXiv** | 2M+ | Physics, math, CS preprints |
| **Semantic Scholar** | 200M+ | Citation metrics, influence scores, references |
| **Google Scholar** | Millions | Fallback citation data, broader coverage |
| **Your Library** | ∞ | Personal semantic research database |

## 🛠️ Technical Stack

- **Language:** Python 3.10+
- **CLI Framework:** Rich for beautiful terminal UI
- **LLM:** llama-cpp-python (TinyLlama 1.1B)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** ChromaDB with persistent storage
- **Graph Analysis:** NetworkX for citation networks
- **Visualization:** 
  - pyvis for interactive HTML graphs
  - matplotlib for static plots
  - Rich for terminal visualization
- **PDF Processing:** PyMuPDF (fitz) for text extraction
- **APIs:** 
  - arxiv (official Python client)
  - semanticscholar (official client)
  - scholarly (Google Scholar scraping)
- **Caching:** JSON-based with 7-day persistence

## 📁 Project Structure

```
deepsci-agent/
├── deepsci/                    # Main package
│   ├── cli/                   # CLI interface & interactive chat
│   │   └── interactive.py    # Chat interface with all features
│   ├── sources/               # Data source integrations
│   │   ├── arxiv_client.py   # arXiv API integration
│   │   ├── citation_client.py # Citation fetching with fallback
│   │   ├── scholar_client.py  # Google Scholar integration
│   │   ├── pdf_processor.py   # PDF download & extraction
│   │   └── citation_cache.py  # 7-day citation cache
│   ├── llm/                   # Local LLM integration
│   │   └── local_llm.py      # TinyLlama wrapper
│   ├── search/                # Vector search engine
│   │   └── vector_store.py   # ChromaDB wrapper
│   └── analysis/              # Citation network analysis
│       ├── citation_graph.py  # Graph building & metrics
│       └── graph_visualizer.py # Multiple visualization modes
├── docs/                      # Comprehensive documentation
│   ├── NEW_FEATURES.md       # Feature guide
│   └── ...
├── data/                      # User data (auto-created)
│   ├── vectordb/             # Your saved papers (persistent)
│   ├── pdfs/                 # Downloaded PDFs (cached)
│   ├── graphs/               # Citation network visualizations
│   └── citation_cache.json   # Citation data cache
├── models/                    # Downloaded AI models
├── tests/                     # Unit tests
├── deepsci_chat.py           # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Development Status

**✅ v0.2.0 - FEATURE COMPLETE!** All major features are functional:

- ✅ arXiv search with citation metrics
- ✅ Google Scholar integration & fallback
- ✅ Local AI summaries (TinyLlama 1.1B)
- ✅ AI-powered paper comparison (2-4 papers)
- ✅ PDF download, extraction, and full-text search
- ✅ Citation network visualization (3 modes)
- ✅ Seminal paper identification (PageRank)
- ✅ Citation path finding
- ✅ Vector search & semantic discovery
- ✅ Personal research library with ChromaDB
- ✅ Interactive CLI with natural language
- ✅ 80-90% citation success rate
- ✅ Persistent caching (citations, PDFs)

### Changelog

**v0.2.0** (2026-02-11)
- ✨ Added citation network visualization with 3 modes (interactive HTML, static images, terminal)
- ✨ Added PDF full-text processing (download, extract, search)
- ✨ Added AI-powered paper comparison (2-4 papers)
- ✨ Added Google Scholar integration for broader coverage
- 🐛 Fixed citation fetching with intelligent fallback (80-90% success rate)
- 🐛 Fixed AI comparison output formatting
- 📚 Added comprehensive documentation
- ⚡ Improved caching with 7-day persistence

**v0.1.0** (2026-01-15)
- 🎉 Initial release
- ✨ arXiv search with Semantic Scholar citations
- ✨ Local AI summaries with TinyLlama
- ✨ Vector search with ChromaDB
- ✨ Interactive CLI interface

### Roadmap (Future Enhancements)

- [ ] **Export functionality** - Save research to Markdown/PDF reports
- [ ] **Literature review generator** - AI-powered comprehensive reviews
- [ ] **Multi-source search** - Unified search across all sources
- [ ] **Author collaboration networks** - Visualize research teams
- [ ] **Research gap analysis** - Identify understudied areas
- [ ] **Larger AI models** - Option for Phi-2 or Mistral (better quality)
- [ ] **Docker containerization** - Easy deployment
- [ ] **PyPI package** - Install via `pip install deepsci-agent`
- [ ] **Multi-lingual support** - Non-English papers

## 📚 Documentation

- **[NEW_FEATURES.md](docs/NEW_FEATURES.md)** - Complete guide to Google Scholar & paper comparison
- **[CITATION_FIX.md](CITATION_FIX.md)** - Citation ranking improvements & architecture  
- **[PDF_FEATURE.md](PDF_FEATURE.md)** - PDF processing capabilities & usage
- **[QUICKSTART_NEW_FEATURES.md](QUICKSTART_NEW_FEATURES.md)** - Quick reference guide
- **[COMPARISON_FIX.md](COMPARISON_FIX.md)** - AI comparison bug fixes & improvements

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/DaVas1410/deepsci-agent.git
cd deepsci-agent
pip install -r requirements.txt

# Run tests (when available)
pytest tests/

# Code formatting
black deepsci/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by open-source AI models:
  - [TinyLlama](https://github.com/jzhang38/TinyLlama) by Zhang et al.
  - [Sentence Transformers](https://www.sbert.net/) by UKP Lab
- Data from [arXiv](https://arxiv.org/), [Semantic Scholar](https://www.semanticscholar.org/), and [Google Scholar](https://scholar.google.com/)
- Graph visualization with [NetworkX](https://networkx.org/) and [pyvis](https://pyvis.readthedocs.io/)
- PDF processing with [PyMuPDF](https://pymupdf.readthedocs.io/)

## 🔗 Links

- **Repository:** https://github.com/DaVas1410/deepsci-agent
- **Issues:** https://github.com/DaVas1410/deepsci-agent/issues
- **Discussions:** https://github.com/DaVas1410/deepsci-agent/discussions
- **Author:** [DaVas1410](https://github.com/DaVas1410)

## 🌟 Star History

If you find DeepSci Agent useful, please consider giving it a ⭐ on GitHub!

---

**Made with ❤️ for physics researchers who love the terminal** 🔬⚛️

*"The best research tool is one that understands what you mean, visualizes what you need, and keeps your data private."*

---

## ❓ FAQ

**Q: Do I need an API key?**  
A: No! DeepSci uses free APIs (arXiv, Semantic Scholar) and runs AI locally. No registration required.

**Q: How much disk space do I need?**  
A: ~3GB total: ~640MB for AI model, ~500MB for vector embeddings, rest for PDFs and cache.

**Q: Can I use this for non-physics papers?**  
A: Yes! While optimized for physics, it works with any arXiv paper (math, CS, etc.).

**Q: Is my research data private?**  
A: 100% private. All processing happens locally. Only metadata is fetched from public APIs.

**Q: Can I run this without the AI?**  
A: Yes! Use `python deepsci_chat.py --no-ai` for faster operation without summaries/comparison.

**Q: How accurate are the citation counts?**  
A: 80-90% of papers get accurate citations from Semantic Scholar or Google Scholar. Recent papers may have incomplete data.

**Q: Can I export my research?**  
A: Currently you can visualize citation networks as HTML/PNG. Export to Markdown/PDF is planned for v0.3.0.

**Q: What if a PDF isn't available?**  
A: Most arXiv papers have PDFs. If unavailable, you can still search abstracts and use other features.

---

**⚡ Quick Commands Cheatsheet**

```bash
# Search & Discovery
search quantum computing          # Search arXiv
show 1                           # View paper details
similar to 2                     # Find similar papers

# AI Analysis  
summarize 3                      # AI summary
compare 1 2 3                    # Compare papers

# PDFs
download 1                       # Download PDF
fulltext 1                       # Extract text
search pdf 1 quantum             # Search in PDF

# Citation Networks
graph                            # Build network
graph 1 2 3                      # Network for specific papers
seminal                          # Show influential papers
path 1 5                         # Find citation path

# Library
save 1 2 3                       # Save to library
library search <query>           # Semantic search
library stats                    # Show stats

# Settings
help                             # Show all commands
exit                             # Quit
```
