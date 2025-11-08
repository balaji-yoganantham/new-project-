"""Prompt templates for different agents"""

RESEARCH_PROMPT = """
Research Topic: {topic}

Your task:
1. Identify 5-10 authoritative sources on this topic
2. For each source, extract:
   - Main arguments/findings
   - Supporting evidence
   - Author credentials
   - Publication date
3. Rate source credibility (1-10)
4. Flag any potential biases

Output Format (JSON):
{{
  "sources": [
    {{
      "url": "...",
      "title": "...",
      "description": "...",
      "credibility_score": 8,
      "key_points": ["..."],
      "biases": ["..."],
      "date": "..."
    }}
  ]
}}
"""

FACT_EXTRACTION_PROMPT = """
Extract verifiable facts from the following research data:

{research_data}

Tasks:
1. Extract 10-15 key verifiable facts
   - Must be specific and measurable
   - Include source attribution
   - Rate certainty (High/Medium/Low)

2. For each fact, provide:
   - The fact text
   - Source URLs
   - Certainty level
   - Confidence score (0.0-1.0)

Output as structured JSON with a "facts" array.
"""

ANALYSIS_PROMPT = """
Analyze the following research data:

{research_data}

Tasks:

1. FACTS: Extract 10-15 key verifiable facts
   - Must be specific and measurable
   - Include source attribution
   - Rate certainty (High/Medium/Low)

2. RISKS: Identify potential risks/concerns
   - Technical risks
   - Ethical considerations
   - Limitations of current knowledge
   - Conflicting evidence

3. CONTRADICTIONS: Flag any contradictory information
   - Describe the contradiction
   - List sources involved
   - Suggest resolution approach

Output as structured JSON with "facts", "risks", and "contradictions" arrays.
"""

SYNTHESIS_PROMPT = """
Create a comprehensive research report:

Research Data: {research}
Analysis: {analysis}

Generate:

1. EXECUTIVE SUMMARY (200-300 words)
   - Main findings
   - Critical insights
   - Actionable recommendations

2. KEY HIGHLIGHTS (5-7 bullet points)
   - Most important facts
   - Major risks
   - Surprising discoveries

3. DETAILED SECTIONS:
   - Background & Context
   - Main Findings
   - Risks & Considerations
   - Gaps in Knowledge
   - Recommendations

4. REFERENCES
   - Properly formatted citations
   - Source credibility notes

Output as structured JSON with "executive_summary", "key_highlights", "full_report", and "metadata" fields.
"""

