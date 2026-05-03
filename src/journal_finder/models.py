from pydantic import BaseModel

class JournalMatch(BaseModel):
    journal_name: str
    score: float
    justification: str
    url: str = ""
