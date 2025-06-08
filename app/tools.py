from app.config import settings
from langchain_chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from app.logger import AppLogger

logger = AppLogger.get_logger("tools", json_logs=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def restricted_site_retrieval(query: str) -> str:
    db = Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_db_path
    )
    #docs = db.similarity_search(query, k=4)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    logger.info(f"🔍 Retrieved {docs} documents for query: {query}"    )
    return "\n\n".join([doc.page_content for doc in docs])
