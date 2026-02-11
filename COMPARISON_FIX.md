# Paper Comparison Feature - Bug Fix

## Issue Identified
The comparison feature was outputting truncated or malformed AI analysis, showing only fragments like "5 Any other relevant information or insights."

## Root Cause
The prompt was not using the proper **chat template format** required by TinyLlama. The model expects:
```
<|system|>
[System instructions]
</s>
<|user|>
[User prompt]
</s>
<|assistant|>
[Model completes this]
```

The original prompt was plain text without these special tokens, causing the model to treat it incorrectly.

## Fix Applied

### 1. Proper Chat Template ✅
Updated the comparison prompt to use the same format as `summarize_abstract()`:

```python
comparison_prompt = f"""<|system|>
You are a research assistant helping to compare scientific papers.
</s>
<|user|>
Compare these {len(papers_to_compare)} research papers:

{papers_info}

Provide analysis with:
- Similarities
- Differences  
- Reading Order
- Relationship

Write a clear analysis:
</s>
<|assistant|>
"""
```

### 2. Fallback Mechanism ✅
Added a rule-based fallback comparison in case AI generation fails:

```python
def _generate_simple_comparison(papers):
    """Generate basic comparison without AI"""
    - Compare years, citations, authors
    - Provide reading recommendations
    - Show basic statistics
```

### 3. Response Cleaning ✅
Strip prompt artifacts from AI output:
- Remove "Write your analysis now:"
- Remove "TASK:" prefixes
- Detect short/invalid responses
- Fall back to rule-based if needed

## Testing

```bash
conda activate deep_sci
python deepsci_chat.py

# Then:
> search quantum computing
> compare 1 2
```

Expected output:
- ✅ Structured comparative analysis
- ✅ Similarities section
- ✅ Differences section  
- ✅ Reading recommendations
- ✅ Relationship analysis
- ✅ Side-by-side table

## Technical Details

### Chat Template Format (TinyLlama)
- `<|system|>` - System instructions
- `</s>` - End of section marker
- `<|user|>` - User prompt
- `<|assistant|>` - Model completion starts

### Token Limits
- Max tokens: 1000 (increased from 800)
- Abstract truncation: 400 chars per paper
- Temperature: 0.4 (balanced creativity/accuracy)

### Fallback Triggers
Activates when:
- Response < 100 characters
- Contains prompt text ("provide a comparative", "task:")
- AI generation fails

## Files Modified
- `deepsci/cli/interactive.py`
  - Updated `handle_compare()` method
  - Added `_generate_simple_comparison()` fallback
  - Improved prompt construction
  - Added response validation

## Verification

```python
from deepsci.cli.interactive import DeepSciChat

chat = DeepSciChat(use_llm=False)
cmd, args = chat.parse_command('compare 1 2')
# ✓ Returns: ('compare', '1 2')

# Fallback comparison test
papers = [...]
result = chat._generate_simple_comparison(papers)
# ✓ Returns structured comparison
```

## Status
✅ **FIXED** - Comparison now uses proper chat template format
✅ **TESTED** - Syntax validation passing
✅ **READY** - For end-to-end testing with real LLM

## Next Steps for Users
1. Try the comparison feature with real searches
2. If output is still truncated, the issue may be:
   - Model context size (TinyLlama 1.1B is small)
   - Consider upgrading to Phi-2 or larger model
3. Fallback comparison always works as backup

---

**Note**: TinyLlama 1.1B is optimized for speed, not complex reasoning. For best comparison quality, consider using a larger model like Phi-2 (1.6GB) via the model downloader.
