import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from .base import VectorDatabaseInterface

class FAISSVectorDatabase(VectorDatabaseInterface):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadatas = []
        self.ids = []
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        embeddings = self.model.encode(documents)
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
        
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
    
    def search(self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.index is None:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]]}
        
        query_embedding = self.model.encode([query])
        scores, indices = self.index.search(query_embedding.astype('float32'), min(n_results, len(self.ids)))
        
        result_ids = []
        result_docs = []
        result_metas = []
        
        for idx in indices[0]:
            if idx < len(self.ids):
                metadata = self.metadatas[idx]
                # Apply where filter
                if where:
                    if all(metadata.get(k) == v for k, v in where.items()):
                        result_ids.append(self.ids[idx])
                        result_docs.append(self.documents[idx])
                        result_metas.append(metadata)
                else:
                    result_ids.append(self.ids[idx])
                    result_docs.append(self.documents[idx])
                    result_metas.append(metadata)
        
        return {
            "ids": [result_ids],
            "documents": [result_docs],
            "metadatas": [result_metas]
        }
    
    def delete_collection(self) -> None:
        self.index = None
        self.documents = []
        self.metadatas = []
        self.ids = []