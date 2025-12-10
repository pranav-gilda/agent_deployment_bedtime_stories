# Tuning Guide: Customizing Your Story Generator

This guide explains how to tune the various parameters in `config.py` to customize story generation behavior.

## 🎨 Story Generation Parameters (`STORY_CONFIG`)

### `storyteller_temperature` (0.0 - 1.0)
- **Default**: 0.8
- **What it does**: Controls creativity and randomness in story generation
- **Lower (0.3-0.5)**: More predictable, consistent stories
- **Higher (0.8-1.0)**: More creative, varied stories
- **Tuning tip**: Start at 0.8 for creative stories, lower to 0.6 for more structured narratives

### `max_story_tokens` (500 - 4000)
- **Default**: 2000
- **What it does**: Maximum length of generated story
- **Lower (1000-1500)**: Shorter stories, good for younger children
- **Higher (2500-3000)**: Longer, more detailed stories
- **Tuning tip**: Adjust based on attention span of target age group

### `story_arc_type`
- **Options**: `"hero_journey"`, `"three_act"`, `"simple_adventure"`
- **Default**: `"hero_journey"`
- **What it does**: Determines story structure template
- **`hero_journey`**: Classic adventure with challenges and growth
- **`three_act`**: Traditional beginning-middle-end structure
- **`simple_adventure`**: Straightforward narrative for younger children
- **Tuning tip**: Use `simple_adventure` for ages 5-7, `hero_journey` for 8-10

### `vocabulary_complexity`
- **Options**: `"simple"`, `"age_appropriate"`, `"challenging"`
- **Default**: `"age_appropriate"`
- **What it does**: Controls word choice complexity
- **Tuning tip**: Use `"simple"` for ages 5-6, `"age_appropriate"` for 7-8, `"challenging"` for 9-10

## ⚖️ Judge Parameters (`JUDGE_CONFIG`)

### `judge_temperature` (0.0 - 1.0)
- **Default**: 0.2
- **What it does**: Consistency of judge evaluations
- **Lower (0.1-0.3)**: More consistent, predictable scoring
- **Higher (0.4-0.6)**: More varied evaluations
- **Tuning tip**: Keep low (0.2) for consistent quality control

### `strictness_level` (1 - 10)
- **Default**: 7
- **What it does**: How strict the judge is in evaluation
- **Lower (4-6)**: More lenient, accepts more stories
- **Higher (8-10)**: Very strict, only accepts high-quality stories
- **Tuning tip**: Increase to 8-9 for premium quality, decrease to 5-6 for faster generation

### `minimum_acceptance_score` (0.0 - 10.0)
- **Default**: 7.0
- **What it does**: Minimum score required to accept a story
- **Lower (6.0-6.5)**: Accepts stories with minor issues
- **Higher (7.5-8.0)**: Only accepts high-quality stories
- **Tuning tip**: Balance between quality and generation time

### `max_revision_attempts` (1 - 5)
- **Default**: 3
- **What it does**: Maximum number of refinement iterations
- **Lower (1-2)**: Faster generation, may accept lower quality
- **Higher (4-5)**: More refinement, better quality but slower
- **Tuning tip**: Increase to 4-5 for production quality, decrease to 2 for testing

## 🛡️ Guardrail Parameters (`GUARDRAIL_CONFIG`)

### `enable_content_filter` (True/False)
- **Default**: True
- **What it does**: Filters out prohibited content
- **Tuning tip**: Always keep True for safety

### `enable_age_check` (True/False)
- **Default**: True
- **What it does**: Validates age-appropriateness
- **Tuning tip**: Always keep True for target audience

### `prohibited_themes`
- **Default**: `["violence", "fear", "inappropriate_language", "adult_themes", "scary_monsters", "dangerous_situations"]`
- **What it does**: List of themes to filter out
- **Tuning tip**: Add more themes if needed (e.g., `"sadness"`, `"conflict"`)

### `required_elements`
- **Default**: `["positive_resolution", "kindness", "friendship", "learning_experience"]`
- **What it does**: Elements that must be present in stories
- **Tuning tip**: Add more elements like `"cooperation"`, `"empathy"`, `"courage"`

## 🎭 Orchestration Parameters (`ORCHESTRATION_CONFIG`)

### `enable_iterative_refinement` (True/False)
- **Default**: True
- **What it does**: Enables automatic story improvement loop
- **Tuning tip**: Set to False for faster generation (single pass)

### `enable_user_feedback` (True/False)
- **Default**: True
- **What it does**: Allows users to request changes
- **Tuning tip**: Set to False for automated generation without user interaction

### `enable_categorization` (True/False)
- **Default**: True
- **What it does**: Categorizes requests and applies category-specific strategies
- **Tuning tip**: Set to False to use default strategy for all stories

### `category_strategies`
- **What it does**: Customize generation strategy per category
- **Tuning tip**: Modify `focus`, `tone`, and `structure` for each category to match your preferences

## 🎯 Quick Tuning Presets

### For Ages 5-6 (Younger Children)
```python
STORY_CONFIG = {
    "storyteller_temperature": 0.7,
    "max_story_tokens": 1500,
    "story_arc_type": "simple_adventure",
    "vocabulary_complexity": "simple",
    "sentence_length": "short",
}

JUDGE_CONFIG = {
    "strictness_level": 6,
    "minimum_acceptance_score": 6.5,
}
```

### For Ages 9-10 (Older Children)
```python
STORY_CONFIG = {
    "storyteller_temperature": 0.9,
    "max_story_tokens": 2500,
    "story_arc_type": "hero_journey",
    "vocabulary_complexity": "challenging",
    "sentence_length": "medium",
}

JUDGE_CONFIG = {
    "strictness_level": 8,
    "minimum_acceptance_score": 7.5,
}
```

### For Fast Generation (Testing)
```python
JUDGE_CONFIG = {
    "strictness_level": 5,
    "minimum_acceptance_score": 6.0,
    "max_revision_attempts": 1,
}

ORCHESTRATION_CONFIG = {
    "enable_iterative_refinement": False,
    "enable_user_feedback": False,
}
```

### For Premium Quality
```python
JUDGE_CONFIG = {
    "strictness_level": 9,
    "minimum_acceptance_score": 8.0,
    "max_revision_attempts": 5,
}

STORY_CONFIG = {
    "storyteller_temperature": 0.75,  # Balanced creativity
}
```

## 🔧 Experimentation Tips

1. **Start with defaults**: The default configuration is well-balanced
2. **Change one parameter at a time**: This helps you understand the impact of each setting
3. **Test with various story requests**: Try different categories (adventure, friendship, fantasy)
4. **Monitor judge scores**: If scores are consistently low, adjust `storyteller_temperature` or `strictness_level`
5. **Balance speed vs quality**: More revisions = better quality but slower generation
6. **Age-specific tuning**: Adjust vocabulary and sentence length based on your target age group

## 📊 Understanding Judge Scores

- **9-10**: Exceptional story, publish-ready
- **7-8**: Good story, meets quality standards
- **5-6**: Acceptable but may need improvement
- **Below 5**: Story needs significant revision

Adjust `minimum_acceptance_score` based on your quality requirements.

