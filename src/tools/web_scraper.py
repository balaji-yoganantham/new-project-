"""Web scraping tool for extracting content from URLs"""

from bs4 import BeautifulSoup
import aiohttp
from typing import Dict
import re


class WebScraper:
    """Tool for scraping content from web URLs"""
    
    async def scrape_url(self, url: str) -> Dict:
        """Scrape content from URL
        
        Args:
            url: URL to scrape
        
        Returns:
            Dictionary with url, title, content, and metadata
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        return {
                            "url": url,
                            "title": self._extract_title(soup),
                            "content": self._extract_main_content(soup),
                            "metadata": self._extract_metadata(soup)
                        }
                    else:
                        return {
                            "url": url,
                            "title": "",
                            "content": f"Error: Could not fetch URL (Status {response.status})",
                            "metadata": {}
                        }
        except Exception as e:
            return {
                "url": url,
                "title": "",
                "content": f"Error scraping URL: {str(e)}",
                "metadata": {}
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple methods
        title = soup.find("title")
        if title:
            return title.get_text(strip=True)
        
        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content", "")
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        # Try to find main content areas
        main_content = (
            soup.find('article') or
            soup.find('main') or
            soup.find('div', class_=re.compile(r'content|article|post', re.I)) or
            soup.find('body')
        )
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            # Clean up excessive whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text[:10000]  # Limit content length
        
        return soup.get_text(separator='\n', strip=True)[:10000]
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from page"""
        metadata = {}
        
        # Extract meta tags
        meta_description = soup.find("meta", attrs={"name": "description"})
        if meta_description:
            metadata["description"] = meta_description.get("content", "")
        
        og_description = soup.find("meta", property="og:description")
        if og_description:
            metadata["og_description"] = og_description.get("content", "")
        
        # Extract author
        author = soup.find("meta", attrs={"name": "author"})
        if author:
            metadata["author"] = author.get("content", "")
        
        # Extract publication date
        date_published = soup.find("meta", property="article:published_time")
        if date_published:
            metadata["date_published"] = date_published.get("content", "")
        
        return metadata

