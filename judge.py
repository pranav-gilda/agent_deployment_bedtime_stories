"""
LLM Judge system for evaluating story quality and age-appropriateness.
Provides detailed feedback and scoring for story improvement.
"""

from typing import Dict, List
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from config import JUDGE_CONFIG, STORY_CONFIG, MODEL_CONFIG
from utils import retry_with_backoff, safe_parse_json

load_dotenv()

class StoryJudge:
    """Evaluates stories for quality, age-appropriateness, and engagement."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = MODEL_CONFIG["model_name"]
        self.temperature = JUDGE_CONFIG["judge_temperature"]
        self.max_tokens = JUDGE_CONFIG["max_judge_tokens"]
        self.strictness = JUDGE_CONFIG["strictness_level"]
        self.min_score = JUDGE_CONFIG["minimum_acceptance_score"]
        self.criteria = JUDGE_CONFIG["evaluation_criteria"]
    
    def create_judge_prompt(self, story: str, user_request: str = "") -> str:
        """Create a comprehensive prompt for the judge to evaluate the story."""
        criteria_list = "\n".join([f"- {criterion}" for criterion in self.criteria])
        
        prompt = f"""You are an expert judge evaluating a bedtime story for children aged {STORY_CONFIG['target_age_min']}-{STORY_CONFIG['target_age_max']} years.

STORY TO EVALUATE:
{story[:3000]}  # Limit story length for prompt

USER REQUEST (if provided):
{user_request[:500]}  # Limit request length

EVALUATION CRITERIA (rate each 0-10):
{criteria_list}

ADDITIONAL CONSIDERATIONS:
- Age-appropriateness: Is the content, vocabulary, and themes suitable for ages 5-10?
- Story structure: Does it have a clear beginning, middle, and end with a satisfying resolution?
- Character development: Are characters relatable and well-developed?
- Moral value: Does the story teach a positive lesson or value?
- Engagement level: Will children be interested and engaged?
- Language complexity: Is the vocabulary and sentence structure appropriate?

Please respond with a JSON object in this exact format:
{{
  "scores": {{
    "age_appropriateness": <0-10>,
    "story_structure": <0-10>,
    "character_development": <0-10>,
    "moral_value": <0-10>,
    "engagement_level": <0-10>,
    "language_complexity": <0-10>,
    "overall": <0-10>
  }},
  "feedback": {{
    "what_works_well": "<detailed feedback>",
    "suggestions_for_improvement": "<detailed suggestions>"
  }},
  "verdict": "<ACCEPT or REVISE>"
}}

IMPORTANT: Respond ONLY with valid JSON. No additional text before or after.
"""
        return prompt
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0, max_delay=60.0)
    def _call_judge_api(self, prompt: str) -> str:
        """Make API call with retry logic."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert children's story evaluator with deep knowledge of child development and storytelling. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}  # Force JSON mode
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from API")
        
        return response.choices[0].message.content
    
    def evaluate_story(self, story: str, user_request: str = "") -> Dict:
        """
        Evaluate a story and return detailed feedback.
        Returns dict with scores, feedback, and verdict.
        """
        if not story or not story.strip():
            return {
                "verdict": "ERROR",
                "overall_score": 0.0,
                "detailed_feedback": "Empty story provided for evaluation",
                "meets_threshold": False,
                "error": "Empty story"
            }
        
        prompt = self.create_judge_prompt(story, user_request)
        
        try:
            judge_response = self._call_judge_api(prompt)
            
            # Parse JSON response
            try:
                evaluation_data = json.loads(judge_response)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from text
                evaluation_data = safe_parse_json(judge_response, {})
            
            # Extract data with defaults
            scores = evaluation_data.get("scores", {})
            feedback = evaluation_data.get("feedback", {})
            verdict_str = evaluation_data.get("verdict", "REVISE").upper()
            
            overall_score = scores.get("overall", 0.0)
            if not isinstance(overall_score, (int, float)):
                overall_score = 0.0
            
            # Determine verdict
            if verdict_str == "ACCEPT" or overall_score >= self.min_score:
                verdict = "ACCEPT"
            else:
                verdict = "REVISE"
            
            # Format detailed feedback
            detailed_feedback = f"""SCORES:
{chr(10).join([f"- {k}: {v}/10" for k, v in scores.items() if k != 'overall'])}

Overall Score: {overall_score}/10

FEEDBACK:
What Works Well: {feedback.get('what_works_well', 'N/A')}

Suggestions for Improvement: {feedback.get('suggestions_for_improvement', 'N/A')}

VERDICT: {verdict}
"""
            
            return {
                "verdict": verdict,
                "overall_score": float(overall_score),
                "detailed_feedback": detailed_feedback,
                "meets_threshold": overall_score >= self.min_score,
                "scores": scores,
                "raw_response": judge_response
            }
        
        except Exception as e:
            return {
                "verdict": "ERROR",
                "overall_score": 0.0,
                "detailed_feedback": f"Error during evaluation: {str(e)}",
                "meets_threshold": False,
                "error": str(e)
            }
    
    def generate_revision_prompt(self, original_story: str, judge_feedback: str, user_request: str) -> str:
        """Generate a prompt for revising the story based on judge feedback."""
        return f"""You are a skilled children's storyteller. Please revise the following story based on the judge's feedback.
            
            ORIGINAL USER REQUEST:
            {user_request}
            
            ORIGINAL STORY:
            {original_story}
            
            JUDGE'S FEEDBACK:
            {judge_feedback}
            
            Please create an improved version of the story that addresses all the feedback while maintaining the core narrative AND the storytelling variety/style that was specified in the original instructions. Ensure the story is:
            - Appropriate for children aged {STORY_CONFIG['target_age_min']}-{STORY_CONFIG['target_age_max']}
            - Engaging and well-structured
            - Contains positive themes and a happy resolution
            - Uses age-appropriate vocabulary and sentence structure
            - Maintains the narrative style, perspective, and variety approach from the original generation
            
            REVISED STORY:
            """

