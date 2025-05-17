"""
Database migration to add interests column to personas table.
This handles backward compatibility for personas created before the interests field existed.
"""
import logging
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.schema import Base
from diversity.personas import PersonaManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_interests(db_path: str = "synthetic_essays.db"):
    """Migrate database to add interests column to personas and populate existing records."""
    
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    persona_manager = PersonaManager()
    
    try:
        # Check if interests column exists in personas table
        with engine.connect() as conn:
            # Get the current schema of the personas table
            result = conn.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='personas'
            """))
            schema = result.fetchone()[0]
            
            # Add interests column if it doesn't exist
            if 'interests' not in schema:
                logger.info("Adding interests column to personas table...")
                conn.execute(text("""
                    ALTER TABLE personas 
                    ADD COLUMN interests JSON
                """))
                conn.commit()
                logger.info("Added interests column successfully")
                
                # Now populate existing personas with interests
                logger.info("Populating interests for existing personas...")
                personas = conn.execute(text("SELECT id FROM personas")).fetchall()
                
                for persona_id, in personas:
                    # Generate random interests (1-3 of them)
                    num_interests = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
                    interests = random.sample(persona_manager.interests, num_interests)
                    
                    # Convert to JSON string for SQLite
                    import json
                    interests_json = json.dumps(interests)
                    
                    conn.execute(text("""
                        UPDATE personas 
                        SET interests = :interests
                        WHERE id = :persona_id
                    """), {"interests": interests_json, "persona_id": persona_id})
                
                conn.commit()
                logger.info(f"Successfully updated {len(personas)} personas with interests")
            else:
                logger.info("interests column already exists")
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    # Run migration as a standalone script
    migrate_add_interests()