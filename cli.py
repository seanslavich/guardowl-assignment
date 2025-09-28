#!/usr/bin/env python3
"""CLI interface for Guard Owl Chatbot"""

import json
import sys
from datetime import datetime
from src.config import settings
from src.database.sqlite_db import SQLiteDatabase
from src.vector_db.chroma_db import ChromaVectorDatabase
from src.llm.groq_llm import GroqLLM
from src.service import GuardOwlService
from src.models import QueryRequest

def main():
    # Initialize components
    database = SQLiteDatabase(settings.sqlite_db_path)
    vector_db = ChromaVectorDatabase(settings.chroma_persist_directory)
    
    if not settings.groq_api_key:
        print("Error: GROQ_API_KEY not set. Please set it in .env file or environment.")
        sys.exit(1)
    
    llm = GroqLLM(settings.groq_api_key)
    service = GuardOwlService(database, vector_db, llm)
    
    # Load data
    try:
        service.load_reports("guard_owl_mock_reports.json")
        print("Data loaded successfully!")
    except FileNotFoundError:
        print("Error: guard_owl_mock_reports.json not found.")
        sys.exit(1)
    
    print("\nGuard Owl Chatbot CLI")
    print("Type 'quit' to exit")
    print("Example queries:")
    print("- What happened at Site S01 last night?")
    print("- Show me all incidents involving a red Toyota Camry")
    print("- Were there any geofence breaches this week?")
    print()
    
    while True:
        try:
            query = input("Query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            # Parse optional filters from query
            site_id = None
            date_range = None
            
            # Simple parsing for site filter
            if "site " in query.lower():
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() == "site" and i + 1 < len(words):
                        potential_site = words[i + 1].upper()
                        if potential_site.startswith('S'):
                            site_id = potential_site
                            break
            
            request = QueryRequest(
                query=query,
                siteId=site_id,
                dateRange=date_range
            )
            
            response = service.query(request)
            
            print(f"\nAnswer: {response.answer}")
            print(f"Sources: {', '.join(response.sources)}")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()