# import os

# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from app.config.settings import settings
# from dotenv import load_dotenv

# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
# load_dotenv()
# chromadb_path = os.getenv("CHROMADB_PATH")
# vectorstore = Chroma(
#     persist_directory=chromadb_path,
#     embedding_function=embeddings,
#     collection_name="business_docs"
# )

# retriever = vectorstore.as_retriever(
#     search_kwargs={"k": 6}
# )

# def get_retriever():
#     return retriever