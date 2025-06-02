from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.logger import AppLogger

logger = AppLogger.get_logger("tools", json_logs=True)

embeddings = OpenAIEmbeddings()

def restricted_site_retrieval(query: str, db_path="chroma_db"):
    db = Chroma(
        collection_name="site_content",
        embedding_function=embeddings,
        persist_directory=db_path
    )
    docs = db.similarity_search(query, k=3)
    logger.info(f"🔍 Retrieved {len(docs)} documents for query: {query}"    )
    return "\n\n".join([doc.page_content for doc in docs])
