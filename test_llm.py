#!/usr/bin/env python3
"""
Test script for local LLM functionality
"""

import sys
sys.path.insert(0, '/home/davas/Documents/deep_sci')

from deepsci.llm.local_llm import LocalLLM
from rich.console import Console

console = Console()

def test_llm():
    """Test the local LLM"""
    
    # Example paper
    title = "Quantum Entanglement in Black Holes"
    abstract = """
    We investigate quantum entanglement properties in the context of black hole physics.
    Our analysis reveals that the entanglement entropy follows a specific scaling law
    with the black hole horizon area. We derive analytical solutions for the entanglement
    structure and show how it relates to the information paradox. The results suggest
    that quantum information is preserved through a novel mechanism involving
    entanglement transfer at the event horizon.
    """
    
    console.print("\n[bold cyan]Testing Local LLM...[/bold cyan]\n")
    console.print(f"[yellow]Title:[/yellow] {title}")
    console.print(f"[yellow]Abstract:[/yellow] {abstract[:100]}...\n")
    
    # Initialize LLM
    llm = LocalLLM()
    
    # Test summarization
    console.print("[bold green]Generating Summary...[/bold green]")
    summary = llm.summarize_abstract(title, abstract)
    console.print(f"\n{summary}\n")
    
    # Test key points extraction
    console.print("[bold green]Extracting Key Points...[/bold green]")
    key_points = llm.extract_key_points(title, abstract)
    console.print(f"\n{key_points}\n")
    
    # Test Q&A
    console.print("[bold green]Answering Question...[/bold green]")
    question = "What is the main finding about information preservation?"
    answer = llm.answer_question(question, abstract)
    console.print(f"\nQ: {question}")
    console.print(f"A: {answer}\n")
    
    console.print("[bold green]✓ All tests completed![/bold green]")

if __name__ == "__main__":
    test_llm()
