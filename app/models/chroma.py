from app.config import settings
import chromadb
from langchain_chroma import Chroma
from chromadb.api.models.Collection import Collection
from langchain.embeddings import OpenAIEmbeddings

CHROMA_PATH = "chroma_db"  # or use an env var / config
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection(name: str) -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)

def get_chroma_db(persist_dir=CHROMA_PATH):
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
