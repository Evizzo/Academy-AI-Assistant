import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import deque
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from logger import logger

load_dotenv()

PINECONE_API_KEY    = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL_NAME= "paraphrase-multilingual-MiniLM-L12-v2"
INDEX_DIMENSION     = 384
CRAWL_DELAY_SEC     = 1
INDEX             = None
EMBEDDING_MODEL   = SentenceTransformer(EMBEDDING_MODEL_NAME)


def initialize_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=INDEX_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-west-2")
        )
    return pc.Index(PINECONE_INDEX_NAME)


def cyrillic_to_latin(text: str) -> str:
    table = str.maketrans({
        'А':'A','а':'a','Б':'B','б':'b','В':'V','в':'v','Г':'G','г':'g',
        'Д':'D','д':'d','Ђ':'Đ','ђ':'đ','Е':'E','е':'e','Ж':'Ž','ж':'ž',
        'З':'Z','з':'z','И':'I','и':'i','Ј':'J','ј':'j','К':'K','к':'k',
        'Л':'L','л':'l','Љ':'Lj','љ':'lj','М':'M','м':'m','Н':'N','н':'n',
        'Њ':'Nj','њ':'nj','О':'O','о':'o','П':'P','п':'p','Р':'R','р':'r',
        'С':'S','с':'s','Т':'T','т':'t','Ћ':'Ć','ћ':'ć','У':'U','у':'u',
        'Ф':'F','ф':'f','Х':'H','х':'h','Ц':'C','ц':'c','Ч':'Č','ч':'č',
        'Џ':'Dž','џ':'dž','Ш':'Š','ш':'š'
    })
    return text.translate(table)


def extract_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()
    found = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        p = urlparse(href)
        if p.netloc == urlparse(base_url).netloc:
            found.add(f"{p.scheme}://{p.netloc}{p.path}")
    return found

def scrape_and_clean(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()
    raw = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    combined = "\n".join(lines)
    return cyrillic_to_latin(combined)


def crawl_site(start_url: str) -> str:
    visited = set()
    queue   = deque([start_url])
    texts   = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            logger.info(f"Fetching {url}")
            resp = requests.get(url, timeout=10)
            html = resp.text

            texts.append(scrape_and_clean(html))

            for link in extract_links(html, start_url):
                if link not in visited:
                    queue.append(link)

            time.sleep(CRAWL_DELAY_SEC)
        except Exception as e:
            logger.warning(f"Skipping {url}: {e}")

    return "\n".join(texts)


def chunk_text_with_langchain(text: str, chunk_size=500, chunk_overlap=50) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def get_embedding(text: str) -> list[float]:
    return EMBEDDING_MODEL.encode(text).tolist()


def main():
    global INDEX
    INDEX = initialize_pinecone()

    start_url = "https://ar.asss.edu.rs/"
    full_text = crawl_site(start_url)
    chunks    = chunk_text_with_langchain(full_text)

    logger.info(f"Generated {len(chunks)} chunks.")

    now     = datetime.utcnow().isoformat()
    vectors = []
    for i, chunk in enumerate(chunks):
        try:
            emb = get_embedding(chunk)
            vectors.append((str(i), emb, {"text": chunk, "date_vectorised": now}))
        except Exception as e:
            logger.error(f"Error embedding chunk {i}: {e}")

    if vectors:
        INDEX.upsert(vectors=vectors)
        logger.info(f"Uploaded {len(vectors)} vectors to Pinecone index '{PINECONE_INDEX_NAME}'.")
    else:
        logger.warning("No vectors to upload.")

if __name__ == "__main__":
    main()
