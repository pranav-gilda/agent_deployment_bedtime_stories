# System Architecture Block Diagram

## Bedtime Story Generator System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                    │
│                    "A story about a cat and a dog"                      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                       │
│  - Coordinates workflow                                                 │
│  - Manages iterative refinement                                         │
│  - Handles user feedback loop                                           │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    REQUEST CATEGORIZER                                  │
│  (Optional - if enabled)                                                │
│  Categories: Adventure, Friendship, Fantasy, Animals, Default           │
│  └─> Selects appropriate generation strategy                            │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STORYTELLER AGENT                                  │
│  - Uses GPT-3.5-turbo                                                   │
│  - Applies category-specific strategy                                   │
│  - Incorporates safety guidelines                                       │
│  - Generates story with appropriate structure                           │
│  - Includes variety system (narrative style, perspective, structure)    │
│  - Retry logic with exponential backoff                                 │
│  - Input validation and sanitization                                   │
│                                                                         │
│  Input: User request + Category + Safety guidelines + Variety config    │
│  Output: Generated story                                                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      GUARDRAILS SYSTEM                                  │
│  - Content Safety Check:                                                │
│    • LLM-based context-aware moderation (primary)                       │
│    • Keyword-based fallback with context checking                       │
│    • Prohibited themes (violence, fear, etc.)                           │
│    • Inappropriate language detection                                   │
│  - Age-Appropriateness Check:                                           │
│    • Sentence length validation                                         │
│    • Vocabulary complexity check                                        │
│    • Positive elements verification                                     │
│  - Error handling with fallback mechanisms                              │
│                                                                         │
│  Output: Validation result (is_valid, violations, issues)               │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────┴──────────┐
                    │  Valid?             │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                   NO                    YES
                    │                     │
                    ▼                     ▼
        ┌──────────────────┐   ┌──────────────────────────────┐
        │ Request Revision │   │   LLM JUDGE AGENT            │
        │ (with safety     │   │   - Uses GPT-3.5-turbo       │
        │  focus)          │   │   - Evaluates on criteria:   │
        └────────┬─────────┘   │     • Age-appropriateness    │
                 │             │     • Story structure        │
                 │             │     • Character development  │
                 │             │     • Moral value            │
                 │             │     • Engagement level       │
                 │             │     • Language complexity    │
                 │             │   - Provides score (0-10)    │
                 │             │   - Detailed feedback        │
                 │             │   - Verdict: ACCEPT/REVISE   │
                 │             └──────────────┬───────────────┘
                 │                            │
                 │                            ▼
                 │                  ┌──────────────────┐
                 │                  │ Score >= 7.0?    │
                 │                  └────────┬─────────┘
                 │                           │
                 │                  ┌────────┴───────┐
                 │                  │                │
                 │                 NO               YES
                 │                  │                │
                 │                  ▼                │
                 │         ┌─────────────────┐       │
                 │         │ Generate        │       │
                 │         │ Revision Prompt │       │
                 │         │ (with feedback) │       │
                 │         └────────┬────────┘       │
                 │                  │                │
                 │                  │                │
                 └──────────────────┴────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   ITERATIVE REFINEMENT LOOP   │
                    │   (Max 3 attempts)            │
                    │                               │
                    │   Storyteller → Judge →       │
                    │   (if not accepted) → Revise  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   FINAL VALIDATION            │
                    │   - Guardrails check          │
                    │   - Final judge evaluation    │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   USER FEEDBACK LOOP          │
                    │   (Optional)                  │
                    │   - Display story             │
                    │   - Request changes           │
                    │   - Generate revised version  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   STORY STORAGE               │
                    │   - SQLite database           │
                    │   - Automatic persistence     │
                    │   - Error handling & retries  │
                    │   - WAL mode for concurrency  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   FINAL OUTPUT                │
                    │   - Story text                │
                    │   - Quality score             │
                    │   - Category                  │
                    │   - Variety configuration     │
                    │   - Metadata                  │
                    │   - Story ID (if saved)       │
                    └───────────────────────────────┘
