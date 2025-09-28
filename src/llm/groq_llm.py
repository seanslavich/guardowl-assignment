from groq import Groq
from typing import List
from .base import LLMInterface
from ..models import SecurityReport

class GroqLLM(LLMInterface):
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def generate_summary(self, query: str, reports: List[SecurityReport]) -> str:
        if not reports:
            return "No relevant reports found for your query."
        
        reports_text = "\n".join([
            f"Report {r.id} (Site {r.siteId}, {r.date.strftime('%Y-%m-%d %H:%M')}): {r.text}"
            for r in reports
        ])
        
        prompt = f"""Based on the following security reports, provide a concise 2-5 sentence summary answering this query: "{query}"

Reports:
{reports_text}

Provide a clear, factual summary focusing on the most relevant information."""
        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        
        return response.choices[0].message.content