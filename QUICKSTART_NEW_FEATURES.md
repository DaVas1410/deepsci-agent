# 🚀 Quick Start: New Features

## Try Them Now!

### Setup (30 seconds)
```bash
cd /home/davas/Documents/deep_sci
conda activate deep_sci
python deepsci_chat.py
```

---

## Feature 1: Paper Comparison 📊

### Simple Workflow
```
You: search quantum machine learning
✓ Found 10 papers from arXiv

You: compare 1 2
🔍 Comparing 2 papers with AI...

📊 Comparative Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Similarities:**
Both papers explore the intersection of quantum computing 
and machine learning. They share a focus on quantum advantage
for specific ML tasks...

**Differences:**
Paper 1 focuses on variational quantum algorithms while
Paper 2 emphasizes quantum kernel methods...

**Reading Recommendation:**
Start with Paper 1 for foundational concepts, then read
Paper 2 for advanced applications...

**Relationship:**
Paper 2 builds upon techniques introduced in Paper 1...

Side-by-Side Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Title                    Year  Citations  Authors
1  Quantum Computing...     2023  45         Smith et al.
2  Neural Networks on...    2023  28         White et al.
```

### Advanced: Compare 3-4 Papers
```
You: compare 1 2 3 4
[Comprehensive analysis of all 4 papers]
```

---

## Feature 2: Google Scholar 🔍

### Programmatic Usage

#### Search for Papers
```python
from deepsci.sources import ScholarClient

scholar = ScholarClient()

# Search
papers = scholar.search_papers("quantum entanglement", max_results=5)

for paper in papers:
    print(f"{paper['title']}")
    print(f"  Citations: {paper['citation_count']}")
    print(f"  Year: {paper['year']}")
    print(f"  Venue: {paper['venue']}")
```

#### Enrich Paper Data
```python
# Get citation data for a specific paper
data = scholar.enrich_paper_with_scholar("Attention Is All You Need")

print(f"Citations: {data['citation_count']}")  # 217,637!
print(f"Venue: {data['venue']}")
```

#### Author Information
```python
# Get h-index and research interests
author = scholar.get_author_info("Geoffrey Hinton")

print(f"H-index: {author['h_index']}")
print(f"Affiliation: {author['affiliation']}")
print(f"Interests: {author['interests']}")
```

### When to Use Scholar

✅ **Good for:**
- Citation data for non-arXiv papers
- Author credentials and h-index
- Finding highly-cited classic papers
- Papers outside physics domain

❌ **Not recommended for:**
- Primary physics searches (use arXiv)
- Bulk operations (rate limits)
- Real-time applications

---

## Combined Workflow Example

### Research Session
```bash
# 1. Start the agent
python deepsci_chat.py

# 2. Search arXiv
> search quantum error correction

# 3. Compare top papers
> compare 1 2 3

# 4. Save interesting ones
> save 1 3

# 5. Search your library
> library search error correction codes

# 6. Find similar papers
> similar to 1
```

### With Scholar (Python Script)
```python
from deepsci.sources import ArxivClient, ScholarClient

# Search arXiv
arxiv = ArxivClient()
papers = arxiv.search("quantum computing")

# Enrich with Scholar data
scholar = ScholarClient()
for paper in papers[:3]:  # First 3 only (rate limits)
    scholar_data = scholar.enrich_paper_with_scholar(paper.title)
    if scholar_data:
        print(f"{paper.title}: {scholar_data['citation_count']} citations")
```

---

## Quick Reference

### Compare Command
```
compare <numbers>     # Compare 2-4 papers
compare 1 2           # Compare two
compare 1 2 3         # Compare three
compare 1 2 3 4       # Compare four (max)
```

### Scholar API
```python
scholar.search_papers(query, max_results)
scholar.enrich_paper_with_scholar(title)
scholar.get_author_info(name)
scholar.get_cited_by(title, max_results)
```

---

## Tips & Tricks

### Paper Comparison
💡 Compare papers on similar topics for best results
💡 Use after initial search to decide what to read
💡 Max 4 papers - AI context limit
💡 Takes 5-10 seconds for AI analysis

### Google Scholar
💡 Use sparingly - rate limits are aggressive
💡 2-second delay built-in between requests
💡 Perfect for enriching arXiv data
💡 Great for finding classic papers

---

## Troubleshooting

### "Paper comparison requires AI to be enabled"
**Fix**: Don't use `--no-ai` flag

### Scholar returns empty results
**Cause**: Rate limited by Google
**Fix**: Wait 5-10 minutes, then retry

### Compare command not found
**Check**: Did you search for papers first?

---

## Learn More

📖 **Detailed Guide**: `docs/NEW_FEATURES.md`
📖 **Full Docs**: `README.md`
📖 **Vector Search**: `docs/VECTOR_SEARCH_EXPLAINED.md`

---

## Ready to Try?

```bash
conda activate deep_sci
python deepsci_chat.py

# Then:
> search your favorite topic
> compare 1 2
```

🎉 **Have fun researching!**
