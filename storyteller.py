"""
Storyteller agent that generates age-appropriate bedtime stories.
Uses categorization and structured prompting for better stories.
"""

from typing import Dict, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
from config import STORY_CONFIG, MODEL_CONFIG, ORCHESTRATION_CONFIG
from guardrails import StoryGuardrails
from categorizer import StoryCategorizer
from parent_config import apply_parent_settings_to_config
from story_variety import get_variety_prompt_additions, create_variety_config
from utils import retry_with_backoff, validate_user_input, sanitize_text

load_dotenv()

class Storyteller:
    """Generates bedtime stories with age-appropriate content."""
    
    def __init__(self, parent_settings: Optional[Dict] = None):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = MODEL_CONFIG["model_name"]
        self.guardrails = StoryGuardrails()
        self.enable_categorization = ORCHESTRATION_CONFIG["enable_categorization"]
        self.category_strategies = ORCHESTRATION_CONFIG["category_strategies"]
        self.categorizer = StoryCategorizer()
        
        # Apply parent settings if provided
        self.parent_settings = parent_settings or {}
        self.technical_overrides = apply_parent_settings_to_config(self.parent_settings)
        
        # Use overrides or defaults
        self.temperature = self.technical_overrides.get("storyteller_temperature", STORY_CONFIG["storyteller_temperature"])
        self.max_tokens = STORY_CONFIG["max_story_tokens"]
        self.story_arc_type = self.technical_overrides.get("story_arc_type", STORY_CONFIG["story_arc_type"])
    
    def categorize_request(self, user_request: str) -> Dict:
        """Categorize the user's story request and extract key elements."""
        if not self.enable_categorization:
            return {
                "category": "default",
                "characters": [],
                "theme": "",
                "setting": "",
                "elements": [],
                "tone": "neutral"
            }
        
        # Use LLM-based categorizer for better understanding
        return self.categorizer.categorize_and_extract(user_request)
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0, max_delay=60.0)
    def _call_story_api(self, prompt: str) -> str:
        """Make API call with retry logic."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a skilled children's storyteller who creates engaging, age-appropriate bedtime stories with positive messages. You carefully follow user requests and incorporate all specified elements."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=60.0  # 60 second timeout
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from API")
        
        return response.choices[0].message.content
    
    def create_story_prompt(self, user_request: str, categorization: Dict, revision_context: Optional[str] = None, variety_config: Optional[Dict] = None) -> str:
        """Create a comprehensive prompt for story generation."""
        category = categorization.get("category", "default")
        strategy = self.category_strategies.get(category, self.category_strategies["default"])
        safety_guidelines = self.guardrails.generate_safety_prompt_addition()
        
        # Get variety configuration (different narrative style, perspective, etc.)
        if variety_config is None:
            from story_variety import create_variety_config
            variety_config = create_variety_config()
        
        # Generate variety instructions based on config
        narrative_style = variety_config.get("narrative_style", {})
        perspective = variety_config.get("perspective", {})
        structure = variety_config.get("structure", {})
        dialogue_style = variety_config.get("dialogue_style", {})
        moral_style = variety_config.get("moral_style", {})
        world_building = variety_config.get("world_building_focus", "")
        
        variety_instructions = f"""
STORYTELLING VARIETY INSTRUCTIONS:

NARRATIVE STYLE: {narrative_style.get('name', 'Balanced')}
{narrative_style.get('tone_instruction', 'Balance dialogue, description, and action.')}
- Aim for approximately {int(narrative_style.get('dialogue_ratio', 0.4) * 100)}% dialogue in the story
- Balance dialogue with {narrative_style.get('name', 'balanced').lower()} elements

NARRATIVE PERSPECTIVE: {perspective.get('name', 'Third Person')}
{perspective.get('instruction', 'Use third person narration.')}

STORY STRUCTURE: {structure.get('name', 'Linear')}
{structure.get('instruction', 'Tell the story in chronological order.')}

DIALOGUE STYLE: {dialogue_style.get('name', 'Natural')}
{dialogue_style.get('instruction', 'Characters speak naturally.')}

WORLD-BUILDING FOCUS:
{world_building}
- Spend time building the world and setting
- Make the environment interesting and detailed
- Show how characters interact with their world

MORAL INTEGRATION: {moral_style.get('name', 'Show, Don\'t Tell')}
{moral_style.get('instruction', 'Show the moral through actions, don\'t state it directly.')}
- Avoid preaching or stating lessons directly
- Let the story teach through what happens
- Focus on showing, not telling

