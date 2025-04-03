import os
import re
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from logger import logger

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
TOP_K = int(os.getenv("TOP_K", "15"))
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west1-gcp")
DATA_FILE = "dataToVectorise/data.txt"
CHUNK_SIZE = 3
INDEX_DIMENSION = 384


def initialize_pinecone():
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=INDEX_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-west-2")
            )
        return pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pinecone: {e}")


INDEX = initialize_pinecone()
EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)


def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    sentences = re.split(r'(?<!\d{4})(?<=[.!?])\s+', text)
    logger.debug(f"Split text into {len(sentences)} sentences.")
    return [' '.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]


def get_embedding(text: str) -> list:
    try:
        embedding = EMBEDDING_MODEL.encode(text).tolist()
        logger.debug("Generated embedding successfully.")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        text_data = f.read()
    chunks = split_text(text_data, CHUNK_SIZE)
    logger.info(f"Created {len(chunks)} text chunks.")

    vectors = []
    now = datetime.now().isoformat()
    for i, chunk in enumerate(chunks):
        try:
            embedding = get_embedding(chunk)
            vectors.append((str(i), embedding, {"text": chunk, "date_vectorised": now}))
            logger.info(f"Generated embedding for chunk {i}.")
        except Exception as e:
            logger.error(f"Error for chunk {i}: {e}")
            continue

    if vectors:
        INDEX.upsert(vectors=vectors)
        logger.info(f"Upserted {len(vectors)} vectors into Pinecone index '{PINECONE_INDEX_NAME}'.")
    else:
        logger.warning("No vectors to upsert.")


if __name__ == "__main__":
    main()
