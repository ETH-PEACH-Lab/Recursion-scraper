"""
Data models for LeetCode problem data.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
import json


@dataclass
class Problem:
    """Represents a LeetCode problem."""
    title: str
    title_slug: str
    question_id: str
    difficulty: str
    topic_tags: List[str]
    url: str
    content: Optional[str] = None
    tutorial: Optional[str] = None
    solutions: Optional[List[dict]] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class Solution:
    """Represents a solution to a problem."""
    title: str
    content: str
    language: str
    votes: int
    author: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)
