#!/usr/bin/env python3
"""Test script to verify prompt storage functionality."""

import asyncio
from datetime import datetime

from database.manager import DatabaseManager
from diversity.manager import DiversityManager
from generation.generator import EssayGenerator
from generation.llm_manager import LLMManager


async def test_prompt_storage():
    """Test that prompts are stored correctly in the database."""
    
    # Initialize components
    db_manager = DatabaseManager("test_prompts.db")
    diversity_manager = DiversityManager()
    
    # Mock models config (we'll mock the actual LLM call)
    models_config = [
        {
            "name": "Test Model",
            "model": "test-model",
            "provider": "test",
            "temperature": 0.8
        }
    ]
    
    # Create a test research seed
    test_seed = {
        'angle': 'Test topic angle',
        'facts': ['Fact 1', 'Fact 2', 'Fact 3'],
        'quotes': ['Quote 1', 'Quote 2'],
        'sources': ['Source 1', 'Source 2']
    }
    
    # Generate a single combination
    combinations = diversity_manager.generate_combinations([test_seed], num_essays=1)
    print(f"Generated {len(combinations)} combination(s)")
    
    # Create prompt data from combination
    prompt_data = diversity_manager.create_composite_prompt(combinations[0])
    
    # Print prompt data structure
    print("\nPrompt data structure:")
    print(f"- Has base_prompt: {'base_prompt' in prompt_data}")
    print(f"- Has prompt (modulated): {'prompt' in prompt_data}")
    print(f"- Has prompt_metadata: {'prompt_metadata' in prompt_data}")
    print(f"- Has metadata: {'metadata' in prompt_data}")
    
    # Print actual prompts (truncated)
    print("\nBase prompt (first 200 chars):")
    print(prompt_data['base_prompt'][:200] + "...")
    
    print("\nModulated prompt (first 200 chars):")
    print(prompt_data['prompt'][:200] + "...")
    
    print("\nPrompt metadata keys:")
    print(list(prompt_data['prompt_metadata'].keys()))
    
    # Save prompt to database
    import hashlib
    prompt_hash = hashlib.sha256(prompt_data['prompt'].encode()).hexdigest()
    
    saved_prompt = db_manager.save_prompt(
        base_prompt=prompt_data['base_prompt'],
        modulated_prompt=prompt_data['prompt'],
        metadata=prompt_data['prompt_metadata'],
        prompt_hash=prompt_hash
    )
    
    print(f"\nPrompt saved with ID: {saved_prompt.id}")
    print(f"Prompt hash: {saved_prompt.hash[:16]}...")
    
    # Verify the prompt was saved
    from database.schema import Prompt
    with db_manager.get_session() as session:
        verified_prompt = session.query(Prompt).filter_by(id=saved_prompt.id).first()
        print(f"\nPrompt verification:")
        print(f"- Base prompt length: {len(verified_prompt.base_prompt)}")
        print(f"- Modulated prompt length: {len(verified_prompt.modulated_prompt)}")
        print(f"- Metadata keys: {list(verified_prompt.prompt_metadata.keys())}")
        
    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_prompt_storage())