# DeepSci Agent - Quick Demo

## 🚀 Getting Started

### 1. Activate your environment
```bash
conda activate deep_sci
cd /home/davas/Documents/deep_sci
```

### 2. Try the Interactive Chatbot (Recommended!)

```bash
python -m deepsci.cli.main interactive
```

This starts a chat interface where you can type naturally:

**Example conversation:**
```
You: find papers on quantum entanglement
[Shows table of papers from arXiv]

You: show 1
[Shows detailed info about paper #1]

You: search for dark matter
[New search results]

You: help
[Shows all available commands]

You: exit
[Goodbye!]
```

### 3. Or use command-line mode

```bash
# Quick search
python -m deepsci.cli.main search "quantum mechanics" --limit 5

# Search with more results
python -m deepsci.cli.main search "string theory" --limit 20
```

## 💡 Natural Language Examples

The chatbot understands various ways to ask:
- "find papers on black holes"
- "search for quantum computing research"
- "what about gravitational waves"
- "look for papers on dark energy"

## 🎯 Current Features

✅ **Working Now:**
- arXiv paper search
- Interactive chatbot interface
- Natural language command parsing
- Paper metadata and abstracts
- Rich formatted output

🚧 **Coming Soon:**
- AI-powered paper summaries (using local LLM)
- PubMed and Google Scholar integration
- Vector search for semantic discovery
- Paper comparison
- Q&A over your research corpus

## 📝 Tips

1. Use interactive mode for the best experience
2. Type "help" anytime to see available commands
3. Use "show <number>" to view paper details
4. Results are limited to 10 by default (customizable)

---

**Repository:** https://github.com/DaVas1410/deepsci-agent
**Version:** 0.1.0
