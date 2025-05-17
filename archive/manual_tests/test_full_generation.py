#!/usr/bin/env python3
"""Test full generation with prompt storage."""

import asyncio
import os
from database.manager import DatabaseManager
from sqlite3 import connect

async def test_full_generation():
    """Test that a new generation run properly creates and links prompts."""
    
    # Use the main database
    db_manager = DatabaseManager("synthetic_essays.db")
    
    # Verify tables exist
    conn = connect("synthetic_essays.db")
    cursor = conn.cursor()
    
    # Check prompts table
    cursor.execute("SELECT COUNT(*) FROM prompts")
    prompt_count_before = cursor.fetchone()[0]
    print(f"Prompts in database before: {prompt_count_before}")
    
    # Check essays table  
    cursor.execute("SELECT COUNT(*) FROM essays WHERE prompt_id IS NOT NULL")
    linked_essays_before = cursor.fetchone()[0]
    print(f"Essays with linked prompts before: {linked_essays_before}")
    
    # Now run a small generation (this mimics what main.py would do)
    from main import main
    
    # Override sys.argv to run with minimal essays
    import sys
    original_argv = sys.argv
    sys.argv = ['main.py', '--num-essays', '2']
    
    try:
        await main()
    finally:
        sys.argv = original_argv
    
    # Check counts after
    cursor.execute("SELECT COUNT(*) FROM prompts")
    prompt_count_after = cursor.fetchone()[0]
    print(f"\nPrompts in database after: {prompt_count_after}")
    print(f"New prompts created: {prompt_count_after - prompt_count_before}")
    
    cursor.execute("SELECT COUNT(*) FROM essays WHERE prompt_id IS NOT NULL")
    linked_essays_after = cursor.fetchone()[0]
    print(f"Essays with linked prompts after: {linked_essays_after}")
    print(f"New essays with prompts: {linked_essays_after - linked_essays_before}")
    
    # Check the latest prompts
    cursor.execute("""
        SELECT p.id, LENGTH(p.base_prompt), LENGTH(p.modulated_prompt), 
               COUNT(e.id) as essay_count
        FROM prompts p
        LEFT JOIN essays e ON e.prompt_id = p.id
        GROUP BY p.id
        ORDER BY p.id DESC
        LIMIT 5
    """)
    
    print("\nLatest prompts:")
    for row in cursor.fetchall():
        print(f"  Prompt {row[0]}: base={row[1]} chars, modulated={row[2]} chars, essays={row[3]}")
    
    conn.close()
    print("\nTest completed!")

if __name__ == "__main__":
    # Check if we have required environment variables
    required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'PERPLEXITY_API_KEY']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        print(f"Warning: Missing environment variables: {missing}")
        print("You may want to set these in a .env file")
    
    asyncio.run(test_full_generation())