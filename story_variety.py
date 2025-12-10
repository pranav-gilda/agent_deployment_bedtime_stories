"""
Story variety system - adds different narrative styles, perspectives, and structures.
Addresses the issue of stories feeling too similar by introducing controlled randomness
and diverse storytelling approaches.
"""

import random
from typing import Dict, List
from config import STORY_CONFIG

# Narrative Styles - Different ways to tell stories
NARRATIVE_STYLES = {
    "conversational": {
        "name": "Conversational",
        "description": "Heavy on dialogue, characters talk to each other naturally",
        "dialogue_ratio": 0.5,  # 50% dialogue
        "tone_instruction": "Use lots of dialogue and conversations between characters. Show relationships through what they say to each other.",
        "opening_style": "Start with characters talking or a conversation"
    },
    "descriptive": {
        "name": "Descriptive",
        "description": "Rich world-building and vivid descriptions",
        "dialogue_ratio": 0.2,  # 20% dialogue
        "tone_instruction": "Focus on describing the world, setting, and atmosphere. Paint vivid pictures with words. Show what things look, feel, and sound like.",
        "opening_style": "Start with a detailed description of the setting or world"
    },
    "action_oriented": {
        "name": "Action-Oriented",
        "description": "Focus on what happens, movement and events",
        "dialogue_ratio": 0.3,  # 30% dialogue
        "tone_instruction": "Focus on action and what characters do. Show movement, activities, and events happening. Keep the pace moving.",
        "opening_style": "Start with something happening or an action"
    },
    "reflective": {
        "name": "Reflective",
        "description": "Characters think and feel, internal thoughts",
        "dialogue_ratio": 0.35,  # 35% dialogue
        "tone_instruction": "Include characters' thoughts and feelings. Show what they're thinking about. Balance action with reflection.",
        "opening_style": "Start with a character's thoughts or feelings about something"
    },
    "balanced": {
        "name": "Balanced",
        "description": "Mix of dialogue, description, and action",
        "dialogue_ratio": 0.4,  # 40% dialogue
        "tone_instruction": "Balance dialogue, description, and action. Mix conversations with world-building and events.",
        "opening_style": "Start with a balanced mix of setting and character introduction"
    }
}

# Story Perspectives - Different narrative viewpoints
STORY_PERSPECTIVES = {
    "third_person_omniscient": {
        "name": "Third Person (All-Knowing)",
        "description": "Narrator knows everything, can show multiple characters' thoughts",
        "instruction": "Use third person narration where the narrator knows what all characters are thinking and feeling. Use 'he', 'she', 'they'."
    },
    "third_person_limited": {
        "name": "Third Person (One Character)",
        "description": "Follow one main character, see through their eyes",
        "instruction": "Use third person but focus on one main character. Show the story through their perspective. Use 'he', 'she', 'they' but only reveal what the main character knows."
    },
    "first_person": {
        "name": "First Person",
        "description": "Story told by a character using 'I'",
        "instruction": "Tell the story in first person from a character's perspective. Use 'I', 'me', 'my'. The character is telling their own story."
    },
    "second_person": {
        "name": "Second Person (Interactive)",
        "description": "Addresses the reader as 'you', making them part of the story",
        "instruction": "Tell the story using 'you' to address the reader. Make the reader feel like they're part of the adventure. Use 'you', 'your'."
    }
}

# Story Structures - Different ways to organize the narrative
STORY_STRUCTURES = {
    "linear": {
        "name": "Linear",
        "description": "Events happen in chronological order",
        "instruction": "Tell the story in chronological order from beginning to end."
    },
    "in_media_res": {
        "name": "Start in the Middle",
        "description": "Begin with action, then explain how we got there",
        "instruction": "Start the story in the middle of an exciting moment, then go back to show how the characters got there, then continue forward."
    },
    "flashback": {
        "name": "With Flashback",
        "description": "Include a meaningful memory or past event",
        "instruction": "Include a flashback to an earlier time that helps explain the current situation or character motivations."
    },
    "parallel": {
        "name": "Parallel Stories",
        "description": "Follow multiple characters or storylines",
        "instruction": "Follow two or more characters or storylines that eventually come together. Show what different characters are doing."
    }
}

# Opening Styles - Different ways to start stories
OPENING_STYLES = [
    "Start with a character doing something ordinary that becomes extraordinary",
    "Start with a question or mystery",
    "Start with dialogue - someone saying something interesting",
    "Start with a description of an unusual place or object",
    "Start with a character's wish or dream",
    "Start with an action - something happening right away",
    "Start with a sound or sensation",
    "Start with a character's name and what makes them special"
]

