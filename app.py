"""
Streamlit UI for Bedtime Story Generator
Provides both user-friendly interface and debug/observability view.
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from orchestrator import StoryOrchestrator
from parent_config import PERSONAS, VALUES, INTERESTS, DEFAULT_PARENT_SETTINGS
from config import STORY_CONFIG, JUDGE_CONFIG, GUARDRAIL_CONFIG, ORCHESTRATION_CONFIG
from story_storage import StoryStorage
from utils import validate_user_input, validate_parent_settings

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌙 Bedtime Story Generator",
    page_icon="🌙",
    layout="wide"
)

# Initialize session state
if "stories" not in st.session_state:
    st.session_state.stories = []
if "parent_settings" not in st.session_state:
    st.session_state.parent_settings = DEFAULT_PARENT_SETTINGS.copy()
if "storage" not in st.session_state:
    try:
        st.session_state.storage = StoryStorage()
    except Exception as e:
        st.session_state.storage = None
        st.session_state.storage_error = str(e)

def main():
    """Main Streamlit application."""
    
    # Sidebar for mode selection
    st.sidebar.title("🌙 Story Generator")
    mode = st.sidebar.radio(
        "Select Mode",
        ["👤 User View", "📚 Story History", "🔧 Debug View"],
        help="User View: Simple interface\nStory History: View past stories\nDebug View: Advanced controls"
    )
    
    if mode == "👤 User View":
        user_view()
    elif mode == "📚 Story History":
        story_history_view()
    else:
        debug_view()

def user_view():
    """User-friendly interface for parents and kids."""
    st.title("🌙 Bedtime Story Generator")
    st.markdown("Create personalized, age-appropriate bedtime stories for children aged 5-10")
    
    # Parent Settings Section
    with st.expander("⚙️ Story Preferences (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Persona selection
            persona_options = {k: v["name"] + " - " + v["description"] for k, v in PERSONAS.items()}
            selected_persona = st.selectbox(
                "Story Style",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                index=list(persona_options.keys()).index(st.session_state.parent_settings.get("persona", "balanced_storyteller"))
            )
            
            # Values selection
            value_options = {k: v["name"] for k, v in VALUES.items()}
            selected_values = st.multiselect(
                "Values to Emphasize",
                options=list(value_options.keys()),
                format_func=lambda x: value_options[x],
                default=st.session_state.parent_settings.get("values", ["kindness", "friendship"])
            )
        
        with col2:
            # Interests selection
            interest_options = {k: v["name"] for k, v in INTERESTS.items()}
            selected_interests = st.multiselect(
                "Interests to Include",
                options=list(interest_options.keys()),
                format_func=lambda x: interest_options[x],
                default=st.session_state.parent_settings.get("interests", [])
            )
            
            # Optional child name
            child_name = st.text_input(
                "Child's Name (Optional)",
                value=st.session_state.parent_settings.get("child_name", ""),
                help="If provided, may be used in character names"
            )
        
        # Custom elements
        custom_elements = st.text_area(
            "Additional Elements (Optional)",
            value=st.session_state.parent_settings.get("custom_elements", ""),
            help="Any other elements you'd like included (e.g., 'include a magical garden')",
            height=80
        )
        
        # Update session state
        st.session_state.parent_settings = {
            "persona": selected_persona,
            "values": selected_values,
            "interests": selected_interests,
            "child_name": child_name,
            "custom_elements": custom_elements
        }
    
    # Story Request Section
    st.markdown("---")
    st.subheader("📖 What story would you like to hear?")
    
    # Example requests
    example_requests = [
        "A story about a brave little mouse",
        "An adventure with a friendly dragon",
        "A story about two best friends helping each other",
        "A magical forest adventure"
    ]
    
    selected_example = st.selectbox("Or choose an example:", [""] + example_requests)
    
    user_request = st.text_area(
        "Story Request",
        value=selected_example if selected_example else "",
        height=100,
        placeholder="Tell me what kind of story you want... (e.g., 'A story about a cat and a dog who become friends')"
    )
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("✨ Generate Story", type="primary", use_container_width=True)
    
    if generate_button and user_request.strip():
        with st.spinner("✨ Creating your magical story..."):
            try:
                orchestrator = StoryOrchestrator(parent_settings=st.session_state.parent_settings)
                result = orchestrator.generate_story_with_judge(user_request)
                
                # Store in session
                st.session_state.stories.append(result)
                
                # Display story
                st.markdown("---")
                st.subheader("📖 Your Story")
                st.markdown(f"**Category:** {result['category'].title()}")
                st.markdown(f"**Quality Score:** {result['judge_score']:.1f}/10 ⭐")
                
                st.markdown("---")
                st.markdown(result['story'])
                st.markdown("---")
                
                # Success indicators
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.success(f"✅ Guardrails: Passed" if result['is_valid'] else f"⚠️ Guardrails: Issues")
                with col2:
                    st.success(f"✅ Quality: {'Met' if result['meets_quality_threshold'] else 'Below threshold'}")
                with col3:
                    st.info(f"🔄 Revisions: {result['revision_count']}")
                with col4:
                    st.info(f"📁 Category: {result['category'].title()}")
                
            except Exception as e:
                st.error(f"❌ Error generating story: {str(e)}")
                st.info("Please check that your OPENAI_API_KEY is set in the .env file")
    
    elif generate_button:
        st.warning("⚠️ Please enter a story request!")

def story_history_view():
    """Enhanced observability view with story history, search, and statistics."""
    st.title("📚 Story History & Observability")
    st.markdown("Review past stories, analyze patterns, and track story quality over time")
    
    if st.session_state.storage is None:
        st.error("⚠️ Story storage is not available. Stories are not being saved.")
        if hasattr(st.session_state, 'storage_error'):
            st.info(f"Error: {st.session_state.storage_error}")
        return
    
    storage = st.session_state.storage
    
    # Statistics Dashboard
    with st.expander("📊 Statistics Dashboard", expanded=True):
        try:
            stats = storage.get_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Stories", stats.get('total_stories', 0))
            with col2:
                st.metric("Average Score", f"{stats.get('average_score', 0):.1f}/10")
            with col3:
                st.metric("Quality Threshold Met", stats.get('stories_meeting_threshold', 0))
            with col4:
                st.metric("Avg Revisions", f"{stats.get('average_revisions', 0):.1f}")
            
            if stats.get('category_distribution'):
                st.markdown("**Category Distribution:**")
                cat_data = stats['category_distribution']
                for category, count in cat_data.items():
                    st.progress(count / stats['total_stories'], text=f"{category.title()}: {count}")
        
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
    
    # Search and Filter
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search Stories", placeholder="Search by request or story content...")
    
    with col2:
        filter_category = st.selectbox(
            "Filter by Category",
            options=["All"] + ["adventure", "friendship", "fantasy", "animals", "default"]
        )
    
    col3, col4 = st.columns(2)
    with col3:
        min_score_filter = st.slider("Minimum Score", 0.0, 10.0, 0.0, 0.5)
    with col4:
        max_stories = st.slider("Max Stories to Show", 10, 100, 50)
    
    # Load stories
    try:
        if search_query:
            stories = storage.search_stories(search_query, limit=max_stories)
        elif filter_category != "All":
            stories = storage.filter_stories(
                category=filter_category,
                min_score=min_score_filter if min_score_filter > 0 else None,
                limit=max_stories
            )
        else:
            stories = storage.get_all_stories(limit=max_stories)
        
        if not stories:
            st.info("No stories found. Generate some stories first!")
            return
        
        st.markdown(f"### Found {len(stories)} Stories")
        
        # Story List
        for idx, story in enumerate(stories):
            with st.expander(
                f"Story #{story['id']} - {story['category'].title()} | Score: {story['judge_score']:.1f}/10 | {story['created_at']}",
                expanded=False
            ):
                # Story metadata
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Quality Score", f"{story['judge_score']:.1f}/10")
                with col2:
                    st.metric("Category", story['category'].title())
                with col3:
                    st.metric("Revisions", story['revision_count'])
                with col4:
                    status = "✅ Pass" if story['is_valid'] else "⚠️ Issues"
                    st.metric("Guardrails", status)
                
                # User request
                st.markdown(f"**Original Request:** {story['user_request']}")
                
                # Story text
                st.markdown("**Story:**")
                st.text_area("", value=story['story'], height=200, key=f"story_text_{story['id']}", disabled=True)
                
                # Detailed information
                tab1, tab2, tab3, tab4 = st.tabs(["Categorization", "Judge Feedback", "Validation", "Variety Config"])
                
                with tab1:
                    if story.get('categorization'):
                        st.json(story['categorization'])
                    else:
                        st.info("No categorization data available")
                
                with tab2:
                    if story.get('judge_feedback'):
                        st.text_area("", value=story['judge_feedback'], height=200, key=f"feedback_{story['id']}", disabled=True)
                    else:
                        st.info("No judge feedback available")
                
                with tab3:
                    if story.get('validation'):
                        st.json(story['validation'])
                    else:
                        st.info("No validation data available")
                
                with tab4:
                    if story.get('variety_config'):
                        st.json(story['variety_config'])
                    else:
                        st.info("No variety configuration data available")
                
                # Actions
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete", key=f"delete_{story['id']}"):
                        if storage.delete_story(story['id']):
                            st.success("Story deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete story")
        
        # Export option
        st.markdown("---")
        if st.button("📥 Export All Stories (JSON)"):
            import json
            stories_json = json.dumps(stories, indent=2, default=str)
            st.download_button(
                label="Download Stories",
                data=stories_json,
                file_name=f"stories_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    except Exception as e:
        st.error(f"Error loading stories: {str(e)}")

def debug_view():
    """Debug view with observability and hyperparameter tuning."""
    st.title("🔧 Debug & Observability View")
    st.markdown("Advanced controls for tuning and monitoring story generation")
    
    # Tabs for different debug sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Generation", "⚙️ Hyperparameters", "📈 Observability", "🎯 Parent Settings"])
    
    with tab1:
        st.subheader("Story Generation")
        
        user_request = st.text_area(
            "Story Request",
            height=100,
            placeholder="Enter story request..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            enable_refinement = st.checkbox(
                "Enable Iterative Refinement",
                value=ORCHESTRATION_CONFIG["enable_iterative_refinement"]
            )
            enable_categorization = st.checkbox(
                "Enable Categorization",
                value=ORCHESTRATION_CONFIG["enable_categorization"]
            )
        
        with col2:
            max_revisions = st.slider(
                "Max Revisions",
                min_value=0,
                max_value=5,
                value=JUDGE_CONFIG["max_revision_attempts"]
            )
        
        if st.button("🚀 Generate with Debug Info", type="primary"):
            if user_request.strip():
                with st.spinner("Generating story with debug information..."):
                    # Create temporary config overrides
                    temp_config = {
                        "enable_iterative_refinement": enable_refinement,
                        "enable_categorization": enable_categorization,
                        "max_revision_attempts": max_revisions
                    }
                    
                    # Temporarily override config (in real implementation, would use a config manager)
                    original_refinement = ORCHESTRATION_CONFIG["enable_iterative_refinement"]
                    original_categorization = ORCHESTRATION_CONFIG["enable_categorization"]
                    original_max_revisions = JUDGE_CONFIG["max_revision_attempts"]
                    
                    try:
                        ORCHESTRATION_CONFIG["enable_iterative_refinement"] = enable_refinement
                        ORCHESTRATION_CONFIG["enable_categorization"] = enable_categorization
                        JUDGE_CONFIG["max_revision_attempts"] = max_revisions
                        
                        orchestrator = StoryOrchestrator(parent_settings=st.session_state.parent_settings)
                        result = orchestrator.generate_story_with_judge(user_request)
                        
                        # Display results
                        display_debug_results(result)
                        
                    finally:
                        # Restore original config
                        ORCHESTRATION_CONFIG["enable_iterative_refinement"] = original_refinement
                        ORCHESTRATION_CONFIG["enable_categorization"] = original_categorization
                        JUDGE_CONFIG["max_revision_attempts"] = original_max_revisions
            else:
                st.warning("Please enter a story request")
    
    with tab2:
        st.subheader("Hyperparameter Tuning")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Story Generation")
            storyteller_temp = st.slider(
                "Storyteller Temperature",
                min_value=0.0,
                max_value=1.0,
                value=STORY_CONFIG["storyteller_temperature"],
                step=0.1,
                help="Higher = more creative, Lower = more consistent"
            )
            
            max_tokens = st.slider(
                "Max Story Tokens",
                min_value=500,
                max_value=4000,
                value=STORY_CONFIG["max_story_tokens"],
                step=100
            )
            
            story_arc = st.selectbox(
                "Story Arc Type",
                options=["hero_journey", "three_act", "simple_adventure"],
                index=["hero_journey", "three_act", "simple_adventure"].index(STORY_CONFIG["story_arc_type"])
            )
        
        with col2:
            st.markdown("### Judge Configuration")
            judge_temp = st.slider(
                "Judge Temperature",
                min_value=0.0,
                max_value=1.0,
                value=JUDGE_CONFIG["judge_temperature"],
                step=0.1
            )
            
            strictness = st.slider(
                "Judge Strictness",
                min_value=1,
                max_value=10,
                value=JUDGE_CONFIG["strictness_level"]
            )
            
            min_score = st.slider(
                "Minimum Acceptance Score",
                min_value=0.0,
                max_value=10.0,
                value=JUDGE_CONFIG["minimum_acceptance_score"],
                step=0.5
            )
        
        if st.button("💾 Apply Hyperparameters", type="primary"):
            STORY_CONFIG["storyteller_temperature"] = storyteller_temp
            STORY_CONFIG["max_story_tokens"] = max_tokens
            STORY_CONFIG["story_arc_type"] = story_arc
            JUDGE_CONFIG["judge_temperature"] = judge_temp
            JUDGE_CONFIG["strictness_level"] = strictness
            JUDGE_CONFIG["minimum_acceptance_score"] = min_score
            st.success("✅ Hyperparameters updated! (Note: Changes are temporary for this session)")
    
    with tab3:
        st.subheader("Observability Dashboard")
        
        # Try to load from storage if available
        stories_to_show = []
        if st.session_state.storage:
            try:
                stored_stories = st.session_state.storage.get_all_stories(limit=10)
                stories_to_show = stored_stories
            except:
                stories_to_show = st.session_state.stories
        else:
            stories_to_show = st.session_state.stories
        
        if stories_to_show:
            st.markdown(f"### Generated Stories ({len(stories_to_show)})")
            
            for idx, story_data in enumerate(reversed(stories_to_show[-5:]), 1):
                with st.expander(f"Story #{len(st.session_state.stories) - idx + 1} - Score: {story_data['judge_score']:.1f}/10"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Quality Score", f"{story_data['judge_score']:.1f}/10")
                        st.metric("Category", story_data['category'].title())
                    with col2:
                        st.metric("Revisions", story_data['revision_count'])
                        st.metric("Guardrails", "✅ Pass" if story_data['is_valid'] else "⚠️ Issues")
                    with col3:
                        st.metric("Quality Threshold", "✅ Met" if story_data['meets_quality_threshold'] else "❌ Below")
                    
                    if 'categorization' in story_data:
                        st.markdown("**Categorization Analysis:**")
                        cat = story_data['categorization']
                        st.json({
                            "Category": cat.get("category", "N/A"),
                            "Characters": cat.get("characters", []),
                            "Theme": cat.get("theme", "N/A"),
                            "Setting": cat.get("setting", "N/A"),
                            "Elements": cat.get("elements", [])
                        })
                    
                    if 'judge_feedback' in story_data:
                        with st.expander("Judge Feedback"):
                            st.text(story_data['judge_feedback'])
                    
                    if 'validation' in story_data:
                        with st.expander("Guardrail Validation"):
                            st.json(story_data['validation'])
                    
                    st.markdown("**Story Text:**")
                    st.text_area("", value=story_data['story'], height=200, key=f"story_{idx}", disabled=True)
        else:
            st.info("No stories generated yet. Generate a story to see observability data.")
    
    with tab4:
        st.subheader("Parent Settings Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            persona_options = {k: v["name"] + " - " + v["description"] for k, v in PERSONAS.items()}
            selected_persona = st.selectbox(
                "Persona",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                index=list(persona_options.keys()).index(st.session_state.parent_settings.get("persona", "balanced_storyteller"))
            )
            
            value_options = {k: v["name"] + " - " + v["description"] for k, v in VALUES.items()}
            selected_values = st.multiselect(
                "Values",
                options=list(value_options.keys()),
                format_func=lambda x: value_options[x],
                default=st.session_state.parent_settings.get("values", ["kindness", "friendship"])
            )
        
        with col2:
            interest_options = {k: v["name"] + " - " + v["description"] for k, v in INTERESTS.items()}
            selected_interests = st.multiselect(
                "Interests",
                options=list(interest_options.keys()),
                format_func=lambda x: interest_options[x],
                default=st.session_state.parent_settings.get("interests", [])
            )
            
            child_name = st.text_input("Child's Name (Optional)")
            custom_elements = st.text_area("Custom Elements", height=100)
        
        st.session_state.parent_settings = {
            "persona": selected_persona,
            "values": selected_values,
            "interests": selected_interests,
            "child_name": child_name,
            "custom_elements": custom_elements
        }
        
        st.json(st.session_state.parent_settings)

def display_debug_results(result: Dict):
    """Display detailed debug results."""
    st.markdown("---")
    st.subheader("📊 Generation Results")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Quality Score", f"{result['judge_score']:.1f}/10")
    with col2:
        st.metric("Revisions", result['revision_count'])
    with col3:
        st.metric("Category", result['category'].title())
    with col4:
        st.metric("Guardrails", "✅ Pass" if result['is_valid'] else "⚠️ Fail")
    
    # Story
    st.markdown("### Generated Story")
    st.text_area("", value=result['story'], height=300, disabled=True, key="debug_story")
    
    # Categorization
    if 'categorization' in result:
        st.markdown("### Categorization Analysis")
        st.json(result['categorization'])
    
    # Judge Feedback
    if 'judge_feedback' in result:
        st.markdown("### Judge Feedback")
        st.text_area("", value=result['judge_feedback'], height=200, disabled=True, key="debug_feedback")
    
    # Validation
    if 'validation' in result:
        st.markdown("### Guardrail Validation")
        st.json(result['validation'])

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found in environment variables.")
        st.info("Please create a .env file with your OpenAI API key:\nOPENAI_API_KEY=your_key_here")
        st.stop()
    
    main()

