from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..models import SecurityReport

class DatabaseInterface(ABC):
    @abstractmethod
    def create_tables(self) -> None:
        pass
    
    @abstractmethod
    def insert_report(self, report: SecurityReport) -> None:
        pass
    
    @abstractmethod
    def get_reports(self, 
                   site_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[SecurityReport]:
        pass
    
    @abstractmethod
    def get_report_by_id(self, report_id: str) -> Optional[SecurityReport]:
        pass