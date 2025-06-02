from langchain.vectorstores import Chroma
import chromadb
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tldextract
from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from app.logger import AppLogger

logger = AppLogger.get_logger("crawler")

embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

def get_chroma_db(persist_dir="chroma_db"):
    return Chroma(
        collection_name="site_content",
        embedding_function=embeddings,
        persist_directory=persist_dir
    )

async def fetch(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text(separator=" ", strip=True)
    except:
        return None

async def crawl_site(start_url: str, max_pages=100):
    logger.info("🕸️ Starting crawl job...")
    visited = set()
    to_visit = [start_url]
    domain = tldextract.extract(start_url).registered_domain
    contents = []

    async with aiohttp.ClientSession() as session:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            text = await fetch(session, url)
            logger.info(f"✅ Successfully stored: {url}")
            if text:
                contents.append(Document(page_content=text, metadata={"source": url}))

                soup = BeautifulSoup(text, 'html.parser')
                for a in soup.find_all("a", href=True):
                    full_url = urljoin(url, a["href"])
                    ext = tldextract.extract(full_url)
                    if ext.registered_domain == domain and full_url not in visited:
                        to_visit.append(full_url)
    logger.info("✅ Crawl job completed.")
    
    return contents

async def embed_site(url: str, db_path="chroma_db"):
    print(f"Embedding site: {url}")
    raw_docs = await crawl_site(url)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(raw_docs)

    db = get_chroma_db(db_path)
    db.add_documents(docs)
    db.persist()
