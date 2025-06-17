import os
import re
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from logger import logger
from simple_term_menu import TerminalMenu

def choose_chunking_method():
    options = ["1. Segmentacija po rečenicama", "2. Segmentacija na osnovu '----------------'"]
    terminal_menu = TerminalMenu(options, title="Izaberite metod segmentacije:")
    menu_entry_index = terminal_menu.show()
    return menu_entry_index + 1

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west1-gcp")
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


def split_text_by_sentences(text, chunk_size=3):
    sentences = re.split(r'(?<!\d{4})(?<=[.!?])\s+', text)
    return [' '.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]


def split_text_by_delimiter(text, delimiter="----------------"):
    chunks = text.split(delimiter)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def get_embedding(text: str) -> list:
    try:
        embedding = EMBEDDING_MODEL.encode(text).tolist()
        logger.debug("Generated embedding successfully.")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def main():
    datafile = input("Unesite putanju do tekstualnog fajla: ")

    with open(datafile, "r", encoding="utf-8") as f:
        text_data = f.read()

    chunking_method = choose_chunking_method()

    if chunking_method == 1:
        chunks = split_text_by_sentences(text_data, CHUNK_SIZE)
    elif chunking_method == 2:
        chunks = split_text_by_delimiter(text_data)
    else:
        print("Nepoznat izbor. Izlaz iz programa.")
        return

    logger.info(f"Kreirano {len(chunks)} segmenata teksta.")

    vectors = []
    now = datetime.now().isoformat()
    for i, chunk in enumerate(chunks):
        try:
            embedding = get_embedding(chunk)
            vectors.append((str(i), embedding, {
                "text": chunk,
                "date_vectorised": now,
                "source": "file"
            }))
            logger.info(f"Generisan embedding za segment {i}.")
        except Exception as e:
            logger.error(f"Greška pri obradi segmenta {i}: {e}")
            continue

    if vectors:
        INDEX.upsert(vectors=vectors)
        logger.info(f"Upisano {len(vectors)} vektora u Pinecone indeks '{PINECONE_INDEX_NAME}'.")
    else:
        logger.warning("Nema vektora za upis.")


if __name__ == "__main__":
    main()
