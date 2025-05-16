from pydantic import BaseModel, Field
from typing import List

class ResearchData(BaseModel):
    facts: List[str] = Field(
        ..., 
        description="A list of key facts, 5-7 specific and relevant facts about the topic.",
        min_length=1
    )
    quotes: List[str] = Field(
        ..., 
        description="A list of relevant quotes, 2-3 from experts or studies with attribution.",
        min_length=1
    )
    sources: List[str] = Field(
        ..., 
        description="A list of credible sources and references with full citations.",
        min_length=1
    )