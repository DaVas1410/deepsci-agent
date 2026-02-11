# New Features Guide

## Paper Comparison (AI-Powered)

### What It Does
Compare 2-4 research papers side-by-side with intelligent AI analysis. Get insights on similarities, differences, and reading recommendations.

### How to Use
```bash
# 1. Search for papers
> search quantum computing

# 2. Compare papers from results (by number)
> compare 1 2
> compare 1 2 3    # Compare up to 4 papers
```

### What You Get
- **AI Comparative Analysis**: Intelligent analysis covering:
  - Key similarities in approach or findings
  - Key differences and unique contributions
  - Which paper to read first and why
  - How the papers relate to each other
  
- **Side-by-Side Table**: Quick comparison of:
  - Titles
  - Publication years
  - Citation counts
  - Authors

### Requirements
- AI must be enabled (default)
- Papers must be in current search results

### Example Output
```
📊 Comparative Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[AI-generated comparative analysis...]

Side-by-Side Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Title                    Year  Citations  Authors
1  Quantum Computing...     2023  45         Alice Smith et al.
2  Neural Networks on...    2023  28         Carol White et al.
```

---

## Google Scholar Integration

### What It Does
Access additional citation data and discover papers through Google Scholar's massive index.

### Programmatic Usage
```python
from deepsci.sources import ScholarClient

scholar = ScholarClient()

# Search for papers
results = scholar.search_papers("quantum entanglement", max_results=10)

# Enrich paper with Scholar data
data = scholar.enrich_paper_with_scholar("Paper Title Here")
# Returns: citation_count, venue, publisher, etc.

# Get author information
author_info = scholar.get_author_info("Einstein")
# Returns: h-index, i10-index, affiliation, interests
```

### Features
1. **Search Papers**: Find papers with citation counts
2. **Enrich Metadata**: Add citation data to existing papers
3. **Author Info**: Get h-index, affiliation, research interests
4. **Related Papers**: Find papers that cite a given paper

### Important Notes
⚠️ **Rate Limiting**: Google Scholar actively blocks scrapers
- Built-in 2-second delay between requests
- May still encounter blocks with heavy use
- This is expected behavior for web scraping
- If blocked, wait several minutes before retrying

✅ **Best Practices**:
- Use sparingly for enrichment only
- Prefer arXiv + Semantic Scholar for primary searches
- Don't run in tight loops
- Respect Scholar's terms of service

### When to Use Scholar
- Need citation data for non-arXiv papers
- Looking for papers outside physics
- Checking author credentials
- Finding highly-cited classic papers

### When NOT to Use Scholar
- Primary physics research (use arXiv)
- Bulk operations (will get rate limited)
- Real-time applications
- Automated systems

---

## Combined Workflow Example

```bash
# Start the chat
$ conda activate deep_sci
$ python deepsci_chat.py

# Search and compare
> search quantum machine learning
Found 10 papers from arXiv

# Compare top results
> compare 1 2 3

# Save interesting papers
> save 1 2

# Find similar papers in library
> similar to 1

# Search your library
> library search quantum algorithms
```

---

## Technical Details

### Files
- `deepsci/sources/scholar_client.py` - Google Scholar client
- `deepsci/cli/interactive.py` - Enhanced with compare feature

### Dependencies
- `scholarly>=1.7.0` - Google Scholar scraping
- Existing: `llama-cpp-python`, `rich`, `chromadb`

### Performance
- **Compare**: ~5-10 seconds for AI analysis (local LLM)
- **Scholar Search**: ~2-3 seconds per result (rate limited)
- **Scholar Enrich**: ~2 seconds per paper

### Limitations
1. **Compare Feature**:
   - Maximum 4 papers per comparison
   - Requires AI enabled
   - Papers must be in current results

2. **Scholar Integration**:
   - Web scraping (fragile)
   - Rate limiting (aggressive)
   - No official API
   - May break with Scholar UI changes

---

## Future Enhancements

Potential additions:
- [ ] Export comparisons to Markdown/PDF
- [ ] Visual comparison charts
- [ ] Citation graph visualization
- [ ] Scholar + arXiv combined search
- [ ] Automatic Scholar enrichment toggle
- [ ] Batch paper comparison (>4 papers)

---

## Troubleshooting

### "Paper comparison requires AI to be enabled"
**Solution**: Start with AI enabled (default) or don't use `--no-ai` flag

### Scholar search returns empty results
**Possible causes**:
1. Rate limited by Google Scholar (most common)
2. Network connectivity issues
3. Scholar changed their page structure

**Solutions**:
1. Wait 5-10 minutes and try again
2. Use arXiv search instead for physics papers
3. Check internet connection

### Compare command not working
**Check**:
1. Have you searched for papers first?
2. Are paper numbers valid (1-10)?
3. Did you provide at least 2 papers?
4. Is AI enabled?

---

## Questions?

See main documentation:
- `README.md` - Project overview
- `docs/VECTOR_SEARCH_EXPLAINED.md` - Vector search details
- `DEMO.md` - Interactive demo guide
