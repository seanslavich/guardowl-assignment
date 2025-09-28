from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorDatabaseInterface(ABC):
    @abstractmethod
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        pass
    
    @abstractmethod
    def search(self, query: str, n_results: int = 5, where: Dict[str, Any] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def delete_collection(self) -> None:
        pass