```

## Component Details

### 1. **Orchestrator**
- Central coordinator for the entire workflow
- Manages iterative refinement loop
- Handles user feedback integration
- Tracks revision attempts
- Integrates story storage with error handling
- Manages variety configuration per story

### 2. **Request Categorizer**
- LLM-based analysis of user input (handles short and long prompts)
- Extracts characters, themes, settings, elements
- Applies category-specific generation strategies
- Categories: Adventure, Friendship, Fantasy, Animals, Default
- Retry logic with exponential backoff
- Input validation and sanitization

### 3. **Storyteller Agent**
- Primary story generation component
- Uses GPT-3.5-turbo with configurable temperature
- Incorporates safety guidelines and age-appropriate constraints
- Applies story structure templates (Hero's Journey, Three Act, Simple Adventure)
- **Story Variety System**: Random narrative styles, perspectives, structures per story
- **Error Handling**: Retry logic with exponential backoff, timeout handling
- **Input Validation**: Comprehensive validation and sanitization
- **Parent Settings Integration**: Personas, values, interests

### 4. **Guardrails System**
- **Content Safety**: 
  - LLM-based context-aware moderation (primary method)
  - Keyword-based fallback with context checking
  - Filters prohibited themes, inappropriate language
- **Age-Appropriateness**: Validates vocabulary, sentence length, positive elements
- **Error Handling**: Graceful fallback to keyword-based checks if LLM fails
- Provides validation feedback for refinement

### 5. **LLM Judge Agent**
- Evaluates story quality on multiple criteria
- **Structured Outputs**: Uses JSON mode for reliable parsing
- Provides detailed feedback and scoring (0-10)
- Makes accept/reject decisions based on quality threshold
- Generates revision prompts when needed
- **Error Handling**: Retry logic, fallback parsing, timeout handling

### 6. **Iterative Refinement Loop**
- Automatically refines stories that don't meet quality threshold
- Maximum 3 revision attempts
- Uses judge feedback to guide improvements

### 7. **User Feedback Loop** (Optional)
- Allows users to request specific changes
- Generates revised versions based on user input
- Enhances user experience and story customization

### 8. **Story Storage System**
- SQLite database for persistent storage
- Automatic saving of all generated stories
- Stores complete metadata (categorization, scores, variety config, etc.)
- **Error Handling**: Retry logic, WAL mode for concurrency, graceful degradation
- Search and filter capabilities
- Statistics and analytics

### 9. **Error Handling & Resilience**
- **Retry Logic**: Exponential backoff for API calls (rate limits, timeouts)
- **Input Validation**: Comprehensive validation of user inputs and settings
- **Timeout Handling**: Configurable timeouts for all API calls
- **Graceful Degradation**: Fallback mechanisms when primary methods fail
- **Error Recovery**: System continues operation even if non-critical components fail

## Configuration Points

All components are highly configurable through `config.py`:
- Story generation parameters (temperature, tokens, structure)
- Judge evaluation criteria and thresholds
- Guardrail settings and prohibited content
- Orchestration behavior (iterative refinement, user feedback)
- Category-specific strategies

## Data Flow

1. **User Request** → Input Validation → Orchestrator
2. **Orchestrator** → Categorizer (with retry) → Storyteller (with retry)
3. **Storyteller** → Guardrails (LLM-based with fallback) → Validation
4. **Valid Story** → Judge (JSON mode, with retry) → Evaluation
5. **If not accepted** → Revision Prompt → Storyteller (loop)
6. **Final Story** → Story Storage (with error handling) → User Feedback (optional) → Final Output

## Error Handling Flow

- **API Failures**: Retry with exponential backoff (up to 3 attempts)
- **Rate Limits**: Automatic backoff and retry
- **Timeouts**: Configurable timeouts (30-60 seconds)
- **Empty Responses**: Validation and fallback handling
- **Database Errors**: Retry logic, WAL mode, graceful degradation
- **Invalid Inputs**: Comprehensive validation with clear error messages
- **Guardrail Failures**: Fallback to keyword-based checks
- **Judge Parsing Errors**: JSON mode with fallback parsing

## Key Improvements

1. **Robust Error Handling**: Retry logic, timeouts, graceful degradation
2. **Structured Outputs**: JSON mode for judge responses (reliable parsing)
3. **LLM-Based Guardrails**: Context-aware content moderation with fallback
4. **Input Validation**: Comprehensive validation of all user inputs
5. **Story Variety**: Random narrative styles ensure unique stories
6. **Persistent Storage**: SQLite database with error handling
7. **Production-Ready**: Handles edge cases, API failures, and errors gracefully

