"""Research Agent for gathering web information"""

try:
    import autogen
except ImportError:
    autogen = None  # Autogen is optional

from typing import List, Dict
from datetime import datetime
from src.utils.groq_client import GroqClient
from src.tools.web_search import WebSearchTool
from src.tools.web_scraper import WebScraper
from src.utils.prompt_templates import RESEARCH_PROMPT
import json


class ResearchAgent:
    """Agent specialized in gathering comprehensive web information"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.groq = GroqClient({
            "api_key": config.get("api_key"),
            "model": config.get("model", "llama-3.3-70b-versatile"),
            "max_tokens": config.get("max_tokens", 4000),
            "temperature": config.get("temperature", 0.3)
        })
        self.search_tool = WebSearchTool()
        self.scraper = WebScraper()
        
        # Autogen agent configuration (optional)
        if autogen:
            try:
                self.agent = autogen.AssistantAgent(
                    name=config.get("name", "WebResearcher"),
                    llm_config={
                    "config_list": [{
                        "model": config.get("model", "llama-3.3-70b-versatile"),
                            "api_key": config.get("api_key"),
                            "api_type": "groq",
                            "base_url": "https://api.groq.com/openai/v1"
                        }],
                        "temperature": config.get("temperature", 0.3)
                    },
                    system_message=self._get_system_message()
                )
            except Exception:
                self.agent = None
        else:
            self.agent = None
    
    def _get_system_message(self) -> str:
        return """You are a research agent specializing in gathering 
        comprehensive web information. Your tasks:
        1. Search for relevant sources on the given topic
        2. Validate source credibility
        3. Extract key information
        4. Organize findings with proper citations"""
    
    async def research_topic(self, topic: str, depth: int = 5) -> Dict:
        """Main research method
        
        Args:
            topic: Research topic
            depth: Number of sources to gather
        
        Returns:
            Dictionary with research data
        """
        print(f"  🔍 Searching for sources on: {topic}")
        
        # Search implementation
        search_results = await self.search_tool.search(topic, max_results=depth)
        print(f"  ✅ Found {len(search_results)} search results")
        
        # Content extraction
        contents = await self._extract_contents(search_results)
        print(f"  ✅ Extracted content from {len(contents)} sources")
        
        # Groq-powered relevance filtering (only if we have contents)
        if contents:
            filtered_results = await self._filter_relevant_content(topic, contents)
            print(f"  ✅ Filtered to {len(filtered_results)} relevant sources")
        else:
            print(f"  ⚠️  No contents to filter, using search results directly")
            filtered_results = search_results
        
        return {
            "topic": topic,
            "sources": filtered_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _extract_contents(self, search_results: List[Dict]) -> List[Dict]:
        """Scrape and extract content from URLs
        
        Args:
            search_results: List of search result dictionaries
        
        Returns:
            List of content dictionaries
        """
        contents = []
        for result in search_results:
            url = result.get("url", "")
            if url:
                try:
                    scraped = await self.scraper.scrape_url(url)
                    # Use summary from LangSearch if available, otherwise use scraped content
                    content = result.get("summary", "") or scraped.get("content", "")
                    contents.append({
                        **result,
                        "content": content,
                        "title": scraped.get("title", result.get("title", result.get("name", "")))
                    })
                except Exception as e:
                    print(f"  ⚠️  Error scraping {url}: {str(e)}")
                    contents.append(result)
            else:
                contents.append(result)
        
        return contents
    
    async def _filter_relevant_content(self, topic: str, contents: List[Dict]) -> List[Dict]:
        """Use Groq AI to filter relevant information
        
        Args:
            topic: Research topic
            contents: List of content dictionaries
        
        Returns:
            Filtered list of relevant sources
        """
        if not contents:
            return []
        
        # Prepare content summary for analysis
        content_summary = []
        for i, content in enumerate(contents[:10]):  # Limit to 10 for prompt size
            content_summary.append({
                "index": i,
                "url": content.get("url", ""),
                "title": content.get("title", ""),
                "description": content.get("description", ""),
                "content_preview": content.get("content", "")[:500] if content.get("content") else ""
            })
        
        prompt = RESEARCH_PROMPT.format(topic=topic)
        prompt += f"\n\nSearch Results:\n{json.dumps(content_summary, indent=2)}"
        
        try:
            response = await self.groq.complete_json(prompt)
            
            # Map filtered results back to original content
            filtered_sources = []
            if "sources" in response:
                for source in response["sources"]:
                    url = source.get("url", "")
                    # Find matching content
                    matching_content = next(
                        (c for c in contents if c.get("url") == url),
                        None
                    )
                    
                    if matching_content:
                        filtered_sources.append({
                            **matching_content,
                            "credibility_score": source.get("credibility_score"),
                            "key_points": source.get("key_points", []),
                            "biases": source.get("biases", [])
                        })
                    else:
                        # Add new source from AI analysis
                        filtered_sources.append({
                            "url": url,
                            "title": source.get("title", ""),
                            "description": source.get("description", ""),
                            "credibility_score": source.get("credibility_score"),
                            "key_points": source.get("key_points", []),
                            "biases": source.get("biases", []),
                            "date": source.get("date", "")
                        })
            
            # If filtering returned empty, use original contents
            if not filtered_sources:
                print(f"  ⚠️  Filtering returned no results, using original sources")
                return contents[:5]
            return filtered_sources
        except Exception as e:
            print(f"  ⚠️  Error filtering content: {str(e)}. Using all sources.")
            return contents[:5] if contents else []

