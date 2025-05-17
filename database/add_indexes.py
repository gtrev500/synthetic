#!/usr/bin/env python3
"""
Script to add indexes for persona queries optimization.
"""

import sqlite3
from pathlib import Path
import sys

def add_indexes(db_path):
    """Add indexes to optimize persona queries."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='personas'
        """)
        existing_indexes = {row[0] for row in cursor.fetchall()}
        
        # Add indexes for personas table
        indexes = [
            ("idx_personas_background", "personas(background)"),
            ("idx_personas_created_at", "personas(created_at)")
        ]
        
        for index_name, index_def in indexes:
            if index_name not in existing_indexes:
                print(f"Creating index: {index_name}")
                cursor.execute(f"CREATE INDEX {index_name} ON {index_def}")
            else:
                print(f"Index already exists: {index_name}")
        
        # Check indexes for essays table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='essays'
        """)
        existing_essay_indexes = {row[0] for row in cursor.fetchall()}
        
        # Add indexes for essays table to support persona queries
        essay_indexes = [
            ("idx_essays_persona_id", "essays(persona_id)"),
            ("idx_essays_created_at", "essays(created_at)"),
            ("idx_essays_seed_id", "essays(seed_id)")
        ]
        
        for index_name, index_def in essay_indexes:
            if index_name not in existing_essay_indexes:
                print(f"Creating index: {index_name}")
                cursor.execute(f"CREATE INDEX {index_name} ON {index_def}")
            else:
                print(f"Index already exists: {index_name}")
        
        conn.commit()
        print("All indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")
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
    
    print(f"Adding indexes to database: {db_path}")
    add_indexes(db_path)
    print("Index creation completed")