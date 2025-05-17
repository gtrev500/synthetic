#!/usr/bin/env python3
"""Manually create the prompts table."""

from sqlalchemy import create_engine, text
from database.schema import Base, Prompt

def create_prompts_table():
    """Create the prompts table in the database."""
    
    # Connect to the database
    engine = create_engine("sqlite:///synthetic_essays.db")
    
    # Create all tables defined in the schema
    Base.metadata.create_all(engine)
    
    # Verify the table was created
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'"))
        if result.fetchone():
            print("Prompts table created successfully!")
            
            # Show the table structure
            result = conn.execute(text("PRAGMA table_info(prompts)"))
            print("\nPrompts table structure:")
            for row in result:
                print(f"  {row[1]}: {row[2]}")
                
            # Add prompt_id column to essays if needed
            result = conn.execute(text("PRAGMA table_info(essays)"))
            columns = [row[1] for row in result]
            
            if 'prompt_id' not in columns:
                print("\nAdding prompt_id column to essays table...")
                conn.execute(text("""
                    ALTER TABLE essays 
                    ADD COLUMN prompt_id INTEGER REFERENCES prompts(id)
                """))
                conn.commit()
                print("Added prompt_id column successfully")
            else:
                print("\nprompt_id column already exists in essays table")
        else:
            print("Failed to create prompts table")

if __name__ == "__main__":
    create_prompts_table()