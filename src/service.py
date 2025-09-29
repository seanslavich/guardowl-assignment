import json
from datetime import datetime
from typing import List, Optional
from .database.base import DatabaseInterface
from .vector_db.base import VectorDatabaseInterface
from .llm.base import LLMInterface
from .models import SecurityReport, QueryRequest, QueryResponse

class GuardOwlService:
    def __init__(self, 
                 database: DatabaseInterface,
                 vector_db: VectorDatabaseInterface,
                 llm: LLMInterface):
        self.database = database
        self.vector_db = vector_db
        self.llm = llm
    
    def load_reports(self, json_file_path: str) -> None:
        """Load reports from JSON file into database and vector store"""
        with open(json_file_path, 'r') as f:
            reports_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for report_data in reports_data:
            report = SecurityReport(
                id=report_data['id'],
                siteId=report_data['siteId'],
                date=datetime.fromisoformat(report_data['date'].replace('Z', '+00:00')).replace(tzinfo=None),
                guardId=report_data['guardId'],
                text=report_data['text']
            )
            
            # Store in database
            self.database.insert_report(report)
            
            # Prepare for vector store
            documents.append(report.text)
            metadatas.append({
                'id': report.id,
                'siteId': report.siteId,
                'date': report.date.isoformat(),
                'guardId': report.guardId
            })
            ids.append(report.id)
        
        # Store in vector database
        self.vector_db.add_documents(documents, metadatas, ids)
    
    def query(self, request: QueryRequest) -> QueryResponse:
        """Process query and return structured response"""
        # Build vector search filters
        where_filter = {}
        if request.siteId:
            where_filter['siteId'] = request.siteId
        
        # Search vector database
        search_results = self.vector_db.search(
            query=request.query,
            n_results=10,
            where=where_filter if where_filter else None
        )
        
        # Get report IDs from search results
        report_ids = search_results['ids'][0] if search_results['ids'] else []
        
        # Fetch full reports from database with additional filters
        start_date = None
        end_date = None
        if request.dateRange:
            if 'start' in request.dateRange:
                start_date = datetime.fromisoformat(request.dateRange['start']).replace(tzinfo=None)
            if 'end' in request.dateRange:
                end_date = datetime.fromisoformat(request.dateRange['end']).replace(tzinfo=None)
        
        relevant_reports = []
        for report_id in report_ids:
            report = self.database.get_report_by_id(report_id)
            if report:
                # Apply date filtering
                if start_date and report.date < start_date:
                    continue
                if end_date and report.date > end_date:
                    continue
                relevant_reports.append(report)
        
        # Generate summary using LLM
        summary = self.llm.generate_summary(request.query, relevant_reports)
        
        return QueryResponse(
            answer=summary,
            sources=[r.id for r in relevant_reports]
        )