from langchain_chroma import Chroma
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
import chromadb

logger = AppLogger.get_logger("crawler", json_logs=False)

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
    logger.info(f"Domain extracted: {domain}")
    if not domain:
        logger.error("Invalid URL or domain extraction failed.")
        return []
    # Initialize an empty list to store the contents
    contents = []

    async with aiohttp.ClientSession() as session:
        logger.info(f"Links: {to_visit}")
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            logger.info(f"🔍 Crawling: {url}")
            text = await fetch(session, url)
            logger.info(f"Fetched {len(text) if text else 0 } characters from {url}")
            if text:
                contents.append(Document(page_content=text, metadata={"source": url}))

                #logger.info(f"Parsing HTML content: {contents}")
                soup = BeautifulSoup(text, 'html.parser')
                logger.info(f"Found {len(soup.find_all('a', href=True))} links on {url}")
                # Find all links on the page
                for a in soup.find_all("a", href=True):
                    full_url = urljoin(url, a["href"])
                    ext = tldextract.extract(full_url)
                    if ext.registered_domain == domain and full_url not in visited:
                        to_visit.append(full_url)
    logger.info("✅ Crawl job completed.")
    return contents

async def embed_site(url: str, db_path="chroma_db"):
    logger.info(f"Embedding site: {url}")
    raw_docs = await crawl_site(url)
    #logger.info(raw_docs)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(raw_docs)
    #logger.info(f"docs: {docs}")
    db = get_chroma_db(db_path)
    db.add_documents(docs)
    logger.info(f"✅ Chroma collection created with {db._collection.count()} documents")
