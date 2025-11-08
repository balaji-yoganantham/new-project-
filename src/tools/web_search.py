"""Web search tool using LangSearch API or Brave Search API"""

import aiohttp
import os
import json
from typing import List, Dict, Optional


class WebSearchTool:
    """Tool for performing web searches using LangSearch API or Brave Search API"""
    
    def __init__(self, api_key: Optional[str] = None, search_provider: str = "langsearch"):
        """
        Initialize web search tool
        
        Args:
            api_key: API key for the search provider
            search_provider: Either "langsearch" or "brave" (default: "langsearch")
        """
        self.search_provider = search_provider.lower()
        
        if self.search_provider == "langsearch":
            self.api_key = api_key or os.getenv("LANGSEARCH_API_KEY")
            self.base_url = "https://api.langsearch.com/v1/web-search"
        elif self.search_provider == "brave":
            self.api_key = api_key or os.getenv("BRAVE_API_KEY")
            self.base_url = "https://api.search.brave.com/res/v1/web/search"
        else:
            raise ValueError(f"Unsupported search provider: {search_provider}. Use 'langsearch' or 'brave'")
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform web search using LangSearch or Brave API
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            # Fallback: return mock results if API key not available
            provider_name = "LANGSEARCH_API_KEY" if self.search_provider == "langsearch" else "BRAVE_API_KEY"
            print(f"  ⚠️  Warning: {provider_name} not set. Using mock search results.")
            return self._get_mock_results(query, max_results)
        
        print(f"  🔍 Using {self.search_provider} API with key: {self.api_key[:10]}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                if self.search_provider == "langsearch":
                    return await self._search_langsearch(session, query, max_results)
                else:
                    return await self._search_brave(session, query, max_results)
        except Exception as e:
            print(f"Search error: {str(e)}. Using mock results.")
            return self._get_mock_results(query, max_results)
    
    async def _search_langsearch(self, session: aiohttp.ClientSession, query: str, max_results: int) -> List[Dict]:
        """Perform search using LangSearch API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "freshness": "noLimit",
            "summary": True,
            "count": max_results
        }
        
        print(f"  🔍 LangSearch API: POST {self.base_url}")
        print(f"  📝 Query: {query}")
        
        try:
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"  📊 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ LangSearch response received. Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Check if response has error code
                    if isinstance(data, dict) and "code" in data:
                        if data["code"] != 200:
                            error_msg = data.get("msg", "Unknown error")
                            print(f"  ⚠️  LangSearch API returned error code {data['code']}: {error_msg}")
                            return self._get_mock_results(query, max_results)
                    
                    parsed_results = self._parse_langsearch_results(data)
                    if parsed_results:
                        print(f"  ✅ Parsed {len(parsed_results)} results from LangSearch")
                        return parsed_results
                    else:
                        print(f"  ⚠️  LangSearch returned empty results after parsing.")
                        print(f"  📊 Response structure: {str(data)[:500]}")
                        return self._get_mock_results(query, max_results)
                else:
                    error_text = await response.text()
                    print(f"  ⚠️  LangSearch API error: {response.status}")
                    print(f"  ⚠️  Error details: {error_text[:500]}")
                    return self._get_mock_results(query, max_results)
        except Exception as e:
            print(f"  ❌ LangSearch API exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_mock_results(query, max_results)
    
    async def _search_brave(self, session: aiohttp.ClientSession, query: str, max_results: int) -> List[Dict]:
        """Perform search using Brave API"""
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": max_results
        }
        
        async with session.get(
            self.base_url,
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_brave_results(data)
            else:
                print(f"Brave API error: {response.status}")
                return self._get_mock_results(query, max_results)
    
    def _parse_langsearch_results(self, data: Dict) -> List[Dict]:
        """Parse search results from LangSearch API response"""
        results = []
        
        # LangSearch API returns: {"code": 200, "data": {"webPages": {"value": [...]}}}
        items = []
        
        # Check for LangSearch API format: data.webPages.value
        if "data" in data and isinstance(data["data"], dict):
            data_obj = data["data"]
            if "webPages" in data_obj and isinstance(data_obj["webPages"], dict):
                items = data_obj["webPages"].get("value", [])
        
        # Fallback to other formats
        if not items:
            if "results" in data:
                items = data["results"]
            elif "webPages" in data:
                items = data["webPages"].get("value", [])
            elif "value" in data:
                items = data["value"]
            elif isinstance(data, list):
                items = data
            else:
                # Try to find any list of results
                for key in data:
                    if isinstance(data[key], list) and len(data[key]) > 0:
                        items = data[key]
                        break
        
        # If still no items, check for nested structures
        if not items:
            for key in ["organic", "organic_results", "web", "web_results"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
                elif key in data and isinstance(data[key], dict):
                    if "results" in data[key]:
                        items = data[key]["results"]
                        break
                    elif "value" in data[key]:
                        items = data[key]["value"]
                        break
        
        for item in items:
            if isinstance(item, dict):
                # LangSearch API format: name, url, snippet, summary
                results.append({
                    "url": item.get("url") or item.get("link") or item.get("webUrl") or item.get("href", ""),
                    "title": item.get("name") or item.get("title") or item.get("headline", ""),
                    "description": item.get("snippet") or item.get("description") or item.get("text") or item.get("abstract", ""),
                    "summary": item.get("summary", ""),  # LangSearch provides summary field
                    "date": item.get("datePublished") or item.get("date") or item.get("published_date", "")
                })
        
        # If no results found, log the data structure for debugging
        if not results:
            print(f"  ⚠️  No results parsed from LangSearch response.")
            print(f"  📊 Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and "data" in data:
                print(f"  📊 Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Not a dict'}")
        
        return results
    
    def _parse_brave_results(self, data: Dict) -> List[Dict]:
        """Parse search results from Brave API response"""
        results = []
        web_results = data.get("web", {}).get("results", [])
        
        for item in web_results:
            results.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "date": item.get("age", "")
            })
        
        return results
    
    def _get_mock_results(self, query: str, max_results: int) -> List[Dict]:
        """Generate mock search results for testing"""
        return [
            {
                "url": f"https://example.com/result{i}",
                "title": f"Result {i} for {query}",
                "description": f"This is a mock result for the query: {query}",
                "date": "2024-01-01"
            }
            for i in range(1, min(max_results, 5) + 1)
        ]

