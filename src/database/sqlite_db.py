import sqlite3
from typing import List, Optional
from datetime import datetime
from .base import DatabaseInterface
from ..models import SecurityReport

class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    site_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    guard_id TEXT NOT NULL,
                    text TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_site_id ON reports(site_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON reports(date)")
    
    def insert_report(self, report: SecurityReport) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO reports (id, site_id, date, guard_id, text) VALUES (?, ?, ?, ?, ?)",
                (report.id, report.siteId, report.date.isoformat(), report.guardId, report.text)
            )
    
    def get_reports(self, 
                   site_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[SecurityReport]:
        query = "SELECT id, site_id, date, guard_id, text FROM reports WHERE 1=1"
        params = []
        
        if site_id:
            query += " AND site_id = ?"
            params.append(site_id)
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return [
                SecurityReport(
                    id=row[0],
                    siteId=row[1],
                    date=datetime.fromisoformat(row[2]),
                    guardId=row[3],
                    text=row[4]
                )
                for row in cursor.fetchall()
            ]
    
    def get_report_by_id(self, report_id: str) -> Optional[SecurityReport]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, site_id, date, guard_id, text FROM reports WHERE id = ?",
                (report_id,)
            )
            row = cursor.fetchone()
            if row:
                return SecurityReport(
                    id=row[0],
                    siteId=row[1],
                    date=datetime.fromisoformat(row[2]),
                    guardId=row[3],
                    text=row[4]
                )
            return None