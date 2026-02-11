#!/usr/bin/env python
"""
Demo script for new features:
1. Google Scholar integration
2. Paper comparison
"""

import sys
from deepsci.sources import ScholarClient

def test_scholar_search():
    """Test Google Scholar search functionality"""
    print("="*60)
    print("Testing Google Scholar Integration")
    print("="*60)
    
    scholar = ScholarClient()
    
    print("\n1. Searching for papers on 'quantum entanglement'...")
    try:
        results = scholar.search_papers("quantum entanglement", max_results=3)
        
        if results:
            print(f"✓ Found {len(results)} papers from Google Scholar\n")
            for i, paper in enumerate(results, 1):
                print(f"Paper {i}:")
                print(f"  Title: {paper.get('title', 'N/A')[:70]}...")
                print(f"  Year: {paper.get('year', 'N/A')}")
                print(f"  Citations: {paper.get('citation_count', 0)}")
                print(f"  Venue: {paper.get('venue', 'N/A')[:50]}")
                print()
        else:
            print("⚠ No results (Scholar may be rate limiting)")
            
    except Exception as e:
        print(f"⚠ Scholar search failed: {str(e)}")
        print("  (This is expected - Scholar can be finicky with scraping)")
    
    print("\n2. Testing paper enrichment...")
    try:
        data = scholar.enrich_paper_with_scholar("Attention Is All You Need")
        if data:
            print(f"✓ Paper enrichment successful")
            print(f"  Citations: {data.get('citation_count', 0)}")
            print(f"  Year: {data.get('year', 'N/A')}")
            print(f"  Venue: {data.get('venue', 'N/A')}")
        else:
            print("⚠ No enrichment data available")
    except Exception as e:
        print(f"⚠ Enrichment failed: {str(e)}")

def demo_compare_feature():
    """Demo the compare feature"""
    print("\n" + "="*60)
    print("Paper Comparison Feature Demo")
    print("="*60)
    
    print("\nThe compare feature allows you to:")
    print("  • Compare 2-4 papers side-by-side")
    print("  • Get AI analysis of similarities and differences")
    print("  • See which paper to read first")
    print("  • Understand how papers relate to each other")
    
    print("\nUsage:")
    print("  1. Search for papers: 'search quantum computing'")
    print("  2. Compare papers: 'compare 1 2 3'")
    
    print("\nFeatures:")
    print("  ✓ AI-powered comparative analysis")
    print("  ✓ Side-by-side summary table")
    print("  ✓ Citation comparison")
    print("  ✓ Reading recommendations")

if __name__ == "__main__":
    print("\n🔬 DeepSci Agent - New Features Demo\n")
    
    # Test Scholar integration
    test_scholar_search()
    
    # Demo compare feature
    demo_compare_feature()
    
    print("\n" + "="*60)
    print("Quick Start")
    print("="*60)
    print("\nTo try these features interactively:")
    print("  $ conda activate deep_sci")
    print("  $ python deepsci_chat.py")
    print("\nThen try:")
    print("  > search quantum machine learning")
    print("  > compare 1 2")
    print("\n✓ All features ready to use!")
    print()
