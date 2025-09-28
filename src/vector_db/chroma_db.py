import chromadb
from typing import List, Dict, Any, Optional
from .base import VectorDatabaseInterface

class ChromaVectorDatabase(VectorDatabaseInterface):
    def __init__(self, persist_directory: str, collection_name: str = "security_reports"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
    
    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection.name)