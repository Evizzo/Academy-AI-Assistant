import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from logger import logger
import torch
if hasattr(torch.classes, '__path__'):
    torch.classes.__path__ = []
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
TOP_K = int(os.getenv("TOP_K", "15"))
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west1-gcp")

def initialize_pinecone():
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            raise ValueError(f"Pinecone index '{PINECONE_INDEX_NAME}' does not exist.")
        return pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pinecone: {e}")

INDEX = initialize_pinecone()
EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)

def search_context(query: str) -> str:
    query_embedding = EMBEDDING_MODEL.encode(query).tolist()
    result = INDEX.query(vector=query_embedding, top_k=TOP_K, include_metadata=True)
    contexts = []
    for match in result.get("matches", []):
        metadata = match.get("metadata", {})
        text = metadata.get("text", "")
        if text:
            contexts.append(text)
    combined_context = "\n".join(contexts)
    logger.info(f"Found {len(contexts)} context chunks.")
    return combined_context
