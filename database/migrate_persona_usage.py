#!/usr/bin/env python3
"""
Migration script to add persona usage tracking table.
This adds the persona_usage table for tracking when personas are used.
"""

import sqlite3
from pathlib import Path
import sys

def add_persona_usage_table(db_path):
    """Add the persona_usage table to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='persona_usage'
        """)
        
        if cursor.fetchone():
            print("persona_usage table already exists")
            return
        
        # Create the new table
        cursor.execute('''
            CREATE TABLE persona_usage (
                id INTEGER PRIMARY KEY,
                persona_id INTEGER,
                topic VARCHAR(500),
                stance_id INTEGER,
                essay_id INTEGER,
                created_at DATETIME,
                FOREIGN KEY(persona_id) REFERENCES personas(id),
                FOREIGN KEY(stance_id) REFERENCES stances(id),
                FOREIGN KEY(essay_id) REFERENCES essays(id)
            )
        ''')
        
        # Create indexes for common queries
        cursor.execute('''
            CREATE INDEX idx_persona_usage_persona_id 
            ON persona_usage(persona_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_persona_usage_topic 
            ON persona_usage(topic)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_persona_usage_created_at 
            ON persona_usage(created_at)
        ''')
        
        # Populate initial data from existing essays
        print("Populating persona_usage from existing essays...")
        cursor.execute('''
            INSERT INTO persona_usage (persona_id, topic, stance_id, essay_id, created_at)
            SELECT 
                e.persona_id,
                r.angle as topic,
                e.stance_id,
                e.id as essay_id,
                e.created_at
            FROM essays e
            LEFT JOIN research_seeds r ON e.seed_id = r.id
            WHERE e.persona_id IS NOT NULL
        ''')
        
        count = cursor.rowcount
        conn.commit()
        print(f"Added {count} usage records from existing essays")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    # Default database path
    db_path = 'synthetic_essays.db'
    
    # Allow specifying custom path as argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    # Make sure database exists
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)
    
    print(f"Migrating database: {db_path}")
    add_persona_usage_table(db_path)
    print("Migration completed successfully")