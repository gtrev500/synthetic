"""
Test suite to verify PersonaUsage topic optimization.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from database.manager import DatabaseManager
from database.schema import Essay, PersonaUsage, ResearchSeed, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_manager(test_db):
    """Create a database manager with test database."""
    manager = DatabaseManager(':memory:')
    manager.engine = test_db
    manager.SessionLocal = sessionmaker(bind=test_db)
    return manager


def test_save_essay_with_topic_provided(db_manager):
    """Test that save_essay uses the provided topic without querying database."""
    
    # Create test data
    essay_data = {
        'content': 'Test essay content.',
        'topic': 'The impact of AI on education',  # Topic provided directly
        'seed_id': 1,
        'stance_id': 1,
        'persona_id': 1,
        'evidence_id': 1,
        'style_id': 1,
        'quality_id': 1,
        'model_name': 'test_model',
        'temperature': 0.8,
        'prompt_hash': 'test_hash'
    }
    
    # Mock the session to track queries
    with patch.object(db_manager, 'get_session') as mock_get_session:
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock the essay object
        mock_essay = Mock()
        mock_essay.id = 1
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        
        # Set up query mock to track if ResearchSeed is queried
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        
        # Create the Essay instance when add is called
        def mock_add(obj):
            if isinstance(obj, Essay):
                obj.id = 1
        mock_session.add.side_effect = mock_add
        
        # Call save_essay
        essay = db_manager.save_essay(essay_data, 'test_run_id')
        
        # Verify ResearchSeed was NOT queried
        research_seed_queries = [
            call for call in mock_session.query.call_args_list 
            if ResearchSeed in str(call)
        ]
        assert len(research_seed_queries) == 0, "ResearchSeed should not be queried when topic is provided"
        
        # Verify PersonaUsage was created with the correct topic
        persona_usage_adds = [
            call[0][0] for call in mock_session.add.call_args_list 
            if isinstance(call[0][0], PersonaUsage)
        ]
        assert len(persona_usage_adds) == 1
        assert persona_usage_adds[0].topic == 'The impact of AI on education'


def test_save_essay_backward_compatibility(db_manager):
    """Test that save_essay falls back to seed query when topic not provided."""
    
    # Create test data without topic field (backward compatibility)
    essay_data = {
        'content': 'Test essay content.',
        # 'topic' field is missing
        'seed_id': 1,
        'stance_id': 1,
        'persona_id': 1,
        'evidence_id': 1,
        'style_id': 1,
        'quality_id': 1,
        'model_name': 'test_model',
        'temperature': 0.8,
        'prompt_hash': 'test_hash'
    }
    
    with patch.object(db_manager, 'get_session') as mock_get_session:
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock the research seed object
        mock_seed = Mock()
        mock_seed.angle = 'AI ethics in healthcare'
        
        # Set up query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_seed
        
        # Mock the essay object
        def mock_add(obj):
            if isinstance(obj, Essay):
                obj.id = 1
        mock_session.add.side_effect = mock_add
        
        # Call save_essay
        essay = db_manager.save_essay(essay_data, 'test_run_id')
        
        # Verify ResearchSeed WAS queried
        research_seed_queries = [
            call for call in mock_session.query.call_args_list 
            if call.args and call.args[0] == ResearchSeed
        ]
        assert len(research_seed_queries) == 1, "ResearchSeed should be queried when topic is not provided"
        
        # Verify PersonaUsage was created with the seed angle
        persona_usage_adds = [
            call[0][0] for call in mock_session.add.call_args_list 
            if isinstance(call[0][0], PersonaUsage)
        ]
        assert len(persona_usage_adds) == 1
        assert persona_usage_adds[0].topic == 'AI ethics in healthcare'


def test_integration_with_actual_database(db_manager):
    """Test the full integration with an actual database."""
    
    # Create required entities first
    with db_manager.get_session() as session:
        seed = ResearchSeed(
            id=1,
            angle='AI impact on education',
            facts=['fact1'],
            quotes=['quote1'], 
            sources=['source1'],
            created_at=datetime.now()
        )
        session.add(seed)
        session.commit()
    
    # Create essay with topic provided
    essay_data = {
        'content': 'Test essay content.',
        'topic': 'Technology in Education',  # Direct topic
        'seed_id': 1,
        'stance_id': 1,
        'persona_id': 1,
        'evidence_id': 1,
        'style_id': 1,
        'quality_id': 1,
        'model_name': 'test_model',
        'temperature': 0.8,
        'prompt_hash': 'test_hash'
    }
    
    # Save essay - save_essay creates its own session context
    essay = db_manager.save_essay(essay_data, 'test_run_id')
    
    # Get the essay ID within the same session
    with db_manager.get_session() as session:
        saved_essay = session.query(Essay).filter_by(
            content='Test essay content.',
            model_name='test_model'
        ).first()
        assert saved_essay is not None
        essay_id = saved_essay.id
        
        # Verify PersonaUsage was created with the provided topic
        persona_usage = session.query(PersonaUsage).filter_by(essay_id=essay_id).first()
        assert persona_usage is not None
        assert persona_usage.topic == 'Technology in Education'
        assert persona_usage.persona_id == 1
        assert persona_usage.stance_id == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])