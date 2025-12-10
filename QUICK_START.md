# Quick Start Guide

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_key_here
     ```
   - Get your API key from: https://platform.openai.com/api-keys

3. **Run the story generator:**
   
   **Option A: Streamlit UI (Recommended)**
   ```bash
   streamlit run app.py
   ```
   Then open your browser to the URL shown (usually http://localhost:8501)
   
   **Option B: Command Line**
   ```bash
   python main.py
   ```

## Basic Usage

### Using Streamlit UI (Recommended)

1. Run `streamlit run app.py`
2. Choose **User View** for a simple interface, **Story History** to review past stories, or **Debug View** for advanced controls
3. In User View:
   - Optionally set story preferences (persona, values, interests)
   - Enter your story request
   - Click "Generate Story"
   - View your personalized story with quality metrics

### Using Command Line

1. When prompted, enter your story request (e.g., "A story about a brave little mouse")
2. The system will:
   - Generate an initial story
   - Evaluate it with the LLM judge
   - Refine it if needed (up to 3 iterations)
   - Display the final story with quality metrics

## Customization

### Parent-Friendly Settings (Streamlit UI)

In the **User View**, you can easily customize stories with:
- **Story Style (Persona)**: Choose from 5 personas (Adventurous Explorer, Creative Dreamer, etc.)
- **Values**: Select values to emphasize (Kindness, Friendship, Courage, etc.)
- **Interests**: Add interests to include (Animals, Space, Dinosaurs, etc.)
- **Child's Name**: Optionally personalize with your child's name

### Advanced Tuning

All technical parameters are tunable in `config.py`. See `TUNING_GUIDE.md` for detailed instructions.

In **Story History View**, you can:
- Review all past stories with search and filtering
- View statistics dashboard (total stories, average scores, category distribution)
- See detailed story metadata (categorization, judge feedback, validation)
- Export stories as JSON

In **Debug View**, you can:
- Tune hyperparameters in real-time
- View observability data (scores, revisions, categorization)
- Monitor guardrail validations
- See detailed judge feedback

### Quick Customizations:

**For more creative stories:**
- Increase `storyteller_temperature` to 0.9

**For faster generation:**
- Set `enable_iterative_refinement` to False
- Reduce `max_revision_attempts` to 1

**For higher quality:**
- Increase `strictness_level` to 9
- Increase `minimum_acceptance_score` to 8.0

## Example Story Requests

- "A story about a girl named Alice and her best friend Bob, who happens to be a cat"
- "An adventure story about a young explorer discovering a magical forest"
- "A friendship story about two animals learning to work together"
- "A fantasy story with a friendly dragon and a brave princess"

## System Architecture

See `SYSTEM_DIAGRAM.md` for a detailed block diagram of the system architecture.

## Troubleshooting

**Error: OPENAI_API_KEY not found**
- Make sure you have a `.env` file with your API key
- Check that the key is correctly formatted

**Stories are too long/short:**
- Adjust `max_story_tokens` in `config.py`

**Stories are not creative enough:**
- Increase `storyteller_temperature` in `config.py`

**Quality scores are too low:**
- Increase `max_revision_attempts` to allow more refinement
- Adjust `storyteller_temperature` for better initial stories

