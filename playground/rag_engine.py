from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 1. Create a raw LangChain Document
raw_text = "Your long input text goes here..."

doc = Document(page_content=raw_text, metadata={"source": "my_file.txt"})

# 2. Split into chunks of ~500 characters
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents([doc])

# 3. Generate embeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")  # Or HuggingFaceEmbeddings for local

# 4. Store in a vector store (e.g., Chroma)
vectorstore = Chroma.from_documents(documents=chunks, embedding=embedding_model, persist_directory="./chroma_db")


def get_result(query: str) -> str:
    """Get the vector store instance."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(str)
    return results

if __name__ == "__main__":
    # Example usage
    query = "What is the role of mitochondria?"
    results = get_result(query)
    for doc in results:
        print(doc.page_content)