# Dialogue Styles - How characters talk
DIALOGUE_STYLES = {
    "natural": {
        "name": "Natural Conversation",
        "instruction": "Characters speak naturally, like real people. Use contractions, simple words, and natural flow."
    },
    "playful": {
        "name": "Playful and Fun",
        "instruction": "Characters use playful language, jokes, and fun expressions. Keep it light and cheerful."
    },
    "thoughtful": {
        "name": "Thoughtful and Reflective",
        "instruction": "Characters think before they speak. Their dialogue shows their thinking process and feelings."
    },
    "energetic": {
        "name": "Energetic and Excited",
        "instruction": "Characters speak with energy and excitement. Use exclamations and enthusiastic language."
    }
}

# World-Building Elements - Things to emphasize
WORLD_BUILDING_FOCUS = [
    "Focus on creating a vivid, interesting world with unique details",
    "Describe the environment and setting in detail",
    "Show how the world works - its rules, magic, or special features",
    "Include sensory details - what things look, sound, feel, smell like",
    "Create interesting places and locations",
    "Show the relationship between characters and their world"
]

# Moral Integration Styles - How to include lessons without preaching
MORAL_STYLES = {
    "show_dont_tell": {
        "name": "Show, Don't Tell",
        "instruction": "Show the moral through actions and events, don't state it directly. Let readers discover the lesson through what happens."
    },
    "embedded": {
        "name": "Embedded in Story",
        "instruction": "Weave the lesson naturally into the story events. Make it part of the plot, not a separate message."
    },
    "character_growth": {
        "name": "Through Character Growth",
        "instruction": "Show the lesson through how a character changes or grows. The moral comes from their journey."
    },
    "subtle": {
        "name": "Subtle and Implied",
        "instruction": "Hint at the lesson but don't state it explicitly. Let it emerge naturally from the story."
    }
}

def get_random_narrative_style() -> Dict:
    """Get a random narrative style."""
    return random.choice(list(NARRATIVE_STYLES.values()))

def get_random_perspective() -> Dict:
    """Get a random story perspective."""
    return random.choice(list(STORY_PERSPECTIVES.values()))

def get_random_structure() -> Dict:
    """Get a random story structure."""
    return random.choice(list(STORY_STRUCTURES.values()))

def get_random_opening() -> str:
    """Get a random opening style."""
    return random.choice(OPENING_STYLES)

def get_random_dialogue_style() -> Dict:
    """Get a random dialogue style."""
    return random.choice(list(DIALOGUE_STYLES.values()))

def get_random_moral_style() -> Dict:
    """Get a random moral integration style."""
    return random.choice(list(MORAL_STYLES.values()))

def get_variety_prompt_additions() -> str:
    """
    Generate prompt additions for story variety.
    Combines different elements to create unique storytelling approaches.
    """
    narrative_style = get_random_narrative_style()
    perspective = get_random_perspective()
    structure = get_random_structure()
    opening = get_random_opening()
    dialogue_style = get_random_dialogue_style()
    moral_style = get_random_moral_style()
    world_building = random.choice(WORLD_BUILDING_FOCUS)
    
    variety_prompt = f"""
STORYTELLING VARIETY INSTRUCTIONS:

NARRATIVE STYLE: {narrative_style['name']}
{narrative_style['tone_instruction']}
- Aim for approximately {int(narrative_style['dialogue_ratio'] * 100)}% dialogue in the story
- Balance dialogue with {narrative_style['name'].lower()} elements

NARRATIVE PERSPECTIVE: {perspective['name']}
{perspective['instruction']}

STORY STRUCTURE: {structure['name']}
{structure['instruction']}

OPENING STYLE:
{opening}

DIALOGUE STYLE: {dialogue_style['name']}
{dialogue_style['instruction']}

WORLD-BUILDING FOCUS:
{world_building}
- Spend time building the world and setting
- Make the environment interesting and detailed
- Show how characters interact with their world

MORAL INTEGRATION: {moral_style['name']}
{moral_style['instruction']}
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
    
    return variety_prompt

def get_weighted_random_style(preference: str = None) -> Dict:
    """
    Get a narrative style, optionally weighted by preference.
    If no preference, returns truly random.
    """
    if preference and preference in NARRATIVE_STYLES:
        # 70% chance of preferred style, 30% random
        if random.random() < 0.7:
            return NARRATIVE_STYLES[preference]
    
    return get_random_narrative_style()

def create_variety_config() -> Dict:
    """
    Create a complete variety configuration for a story.
    Returns a dict with all variety settings.
    """
    return {
        "narrative_style": get_random_narrative_style(),
        "perspective": get_random_perspective(),
        "structure": get_random_structure(),
        "opening": get_random_opening(),
        "dialogue_style": get_random_dialogue_style(),
        "moral_style": get_random_moral_style(),
        "world_building_focus": random.choice(WORLD_BUILDING_FOCUS)
    }

