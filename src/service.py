import json
from datetime import datetime
from typing import List, Optional, Dict, Any
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
        
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        
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
        # Parse date range for SQL filtering
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = None
        if request.dateRange:
            if 'start' in request.dateRange:
                start_date = datetime.fromisoformat(request.dateRange['start']).replace(tzinfo=None)
            if 'end' in request.dateRange:
                end_date = datetime.fromisoformat(request.dateRange['end']).replace(tzinfo=None)
                # If only date provided (no time), make it end of day for inclusive behavior
                if 'T' not in request.dateRange['end']:
                    end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # Check if any SQL filters are needed
        has_filters = request.siteId or start_date or end_date
        
        if has_filters:
            # Step 1: SQL filtering for structured data (fast, indexed)
            candidate_reports = self.database.get_reports(
                site_id=request.siteId,
                start_date=start_date,
                end_date=end_date
            )
            
            if not candidate_reports:
                return QueryResponse(
                    answer="No reports found matching the specified criteria.",
                    sources=[]
                )
            
            # Step 2: Vector search with candidate ID constraint
            candidate_ids = [r.id for r in candidate_reports]
            id_to_report = {r.id: r for r in candidate_reports}
            
            search_results = self.vector_db.search(
                query=request.query,
                n_results=min(10, len(candidate_reports)),  # Increased back to 10 for better recall
                where={'id': {'$in': candidate_ids}}
            )
            
            result_ids: List[str] = search_results['ids'][0] if search_results['ids'] else []
            relevant_reports = [id_to_report[rid] for rid in result_ids if rid in id_to_report]
        else:
            # No filters - search all reports via vector database
            search_results = self.vector_db.search(
                query=request.query,
                n_results=10  # Increased back to 10 for better recall
            )
            
            result_ids: List[str] = search_results['ids'][0] if search_results['ids'] else []
            
            # Get reports from database
            relevant_reports = []
            for rid in result_ids:
                report = self.database.get_report_by_id(rid)
                if report:
                    relevant_reports.append(report)
        
        # Generate summary using LLM
        summary = self.llm.generate_summary(request.query, relevant_reports)
        
        # Extract only report IDs that are actually mentioned in the LLM response
        mentioned_sources = []
        for report in relevant_reports:
            if report.id in summary:
                mentioned_sources.append(report.id)
        
        return QueryResponse(
            answer=summary,
            sources=mentioned_sources
        )