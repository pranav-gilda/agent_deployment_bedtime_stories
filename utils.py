"""
Utility functions for error handling, retries, and validation.
"""

import time
import re
from typing import Tuple, Optional
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError


def validate_user_input(user_request: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user input before processing.
    Returns (is_valid, error_message)
    """
    if not user_request:
        return False, "Input cannot be empty"
    
    if not isinstance(user_request, str):
        return False, "Input must be a string"
    
    user_request = user_request.strip()
    
    if not user_request:
        return False, "Input cannot be empty or only whitespace"
    
    if len(user_request) > 5000:
        return False, f"Input too long ({len(user_request)} characters). Maximum 5000 characters allowed."
    
    if len(user_request) < 2:
        return False, "Input too short. Please provide at least 2 characters."
    
    # Check for potentially malicious content (basic)
    dangerous_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, user_request, re.IGNORECASE):
            return False, "Input contains potentially unsafe content"
    
    return True, None


def validate_parent_settings(parent_settings: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate parent settings structure.
    Returns (is_valid, error_message)
    """
    if not isinstance(parent_settings, dict):
        return False, "Parent settings must be a dictionary"
    
    valid_personas = ["adventurous_explorer", "creative_dreamer", "gentle_friend", 
                     "curious_learner", "balanced_storyteller"]
    valid_values = ["kindness", "friendship", "courage", "honesty", "empathy", 
                   "perseverance", "gratitude"]
    valid_interests = ["animals", "space", "dinosaurs", "princesses", "superheroes", 
                      "nature", "music", "art"]
    
    if "persona" in parent_settings:
        if parent_settings["persona"] not in valid_personas:
            return False, f"Invalid persona. Must be one of: {valid_personas}"
    
    if "values" in parent_settings:
        if not isinstance(parent_settings["values"], list):
            return False, "Values must be a list"
        for value in parent_settings["values"]:
            if value not in valid_values:
                return False, f"Invalid value: {value}. Must be one of: {valid_values}"
    
    if "interests" in parent_settings:
        if not isinstance(parent_settings["interests"], list):
            return False, "Interests must be a list"
        for interest in parent_settings["interests"]:
            if interest not in valid_interests:
                return False, f"Invalid interest: {interest}. Must be one of: {valid_interests}"
    
    if "child_name" in parent_settings and parent_settings["child_name"]:
        if not isinstance(parent_settings["child_name"], str):
            return False, "Child name must be a string"
        if len(parent_settings["child_name"]) > 100:
            return False, "Child name too long (max 100 characters)"
    
    return True, None


def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    Decorator for retrying API calls with exponential backoff.
    Handles rate limits, connection errors, and timeouts.
    """
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=base_delay, min=base_delay, max=max_delay),
            retry=retry_if_exception_type((RateLimitError, APIConnectionError, APITimeoutError)),
            reraise=True
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (RateLimitError, APIConnectionError, APITimeoutError) as e:
                # Log the error (in production, use proper logging)
                print(f"⚠️  API error (will retry): {type(e).__name__}: {str(e)}")
                raise
            except APIError as e:
                # Don't retry on other API errors (e.g., invalid API key, bad request)
                print(f"❌ API error (won't retry): {type(e).__name__}: {str(e)}")
                raise
            except Exception as e:
                # Don't retry on unexpected errors
                print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


def safe_parse_json(text: str, fallback: Optional[dict] = None) -> dict:
    """
    Safely parse JSON from text, with fallback.
    """
    import json
    if fallback is None:
        fallback = {}
    
    try:
        # Try to find JSON in the text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return fallback
    except (json.JSONDecodeError, AttributeError):
        return fallback


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input/output.
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        return str(text)[:max_length]
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "... [truncated]"
    
    return text

