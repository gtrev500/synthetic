"""
Test suite for PersonaRepository functionality.
"""

import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.schema import Base, Persona, Essay, Stance, ResearchSeed, PersonaUsage
from database.manager import DatabaseManager
from database.persona_repository import PersonaRepository


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    
    # Mock DatabaseManager
    class MockDatabaseManager:
        def __init__(self):
            self.engine = engine
            self.SessionLocal = Session
    
    db_manager = MockDatabaseManager()
    return db_manager


@pytest.fixture
def sample_personas(test_db):
    """Create sample personas for testing."""
    Session = test_db.SessionLocal
    session = Session()
    
    personas = [
        Persona(
            id=1,
            background="STEM major taking humanities",
            strengths=json.dumps(["analytical skills", "research integration"]),
            weaknesses=json.dumps(["informal tone when inappropriate", "grammar struggles"]),
            interests=json.dumps(["technology ethics", "environmental sustainability"]),
            created_at=datetime.now()
        ),
        Persona(
            id=2,
            background="international student from Asia",
            strengths=json.dumps(["methodical structure", "clear thesis development"]),
            weaknesses=json.dumps(["limited vocabulary", "citation problems"]),
            interests=json.dumps(["cultural preservation", "education equality"]),
            created_at=datetime.now()
        ),
        Persona(
            id=3,
            background="military veteran student",
            strengths=json.dumps(["persuasive rhetoric", "engaging introductions"]),
            weaknesses=json.dumps(["over-generalization", "weak transitions"]),
            interests=json.dumps(["healthcare reform", "political theory"]),
            created_at=datetime.now()
        )
    ]
    
    session.add_all(personas)
    
    # Add some stances and research seeds for testing
    stance = Stance(id=1, name="somewhat_for", position=0.6, certainty="moderate")
    seed = ResearchSeed(id=1, angle="AI ethics in healthcare", created_at=datetime.now())
    
    session.add(stance)
    session.add(seed)
    
    # Add some essays for usage testing
    essays = [
        Essay(
            id=1,
            persona_id=1,
            stance_id=1,
            seed_id=1,
            created_at=datetime.now() - timedelta(days=2)
        ),
        Essay(
            id=2,
            persona_id=1,
            stance_id=1,
            seed_id=1,
            created_at=datetime.now() - timedelta(days=1)
        )
    ]
    
    session.add_all(essays)
    session.commit()
    session.close()
    
    return personas


def test_find_by_background(test_db, sample_personas):
    """Test finding personas by background."""
    repo = PersonaRepository(test_db)
    
    # Find STEM major
    results = repo.find_by_background("STEM major taking humanities")
    assert len(results) == 1
    assert results[0].id == 1
    
    # Find international student
    results = repo.find_by_background("international student from Asia")
    assert len(results) == 1
    assert results[0].id == 2
    
    # Find non-existent background
    results = repo.find_by_background("non-existent background")
    assert len(results) == 0


def test_find_by_attributes(test_db, sample_personas):
    """Test finding personas by attributes."""
    repo = PersonaRepository(test_db)
    
    # Find by single strength
    results = repo.find_by_attributes(strengths=["analytical skills"])
    assert len(results) == 1
    assert results[0].id == 1
    
    # Find by multiple strengths (OR)
    results = repo.find_by_attributes(
        strengths=["analytical skills", "persuasive rhetoric"],
        require_all=False
    )
    assert len(results) == 2
    assert {r.id for r in results} == {1, 3}
    
    # Find by weakness
    results = repo.find_by_attributes(weaknesses=["limited vocabulary"])
    assert len(results) == 1
    assert results[0].id == 2
    
    # Find by interest
    results = repo.find_by_attributes(interests=["technology ethics"])
    assert len(results) == 1
    assert results[0].id == 1
    
    # Find by multiple attributes (AND)
    results = repo.find_by_attributes(
        strengths=["analytical skills"],
        interests=["environmental sustainability"],
        require_all=True
    )
    assert len(results) == 1
    assert results[0].id == 1
    
    # Find with no matches
    results = repo.find_by_attributes(interests=["non-existent interest"])
    assert len(results) == 0


