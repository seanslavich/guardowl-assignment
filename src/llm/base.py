from abc import ABC, abstractmethod
from typing import List
from ..models import SecurityReport

class LLMInterface(ABC):
    @abstractmethod
    def generate_summary(self, query: str, reports: List[SecurityReport]) -> str:
        pass