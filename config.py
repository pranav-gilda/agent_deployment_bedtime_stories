"""
Configuration file for tunable parameters in the bedtime story generator.
Adjust these values to customize story generation behavior.
"""

# Story Generation Parameters
STORY_CONFIG = {
    # Temperature controls creativity (0.0 = deterministic, 1.0 = very creative)
    "storyteller_temperature": 0.8,  # Higher for more creative stories
    
    # Maximum tokens for the story
    "max_story_tokens": 2000,
    
    # Story structure parameters
    "include_moral": True,  # Whether to include a moral lesson
    "include_characters": True,  # Whether to develop characters
    "story_arc_type": "hero_journey",  # Options: "hero_journey", "three_act", "simple_adventure"
    
    # Age-specific parameters (5-10 years)
    "target_age_min": 5,
    "target_age_max": 10,
    "vocabulary_complexity": "age_appropriate",  # Options: "simple", "age_appropriate", "challenging"
    "sentence_length": "short_to_medium",  # Options: "short", "short_to_medium", "medium"
}

# Judge Parameters
JUDGE_CONFIG = {
    # Temperature for judge (lower = more consistent evaluation)
    "judge_temperature": 0.2,
    
    # Maximum tokens for judge evaluation
    "max_judge_tokens": 500,
    
    # Judge strictness (1-10, higher = stricter)
    "strictness_level": 7,
    
    # What the judge evaluates
    "evaluation_criteria": [
        "age_appropriateness",
        "story_structure",
        "character_development",
        "moral_value",
        "engagement_level",
        "language_complexity"
    ],
    
    # Minimum score to accept story (0-10)
    "minimum_acceptance_score": 7.0,
    
    # Maximum revision attempts
    "max_revision_attempts": 3,
}

# Guardrail Parameters
GUARDRAIL_CONFIG = {
    # Enable/disable guardrails
    "enable_content_filter": True,
    "enable_age_check": True,
    "enable_safety_check": True,
    
    # Prohibited content categories
    "prohibited_themes": [
        "violence",
        "fear",
        "inappropriate_language",
        "adult_themes",
        "scary_monsters",
        "dangerous_situations"
    ],
    
    # Required positive elements
    "required_elements": [
        "positive_resolution",
        "kindness",
        "friendship",
        "learning_experience"
    ],
}

# Orchestration Parameters
ORCHESTRATION_CONFIG = {
    # Enable iterative refinement
    "enable_iterative_refinement": True,
    
    # Enable user feedback loop
    "enable_user_feedback": True,
    
    # Story categorization
    "enable_categorization": True,
    
    # Categories and their strategies
    "category_strategies": {
        "adventure": {
            "focus": "exploration and discovery",
            "tone": "exciting but safe",
            "structure": "hero_journey"
        },
        "friendship": {
            "focus": "relationships and empathy",
            "tone": "warm and caring",
            "structure": "three_act"
        },
        "fantasy": {
            "focus": "magic and wonder",
            "tone": "mystical but not scary",
            "structure": "hero_journey"
        },
        "animals": {
            "focus": "nature and animals",
            "tone": "educational and fun",
            "structure": "simple_adventure"
        },
        "default": {
            "focus": "general positive themes",
            "tone": "uplifting",
            "structure": "three_act"
        }
    }
}

# Model Configuration
MODEL_CONFIG = {
    "model_name": "gpt-3.5-turbo",
    "api_version": "v1",  # Using latest API version
}

