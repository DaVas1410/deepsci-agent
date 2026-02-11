#!/usr/bin/env python
"""Quick test for compare functionality"""

from deepsci.sources import ArxivClient, Paper
from datetime import datetime

# Create mock papers for testing
papers = [
    Paper(
        id="2301.12345",
        title="Quantum Computing for Machine Learning",
        authors=["Alice Smith", "Bob Jones"],
        abstract="This paper explores the intersection of quantum computing and machine learning...",
        published=datetime(2023, 1, 15),
        updated=datetime(2023, 1, 15),
        url="https://arxiv.org/abs/2301.12345",
        pdf_url="https://arxiv.org/pdf/2301.12345",
        categories=["quant-ph", "cs.LG"],
        citation_count=45
    ),
    Paper(
        id="2302.54321",
        title="Neural Networks on Quantum Hardware",
        authors=["Carol White", "David Brown"],
        abstract="We present a novel approach to implementing neural networks on quantum hardware...",
        published=datetime(2023, 2, 20),
        updated=datetime(2023, 2, 20),
        url="https://arxiv.org/abs/2302.54321",
        pdf_url="https://arxiv.org/pdf/2302.54321",
        categories=["quant-ph", "cs.NE"],
        citation_count=28
    )
]

print("✓ Mock papers created")
print(f"  Paper 1: {papers[0].title}")
print(f"  Paper 2: {papers[1].title}")
print("\nCompare command test ready!")
print("Usage: python deepsci_chat.py")
print("Then: search quantum computing")
print("Then: compare 1 2")
