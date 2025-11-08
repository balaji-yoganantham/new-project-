"""Data models and schemas for the Research Assistant"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class Source(BaseModel):
    """Represents a web source"""
    url: str
    title: str
    description: Optional[str] = None
    credibility_score: Optional[int] = Field(None, ge=1, le=10)
    key_points: List[str] = []
    biases: List[str] = []
    date: Optional[str] = None
    content: Optional[str] = None


class Fact(BaseModel):
    """Represents a verifiable fact"""
    text: str
    source_urls: List[str] = []
    certainty: str = Field(default="Medium", pattern="^(High|Medium|Low)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class Risk(BaseModel):
    """Represents a risk or concern"""
    category: str
    description: str
    severity: str = Field(default="Medium", pattern="^(High|Medium|Low)$")
    mitigation: Optional[str] = None


class Contradiction(BaseModel):
    """Represents contradictory information"""
    description: str
    sources: List[str] = []
    resolution_approach: Optional[str] = None


class ResearchData(BaseModel):
    """Complete research data structure"""
    topic: str
    sources: List[Source] = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AnalysisData(BaseModel):
    """Analysis results structure"""
    facts: List[Fact] = []
    risks: List[Risk] = []
    contradictions: List[Contradiction] = []
    confidence_scores: Dict[str, float] = {}


class SynthesisData(BaseModel):
    """Synthesis results structure"""
    executive_summary: str
    key_highlights: List[str] = []
    full_report: str
    metadata: Dict = {}

