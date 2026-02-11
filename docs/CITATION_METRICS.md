# 🎉 Multi-Source Search + Citation Metrics Added!

## What's New

### 📊 **Citation Metrics**
- **Citation counts** from Semantic Scholar
- **Influential citations** marked with ⭐
- **Automatic ranking** by citation count
- **Citation velocity** tracking (citations/year)

### 🔬 **PubMed Integration**
- Search biomedical and biophysics literature
- Access PubMed's 35+ million articles
- Combined results with arXiv

### 🎯 **Enhanced Search**

**Multi-source search:**
```bash
You: search quantum mechanics
# Searches both arXiv AND PubMed, ranked by citations
```

**Source-specific search:**
```bash
You: search arxiv:quantum mechanics   # arXiv only
You: search pubmed:brain imaging      # PubMed only
```

**Toggle citations:**
```bash
You: citations off   # Faster searches, no citation data
You: citations on    # Show citations (default)
```

## Example Output

```
Found 15 papers (ranked by citations)
╭───┬────────────────────────────┬───────────┬──────┬────────────┬────────╮
│ # │ Title                      │ Authors   │ Year │ Citations  │ Source │
├───┼────────────────────────────┼───────────┼──────┼────────────┼────────┤
│ 1 │ Quantum Entanglement...    │ Bell et.  │ 2019 │ 1847 (45⭐)│ ARXIV  │
│ 2 │ Dark Matter Detection...   │ Smith et. │ 2020 │ 892 (12⭐) │ ARXIV  │
│ 3 │ Neural Networks for...     │ Jones et. │ 2021 │ 234        │ PUBMED │
╰───┴────────────────────────────┴───────────┴──────┴────────────┴────────╯

Citations with ⭐ are highly influential
```

## Citation Metrics Explained

- **Citation Count**: Total times the paper has been cited
- **Influential Citations (⭐)**: High-quality citations from important papers
- **Citation Velocity**: Citations per year since publication
- **Ranking**: Papers automatically sorted by citation count

## Data Sources

1. **arXiv** (2M+ physics papers)
   - Preprints and published papers
   - Physics, math, CS, etc.

2. **PubMed** (35M+ biomedical papers)
   - Peer-reviewed journals
   - Life sciences, biophysics

3. **Semantic Scholar** (Citation data)
   - 200M+ papers analyzed
   - Citation counts and metrics
   - Influential citation detection

## Performance

- **With citations ON**: ~5-10 seconds per search (fetches metrics)
- **With citations OFF**: ~2-3 seconds per search (faster)
- **Automatic rate limiting**: Respects all API limits

## Try It Now!

```bash
conda activate deep_sci
cd /home/davas/Documents/deep_sci
python -m deepsci.cli.main interactive

# Try these searches:
You: search quantum entanglement
You: search arxiv:string theory
You: search pubmed:neuroscience fmri
You: citations off
You: search dark matter
```

---

**Total Sources**: 3 (arXiv, PubMed, Semantic Scholar)
**Total Searchable Papers**: 37M+
**Citation Database**: 200M+ papers

🚀 **Your research agent just got a LOT more powerful!**
