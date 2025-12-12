# 🌙 Bedtime Story Generator

A sophisticated AI-powered bedtime story generator that creates age-appropriate stories (ages 5-10) using GPT-3.5-turbo with an LLM judge, guardrails, and iterative refinement.

## 🎯 Overview

This system generates personalized bedtime stories through an agentic workflow that includes:
- **LLM-based categorization** for understanding short and long prompts
- **LLM judge** for quality evaluation with iterative refinement
- **Age-appropriate guardrails** with LLM-based content moderation
- **Story variety system** ensuring unique narratives each time
- **Story storage & observability** with SQLite database
- **Streamlit UI** with three distinct views

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Running the Application

**Streamlit UI (Recommended):**
```bash
streamlit run app.py
```

**Command Line Interface:**
```bash
python main.py
```

## 📱 Three Views

The Streamlit application provides three distinct interfaces:

### 1. 👤 User View
Simple, parent-friendly interface for generating stories with optional preferences.

![User View](dashboard/User%20View.png)

- Clean, intuitive interface
- Parent settings (personas, values, interests)
- One-click story generation
- Quality indicators and feedback

### 2. 📚 Story History
Review and manage all generated stories with search, filtering, and statistics.

![Story History](dashboard/Story%20History.png)

- Search stories by keyword
- Filter by category, score, date
- View detailed metadata
- Export stories as JSON
- Statistics dashboard

### 3. 🔧 Debug View
Advanced observability and hyperparameter tuning for developers.

![Debug Tuning](dashboard/Debug%20Tuning.png)

- Real-time generation monitoring
- Hyperparameter tuning controls
- Detailed observability metrics
- Judge feedback analysis
- Guardrail validation details

## 🏗️ System Architecture

The system uses an orchestrated agentic workflow:

1. **Categorizer** - Analyzes user request and extracts key elements
2. **Storyteller** - Generates story with variety system (narrative style, perspective, structure)
3. **Judge** - Evaluates story quality and provides feedback
4. **Guardrails** - Ensures age-appropriateness and safety
5. **Orchestrator** - Coordinates iterative refinement loop
6. **Storage** - Persists stories with metadata for observability

See [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md) for detailed architecture.

## ✨ Key Features

- **Automatic Variety**: Each story uses a unique narrative style, perspective, and structure
- **Iterative Refinement**: Stories are improved based on judge feedback
- **Robust Error Handling**: Retries, timeouts, and graceful degradation
- **Input Validation**: Comprehensive sanitization and validation
- **Structured Outputs**: JSON mode for reliable parsing
- **Parent-Friendly Config**: Intuitive settings (personas, values, interests)

## 📖 Documentation

- [QUICK_START.md](QUICK_START.md) - Setup and basic usage
- [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) - Detailed UI guide
- [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md) - Architecture and data flow
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Feature documentation

## 🔒 Safety & Guardrails

- Age-appropriate content validation (ages 5-10)
- LLM-based content moderation with keyword fallback
- Prohibited theme detection
- Required positive elements enforcement
- Vocabulary and sentence complexity checks

## 🛠️ Configuration

All system parameters can be tuned in `config.py`:
- Story generation parameters (temperature, tokens, arc type)
- Judge evaluation criteria and thresholds
- Guardrail settings and prohibited themes
- Orchestration settings (refinement, categorization)

## 📝 Requirements

- `openai>=1.0.0` - OpenAI API client
- `streamlit>=1.28.0` - Web UI framework
- `python-dotenv>=1.0.0` - Environment variable management
- `tenacity>=8.2.0` - Retry logic with exponential backoff

## 🎓 Assignment Context

This project was developed as a coding assignment demonstrating:
- Agentic workflow design with multiple LLM agents
- Prompt engineering and iterative refinement strategies
- Production-ready error handling and validation
- Observability and debugging capabilities
- User experience design for different user types

---

**Note**: Remember to add your OpenAI API key to `.env` file. Never commit API keys to version control.
