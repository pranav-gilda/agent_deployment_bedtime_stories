"""
Age-appropriate guardrails and content safety checks for bedtime stories.
Ensures all content is suitable for children aged 5-10.
"""

from typing import Dict, List, Tuple
from config import GUARDRAIL_CONFIG, STORY_CONFIG
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import retry_with_backoff
from config import MODEL_CONFIG

load_dotenv()


class StoryGuardrails:
    """Implements safety checks and age-appropriateness validation."""
    
    def __init__(self):
        self.prohibited_themes = GUARDRAIL_CONFIG["prohibited_themes"]
        self.required_elements = GUARDRAIL_CONFIG["required_elements"]
        self.target_age_min = STORY_CONFIG["target_age_min"]
        self.target_age_max = STORY_CONFIG["target_age_max"]
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = MODEL_CONFIG["model_name"]
        self.use_llm_guardrails = True  # Enable LLM-based guardrails
    
    @retry_with_backoff(max_attempts=2, base_delay=1.0, max_delay=20.0)
    def _llm_content_safety_check(self, story: str) -> Tuple[bool, List[str]]:
        """LLM-based content safety check with context awareness."""
        prompt = f"""Analyze this bedtime story for children aged {self.target_age_min}-{self.target_age_max} years.

STORY:
{story[:2000]}

Check for:
1. Violence, danger, or harmful content (even if mentioned in a safe context)
2. Scary or frightening content that could cause nightmares
3. Inappropriate language or themes
4. Content that is not suitable for ages {self.target_age_min}-{self.target_age_max}

Respond with JSON:
{{
  "is_safe": true/false,
  "violations": ["violation1", "violation2"],
  "concerns": ["concern1", "concern2"]
}}

If the story is safe, return {{"is_safe": true, "violations": [], "concerns": []}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content safety expert for children's stories. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"},
                timeout=20.0
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            is_safe = result.get("is_safe", False)
            violations = result.get("violations", [])
            concerns = result.get("concerns", [])
            
            return is_safe, violations + concerns
        
        except Exception as e:
            # Fallback to keyword-based check
            return self._keyword_content_safety_check(story)
    
    def _keyword_content_safety_check(self, story: str) -> Tuple[bool, List[str]]:
        """Fallback keyword-based content safety check."""
        violations = []
        story_lower = story.lower()
        
        # More sophisticated keyword checking with context
        danger_keywords = ["kill", "death", "die", "blood", "weapon", "gun", "knife"]
        fear_keywords = ["terrifying", "horror", "nightmare", "scary", "frightening"]
        inappropriate_keywords = ["hate", "stupid", "idiot", "dumb"]
        
        # Check for dangerous content (but allow in safe contexts like "not scary")
        for keyword in danger_keywords:
            if keyword in story_lower:
                # Check if negated
                context = story_lower[max(0, story_lower.find(keyword)-20):story_lower.find(keyword)+20]
                if "not " not in context and "no " not in context and "never " not in context:
                    violations.append(f"Contains dangerous content: '{keyword}'")
        
        for keyword in fear_keywords:
            if keyword in story_lower:
                context = story_lower[max(0, story_lower.find(keyword)-20):story_lower.find(keyword)+20]
                if "not " not in context and "no " not in context:
                    violations.append(f"Contains scary content: '{keyword}'")
        
        for keyword in inappropriate_keywords:
            if keyword in story_lower:
                violations.append(f"Contains inappropriate language: '{keyword}'")
        
        is_safe = len(violations) == 0
        return is_safe, violations
    
    def check_content_safety(self, story: str) -> Tuple[bool, List[str]]:
        """
        Check if story contains prohibited content.
        Returns (is_safe, list_of_violations)
        """
        if not GUARDRAIL_CONFIG["enable_content_filter"]:
            return True, []
        
        if not story or not story.strip():
            return False, ["Empty story"]
        
        # Use LLM-based check if enabled, otherwise use keyword-based
        if self.use_llm_guardrails:
            try:
                return self._llm_content_safety_check(story)
            except Exception:
                # Fallback to keyword-based
                return self._keyword_content_safety_check(story)
        else:
            return self._keyword_content_safety_check(story)
    
    def check_age_appropriateness(self, story: str) -> Tuple[bool, List[str]]:
        """
        Check if story is appropriate for target age range.
        Returns (is_appropriate, list_of_issues)
        """
        issues = []
        
        if not GUARDRAIL_CONFIG["enable_age_check"]:
            return True, []
        
        # Check sentence length (should be relatively short for ages 5-10)
        sentences = story.split('.')
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        if len(long_sentences) > 3:
            issues.append("Too many long sentences for target age group")
        
        # Check vocabulary complexity (simple heuristic)
        complex_words = ["nevertheless", "consequently", "furthermore", "therefore"]
        complex_count = sum(1 for word in complex_words if word.lower() in story.lower())
        if complex_count > 5:
            issues.append("Vocabulary may be too complex for younger children")
        
        # Check for required positive elements
        positive_keywords = ["kind", "friend", "help", "love", "happy", "smile", "laugh", "joy"]
        positive_count = sum(1 for word in positive_keywords if word.lower() in story.lower())
        if positive_count < 3:
            issues.append("Story may lack sufficient positive elements")
        
        is_appropriate = len(issues) == 0
        return is_appropriate, issues
    
    def validate_story(self, story: str) -> Dict:
        """
        Comprehensive validation of story.
        Returns dict with validation results.
        """
        is_safe, safety_violations = self.check_content_safety(story)
        is_appropriate, age_issues = self.check_age_appropriateness(story)
        
        return {
            "is_valid": is_safe and is_appropriate,
            "is_safe": is_safe,
            "is_age_appropriate": is_appropriate,
            "safety_violations": safety_violations,
            "age_issues": age_issues,
            "all_issues": safety_violations + age_issues
        }
    
    def generate_safety_prompt_addition(self) -> str:
        """Generate prompt addition to guide story generation safely."""
        return f"""
IMPORTANT SAFETY GUIDELINES FOR STORY GENERATION:
- Target audience: Children aged {self.target_age_min}-{self.target_age_max} years
- PROHIBITED: Violence, fear, scary monsters, dangerous situations, inappropriate language
- REQUIRED: Positive resolution, kindness, friendship, learning experiences
- Use simple to medium-complexity vocabulary
- Keep sentences relatively short and clear
- Include positive themes and uplifting messages
- Ensure happy endings that teach valuable lessons
"""

