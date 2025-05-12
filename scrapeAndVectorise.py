import os
import time
import re
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
CRAWL_DELAY_SEC     = 1    # politeness delay
MAX_PAGES           = 30  # stop after this many pages
MAX_DEPTH           = 2    # max link-hops from start

IMAGE_EXTENSIONS    = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico', '.tif', '.tiff'}
DOC_EXTENSIONS      = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}

INDEX               = None
EMBEDDING_MODEL     = SentenceTransformer(EMBEDDING_MODEL_NAME)


def initializePinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=INDEX_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-west-2")
        )
    return pc.Index(PINECONE_INDEX_NAME)


def cyrillicToLatin(text: str) -> str:
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


def extractLinks(html: str, baseUrl: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()
    found = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(baseUrl, a["href"])
        p = urlparse(href)
        ext = os.path.splitext(p.path)[1].lower()
        if p.netloc == urlparse(baseUrl).netloc and ext not in IMAGE_EXTENSIONS|DOC_EXTENSIONS:
            found.add(f"{p.scheme}://{p.netloc}{p.path}")
    return found


def scrapeAndClean(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()
    raw = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    combined = "\n".join(lines)
    latin = cyrillicToLatin(combined)
    return cleanText(latin)


def cleanText(text: str) -> str:
    t = re.sub(r"\s+", " ", text)
    t = t.replace("—", "-").replace("“", '"').replace("”", '"')
    t = t.lower()
    t = re.sub(r"(home|kontakt|footer).{0,100}", "", t)
    return t


def crawlSite(startUrl: str) -> str:
    visited = set()
    queue   = deque([(startUrl, 0)])
    texts   = []
    pages   = 0

    while queue and pages < MAX_PAGES:
        url, depth = queue.popleft()
        if url in visited or depth>MAX_DEPTH:
            continue
        visited.add(url)
        pages += 1

        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in IMAGE_EXTENSIONS|DOC_EXTENSIONS:
            continue

        try:
            logger.info(f"Fetching {url}")
            resp = requests.get(url, timeout=10)
            html = resp.text

            texts.append(scrapeAndClean(html))

            if depth < MAX_DEPTH:
                for link in extractLinks(html, startUrl):
                    if link not in visited:
                        queue.append((link, depth+1))

            time.sleep(CRAWL_DELAY_SEC)
        except Exception as e:
            logger.warning(f"Skipping {url}: {e}")

    return "\n".join(texts)


def chunkTextWithLangchain(text: str, chunkSize=500, chunkOverlap=50) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunkSize, chunk_overlap=chunkOverlap)
    return splitter.split_text(text)


def getEmbedding(text: str) -> list[float]:
    return EMBEDDING_MODEL.encode(text).tolist()


def main():
    global INDEX
    INDEX = initializePinecone()

    startUrl = "https://ar.asss.edu.rs/"
    fullText = crawlSite(startUrl)
    chunks   = chunkTextWithLangchain(fullText)

    logger.info(f"Generated {len(chunks)} chunks.")

    now     = datetime.utcnow().isoformat()
    vectors = []
    for i, chunk in enumerate(chunks):
        try:
            emb = getEmbedding(chunk)
            metadata = {
                "text": chunk,
                "date_vectorised": now,
                "source": "scraping"
            }
            vectors.append((str(i), emb, metadata))
        except Exception as e:
            logger.error(f"Error embedding chunk {i}: {e}")

    if vectors:
        INDEX.upsert(vectors=vectors)
        logger.info(f"Uploaded {len(vectors)} vectors to Pinecone index '{PINECONE_INDEX_NAME}'.")
    else:
        logger.warning("No vectors to upload.")

if __name__ == "__main__":
    main()