def test_find_compatible_for_topic(test_db, sample_personas):
    """Test finding compatible personas for topics."""
    repo = PersonaRepository(test_db)
    
    # Topic related to technology ethics
    results = repo.find_compatible_for_topic(
        "The ethics of artificial intelligence in healthcare systems"
    )
    
    # Should find personas with relevant interests
    assert len(results) >= 1
    # First persona should have highest score due to both "technology ethics" and "healthcare" keywords
    first_persona, first_score = results[0]
    assert first_persona.id in [1, 3]  # Either STEM major or veteran (healthcare interest)
    assert first_score > 0
    
    # Test with exclusions
    results = repo.find_compatible_for_topic(
        "Educational policy and equality",
        used_personas=[2]  # Exclude international student
    )
    
    # Should not include persona 2
    persona_ids = [p.id for p, _ in results]
    assert 2 not in persona_ids
    
    # Test with minimum score
    results = repo.find_compatible_for_topic(
        "Quantum physics research",
        min_compatibility_score=0.8
    )
    
    # Might return empty if no personas have high enough score
    assert isinstance(results, list)


def test_get_persona_usage(test_db, sample_personas):
    """Test getting persona usage statistics."""
    repo = PersonaRepository(test_db)
    
    # Get usage for persona 1 (has 2 essays)
    usage = repo.get_persona_usage(1)
    
    assert usage['total_essays'] == 2
    assert usage['last_used'] is not None
    assert usage['first_used'] is not None
    assert usage['last_used'] > usage['first_used']
    
    # Check topics and stances
    assert 'AI ethics in healthcare' in usage['topics']
    assert usage['topics']['AI ethics in healthcare'] == 2
    assert 'somewhat_for' in usage['stances']
    assert usage['stances']['somewhat_for'] == 2
    
    # Get usage for persona with no essays
    usage = repo.get_persona_usage(3)
    assert usage['total_essays'] == 0
    assert len(usage['topics']) == 0
    assert usage['last_used'] is None


def test_find_underused_personas(test_db, sample_personas):
    """Test finding underused personas."""
    repo = PersonaRepository(test_db)
    
    # Find personas with usage under 3
    results = repo.find_underused_personas(max_usage_count=3)
    
    # All personas should be available (1 has 2 uses, others have 0)
    # Results are now tuples of (persona, usage_count)
    assert len(results) == 3
    persona_ids = [p.id for p, _ in results]
    assert set(persona_ids) == {1, 2, 3}
    
    # Check ordering - least used should come first
    # Persona 2 and 3 have 0 uses, Persona 1 has 2 uses
    usage_counts = [count for _, count in results]
    assert usage_counts == sorted(usage_counts)  # Verify ascending order
    
    # Find personas with max 1 use  
    results = repo.find_underused_personas(max_usage_count=1)
    
    # Only personas 2 and 3 should be available (persona 1 has 2 uses)
    assert len(results) == 2
    persona_ids = [p.id for p, _ in results]
    assert set(persona_ids) == {2, 3}
    
    # Test with limit
    results = repo.find_underused_personas(max_usage_count=3, limit=2)
    assert len(results) <= 2
    
    # Test without ordering
    results = repo.find_underused_personas(max_usage_count=3, order_by_usage=False)
    assert len(results) == 3


def test_extract_keywords(test_db):
    """Test keyword extraction from topics."""
    repo = PersonaRepository(test_db)
    
    keywords = repo._extract_keywords(
        "The impact of artificial intelligence on healthcare policy"
    )
    
    assert "impact" in keywords
    assert "artificial" in keywords
    assert "intelligence" in keywords
    assert "healthcare" in keywords
    assert "policy" in keywords
    
    # Stop words should be removed
    assert "the" not in keywords
    assert "of" not in keywords
    assert "on" not in keywords


def test_calculate_compatibility_score(test_db):
    """Test compatibility score calculation."""
    repo = PersonaRepository(test_db)
    
    topic_keywords = {"technology", "ethics", "healthcare", "ai"}
    
    # High compatibility
    score = repo._calculate_compatibility_score(
        topic_keywords,
        ["technology ethics", "healthcare reform"],
        "STEM major taking humanities"
    )
    assert score > 0.5
    
    # Low compatibility
    score = repo._calculate_compatibility_score(
        topic_keywords,
        ["artistic expression", "cultural preservation"],
        "humanities major exploring sciences"
    )
    assert score < 0.3
    
    # Background boost
    score = repo._calculate_compatibility_score(
        {"science", "research", "innovation"},
        ["economic policy"],
        "STEM major taking humanities"
    )
    assert score > 0  # Should get some score from background match