IMPORTANT VARIETY GUIDELINES:
- Use conversations and dialogue to show relationships and character personalities
- Build the world through descriptions and details
- Show characters doing things, not just thinking about them
- Balance action, dialogue, and description
- Make each story feel unique with its own voice and style
- Avoid repetitive patterns - vary sentence structure and pacing
"""
        
        # Use story arc from technical overrides or config
        story_arc_type = self.story_arc_type
        
        story_arc_guidance = ""
        if story_arc_type == "hero_journey":
            story_arc_guidance = """
Story Structure (Hero's Journey):
1. Beginning: Introduce character and their world
2. Call to Adventure: Something interesting happens
3. Journey: Character faces challenges and makes friends
4. Resolution: Problem is solved through kindness/bravery
5. Return: Character learns a valuable lesson
"""
        elif story_arc_type == "three_act":
            story_arc_guidance = """
Story Structure (Three Act):
1. Act 1: Setup - Introduce characters and setting
2. Act 2: Confrontation - Character faces a challenge
3. Act 3: Resolution - Challenge is overcome, lesson learned
"""
        else:
            story_arc_guidance = """
Story Structure (Simple Adventure):
1. Beginning: Introduce characters
2. Middle: An adventure or challenge occurs
3. End: Happy resolution with a lesson
"""
        
        revision_note = ""
        if revision_context:
            revision_note = f"\n\nREVISION CONTEXT:\n{revision_context}\n\nPlease incorporate the feedback while maintaining the story's core elements."
        
        # Build personalized elements from categorization
        personalization = ""
        if categorization.get("characters"):
            personalization += f"\nCHARACTERS TO INCLUDE: {', '.join(categorization['characters'])}\n"
        if categorization.get("theme"):
            personalization += f"THEME: {categorization['theme']}\n"
        if categorization.get("setting") and categorization['setting'].lower() != "any":
            personalization += f"SETTING: {categorization['setting']}\n"
        if categorization.get("elements"):
            personalization += f"SPECIAL ELEMENTS: {', '.join(categorization['elements'])}\n"
        
        # Add parent settings custom prompts
        parent_custom = self.technical_overrides.get("custom_prompts", "")
        if parent_custom:
            personalization += f"\nPARENT PREFERENCES:\n{parent_custom}\n"
        
        # Use tone from categorization or strategy
        tone = categorization.get("tone", strategy.get("tone", "uplifting"))
        if tone == "neutral":
            tone = strategy.get("tone", "uplifting")
        
        prompt = f"""You are a talented children's storyteller specializing in bedtime stories for ages {STORY_CONFIG['target_age_min']}-{STORY_CONFIG['target_age_max']}.

{safety_guidelines}

STORY REQUEST:
{user_request}

CATEGORY: {category}
FOCUS: {strategy['focus']}
TONE: {tone}
{personalization}

{story_arc_guidance}

STORY REQUIREMENTS:
- Length: Approximately {STORY_CONFIG['max_story_tokens'] // 4} words (engaging but not too long)
- Include: Positive themes, friendship, kindness, and a valuable lesson
- Vocabulary: {STORY_CONFIG['vocabulary_complexity']} for ages {STORY_CONFIG['target_age_min']}-{STORY_CONFIG['target_age_max']}
- Sentences: {STORY_CONFIG['sentence_length']} length
- Ending: Happy, uplifting, with a clear moral or lesson
- Characters: Relatable and well-developed
- IMPORTANT: Follow the story request closely. If specific characters, settings, or elements are mentioned, make sure they are central to the story.

{variety_instructions}
{revision_note}

Please write a complete, engaging bedtime story that follows these guidelines and adheres closely to the user's request. Make it unique with its own voice, style, and perspective:
"""
        return prompt
    
    def generate_story(self, user_request: str, revision_context: Optional[str] = None, variety_config: Optional[Dict] = None) -> Dict:
        """
        Generate a story based on user request.
        Returns dict with story text and metadata.
        """
        categorization = self.categorize_request(user_request)
        
        # Create variety config if not provided (ensures each story is different)
        if variety_config is None:
            variety_config = create_variety_config()
        
        prompt = self.create_story_prompt(user_request, categorization, revision_context, variety_config)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled children's storyteller who creates engaging, age-appropriate bedtime stories with positive messages. You carefully follow user requests and incorporate all specified elements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            story = response.choices[0].message.content
            
            # Validate the story (ensure it's not None)
            if story is None:
                story = ""
            validation = self.guardrails.validate_story(story)
            
            return {
                "story": story,
                "category": categorization.get("category", "default"),
                "categorization": categorization,
                "variety_config": variety_config,
                "validation": validation,
                "is_valid": validation["is_valid"]
            }
        
        except Exception as e:
            return {
                "story": "",
                "category": categorization.get("category", "default"),
                "categorization": categorization,
                "validation": {"is_valid": False, "error": str(e)},
                "is_valid": False,
                "error": str(e)
            }

