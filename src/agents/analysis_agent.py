"""Analysis Agent for extracting facts and identifying risks"""

try:
    import autogen
except ImportError:
    autogen = None  # Autogen is optional

from typing import List, Dict
from src.utils.groq_client import GroqClient
from src.utils.prompt_templates import ANALYSIS_PROMPT, FACT_EXTRACTION_PROMPT
import json


class AnalysisAgent:
    """Agent specialized in extracting facts, identifying risks, and detecting contradictions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.groq = GroqClient({
            "api_key": config.get("api_key"),
            "model": config.get("model", "llama-3.3-70b-versatile"),
            "max_tokens": config.get("max_tokens", 3000),
            "temperature": config.get("temperature", 0.2)
        })
        
        # Autogen agent configuration (optional)
        if autogen:
            try:
                self.agent = autogen.AssistantAgent(
                    name=config.get("name", "FactAnalyzer"),
                    llm_config={
                    "config_list": [{
                        "model": config.get("model", "llama-3.3-70b-versatile"),
                            "api_key": config.get("api_key"),
                            "api_type": "groq",
                            "base_url": "https://api.groq.com/openai/v1"
                        }],
                        "temperature": config.get("temperature", 0.2)
                    },
                    system_message=self._get_system_message()
                )
            except Exception:
                self.agent = None
        else:
            self.agent = None
    
    def _get_system_message(self) -> str:
        return """You are an analytical agent specializing in:
        1. Extracting verifiable facts from research data
        2. Identifying potential risks and limitations
        3. Detecting contradictions across sources
        4. Assigning confidence scores to claims"""
    
    async def analyze_research(self, research_data: Dict) -> Dict:
        """Analyze collected research
        
        Args:
            research_data: Research data dictionary
        
        Returns:
            Analysis results dictionary
        """
        print("  🔍 Analyzing research data...")
        
        facts = await self._extract_facts(research_data)
        print(f"  ✅ Extracted {len(facts)} facts")
        
        risks = await self._identify_risks(research_data)
        print(f"  ✅ Identified {len(risks)} risks")
        
        contradictions = await self._detect_contradictions(research_data)
        print(f"  ✅ Found {len(contradictions)} contradictions")
        
        confidence_scores = self._calculate_confidence(facts)
        
        return {
            "facts": facts,
            "risks": risks,
            "contradictions": contradictions,
            "confidence_scores": confidence_scores
        }
    
    async def _extract_facts(self, data: Dict) -> List[Dict]:
        """Extract verifiable facts using Groq AI
        
        Args:
            data: Research data dictionary
        
        Returns:
            List of fact dictionaries
        """
        # Prepare research data for analysis
        sources_summary = []
        for source in data.get("sources", [])[:10]:
            sources_summary.append({
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "key_points": source.get("key_points", []),
                "content_preview": source.get("content", "")[:500] if source.get("content") else ""
            })
        
        research_summary = {
            "topic": data.get("topic", ""),
            "sources": sources_summary
        }
        
        prompt = FACT_EXTRACTION_PROMPT.format(
            research_data=json.dumps(research_summary, indent=2)
        )
        
        try:
            response = await self.groq.complete_json(prompt)
            facts = response.get("facts", [])
            
            # Ensure facts have required fields
            formatted_facts = []
            for fact in facts:
                if isinstance(fact, dict):
                    # Handle different fact formats
                    fact_text = fact.get("text") or fact.get("fact_text") or str(fact)
                    certainty = fact.get("certainty") or fact.get("certainty_level", "Medium")
                    source_urls = fact.get("source_urls") or fact.get("sources", [])
                    confidence_score = fact.get("confidence_score", 0.7)
                    
                    formatted_facts.append({
                        "text": fact_text,
                        "source_urls": source_urls if isinstance(source_urls, list) else [],
                        "certainty": certainty,
                        "confidence_score": confidence_score
                    })
            
            return formatted_facts
        except Exception as e:
            print(f"  ⚠️  Error extracting facts: {str(e)}")
            return []
    
    async def _identify_risks(self, data: Dict) -> List[Dict]:
        """Identify risks and limitations
        
        Args:
            data: Research data dictionary
        
        Returns:
            List of risk dictionaries
        """
        # Prepare data for risk analysis
        sources_summary = []
        for source in data.get("sources", [])[:10]:
            sources_summary.append({
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "key_points": source.get("key_points", []),
                "biases": source.get("biases", [])
            })
        
        research_summary = {
            "topic": data.get("topic", ""),
            "sources": sources_summary
        }
        
        prompt = ANALYSIS_PROMPT.format(
            research_data=json.dumps(research_summary, indent=2)
        )
        
        try:
            response = await self.groq.complete_json(prompt)
            risks = response.get("risks", [])
            
            # Ensure risks have required fields
            formatted_risks = []
            for risk in risks:
                if isinstance(risk, dict):
                    formatted_risks.append({
                        "category": risk.get("category", "General"),
                        "description": risk.get("description", str(risk)),
                        "severity": risk.get("severity", "Medium"),
                        "mitigation": risk.get("mitigation", "")
                    })
            
            return formatted_risks
        except Exception as e:
            print(f"  ⚠️  Error identifying risks: {str(e)}")
            return []
    
    async def _detect_contradictions(self, data: Dict) -> List[Dict]:
        """Detect contradictions across sources
        
        Args:
            data: Research data dictionary
        
        Returns:
            List of contradiction dictionaries
        """
        # Use the same analysis prompt which includes contradiction detection
        sources_summary = []
        for source in data.get("sources", [])[:10]:
            sources_summary.append({
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "key_points": source.get("key_points", []),
                "content_preview": source.get("content", "")[:500] if source.get("content") else ""
            })
        
        research_summary = {
            "topic": data.get("topic", ""),
            "sources": sources_summary
        }
        
        prompt = ANALYSIS_PROMPT.format(
            research_data=json.dumps(research_summary, indent=2)
        )
        
        try:
            response = await self.groq.complete_json(prompt)
            contradictions = response.get("contradictions", [])
            
            # Ensure contradictions have required fields
            formatted_contradictions = []
            for contradiction in contradictions:
                if isinstance(contradiction, dict):
                    formatted_contradictions.append({
                        "description": contradiction.get("description", str(contradiction)),
                        "sources": contradiction.get("sources", []),
                        "resolution_approach": contradiction.get("resolution_approach", "")
                    })
            
            return formatted_contradictions
        except Exception as e:
            print(f"  ⚠️  Error detecting contradictions: {str(e)}")
            return []
    
    def _calculate_confidence(self, facts: List[Dict]) -> Dict[str, float]:
        """Calculate confidence scores for facts
        
        Args:
            facts: List of fact dictionaries
        
        Returns:
            Dictionary mapping fact texts to confidence scores
        """
        confidence_scores = {}
        for fact in facts:
            fact_text = fact.get("text", "")
            if fact_text:
                # Use existing confidence score or calculate based on certainty
                certainty = fact.get("certainty", "Medium")
                certainty_map = {"High": 0.9, "Medium": 0.7, "Low": 0.5}
                confidence_scores[fact_text] = fact.get(
                    "confidence_score",
                    certainty_map.get(certainty, 0.7)
                )
        
        return confidence_scores

