import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["DO_NOT_TRACK"] = "1"
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from core.srv.embedding.embbeding_service import EmbeddingService

class Chroma_db:
    def __init__(self):
        #local chroma db
        load_dotenv()
        chromadb_path = os.getenv("CHROMADB_PATH")
        self.db = chromadb.PersistentClient(path=chromadb_path , settings=Settings(anonymized_telemetry=False))
        self.embedding_service = EmbeddingService(default_model="persian")
        self.default_batch_size = 16   # مناسب CPU

    def get_collections(self):
        return self.db.list_collections()
    # def get_or_create_collection(self ,collection_name:str , has_tokenizer:bool = False):
    #     if has_tokenizer:
    #         return self.db.get_or_create_collection(name=collection_name,metadata={"hnsw:space": "cosine"})
    #     else:
    #         return self.db.get_or_create_collection(
    #             name=collection_name,
    #             embedding_function= EmbeddingService(default_model="persian"),
    #             metadata={"hnsw:space": "cosine"}
    #             )
    def get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """همیشه embedding_function را پاس می‌دهیم"""
        return self.db.get_or_create_collection(
            name=collection_name,
            embedding_function=None,           # ما خودمان مدیریت می‌کنیم
            metadata={"hnsw:space": "cosine"}
            )
    def get_collection(self ,collection_name:str):
        return self.db.get_collection(name=collection_name)
    
    def add_documents(self,collection_name: str,docs:list , metadatas:list, ids:list,batch_size: Optional[int] = None):
        """اضافه کردن چانک‌ها به Chroma"""

        id_prefix = collection_name

        # استفاده از متد جدید

        collection = self.get_or_create_collection(collection_name)
        batch_size = batch_size or self.default_batch_size

        # تولید امبدینگ بچ
        embeddings = self.embedding_service.get_embeddings(
            texts=docs,
            model_name="tookasbert",
            batch_size=batch_size
        ).tolist()

        collection.add(
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )        
    def get_collection_data(self ,collection_name:str):
        return self.db.get_or_create_collection(collection_name).get()
    def delete_collection(self ,collection_name:str):
        return self.db.delete_collection(collection_name)
    # def chunks_to_docs(self ,chunks , id_prefix:str):
        
    #   documents = []
    #   ids = []
    
    #   for idx, chunk in enumerate(chunks):
    #       documents.append(chunk)
    #       ids.append(f"{id_prefix}{idx}")
    
    #   return documents , ids

    def chunks_to_docs(self ,chunks , id_prefix:str):
        
      documents = []
      ids = []
    
      for idx, chunk in enumerate(chunks):
          documents.append(chunk)
          ids.append(f"{id_prefix}{idx}")
    
      return documents , ids

    def retrieve(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        distance_threshold: Optional[float] = None
    ) -> List[Dict]:
        """متد اصلی جستجو (Retrieval)"""
        collection = self.get_or_create_collection(collection_name)

        # امبدینگ query
        query_embedding = self.embedding_service.get_embedding(query,"tookasbert").tolist()

        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # تبدیل به فرمت خوانا
        data = []
        for i in range(len(result["ids"][0])):
            distance = result["distances"][0][i]
            
            if distance_threshold is None or distance <= distance_threshold:
                data.append({
                    "id": result["ids"][0][i],
                    "document": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "distance": float(distance),
                    "similarity": 1 - float(distance)   # اگر cosine distance باشد
                })

        return data    
    
    def delete_file(self ,assistant_id:str , doc_id:str):
        try:
            collection = self.get_collection(assistant_id)
            collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(e)

    def get_chat_collection_name(self ,assistant_id:str)-> str:
        collection_name = f"{assistant_id}_chat"
        return collection_name
    def delete_all_collections(self):
        collections = self.get_collections()
        for collection in collections:
            self.delete_collection(collection.name)
    def count_documents(self, collection_name: str) -> int:
        try:
            collection = self.get_collection(collection_name)
            return collection.count()
        except:
            return 0