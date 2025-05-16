#!/usr/bin/env python3
"""
Test script to verify the synthetic essay system is working correctly.
"""

import asyncio
import os
from pathlib import Path

from config.settings import Settings
from database.manager import DatabaseManager
from diversity.manager import DiversityManager
from generation.llm_manager import LLMManager

async def test_system():
    """Run basic tests to verify system components."""
    print("Testing Synthetic Essay System")
    print("=" * 40)
    
    # Test 1: Configuration
    print("\n1. Testing configuration...")
    try:
        settings = Settings()
        print("✓ Configuration loaded successfully")
        print(f"  - Database path: {settings.db_path}")
        print(f"  - Output directory: {settings.output_dir}")
        print(f"  - Models configured: {len(settings.models)}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return
    
    # Test 2: Database
    print("\n2. Testing database...")
    try:
        db = DatabaseManager(settings.db_path)
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return
    
    # Test 3: API Keys
    print("\n3. Testing API keys...")
    llm_manager = LLMManager(settings.models)
    key_status = llm_manager.validate_api_keys()
    
    all_keys_present = True
    for provider, has_key in key_status.items():
        status = "✓" if has_key else "✗"
        print(f"  {provider}: {status}")
        if not has_key and provider in ['openai', 'anthropic', 'perplexity']:
            all_keys_present = False
    
    if not all_keys_present:
        print("\n⚠️  Some API keys are missing. Create a .env file with your keys.")
        print("   Copy .env.example to .env and add your API keys.")
    
    # Test 4: Diversity Components
    print("\n4. Testing diversity components...")
    try:
        diversity = DiversityManager()
        
        # Test stance generation
        stances = diversity.stance_manager.get_all_stances()
        print(f"✓ Stances: {len(stances)} types available")
        
        # Test persona generation
        persona = diversity.persona_manager.generate_persona()
        print(f"✓ Personas: Generated test persona ({persona['background']})")
        
        # Test evidence patterns
        evidence = diversity.evidence_manager.generate_evidence_pattern()
        print(f"✓ Evidence: {evidence['primary_type']} + {evidence['secondary_type']}")
        
        # Test style parameters
        style = diversity.style_manager.generate_style_parameters()
        print(f"✓ Style: Formality={style['formality']:.2f}, Complexity={style['complexity']:.2f}")
        
        # Test quality levels
        quality = diversity.quality_manager.generate_quality_with_distribution()
        print(f"✓ Quality: Grade {quality['grade']} generated")
        
    except Exception as e:
        print(f"✗ Diversity component error: {e}")
        return
    
    # Test 5: Directory Structure
    print("\n5. Testing directory structure...")
    required_dirs = ['database', 'research', 'diversity', 'generation', 'output', 'config']
    all_present = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            all_present = False
    
    if not all_present:
        print("\n⚠️  Some directories are missing. Make sure you're in the project root.")
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("- Configuration: ✓")
    print("- Database: ✓")
    print(f"- API Keys: {'✓' if all_keys_present else '⚠️  Some missing'}")
    print("- Diversity Components: ✓")
    print(f"- Directory Structure: {'✓' if all_present else '⚠️  Some missing'}")
    
    if all_keys_present and all_present:
        print("\n✅ System is ready to generate essays!")
        print("   Run: python main.py")
    else:
        print("\n⚠️  Please fix the issues above before generating essays.")

if __name__ == "__main__":
    asyncio.run(test_system())