"""Test that interests are properly saved for new personas."""
from database.manager import DatabaseManager
from diversity.personas import PersonaManager

# Create managers
db = DatabaseManager()
personas = PersonaManager()

# Generate a new persona
new_persona = personas.generate_persona()
print(f"Generated persona: {new_persona}")

# Save to database
saved_persona = db.save_persona(new_persona)
print(f"Saved persona ID: {saved_persona.id}")

# Verify it was saved with interests
from database.schema import Persona
with db.get_session() as session:
    loaded_persona = session.query(Persona).filter_by(id=saved_persona.id).first()
    print(f"Background: {loaded_persona.background}")
    print(f"Interests: {loaded_persona.interests}")
    print(f"Strengths: {loaded_persona.strengths}")
    print(f"Weaknesses: {loaded_persona.weaknesses}")