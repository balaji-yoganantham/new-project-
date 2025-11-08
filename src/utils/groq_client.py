"""Groq AI client for API interactions"""

import os
import asyncio
from typing import List, Dict, Optional
from groq import Groq
import json


class GroqClient:
    """Client for interacting with Groq AI API"""
    
    def __init__(self, config: Dict):
        api_key = config.get("api_key") or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key not provided")
        
        self.client = Groq(api_key=api_key)
        self.model = config.get("model", "llama-3.3-70b-versatile")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
    
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """Get completion from Groq AI
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            tools: Optional tools (not fully supported in Groq yet)
        
        Returns:
            Response text
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Run synchronous Groq API call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    async def complete_json(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> Dict:
        """Get JSON response from Groq AI
        
        Args:
            prompt: User prompt requesting JSON output
            system_message: Optional system message
        
        Returns:
            Parsed JSON dictionary
        """
        json_prompt = f"{prompt}\n\nPlease respond with valid JSON only, no additional text."
        
        response_text = await self.complete(json_prompt, system_message)
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to find JSON-like structure
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")

