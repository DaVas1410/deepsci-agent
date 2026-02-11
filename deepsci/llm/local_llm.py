"""
Local LLM integration using llama.cpp
Supports TinyLlama and other GGUF models
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import requests
from llama_cpp import Llama
from rich.console import Console
from tqdm import tqdm

console = Console()


class ModelDownloader:
    """Download and manage LLM models"""
    
    # Available models with their download URLs
    MODELS = {
        "tinyllama-1.1b": {
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "size": "669MB",
            "description": "TinyLlama 1.1B - Fast and lightweight"
        },
        "phi-2": {
            "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
            "filename": "phi-2.Q4_K_M.gguf",
            "size": "1.6GB",
            "description": "Microsoft Phi-2 - Better quality, still fast"
        }
    }
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def download_model(self, model_name: str = "tinyllama-1.1b") -> Path:
        """
        Download a model if it doesn't exist
        
        Args:
            model_name: Name of the model to download
            
        Returns:
            Path to the downloaded model file
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(self.MODELS.keys())}")
        
        model_info = self.MODELS[model_name]
        model_path = self.models_dir / model_info["filename"]
        
        # Check if already downloaded
        if model_path.exists():
            console.print(f"[green]✓[/green] Model already downloaded: {model_path}")
            return model_path
        
        # Download the model
        console.print(f"[cyan]Downloading {model_name} ({model_info['size']})...[/cyan]")
        console.print(f"[dim]This may take a few minutes...[/dim]")
        
        try:
            response = requests.get(model_info["url"], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=model_info["filename"]) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            console.print(f"[green]✓[/green] Model downloaded successfully: {model_path}")
            return model_path
            
        except Exception as e:
            if model_path.exists():
                model_path.unlink()
            raise Exception(f"Failed to download model: {str(e)}")
    
    def list_models(self):
        """List available models"""
        console.print("\n[bold cyan]Available Models:[/bold cyan]\n")
        for name, info in self.MODELS.items():
            status = "✓ Downloaded" if (self.models_dir / info["filename"]).exists() else "Not downloaded"
            console.print(f"  • [bold]{name}[/bold] - {info['description']}")
            console.print(f"    Size: {info['size']} | Status: {status}\n")


class LocalLLM:
    """Local LLM for research paper analysis"""
    
    def __init__(self, model_path: Optional[str] = None, n_ctx: int = 2048, n_gpu_layers: int = 0):
        """
        Initialize the local LLM
        
        Args:
            model_path: Path to GGUF model file. If None, will auto-download TinyLlama
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU (0 = CPU only)
        """
        self.downloader = ModelDownloader()
        
        # Auto-download if no model specified
        if model_path is None:
            console.print("[yellow]No model specified. Using TinyLlama 1.1B...[/yellow]")
            model_path = str(self.downloader.download_model("tinyllama-1.1b"))
        
        console.print(f"[cyan]Loading model: {model_path}[/cyan]")
        
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        
        console.print("[green]✓[/green] Model loaded successfully!")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[list] = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            top_p: Nucleus sampling parameter
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        if stop is None:
            stop = ["</s>", "User:", "Human:"]
        
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            echo=False
        )
        
        return response['choices'][0]['text'].strip()
    
    def summarize_abstract(self, title: str, abstract: str, max_tokens: int = 256) -> str:
        """
        Generate a concise summary of a paper abstract
        
        Args:
            title: Paper title
            abstract: Paper abstract
            max_tokens: Maximum tokens for summary
            
        Returns:
            Summary text
        """
        prompt = f"""<|system|>
You are a helpful research assistant. Provide concise, accurate summaries of scientific papers.
</s>
<|user|>
Summarize this physics paper in 3-4 sentences. Focus on the main contribution and findings.

Title: {title}

Abstract: {abstract}

Provide a clear summary:
</s>
<|assistant|>
"""
        
        return self.generate(prompt, max_tokens=max_tokens, temperature=0.3)
    
    def extract_key_points(self, title: str, abstract: str, max_tokens: int = 256) -> str:
        """
        Extract key points from a paper
        
        Args:
            title: Paper title
            abstract: Paper abstract
            max_tokens: Maximum tokens
            
        Returns:
            Key points as text
        """
        prompt = f"""<|system|>
You are a research assistant. Extract the key findings from scientific papers.
</s>
<|user|>
Extract 3-5 key points from this paper:

Title: {title}

Abstract: {abstract}

List the key points:
</s>
<|assistant|>
"""
        
        return self.generate(prompt, max_tokens=max_tokens, temperature=0.3)
    
    def answer_question(self, question: str, context: str, max_tokens: int = 256) -> str:
        """
        Answer a question based on paper context
        
        Args:
            question: User's question
            context: Paper content or abstract
            max_tokens: Maximum tokens
            
        Returns:
            Answer text
        """
        prompt = f"""<|system|>
You are a helpful research assistant. Answer questions based on the provided context.
</s>
<|user|>
Context: {context}

Question: {question}

Answer:
</s>
<|assistant|>
"""
        
        return self.generate(prompt, max_tokens=max_tokens, temperature=0.5)
