"""
Database migration to add Prompt table and update existing essays.
This handles backward compatibility for essays created before the Prompt table existed.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.schema import Base, Prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database(db_path: str = "synthetic_essays.db"):
    """Migrate database to add Prompt table and link existing essays."""
    
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    
    try:
        # Create the Prompt table if it doesn't exist
        Base.metadata.create_all(engine)
        
        # Check if prompt_id column exists in essays table
        with engine.connect() as conn:
            # Get the current schema of the essays table
            result = conn.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='essays'
            """))
            schema = result.fetchone()[0]
            
            # Add prompt_id column if it doesn't exist
            if 'prompt_id' not in schema:
                logger.info("Adding prompt_id column to essays table...")
                conn.execute(text("""
                    ALTER TABLE essays 
                    ADD COLUMN prompt_id INTEGER REFERENCES prompts(id)
                """))
                conn.commit()
                logger.info("Added prompt_id column successfully")
            else:
                logger.info("prompt_id column already exists")
        
        # Migrate existing essays by creating generic prompt records
        with Session() as session:
            # Find essays with prompt_hash but no prompt_id
            orphan_essays = session.execute(text("""
                SELECT id, prompt_hash 
                FROM essays 
                WHERE prompt_hash IS NOT NULL 
                AND prompt_id IS NULL
            """)).fetchall()
            
            if orphan_essays:
                logger.info(f"Found {len(orphan_essays)} essays without prompt records")
                
                prompt_map = {}
                for essay_id, prompt_hash in orphan_essays:
                    # Check if we already created a prompt for this hash
                    if prompt_hash not in prompt_map:
                        # Create a generic prompt record
                        generic_prompt = Prompt(
                            base_prompt="[Migrated from legacy system - original prompt not available]",
                            modulated_prompt="[Migrated from legacy system - original prompt not available]",
                            metadata={"migration": True, "original_hash": prompt_hash},
                            hash=prompt_hash,
                            created_at=None  # Will be set to current time
                        )
                        session.add(generic_prompt)
                        session.flush()
                        prompt_map[prompt_hash] = generic_prompt.id
                    
                    # Update the essay with the prompt_id
                    session.execute(text("""
                        UPDATE essays 
                        SET prompt_id = :prompt_id 
                        WHERE id = :essay_id
                    """), {"prompt_id": prompt_map[prompt_hash], "essay_id": essay_id})
                
                session.commit()
                logger.info(f"Successfully migrated {len(orphan_essays)} essays")
            else:
                logger.info("No essays to migrate")
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    # Run migration as a standalone script
    migrate_database()