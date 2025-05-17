"""
Persona Repository for managing persona reuse and queries.
Provides sophisticated querying capabilities for finding and reusing personas.
"""

import json
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session

from .schema import Persona, Essay
from .manager import DatabaseManager


class PersonaRepository:
    """Repository for advanced persona queries and reuse management."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.engine = db_manager.engine
        self.Session = db_manager.SessionLocal
    
    def find_by_background(self, background_type: str) -> List[Persona]:
        """Find all personas with a specific background type."""
        with self.Session() as session:
            personas = session.query(Persona).filter(
                Persona.background == background_type
            ).all()
            return personas
    
    def find_by_attributes(
        self, 
        strengths: Optional[List[str]] = None,
        weaknesses: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        require_all: bool = False
    ) -> List[Persona]:
        """
        Find personas by specific attributes.
        
        Args:
            strengths: List of strengths to match
            weaknesses: List of weaknesses to match
            interests: List of interests to match
            require_all: If True, require all specified attributes. If False, match any.
            
        Returns:
            List of matching Persona objects
        """
        with self.Session() as session:
            query = session.query(Persona)
            
            # For SQLite, we need to use JSON extract functions
            conditions = []
            
            if strengths:
                for strength in strengths:
                    conditions.append(
                        func.json_extract(Persona.strengths, '$').like(f'%"{strength}"%')
                    )
            
            if weaknesses:
                for weakness in weaknesses:
                    conditions.append(
                        func.json_extract(Persona.weaknesses, '$').like(f'%"{weakness}"%')
                    )
            
            if interests:
                for interest in interests:
                    conditions.append(
                        func.json_extract(Persona.interests, '$').like(f'%"{interest}"%')
                    )
            
            if conditions:
                if require_all:
                    query = query.filter(and_(*conditions))
                else:
                    query = query.filter(or_(*conditions))
            
            personas = query.all()
            
            # For more precise matching, do additional filtering in Python
            if require_all:
                filtered_personas = []
                for persona in personas:
                    matches = True
                    
                    if strengths and persona.strengths:
                        persona_strengths = json.loads(persona.strengths) if isinstance(persona.strengths, str) else persona.strengths
                        if not all(s in persona_strengths for s in strengths):
                            matches = False
                    
                    if weaknesses and persona.weaknesses:
                        persona_weaknesses = json.loads(persona.weaknesses) if isinstance(persona.weaknesses, str) else persona.weaknesses
                        if not all(w in persona_weaknesses for w in weaknesses):
                            matches = False
                    
                    if interests and persona.interests:
                        persona_interests = json.loads(persona.interests) if isinstance(persona.interests, str) else persona.interests
                        if not all(i in persona_interests for i in interests):
                            matches = False
                    
                    if matches:
                        filtered_personas.append(persona)
                
                return filtered_personas
            
            return personas
    
    def find_compatible_for_topic(
        self, 
        topic: str,
        used_personas: Optional[List[int]] = None,
        min_compatibility_score: float = 0.3
    ) -> List[tuple[Persona, float]]:
        """
        Find personas suitable for a specific topic based on their interests.
        
        Args:
            topic: The essay topic
            used_personas: List of persona IDs to exclude
            min_compatibility_score: Minimum compatibility score (0-1)
            
        Returns:
            List of (Persona, compatibility_score) tuples, sorted by score
        """
        # Extract keywords from topic
        topic_keywords = self._extract_keywords(topic)
        
        with self.Session() as session:
            query = session.query(Persona)
            
            if used_personas:
                query = query.filter(~Persona.id.in_(used_personas))
            
            personas = query.all()
            
            # Score each persona based on interest overlap
            scored_personas = []
            for persona in personas:
                if persona.interests:
                    persona_interests = json.loads(persona.interests) if isinstance(persona.interests, str) else persona.interests
                    score = self._calculate_compatibility_score(
                        topic_keywords, 
                        persona_interests,
                        persona.background
                    )
                    
                    if score >= min_compatibility_score:
                        scored_personas.append((persona, score))
            
            # Sort by score descending
            scored_personas.sort(key=lambda x: x[1], reverse=True)
            
            return scored_personas
    
    def get_persona_usage(self, persona_id: int) -> Dict[str, Any]:
        """
        Get usage statistics for a persona.
        
        Returns:
            Dict with usage stats including topics, stances, and frequency
        """
        with self.Session() as session:
            essays = session.query(Essay).filter(
                Essay.persona_id == persona_id
            ).all()
            
            usage_stats = {
                'total_essays': len(essays),
                'topics': {},
                'stances': {},
                'last_used': None,
                'first_used': None
            }
            
            for essay in essays:
                # Track topics (from research seed)
                if essay.seed and essay.seed.angle:
                    topic_key = essay.seed.angle
                    usage_stats['topics'][topic_key] = usage_stats['topics'].get(topic_key, 0) + 1
                
                # Track stances
                if essay.stance and essay.stance.name:
                    stance_key = essay.stance.name
                    usage_stats['stances'][stance_key] = usage_stats['stances'].get(stance_key, 0) + 1
                
                # Track timing
                if essay.created_at:
                    if not usage_stats['first_used'] or essay.created_at < usage_stats['first_used']:
                        usage_stats['first_used'] = essay.created_at
                    if not usage_stats['last_used'] or essay.created_at > usage_stats['last_used']:
                        usage_stats['last_used'] = essay.created_at
            
            return usage_stats
    
    def find_underused_personas(
        self, 
        max_usage_count: int = 3,
        limit: Optional[int] = None,
        order_by_usage: bool = True
    ) -> List[tuple[Persona, int]]:
        """
        Find personas that haven't been overused, ordered by usage count.
        
        Args:
            max_usage_count: Maximum number of essays per persona
            limit: Maximum number of results to return
            order_by_usage: If True, order by usage count (least used first)
            
        Returns:
            List of (Persona, usage_count) tuples
        """
        with self.Session() as session:
            # Subquery for usage counts
            usage_subquery = session.query(
                Essay.persona_id,
                func.count(Essay.id).label('usage_count')
            ).group_by(Essay.persona_id).subquery()
            
            # Main query joining personas with usage data
            query = session.query(
                Persona,
                func.coalesce(usage_subquery.c.usage_count, 0).label('usage_count')
            ).outerjoin(
                usage_subquery,
                Persona.id == usage_subquery.c.persona_id
            ).filter(
                func.coalesce(usage_subquery.c.usage_count, 0) < max_usage_count
            )
            
            # Order by usage count if requested
            if order_by_usage:
                query = query.order_by(func.coalesce(usage_subquery.c.usage_count, 0))
            
            # Apply limit if specified
            if limit:
                query = query.limit(limit)
            
            # Execute and return results
            return query.all()
    
    def _extract_keywords(self, topic: str) -> Set[str]:
        """Extract keywords from topic text."""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        
        # Remove common words and punctuation
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'is', 'are', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'might', 'must', 'shall', 'can', 'may'
        }
        
        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', topic.lower())
        
        # Filter out stop words and short words
        keywords = {word for word in words if word not in stop_words and len(word) > 3}
        
        # Add topic-specific keywords based on common themes
        theme_keywords = {
            'technology': {'ai', 'technology', 'digital', 'computer', 'software', 'innovation'},
            'environment': {'climate', 'environment', 'sustainability', 'green', 'eco'},
            'healthcare': {'health', 'medical', 'healthcare', 'medicine', 'patient'},
            'education': {'education', 'school', 'learning', 'student', 'teaching'},
            'politics': {'political', 'policy', 'government', 'democracy', 'law'},
        }
        
        for theme, theme_words in theme_keywords.items():
            if any(word in keywords for word in theme_words):
                keywords.update(theme_words)
        
        return keywords
    
    def _calculate_compatibility_score(
        self, 
        topic_keywords: Set[str],
        persona_interests: List[str],
        persona_background: str
    ) -> float:
        """Calculate compatibility score between topic and persona."""
        score = 0.0
        
        # Convert interests to lowercase for comparison
        persona_interests_lower = [interest.lower() for interest in persona_interests]
        
        # Direct interest matches
        for interest in persona_interests_lower:
            interest_words = set(interest.split())
            overlap = len(topic_keywords.intersection(interest_words))
            if overlap > 0:
                score += 0.3 * overlap
        
        # Background relevance
        background_keywords = {
            'stem': {'science', 'technology', 'engineering', 'math', 'technical'},
            'humanities': {'philosophy', 'history', 'literature', 'art', 'culture'},
            'international': {'global', 'international', 'cultural', 'diversity'},
            'veteran': {'military', 'defense', 'service', 'leadership'},
        }
        
        background_lower = persona_background.lower()
        for bg_type, bg_words in background_keywords.items():
            if bg_type in background_lower:
                overlap = len(topic_keywords.intersection(bg_words))
                if overlap > 0:
                    score += 0.2 * overlap
        
        # Normalize score to 0-1 range
        return min(score, 1.0)