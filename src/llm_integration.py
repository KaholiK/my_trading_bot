# File: src/llm_integration.py
# Part 5: LLM Integration & News/Sentiment Processing
#
# This module integrates a large language model (LLM) and a vector database for retrieval-augmented generation.
# We'll set up a pipeline that:
# 1. Ingests news headlines, earnings reports, etc.
# 2. Embeds them into a vector space.
# 3. Uses a local LLM to process queries and produce sentiment or fundamental insights.

import os
from typing import List, Dict, Any
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorDB:
    """
    A simple in-memory vector database that stores embeddings and associated texts.
    In future parts, we might switch to a more scalable solution (like FAISS).
    """
    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self.vectors = []   # list of np.ndarray
        self.texts = []     # list of strings

    def add_document(self, text: str, embedding: np.ndarray):
        self.vectors.append(embedding)
        self.texts.append(text)

    def query(self, query_emb: np.ndarray, top_k: int = 3) -> List[str]:
        if len(self.vectors) == 0:
            return []
        all_vecs = np.vstack(self.vectors)  # shape: (N, embedding_dim)
        sims = cosine_similarity(query_emb.reshape(1, -1), all_vecs).flatten()
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [self.texts[i] for i in top_indices]

class LLMInterface:
    """
    Wraps a local LLM model for inference. For now, assume a small model (e.g., GPT-2) to demonstrate functionality.
    In the future, we might load a large fine-tuned financial model.
    """
    def __init__(self, model_name: str = "gpt2"):
        # In a real scenario, use a specialized financial model or Llama2-like model.
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        if torch.cuda.is_available():
            self.model.to('cuda')
    
    def generate(self, prompt: str, max_length: int = 100) -> str:
        inputs = self.tokenizer.encode(prompt, return_tensors='pt')
        if torch.cuda.is_available():
            inputs = inputs.to('cuda')
        with torch.no_grad():
            outputs = self.model.generate(inputs, max_length=max_length, pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

class EmbeddingModel:
    """
    Simple embedding model placeholder.
    In future parts, we may integrate a sentence-transformer or a specialized financial embedding model.
    """
    def __init__(self):
        # Placeholder: random embeddings for now
        # Eventually, integrate something like sentence-transformers or a finetuned BERT model.
        pass
    
    def embed(self, text: str) -> np.ndarray:
        # Placeholder: return a fixed-size random vector. 
        # Future: Load a real embedding model.
        np.random.seed(abs(hash(text)) % (10**6))
        return np.random.randn(768)

class NewsSentimentPipeline:
    """
    Pipeline to ingest news, generate embeddings, store in vector DB, and use LLM to interpret.
    We'll integrate this pipeline with the main system later.
    """
    def __init__(self):
        self.embed_model = EmbeddingModel()
        self.vector_db = SimpleVectorDB()
        self.llm = LLMInterface(model_name="gpt2")
    
    def add_news_article(self, headline: str, body: str):
        # For now, just add headline+body as a single doc
        text = headline + "\n" + body
        emb = self.embed_model.embed(text)
        self.vector_db.add_document(text, emb)
    
    def query_insights(self, query: str) -> str:
        # Embed query
        q_emb = self.embed_model.embed(query)
        relevant_docs = self.vector_db.query(q_emb, top_k=3)
        # Construct a prompt with the retrieved docs
        prompt = "Given the following financial news context:\n"
        for doc in relevant_docs:
            prompt += f"- {doc}\n"
        prompt += f"\nQuestion: {query}\nAnswer:"
        response = self.llm.generate(prompt, max_length=150)
        return response

if __name__ == "__main__":
    # Example usage
    pipeline = NewsSentimentPipeline()
    pipeline.add_news_article("Apple Earnings Beat Expectations",
                              "Apple reported Q3 earnings that beat analysts' expectations by a wide margin.")
    pipeline.add_news_article("Tesla Faces Regulatory Scrutiny",
                              "Tesla is under investigation by safety regulators after several incidents...")
    
    answer = pipeline.query_insights("What is the sentiment on Apple stock?")
    print("LLM Response:", answer)
