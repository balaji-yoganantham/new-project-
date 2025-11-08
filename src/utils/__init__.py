"""Research Assistant Utilities Module"""

from .groq_client import GroqClient
from .prompt_templates import (
    RESEARCH_PROMPT,
    ANALYSIS_PROMPT,
    SYNTHESIS_PROMPT,
    FACT_EXTRACTION_PROMPT
)

__all__ = [
    "GroqClient",
    "RESEARCH_PROMPT",
    "ANALYSIS_PROMPT",
    "SYNTHESIS_PROMPT",
    "FACT_EXTRACTION_PROMPT"
]

