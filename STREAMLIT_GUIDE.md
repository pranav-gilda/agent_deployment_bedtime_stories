# Streamlit UI Guide

## Overview

The Streamlit UI provides three views:
1. **User View**: Simple, parent-friendly interface for generating stories
2. **Story History**: Review past stories with search, filtering, and statistics
3. **Debug View**: Advanced controls and observability for tuning

## User View

### Story Preferences

**Story Style (Persona)**
- **Adventurous Explorer**: Exciting journeys and discoveries
- **Creative Dreamer**: Magical and imaginative stories
- **Gentle Friend**: Warm stories about friendship and kindness
- **Curious Learner**: Educational stories with lessons
- **Balanced Storyteller**: Mix of adventure, friendship, and learning

**Values to Emphasize**
Select one or more values to incorporate into stories:
- Kindness
- Friendship
- Courage
- Honesty
- Empathy
- Perseverance
- Gratitude

**Interests to Include**
Add interests that will be incorporated into stories:
- Animals
- Space & Planets
- Dinosaurs
- Princesses & Royalty
- Superheroes
- Nature & Outdoors
- Music & Dance
- Art & Creativity

**Child's Name (Optional)**
If provided, may be used in character names for personalization.

**Additional Elements**
Free-form text for any other elements you'd like included.

### Generating Stories

1. Enter your story request (or choose an example)
2. Click "Generate Story"
3. View your personalized story with:
   - Quality score
   - Category
   - Guardrail status
   - Revision count

## Story History View

The Story History view provides comprehensive observability and review capabilities for all generated stories.

### Statistics Dashboard
- **Total Stories**: Count of all generated stories
- **Average Score**: Mean quality score across all stories
- **Quality Threshold Met**: Number of stories meeting quality standards
- **Average Revisions**: Mean number of refinement iterations
- **Category Distribution**: Breakdown of stories by category

### Search and Filter
- **Search**: Search stories by user request or story content
- **Filter by Category**: Filter stories by category (adventure, friendship, fantasy, animals, default)
- **Filter by Score**: Set minimum/maximum quality score range
- **Limit Results**: Control how many stories to display

### Story Details
For each story, view:
- **Quality Metrics**: Score, category, revisions, guardrail status
- **Full Story Text**: Complete generated story
- **Categorization Analysis**: Extracted characters, theme, setting, elements
- **Judge Feedback**: Detailed evaluation and suggestions
- **Guardrail Validation**: Safety and age-appropriateness checks
- **Variety Configuration**: Narrative style, perspective, structure used

### Actions
- **Delete Stories**: Remove stories from the database
- **Export**: Download all stories as JSON for backup or analysis

## Debug View

### Generation Tab
- Generate stories with debug information
- Toggle iterative refinement
- Toggle categorization
- Adjust max revisions

### Hyperparameters Tab
Tune technical parameters in real-time:
- **Storyteller Temperature**: Creativity level (0.0-1.0)
- **Max Story Tokens**: Story length (500-4000)
- **Story Arc Type**: Structure template
- **Judge Temperature**: Evaluation consistency
- **Judge Strictness**: Quality threshold (1-10)
- **Minimum Acceptance Score**: Quality bar (0-10)

### Observability Tab
View detailed information about generated stories:
- Quality scores and metrics
- Categorization analysis
- Judge feedback
- Guardrail validation results
- Full story text
- Variety configuration

### Parent Settings Tab
Configure parent-friendly settings with detailed descriptions.

## Tips

1. **Start Simple**: Use User View with default settings first
2. **Experiment**: Try different personas and values to see how stories change
3. **Review History**: Use Story History view to review past stories and track quality trends
4. **Search & Filter**: Use search and filters in Story History to find specific stories
5. **Debug Mode**: Use Debug View to understand what's happening under the hood
6. **Observability**: Check the Observability tab to see patterns in story quality
7. **Hyperparameter Tuning**: Adjust parameters in Debug View to optimize for your needs
8. **Export Data**: Export stories as JSON for backup or external analysis

## Running the UI

```bash
streamlit run app.py
```

The UI will open in your default browser at `http://localhost:8501`

