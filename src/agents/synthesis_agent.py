"""Synthesis Agent for creating coherent summaries"""

try:
    import autogen
except ImportError:
    autogen = None  # Autogen is optional

from typing import Dict, List
from src.utils.groq_client import GroqClient
from src.utils.prompt_templates import SYNTHESIS_PROMPT
import json


class SynthesisAgent:
    """Agent specialized in creating coherent summaries and organizing insights"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.groq = GroqClient({
            "api_key": config.get("api_key"),
            "model": config.get("model", "llama-3.3-70b-versatile"),
            "max_tokens": config.get("max_tokens", 5000),
            "temperature": config.get("temperature", 0.4)
        })
        
        # Autogen agent configuration (optional)
        if autogen:
            try:
                self.agent = autogen.AssistantAgent(
                    name=config.get("name", "Synthesizer"),
                    llm_config={
                    "config_list": [{
                        "model": config.get("model", "llama-3.3-70b-versatile"),
                            "api_key": config.get("api_key"),
                            "api_type": "groq",
                            "base_url": "https://api.groq.com/openai/v1"
                        }],
                        "temperature": config.get("temperature", 0.4)
                    },
                    system_message=self._get_system_message()
                )
            except Exception:
                self.agent = None
        else:
            self.agent = None
    
    def _get_system_message(self) -> str:
        return """You are a synthesis agent specializing in:
        1. Creating coherent summaries from multiple sources
        2. Organizing insights into structured reports
        3. Generating executive summaries
        4. Formatting research findings"""
    
    async def synthesize(self, research: Dict, analysis: Dict) -> Dict:
        """Create final synthesis
        
        Args:
            research: Research data dictionary
            analysis: Analysis data dictionary
        
        Returns:
            Synthesis results dictionary
        """
        print("  🔍 Synthesizing research and analysis...")
        
        summary = await self._generate_summary(research, analysis)
        print("  ✅ Generated executive summary")
        
        highlights = await self._extract_highlights(analysis)
        print(f"  ✅ Extracted {len(highlights)} key highlights")
        
        report = await self._format_report(summary, highlights, analysis)
        print("  ✅ Formatted full report")
        
        metadata = self._generate_metadata(research, analysis)
        
        return {
            "executive_summary": summary,
            "key_highlights": highlights,
            "full_report": report,
            "metadata": metadata
        }
    
    async def _generate_summary(self, research: Dict, analysis: Dict) -> str:
        """Generate executive summary
        
        Args:
            research: Research data dictionary
            analysis: Analysis data dictionary
        
        Returns:
            Executive summary string
        """
        # Prepare condensed data for synthesis
        research_summary = {
            "topic": research.get("topic", ""),
            "source_count": len(research.get("sources", [])),
            "sources": [
                {
                    "title": s.get("title", ""),
                    "url": s.get("url", ""),
                    "key_points": s.get("key_points", [])[:3]  # Limit key points
                }
                for s in research.get("sources", [])[:5]
            ]
        }
        
        analysis_summary = {
            "fact_count": len(analysis.get("facts", [])),
            "top_facts": [
                {
                    "text": f.get("text", ""),
                    "certainty": f.get("certainty", "Medium")
                }
                for f in analysis.get("facts", [])[:5]
            ],
            "risk_count": len(analysis.get("risks", [])),
            "top_risks": [
                {
                    "category": r.get("category", ""),
                    "description": r.get("description", ""),
                    "severity": r.get("severity", "Medium")
                }
                for r in analysis.get("risks", [])[:3]
            ]
        }
        
        prompt = SYNTHESIS_PROMPT.format(
            research=json.dumps(research_summary, indent=2),
            analysis=json.dumps(analysis_summary, indent=2)
        )
        
        try:
            response = await self.groq.complete_json(prompt)
            
            # Handle different response formats
            if isinstance(response, dict):
                # If response is a dict, try to extract executive_summary
                if "executive_summary" in response:
                    summary = response["executive_summary"]
                elif "main_findings" in response:
                    # Format as structured summary
                    main_findings = response.get("main_findings", "")
                    critical_insights = response.get("critical_insights", "")
                    recommendations = response.get("actionable_recommendations", "")
                    
                    summary = f"{main_findings}\n\nCritical Insights:\n{critical_insights}\n\nRecommendations:\n{recommendations}"
                else:
                    # Use the whole response as summary
                    summary = json.dumps(response, indent=2)
            else:
                summary = str(response)
            
            # Ensure it's a string
            if not isinstance(summary, str):
                summary = str(summary)
            
            return summary if summary else "Summary generation failed."
        except Exception as e:
            print(f"  ⚠️  Error generating summary: {str(e)}")
            # Fallback summary
            return f"Research on {research.get('topic', 'the topic')} analyzed {len(research.get('sources', []))} sources, " \
                   f"extracted {len(analysis.get('facts', []))} facts, and identified {len(analysis.get('risks', []))} risks."
    
    async def _extract_highlights(self, analysis: Dict) -> List[str]:
        """Extract key highlights from analysis
        
        Args:
            analysis: Analysis data dictionary
        
        Returns:
            List of highlight strings
        """
        highlights = []
        
        # Add top facts
        facts = analysis.get("facts", [])
        for fact in facts[:3]:
            if isinstance(fact, dict):
                fact_text = fact.get("text") or fact.get("fact_text") or str(fact)
            else:
                fact_text = str(fact)
            if fact_text and fact_text != "{}":
                highlights.append(f"Key Fact: {fact_text}")
        
        # Add top risks
        risks = analysis.get("risks", [])
        for risk in risks[:2]:
            if isinstance(risk, dict):
                risk_desc = risk.get("description", "")
                if risk_desc:
                    highlights.append(f"Risk: {risk_desc}")
        
        # Ensure we have at least 5 highlights
        if len(highlights) < 5:
            # Add more facts or risks
            for fact in facts[3:5]:
                fact_text = fact.get("text", "") if isinstance(fact, dict) else str(fact)
                if fact_text and len(highlights) < 7:
                    highlights.append(f"Additional Finding: {fact_text}")
        
        return highlights[:7]  # Limit to 7 highlights
    
    async def _format_report(self, summary: str, highlights: List[str], analysis: Dict) -> str:
        """Format full report
        
        Args:
            summary: Executive summary
            highlights: List of highlights
            analysis: Analysis data dictionary
        
        Returns:
            Formatted report string
        """
        report_parts = []
        
        # Executive Summary
        report_parts.append("# Executive Summary\n")
        # Ensure summary is a string
        summary_str = str(summary) if not isinstance(summary, str) else summary
        report_parts.append(summary_str)
        report_parts.append("\n")
        
        # Key Highlights
        report_parts.append("# Key Highlights\n")
        for highlight in highlights:
            # Ensure highlight is a string
            if isinstance(highlight, dict):
                highlight = highlight.get("text", str(highlight))
            highlight_str = str(highlight) if not isinstance(highlight, str) else highlight
            report_parts.append(f"- {highlight_str}")
        report_parts.append("\n")
        
        # Facts Section
        report_parts.append("# Key Facts\n")
        facts = analysis.get("facts", [])
        for i, fact in enumerate(facts[:10], 1):
            fact_text = fact.get("text", "") if isinstance(fact, dict) else str(fact)
            certainty = fact.get("certainty", "Medium") if isinstance(fact, dict) else "Medium"
            report_parts.append(f"{i}. {fact_text} (Certainty: {certainty})")
        report_parts.append("\n")
        
        # Risks Section
        report_parts.append("# Risks and Considerations\n")
        risks = analysis.get("risks", [])
        for i, risk in enumerate(risks, 1):
            if isinstance(risk, dict):
                category = risk.get("category", "General")
                description = risk.get("description", "")
                severity = risk.get("severity", "Medium")
                report_parts.append(f"{i}. [{category}] {description} (Severity: {severity})")
        report_parts.append("\n")
        
        # Contradictions Section
        contradictions = analysis.get("contradictions", [])
        if contradictions:
            report_parts.append("# Contradictions\n")
            for i, contradiction in enumerate(contradictions, 1):
                if isinstance(contradiction, dict):
                    desc = contradiction.get("description", "")
                    report_parts.append(f"{i}. {desc}")
            report_parts.append("\n")
        
        # Ensure all items are strings before joining
        report_parts_str = [str(part) for part in report_parts]
        return "\n".join(report_parts_str)
    
    def _generate_metadata(self, research: Dict, analysis: Dict) -> Dict:
        """Generate metadata for the synthesis
        
        Args:
            research: Research data dictionary
            analysis: Analysis data dictionary
        
        Returns:
            Metadata dictionary
        """
        return {
            "sources_count": len(research.get("sources", [])),
            "facts_count": len(analysis.get("facts", [])),
            "risks_count": len(analysis.get("risks", [])),
            "contradictions_count": len(analysis.get("contradictions", [])),
            "topic": research.get("topic", "")
        }

