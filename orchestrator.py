"""
Orchestration system that coordinates storyteller, judge, and guardrails.
Implements iterative refinement workflow for high-quality stories.
"""

from typing import Dict, Optional
from storyteller import Storyteller
from judge import StoryJudge
from guardrails import StoryGuardrails
from config import JUDGE_CONFIG, ORCHESTRATION_CONFIG
from story_storage import StoryStorage
from story_variety import create_variety_config


class StoryOrchestrator:
    """Orchestrates the story generation workflow with iterative refinement."""
    
    def __init__(self, parent_settings: Optional[Dict] = None, enable_storage: bool = True):
        self.storyteller = Storyteller(parent_settings=parent_settings)
        self.judge = StoryJudge()
        self.guardrails = StoryGuardrails()
        self.enable_iterative_refinement = ORCHESTRATION_CONFIG["enable_iterative_refinement"]
        self.max_revisions = JUDGE_CONFIG["max_revision_attempts"]
        self.storage = StoryStorage() if enable_storage else None
    
    def generate_story_with_judge(self, user_request: str) -> Dict:
        """
        Generate a story with judge evaluation and iterative refinement.
        Returns comprehensive result with story, scores, and metadata.
        """
        print("\n📚 Starting story generation...")
        print(f"📝 User request: {user_request}\n")
        
        # Create variety config for this story (ensures uniqueness)
        variety_config = create_variety_config()
        
        # Initial story generation
        print("✨ Generating initial story...")
        result = self.storyteller.generate_story(user_request, variety_config=variety_config)
        
        if not result["is_valid"]:
            print("⚠️  Initial story failed guardrail checks. Attempting revision...")
            # Try once more with explicit safety focus
            revision_context = "Please ensure the story passes all safety and age-appropriateness checks."
            result = self.storyteller.generate_story(user_request, revision_context)
        
        story = result["story"]
        revision_count = 0
        
        # Iterative refinement loop
        if self.enable_iterative_refinement:
            while revision_count < self.max_revisions:
                print(f"\n🔍 Evaluating story (attempt {revision_count + 1})...")
                
                # Judge evaluation
                evaluation = self.judge.evaluate_story(story, user_request)
                
                print(f"📊 Judge score: {evaluation['overall_score']:.1f}/10")
                print(f"✅ Verdict: {evaluation['verdict']}")
                
                # Check if story meets threshold
                if evaluation["meets_threshold"]:
                    print("🎉 Story approved by judge!")
                    break
                
                # If not approved and we have revisions left, refine
                if revision_count < self.max_revisions - 1:
                    print(f"🔄 Refining story based on feedback...")
                    revision_prompt = self.judge.generate_revision_prompt(
                        story, 
                        evaluation["detailed_feedback"], 
                        user_request
                    )
                    
                    # Generate revised story (keep same variety config for consistency)
                    revised_result = self.storyteller.generate_story(user_request, revision_prompt, variety_config=variety_config)
                    
                    if revised_result["is_valid"]:
                        story = revised_result["story"]
                        revision_count += 1
                    else:
                        print("⚠️  Revised story failed guardrails. Using previous version.")
                        break
                else:
                    print("⚠️  Maximum revisions reached. Using current version.")
                    break
        
        # Final validation
        final_validation = self.guardrails.validate_story(story)
        
        # Final evaluation
        final_evaluation = self.judge.evaluate_story(story, user_request)
        
        final_result = {
            "story": story,
            "user_request": user_request,
            "category": result.get("category", "default"),
            "categorization": result.get("categorization", {}),
            "variety_config": variety_config,
            "revision_count": revision_count,
            "judge_score": final_evaluation["overall_score"],
            "judge_feedback": final_evaluation["detailed_feedback"],
            "validation": final_validation,
            "is_valid": final_validation["is_valid"],
            "meets_quality_threshold": final_evaluation["meets_threshold"],
            "parent_settings": self.storyteller.parent_settings
        }
        
        # Store the story
        if self.storage:
            story_id = self.storage.save_story(final_result)
            if story_id > 0:
                final_result["story_id"] = story_id
                print(f"💾 Story saved with ID: {story_id}")
            else:
                print(f"⚠️  Warning: Could not save story to database")
        
        return final_result
    
    def generate_with_user_feedback(self, user_request: str) -> Dict:
        """
        Generate story with option for user feedback and refinement.
        """
        result = self.generate_story_with_judge(user_request)
        
        if ORCHESTRATION_CONFIG["enable_user_feedback"]:
            print("\n" + "="*60)
            print("📖 YOUR STORY:")
            print("="*60)
            print(result["story"])
            print("="*60)
            
            print(f"\n📊 Quality Score: {result['judge_score']:.1f}/10")
            
            feedback = input("\n💬 Would you like to request changes? (yes/no): ").strip().lower()
            
            if feedback in ["yes", "y"]:
                changes = input("What would you like to change? ")
                revised_result = self.storyteller.generate_story(
                    f"{user_request}. Please incorporate: {changes}",
                    f"User requested changes: {changes}"
                )
                
                if revised_result["is_valid"]:
                    result["story"] = revised_result["story"]
                    result["user_feedback_applied"] = True
                    result["user_requested_changes"] = changes
        
        return result

