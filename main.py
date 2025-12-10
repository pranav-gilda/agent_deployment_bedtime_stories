"""
Hippocratic AI Bedtime Story Generator
A sophisticated system for generating age-appropriate bedtime stories (ages 5-10)
with LLM judge evaluation, guardrails, and iterative refinement.
"""

import os
from dotenv import load_dotenv
from orchestrator import StoryOrchestrator
from config import STORY_CONFIG, JUDGE_CONFIG, GUARDRAIL_CONFIG

load_dotenv()

def print_welcome():
    """Print welcome message and system configuration."""
    print("\n" + "="*60)
    print("🌙 BEDTIME STORY GENERATOR 🌙")
    print("="*60)
    print(f"Target Age: {STORY_CONFIG['target_age_min']}-{STORY_CONFIG['target_age_max']} years")
    print(f"Quality Threshold: {JUDGE_CONFIG['minimum_acceptance_score']}/10")
    print(f"Max Revisions: {JUDGE_CONFIG['max_revision_attempts']}")
    print("="*60 + "\n")

def main():
    """Main entry point for the story generator."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_key_here")
        return
    
    print_welcome()
    
    # Initialize orchestrator
    orchestrator = StoryOrchestrator()
    
    # Get user input
    user_input = input("What kind of story do you want to hear? ")
    
    if not user_input.strip():
        print("No input provided. Using example request...")
        user_input = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."
    
    # Generate story with orchestration
    try:
        result = orchestrator.generate_with_user_feedback(user_input)
        
        # Display final story
        print("\n" + "="*60)
        print("📖 FINAL STORY:")
        print("="*60)
        print(result["story"])
        print("="*60)
        
        # Display metadata
        print(f"\n📊 Story Quality Score: {result['judge_score']:.1f}/10")
        print(f"📁 Category: {result['category'].title()}")
        print(f"🔄 Revisions: {result['revision_count']}")
        print(f"✅ Passed Guardrails: {'Yes' if result['is_valid'] else 'No'}")
        print(f"🎯 Meets Quality Threshold: {'Yes' if result['meets_quality_threshold'] else 'No'}")
        
        if result.get('user_feedback_applied'):
            print(f"💬 User Feedback Applied: {result.get('user_requested_changes', 'N/A')}")
        
        # Show judge feedback summary
        if result.get('judge_feedback'):
            print("\n📝 Judge Feedback Summary:")
            feedback_lines = result['judge_feedback'].split('\n')[:5]
            for line in feedback_lines:
                if line.strip():
                    print(f"   {line}")
        
    except Exception as e:
        print(f"\n❌ Error generating story: {str(e)}")
        print("Please check your API key and try again.")


"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

If I had 2 more hours, I would:
1. Implement a more sophisticated categorization system using an LLM to better understand story requests
2. Add story structure templates (beginning/middle/end) that can be filled in iteratively
3. Create a feedback loop that allows users to rate specific parts of the story (characters, plot, ending)
4. Add multilingual support for generating stories in different languages
5. Implement story persistence and a simple database to track story quality over time
6. Add voice narration capabilities using text-to-speech APIs
7. Create a web interface for better user interaction
"""


if __name__ == "__main__":
    main()
