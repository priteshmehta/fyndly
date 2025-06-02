import chromadb
from chromadb.api.models.Collection import Collection

CHROMA_PATH = "chroma_db"  # or use an env var / config

def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection(name: str = "site_content") -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)

# def get_chroma_db(persist_dir="chroma_db"):
#     return Chroma(
#         collection_name="site_content",
#         embedding_function=embeddings,
#         persist_directory=persist_dir
#     )
