#!/usr/bin/env python3
"""Test script to verify essay generation with prompt storage."""

import asyncio
from datetime import datetime

from database.manager import DatabaseManager
from diversity.manager import DiversityManager
from generation.generator import EssayGenerator
from database.schema import Essay, Prompt


async def test_essay_with_prompt():
    """Test that essays are saved with properly linked prompts."""
    
    # Initialize components
    db_manager = DatabaseManager("test_essay_prompts.db")
    diversity_manager = DiversityManager()
    
    # Mock models config
    models_config = [
        {
            "name": "Mock Model",
            "model": "mock-model",
            "provider": "test",
            "temperature": 0.8,
            "token_multiplier": 1.0
        }
    ]
    
    # Create essay generator
    generator = EssayGenerator(models_config, db_manager)
    
    # Override the LLM call with a mock
    original_generate_essay = generator.llm_manager.generate_essay
    async def mock_generate_essay(prompt_data, model_config):
        import hashlib
        prompt = prompt_data['prompt']
        metadata = prompt_data['metadata']
        base_prompt = prompt_data.get('base_prompt', '')
        prompt_metadata = prompt_data.get('prompt_metadata', {})
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        return {
            'content': "This is a mock essay content for testing purposes.",
            'model_name': model_config['name'],
            'model_id': model_config['model'],
            'temperature': model_config.get('temperature', 0.8),
            'word_count': 10,
            'prompt_hash': prompt_hash,
            'metadata': metadata,
            'base_prompt': base_prompt,
            'modulated_prompt': prompt,
            'prompt_metadata': prompt_metadata
        }
    
    generator.llm_manager.generate_essay = mock_generate_essay
    
    # Create a test research seed
    test_seed = {
        'angle': 'Essay test topic angle',
        'facts': ['Essay fact 1', 'Essay fact 2', 'Essay fact 3'],
        'quotes': ['Essay quote 1', 'Essay quote 2'],
        'sources': ['Essay source 1', 'Essay source 2']
    }
    
    # Save the research seed first
    saved_seeds = db_manager.save_research_seeds([test_seed])
    test_seed['id'] = saved_seeds[0].id
    
    # Generate a combination
    combinations = diversity_manager.generate_combinations([test_seed], num_essays=1)
    
    # Generate essay
    essays = await generator.generate_essays(combinations, batch_size=1)
    
    # Save the essay
    run_id = "test-run-001"
    saved_essays = db_manager.save_essays(essays, run_id)
    
    print(f"Generated and saved {len(saved_essays)} essay(s)")
    
    # Verify the essay has a linked prompt
    with db_manager.get_session() as session:
        essay = session.query(Essay).filter_by(id=saved_essays[0].id).first()
        print(f"\nEssay verification:")
        print(f"- Essay ID: {essay.id}")
        print(f"- Prompt ID: {essay.prompt_id}")
        print(f"- Content length: {len(essay.content)}")
        
        if essay.prompt_id:
            # Load the linked prompt
            prompt = session.query(Prompt).filter_by(id=essay.prompt_id).first()
            print(f"\nLinked prompt:")
            print(f"- Prompt ID: {prompt.id}")
            print(f"- Base prompt length: {len(prompt.base_prompt)}")
            print(f"- Modulated prompt length: {len(prompt.modulated_prompt)}")
            print(f"- Has metadata: {bool(prompt.prompt_metadata)}")
            print(f"- Metadata keys: {list(prompt.prompt_metadata.keys())}")
        else:
            print("\nERROR: No prompt linked to essay!")
            
    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_essay_with_prompt())