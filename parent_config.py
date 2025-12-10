"""
Parent-friendly configuration with personas, values, and interests.
Maps intuitive parent settings to technical parameters.
"""

from typing import Dict, List

# Parent-Friendly Personas
PERSONAS = {
    "adventurous_explorer": {
        "name": "Adventurous Explorer",
        "description": "Loves exciting journeys and discoveries",
        "technical_mapping": {
            "storyteller_temperature": 0.85,
            "story_arc_type": "hero_journey",
            "tone": "exciting but safe"
        }
    },
    "creative_dreamer": {
        "name": "Creative Dreamer",
        "description": "Enjoys magical and imaginative stories",
        "technical_mapping": {
            "storyteller_temperature": 0.9,
            "story_arc_type": "hero_journey",
            "tone": "mystical but not scary"
        }
    },
    "gentle_friend": {
        "name": "Gentle Friend",
        "description": "Prefers warm stories about friendship and kindness",
        "technical_mapping": {
            "storyteller_temperature": 0.75,
            "story_arc_type": "three_act",
            "tone": "warm and caring"
        }
    },
    "curious_learner": {
        "name": "Curious Learner",
        "description": "Enjoys educational stories with lessons",
        "technical_mapping": {
            "storyteller_temperature": 0.7,
            "story_arc_type": "three_act",
            "tone": "educational and fun"
        }
    },
    "balanced_storyteller": {
        "name": "Balanced Storyteller",
        "description": "A mix of adventure, friendship, and learning",
        "technical_mapping": {
            "storyteller_temperature": 0.8,
            "story_arc_type": "hero_journey",
            "tone": "uplifting"
        }
    }
}

# Values to Incorporate
VALUES = {
    "kindness": {
        "name": "Kindness",
        "description": "Emphasize acts of kindness and helping others",
        "prompt_addition": "The story should emphasize kindness, helping others, and being considerate."
    },
    "friendship": {
        "name": "Friendship",
        "description": "Focus on building and maintaining friendships",
        "prompt_addition": "The story should highlight the importance of friendship, working together, and supporting each other."
    },
    "courage": {
        "name": "Courage",
        "description": "Teach about being brave and facing challenges",
        "prompt_addition": "The story should show characters being brave, facing fears, and overcoming challenges with courage."
    },
    "honesty": {
        "name": "Honesty",
        "description": "Emphasize truthfulness and integrity",
        "prompt_addition": "The story should teach the value of honesty, telling the truth, and being trustworthy."
    },
    "empathy": {
        "name": "Empathy",
        "description": "Help understand others' feelings",
        "prompt_addition": "The story should help children understand others' feelings and perspectives, showing empathy and compassion."
    },
    "perseverance": {
        "name": "Perseverance",
        "description": "Teach about not giving up",
        "prompt_addition": "The story should show characters not giving up, trying again, and persevering through difficulties."
    },
    "gratitude": {
        "name": "Gratitude",
        "description": "Emphasize being thankful",
        "prompt_addition": "The story should emphasize gratitude, being thankful for what we have, and appreciating others."
    }
}

# Common Interests/Hobbies
INTERESTS = {
    "animals": {
        "name": "Animals",
        "description": "Include animals as main characters or important elements",
        "prompt_addition": "Include animals as main characters or important story elements. Make them friendly and relatable."
    },
    "space": {
        "name": "Space & Planets",
        "description": "Incorporate space, stars, planets, or astronauts",
        "prompt_addition": "Incorporate space themes like stars, planets, rockets, or friendly astronauts. Keep it age-appropriate and not scary."
    },
    "dinosaurs": {
        "name": "Dinosaurs",
        "description": "Include friendly dinosaurs",
        "prompt_addition": "Include friendly, non-scary dinosaurs as characters. They should be kind and approachable."
    },
    "princesses": {
        "name": "Princesses & Royalty",
        "description": "Include princesses, castles, or royal themes",
        "prompt_addition": "Include princesses, castles, or royal themes. Focus on kindness, leadership, and helping others rather than just being royal."
    },
    "superheroes": {
        "name": "Superheroes",
        "description": "Include superhero themes with positive powers",
        "prompt_addition": "Include superhero themes where characters use their powers (like kindness, helping, or friendship) to help others. No violence."
    },
    "nature": {
        "name": "Nature & Outdoors",
        "description": "Focus on nature, forests, gardens, or outdoor adventures",
        "prompt_addition": "Set the story in nature - forests, gardens, mountains, or outdoor settings. Include appreciation for nature."
    },
    "music": {
        "name": "Music & Dance",
        "description": "Incorporate music, singing, or dancing",
        "prompt_addition": "Incorporate music, singing, dancing, or musical instruments as important story elements."
    },
    "art": {
        "name": "Art & Creativity",
        "description": "Include art, drawing, painting, or creative activities",
        "prompt_addition": "Include art, drawing, painting, or creative activities as important story elements. Show how creativity helps solve problems."
    }
}

# Default Parent Settings
DEFAULT_PARENT_SETTINGS = {
    "persona": "balanced_storyteller",
    "values": ["kindness", "friendship"],  # Default values
    "interests": [],  # No specific interests by default
    "child_name": "",  # Optional: personalize with child's name
    "custom_elements": ""  # Optional: any other elements to include
}

def get_persona_config(persona_key: str) -> Dict:
    """Get technical configuration for a persona."""
    return PERSONAS.get(persona_key, PERSONAS["balanced_storyteller"])

def get_values_prompts(value_keys: List[str]) -> str:
    """Get combined prompt additions for selected values."""
    prompts = []
    for key in value_keys:
        if key in VALUES:
            prompts.append(VALUES[key]["prompt_addition"])
    return "\n".join(prompts)

def get_interests_prompts(interest_keys: List[str]) -> str:
    """Get combined prompt additions for selected interests."""
    prompts = []
    for key in interest_keys:
        if key in INTERESTS:
            prompts.append(INTERESTS[key]["prompt_addition"])
    return "\n".join(prompts)

def apply_parent_settings_to_config(parent_settings: Dict) -> Dict:
    """
    Convert parent-friendly settings to technical configuration.
    Returns a dict that can override STORY_CONFIG values.
    """
    persona_key = parent_settings.get("persona", "balanced_storyteller")
    persona = get_persona_config(persona_key)
    
    technical_overrides = persona["technical_mapping"].copy()
    
    # Add custom elements from parent settings
    custom_prompts = []
    
    # Add values
    values = parent_settings.get("values", [])
    if values:
        custom_prompts.append(get_values_prompts(values))
    
    # Add interests
    interests = parent_settings.get("interests", [])
    if interests:
        custom_prompts.append(get_interests_prompts(interests))
    
    # Add child name if provided
    child_name = parent_settings.get("child_name", "")
    if child_name:
        custom_prompts.append(f"If appropriate, consider incorporating the name '{child_name}' as a character name, or use it as inspiration for character names.")
    
    # Add custom elements
    custom_elements = parent_settings.get("custom_elements", "")
    if custom_elements:
        custom_prompts.append(f"Additional elements to incorporate: {custom_elements}")
    
    technical_overrides["custom_prompts"] = "\n\n".join(custom_prompts)
    
    return technical_overrides

