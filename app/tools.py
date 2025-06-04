from app.config import Settings
from langchain_chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from app.logger import AppLogger

logger = AppLogger.get_logger("tools", json_logs=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def restricted_site_retrieval(query: str) -> str:
    #vector = embeddings.embed_documents("Your text here")
    #vectorstore = Chroma.from_documents(docs, embeddings)
    db = Chroma(
        collection_name=Settings.collection_name,
        embedding_function=embeddings,
        persist_directory=Settings.chroma_db_path
    )
    docs = db.similarity_search(query, k=3)
    logger.info(f"🔍 Retrieved {len(docs)} documents for query: {query}"    )
    return "\n\n".join([doc.page_content for doc in docs])
