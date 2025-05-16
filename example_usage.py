#!/usr/bin/env python3
"""
Example usage of the synthetic essay generation system.
"""

import asyncio
from main import SyntheticEssaySystem

async def example_small_corpus():
    """Generate a small corpus of essays for testing."""
    
    # Initialize the system
    system = SyntheticEssaySystem()
    
    # Define a simple topic
    topic = """
    Should artificial intelligence be regulated by governments? 
    Discuss the potential benefits and risks of AI regulation.
    """
    
    # Generate a small corpus (10 essays for quick testing)
    print("Generating small test corpus...")
    run_id = await system.generate_essay_corpus(topic, num_essays=10)
    
    print(f"\nSuccess! Check the output at: output/{run_id}/")

async def example_custom_topic():
    """Generate essays on a custom topic."""
    
    system = SyntheticEssaySystem()
    
    # More complex topic
    topic = """
    Analyze the impact of remote work on urban development and city planning. 
    Consider economic, social, and environmental factors. How might cities 
    need to adapt their infrastructure and policies to accommodate a more 
    distributed workforce?
    """
    
    # Generate standard corpus
    print("Generating essays on custom topic...")
    run_id = await system.generate_essay_corpus(topic, num_essays=30)
    
    print(f"\nSuccess! Check the output at: output/{run_id}/")

async def example_quality_distribution():
    """Generate essays with a specific quality distribution."""
    
    system = SyntheticEssaySystem()
    
    # First, modify the quality distribution in the diversity manager
    # This would require exposing this functionality in the main system
    
    topic = """
    Evaluate the role of social media in modern democracy. 
    Does it enhance or undermine democratic processes?
    """
    
    print("Generating essays with custom quality distribution...")
    run_id = await system.generate_essay_corpus(topic, num_essays=50)
    
    print(f"\nSuccess! Check the output at: output/{run_id}/")

if __name__ == "__main__":
    # Choose which example to run
    print("Synthetic Essay Generation Examples")
    print("1. Small test corpus (10 essays)")
    print("2. Custom topic (30 essays)")
    print("3. Full corpus with quality distribution (50 essays)")
    
    choice = input("\nSelect example (1-3): ")
    
    if choice == "1":
        asyncio.run(example_small_corpus())
    elif choice == "2":
        asyncio.run(example_custom_topic())
    elif choice == "3":
        asyncio.run(example_quality_distribution())
    else:
        print("Invalid choice. Please run again and select 1-3.")