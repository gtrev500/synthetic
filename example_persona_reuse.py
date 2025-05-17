#!/usr/bin/env python3
"""
Example script demonstrating persona reuse functionality.
"""

from database.manager import DatabaseManager
from database.persona_repository import PersonaRepository


def demonstrate_persona_reuse():
    """Demonstrate various persona reuse capabilities."""
    
    # Initialize database and repository
    db = DatabaseManager('synthetic_essays.db')
    repo = PersonaRepository(db)
    
    print("=== Persona Reuse Demonstration ===\n")
    
    # 1. Find personas by background
    print("1. Finding personas by background:")
    stem_personas = repo.find_by_background("STEM major taking humanities")
    print(f"   Found {len(stem_personas)} STEM major personas")
    if stem_personas:
        p = stem_personas[0]
        print(f"   Example: ID={p.id}, strengths={p.strengths}")
    print()
    
    # 2. Find personas by attributes
    print("2. Finding personas by specific attributes:")
    analytical_personas = repo.find_by_attributes(
        strengths=["analytical skills", "research integration"],
        require_all=False
    )
    print(f"   Found {len(analytical_personas)} personas with analytical skills or research integration")
    print()
    
    # 3. Find compatible personas for a topic
    print("3. Finding personas compatible with a topic:")
    topic = "The ethics of artificial intelligence in healthcare"
    compatible = repo.find_compatible_for_topic(topic, min_compatibility_score=0.1)
    print(f"   Topic: '{topic}'")
    print(f"   Found {len(compatible)} compatible personas:")
    for persona, score in compatible[:3]:  # Show top 3
        print(f"   - {persona.background} (score: {score:.2f})")
        print(f"     Interests: {persona.interests}")
    print()
    
    # 4. Check persona usage
    print("4. Checking persona usage history:")
    if compatible:
        persona_id = compatible[0][0].id
        usage = repo.get_persona_usage(persona_id)
        print(f"   Persona {persona_id} usage:")
        print(f"   - Total essays: {usage['total_essays']}")
        print(f"   - Topics covered: {len(usage['topics'])}")
        if usage['topics']:
            print(f"   - Most common topic: {max(usage['topics'], key=usage['topics'].get)}")
    print()
    
    # 5. Find underused personas
    print("5. Finding underused personas:")
    underused = repo.find_underused_personas(max_usage_count=5, cooldown_hours=1)
    print(f"   Found {len(underused)} personas used less than 5 times")
    print()
    
    # 6. Complex query example
    print("6. Complex query - finding personas for a new essay:")
    new_topic = "Climate change impact on economic policy"
    
    # Get compatible personas
    candidates = repo.find_compatible_for_topic(new_topic, min_compatibility_score=0.2)
    
    # Filter by underused
    underused_ids = {p.id for p in underused}
    available_candidates = [(p, s) for p, s in candidates if p.id in underused_ids]
    
    print(f"   Topic: '{new_topic}'")
    print(f"   Found {len(available_candidates)} suitable underused personas:")
    for persona, score in available_candidates[:3]:
        print(f"   - {persona.background} (score: {score:.2f})")
        usage = repo.get_persona_usage(persona.id)
        print(f"     Used {usage['total_essays']} times previously")
    print()


if __name__ == '__main__':
    demonstrate_persona_reuse()