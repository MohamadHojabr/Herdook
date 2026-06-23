# from functools import lru_cache
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# class EmbeddingService:
#     @lru_cache(maxsize=1000)
#     def load_model(self, model_name: str):
#         # Load the embedding model based on the model name
#         if model_name == "bert":
#             from transformers import BertModel, BertTokenizer
#             tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
#             model = BertModel.from_pretrained("bert-base-uncased")
#             return tokenizer, model
#         elif model_name == "gpt":
#             from transformers import GPT2Tokenizer, GPT2Model
#             tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
#             model = GPT2Model.from_pretrained("gpt2")
#             return tokenizer, model
#         elif model_name == "local":
#             save_directory = "./local_models/persian_bert"
#             from transformers import AutoTokenizer, AutoModel
#             tokenizer = AutoTokenizer.from_pretrained(save_directory)
#             model = AutoModel.from_pretrained(save_directory)
#             return tokenizer, model
#         else:
#             raise ValueError(f"Model {model_name} not supported")
        
#     def get_embedding(self,text):
#         tokenizer , model = self.load_model("local")
#         inputs = tokenizer(text, return_tensors="pt")
#         outputs = model(**inputs)
#         embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
#         return embedding.squeeze()
#     def cosine_similarity_score(self,embedding1, embedding2):
#         """Calculate the cosine distance between two embeddings."""
#         similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))

#         return similarity[0][0]

#     def sentence_distance(self ,sentence1, sentence2):
#         """Calculate the distance between two sentences."""
#         emb1 = self.get_embedding(sentence1)
#         emb2 = self.get_embedding(sentence2)
#         distance = self.cosine_similarity_score(emb1, emb2)
#         return distance


from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional


class EmbeddingService:
    def __init__(self, default_model: str = "persian"):
        self.default_model = default_model
        self._models = {}
        self._device = "cpu"
        
        # تنظیمات بهینه برای CPU
        self._batch_size = 16          # برای CPU مناسب است
        self._warmup_done = False

    @lru_cache(maxsize=6)
    def get_model(self, model_name: str) -> SentenceTransformer:
        if model_name in self._models:
            return self._models[model_name]

        if model_name in ["persian", "local"]:
            model_path = "local_models/persian_bert"   # مسیر خودت
            model = SentenceTransformer(model_path, device="cpu")
            
        # مدل‌های پیشنهادی قوی‌تر برای فارسی (دقت بالاتر)
        elif model_name == "persian_v2":
            model = SentenceTransformer("heydariAI/persian-embeddings", device="cpu")
            
        elif model_name == "tookasbert":
            #model = SentenceTransformer("app/local_models/Tooka-SBERT-V2-Small", device="cpu")
            model = SentenceTransformer("local_models/Tooka-SBERT-V2-Small", device="cpu")
            
        else:
            raise ValueError(f"Model {model_name} not supported")

        self._models[model_name] = model
        return model

    def get_embedding(self, text: str, model_name: Optional[str] = None) -> np.ndarray:
        """امبدینگ تک متن (برای تست و موارد کم)"""
        try:
             # اگر متن خالی یا فقط فاصله بود، امبدینگ صفر برگردان
            if not text or not text.strip():
                dim = self.get_model_dimension(model_name or self.default_model)
                return np.zeros(dim, dtype=np.float32)
            if not text or not text.strip():
                dim = self.get_model_dimension(model_name or self.default_model)
                return np.zeros(dim, dtype=np.float32)

            model_name = model_name or self.default_model
            model = self.get_model(model_name)

            embedding = model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"Error in get_embedding: {e}")
    def get_embeddings(
        self, 
        texts: List[str], 
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None
    ) -> np.ndarray:
        """متد اصلی دریافت امبدینگ"""
        try:
            if not texts:
                return np.array([])

            model_name = model_name or self.default_model
            model = self.get_model(model_name)
            batch_size = batch_size or self._batch_size

            # اطمینان از اینکه batch_size عدد است
            if isinstance(batch_size, list):
                batch_size = 16

            # پاک‌سازی متن‌ها
            valid_texts = []
            for t in texts:
                if isinstance(t, str):
                    stripped = t.strip()
                    if stripped:
                        valid_texts.append(stripped)
                else:
                    stripped = str(t).strip()
                    if stripped:
                        valid_texts.append(stripped)

            if not valid_texts:
                dim = self.get_model_dimension(model_name)
                # اطمینان از اینکه dim عدد است
                if not isinstance(dim, int):
                    dim = 768  # fallback
                return np.zeros((len(texts), dim), dtype=np.float32)

            embeddings = model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            return embeddings.astype(np.float32)

        except Exception as e:
            print(f"❌ Error in get_embeddings: {e}")
            import traceback
            traceback.print_exc()   # برای دیدن stack کامل
            
            # برگرداندن آرایه خالی به جای None
            dim = 768
            return np.zeros((len(texts) if texts else 0, dim), dtype=np.float32)
        
    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """سریع و دقیق"""
        return float(np.dot(emb1, emb2))

    def get_model_dimension(self, model_name: Optional[str] = None) -> int:
        try:
            model = self.get_model(model_name or self.default_model)
            dim = model.get_sentence_embedding_dimension()
            if isinstance(dim, int):
                return dim
            else:
                return 768  # fallback
        except Exception as e:
            print(f"Warning: Could not get model dimension: {e}")
            return 768