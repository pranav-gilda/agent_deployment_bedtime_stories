"""
LLM-based categorizer that understands user intent from both short and long prompts.
Extracts key story elements and categorizes requests intelligently.
"""

from typing import Dict, List
from openai import OpenAI
import os
from dotenv import load_dotenv
from config import MODEL_CONFIG
from utils import retry_with_backoff, sanitize_text

load_dotenv()

class StoryCategorizer:
    """Intelligently categorizes and extracts intent from user story requests."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = MODEL_CONFIG["model_name"]
        self.categories = ["adventure", "friendship", "fantasy", "animals", "default"]
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=30.0)
    def _call_categorizer_api(self, prompt: str) -> str:
        """Make API call with retry logic."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at understanding children's story requests and extracting key story elements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistent categorization
            max_tokens=300,
            timeout=30.0  # 30 second timeout
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from API")
        
        return response.choices[0].message.content
    
    def categorize_and_extract(self, user_request: str) -> Dict:
        """
        Categorize the request and extract key story elements.
        Works well with both short (2-3 words) and long detailed prompts.
        """
        prompt = f"""Analyze this bedtime story request and extract key information.

USER REQUEST:
{user_request}

Please provide:
1. Category (choose one): adventure, friendship, fantasy, animals, or default
2. Key characters mentioned or implied
3. Main theme or focus
4. Setting or environment
5. Special elements to include (magic, animals, specific objects, etc.)
6. Story tone preference (if any)

Respond in this exact format:
CATEGORY: [category]
CHARACTERS: [list of characters or "none specified"]
THEME: [main theme]
SETTING: [setting or "any"]
ELEMENTS: [special elements or "none"]
TONE: [tone preference or "neutral"]
"""
        
        try:
            # Sanitize input
            user_request = sanitize_text(user_request, max_length=5000)
            prompt = f"""Analyze this bedtime story request and extract key information.

USER REQUEST:
{user_request}

Please provide:
1. Category (choose one): adventure, friendship, fantasy, animals, or default
2. Key characters mentioned or implied
3. Main theme or focus
4. Setting or environment
5. Special elements to include (magic, animals, specific objects, etc.)
6. Story tone preference (if any)

Respond in this exact format:
CATEGORY: [category]
CHARACTERS: [list of characters or "none specified"]
THEME: [main theme]
SETTING: [setting or "any"]
ELEMENTS: [special elements or "none"]
TONE: [tone preference or "neutral"]
"""
            
            analysis = self._call_categorizer_api(prompt)
            
            # Parse the response
            category = "default"
            characters = []
            theme = ""
            setting = ""
            elements = []
            tone = "neutral"
            
            lines = analysis.split('\n')
            for line in lines:
                if line.startswith('CATEGORY:'):
                    cat = line.split(':', 1)[1].strip().lower()
                    if cat in self.categories:
                        category = cat
                elif line.startswith('CHARACTERS:'):
                    chars = line.split(':', 1)[1].strip()
                    if chars.lower() != "none specified":
                        characters = [c.strip() for c in chars.split(',')]
                elif line.startswith('THEME:'):
                    theme = line.split(':', 1)[1].strip()
                elif line.startswith('SETTING:'):
                    setting = line.split(':', 1)[1].strip()
                elif line.startswith('ELEMENTS:'):
                    elems = line.split(':', 1)[1].strip()
                    if elems.lower() != "none":
                        elements = [e.strip() for e in elems.split(',')]
                elif line.startswith('TONE:'):
                    tone = line.split(':', 1)[1].strip()
            
            return {
                "category": category,
                "characters": characters,
                "theme": theme,
                "setting": setting,
                "elements": elements,
                "tone": tone,
                "raw_analysis": analysis
            }
        
        except Exception as e:
            # Fallback to simple categorization
            return self._fallback_categorize(user_request)
    
    def _fallback_categorize(self, user_request: str) -> Dict:
        """Simple keyword-based fallback if LLM fails."""
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["adventure", "journey", "quest", "explore", "discover"]):
            category = "adventure"
        elif any(word in request_lower for word in ["friend", "friendship", "together", "help"]):
            category = "friendship"
        elif any(word in request_lower for word in ["magic", "wizard", "fairy", "dragon", "castle", "princess"]):
            category = "fantasy"
        elif any(word in request_lower for word in ["animal", "cat", "dog", "bird", "rabbit", "bear", "lion"]):
            category = "animals"
        else:
            category = "default"
        
        return {
            "category": category,
            "characters": [],
            "theme": "",
            "setting": "",
            "elements": [],
            "tone": "neutral",
            "raw_analysis": "Fallback categorization"
        }

