"""
Story storage and persistence system.
Stores all generated stories with metadata for observability and review.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
import time
from contextlib import contextmanager

class StoryStorage:
    """Manages persistent storage of generated stories."""
    
    def __init__(self, db_path: str = "stories.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def _get_connection(self, timeout=30.0):
        """Get database connection with timeout and retry logic."""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=timeout)
                conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
                yield conn
                conn.close()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
            except Exception as e:
                raise
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        story_text TEXT NOT NULL,
                        user_request TEXT NOT NULL,
                        category TEXT,
                        categorization TEXT,
                        judge_score REAL,
                        judge_feedback TEXT,
                        revision_count INTEGER,
                        is_valid INTEGER,
                        meets_quality_threshold INTEGER,
                        validation TEXT,
                        parent_settings TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        story_hash TEXT
                    )
                ''')
                
                # Index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON stories(created_at DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_category ON stories(category)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_score ON stories(judge_score DESC)
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"⚠️  Database initialization error: {e}")
            # Continue anyway - database might already exist
        except Exception as e:
            print(f"⚠️  Unexpected error initializing database: {e}")
    
    def save_story(self, story_data: Dict) -> int:
        """
        Save a story to the database.
        Returns the story ID.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Convert complex objects to JSON
                categorization_json = json.dumps(story_data.get("categorization", {}))
                validation_json = json.dumps(story_data.get("validation", {}))
                parent_settings_json = json.dumps(story_data.get("parent_settings", {}))
                
                # Create a simple hash for deduplication (optional)
                story_hash = str(hash(story_data.get("story", "")))
                
                cursor.execute('''
                    INSERT INTO stories (
                        story_text, user_request, category, categorization,
                        judge_score, judge_feedback, revision_count,
                        is_valid, meets_quality_threshold, validation,
                        parent_settings, story_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story_data.get("story", ""),
                    story_data.get("user_request", ""),
                    story_data.get("category", "default"),
                    categorization_json,
                    story_data.get("judge_score", 0.0),
                    story_data.get("judge_feedback", ""),
                    story_data.get("revision_count", 0),
                    1 if story_data.get("is_valid", False) else 0,
                    1 if story_data.get("meets_quality_threshold", False) else 0,
                    validation_json,
                    parent_settings_json,
                    story_hash
                ))
                
                story_id = cursor.lastrowid
                conn.commit()
                
                return story_id if story_id is not None else 0
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"⚠️  Database locked, story not saved: {e}")
            else:
                print(f"⚠️  Database error saving story: {e}")
            return 0
        except Exception as e:
            print(f"⚠️  Error saving story: {e}")
            return 0
    
    def get_story(self, story_id: int) -> Optional[Dict]:
        """Retrieve a story by ID."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM stories WHERE id = ?', (story_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"⚠️  Error retrieving story: {e}")
            return None
    
    def get_all_stories(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """Retrieve all stories, optionally limited."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM stories ORDER BY created_at DESC'
                if limit:
                    query += f' LIMIT {limit} OFFSET {offset}'
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️  Error retrieving stories: {e}")
            return []
    
    def search_stories(self, query: str, limit: int = 50) -> List[Dict]:
        """Search stories by user request or story text."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                search_term = f"%{query}%"
                cursor.execute('''
                    SELECT * FROM stories 
                    WHERE user_request LIKE ? OR story_text LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (search_term, search_term, limit))
                
                rows = cursor.fetchall()
                
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️  Error searching stories: {e}")
            return []
    
    def filter_stories(self, 
                      category: Optional[str] = None,
                      min_score: Optional[float] = None,
                      max_score: Optional[float] = None,
                      limit: int = 50) -> List[Dict]:
        """Filter stories by various criteria."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = []
                params = []
                
                if category:
                    conditions.append("category = ?")
                    params.append(category)
                
                if min_score is not None:
                    conditions.append("judge_score >= ?")
                    params.append(min_score)
                
                if max_score is not None:
                    conditions.append("judge_score <= ?")
                    params.append(max_score)
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                params.append(limit)
                
                cursor.execute(f'''
                    SELECT * FROM stories 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', params)
                
                rows = cursor.fetchall()
                
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️  Error filtering stories: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored stories."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total stories
                cursor.execute('SELECT COUNT(*) FROM stories')
                stats['total_stories'] = cursor.fetchone()[0]
                
                # Average score
                cursor.execute('SELECT AVG(judge_score) FROM stories WHERE judge_score > 0')
                result = cursor.fetchone()[0]
                stats['average_score'] = round(result, 2) if result else 0.0
                
                # Category distribution
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM stories 
                    GROUP BY category 
                    ORDER BY count DESC
                ''')
                stats['category_distribution'] = dict(cursor.fetchall())
                
                # Stories by quality threshold
                cursor.execute('SELECT COUNT(*) FROM stories WHERE meets_quality_threshold = 1')
                stats['stories_meeting_threshold'] = cursor.fetchone()[0]
                
                # Average revisions
                cursor.execute('SELECT AVG(revision_count) FROM stories')
                result = cursor.fetchone()[0]
                stats['average_revisions'] = round(result, 2) if result else 0.0
                
                return stats
        except Exception as e:
            print(f"⚠️  Error getting statistics: {e}")
            return {
                'total_stories': 0,
                'average_score': 0.0,
                'category_distribution': {},
                'stories_meeting_threshold': 0,
                'average_revisions': 0.0
            }
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to dictionary."""
        return {
            "id": row["id"],
            "story": row["story_text"],
            "user_request": row["user_request"],
            "category": row["category"],
            "categorization": json.loads(row["categorization"]) if row["categorization"] else {},
            "judge_score": row["judge_score"],
            "judge_feedback": row["judge_feedback"],
            "revision_count": row["revision_count"],
            "is_valid": bool(row["is_valid"]),
            "meets_quality_threshold": bool(row["meets_quality_threshold"]),
            "validation": json.loads(row["validation"]) if row["validation"] else {},
            "parent_settings": json.loads(row["parent_settings"]) if row["parent_settings"] else {},
            "created_at": row["created_at"]
        }
    
    def delete_story(self, story_id: int) -> bool:
        """Delete a story by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM stories WHERE id = ?', (story_id,))
                deleted = cursor.rowcount > 0
                
                conn.commit()
                
                return deleted
        except Exception as e:
            print(f"⚠️  Error deleting story: {e}")
            return False
