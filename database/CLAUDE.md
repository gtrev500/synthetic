# Database Module

This module handles all data persistence for the synthetic essay generation system using SQLAlchemy and SQLite.

## Overview

The database module provides:
- **Schema Definition**: All database models and relationships
- **Data Management**: CRUD operations for all entities
- **Persona Repository**: Advanced querying for persona reuse
- **Migration Support**: Database schema evolution
- **Performance Optimization**: Indexes and query optimization

## Architecture

### Core Components

1. **schema.py**: SQLAlchemy model definitions
   - ResearchSeed: Perplexity API research results
   - Persona: Student identities with backgrounds, strengths, weaknesses, interests
   - Stance: Argument positions (strongly_for → strongly_against)
   - EvidencePattern: Argumentation styles
   - StyleParameter: Writing characteristics
   - QualityLevel: Academic performance grades
   - Prompt: Base and modulated prompt storage
   - Essay: Generated essay content and metadata
   - GenerationRun: Batch run tracking
   - PersonaUsage: Tracks when personas are used for topics

2. **manager.py**: Database operations
   - Session management with context managers
   - CRUD operations for all entities
   - Transaction handling
   - Automatic migration execution

3. **persona_repository.py**: Advanced persona queries
   - Find by background type
   - Find by attributes (strengths, weaknesses, interests)
   - Topic compatibility scoring
   - Usage history tracking
   - Reuse management

4. **migration.py**: Schema evolution
   - Adds Prompt table for prompt storage
   - Links existing essays to prompts
   - Maintains backward compatibility

5. **migrate_persona_usage.py**: Usage tracking migration
   - Adds PersonaUsage table
   - Populates from existing essay data
   - Creates performance indexes

6. **add_indexes.py**: Performance optimization
   - Indexes for persona queries
   - Indexes for essay queries
   - Foreign key optimization

## Data Models

### Persona Model
```python
class Persona:
    id: int
    background: str  # "first-generation student", "STEM major", etc.
    strengths: JSON  # ["analytical skills", "research integration"]
    weaknesses: JSON  # ["grammar struggles", "weak transitions"]
    interests: JSON  # ["social justice", "technology ethics"]
    created_at: datetime
```

### Essay Model
```python
class Essay:
    id: int
    content: str
    word_count: int
    created_at: datetime
    # Foreign keys to all diversity dimensions
    seed_id: int
    stance_id: int
    persona_id: int
    evidence_id: int
    style_id: int
    quality_id: int
    prompt_id: int
    # Metadata
    model_name: str
    temperature: float
    prompt_hash: str
```

### PersonaUsage Model
```python
class PersonaUsage:
    id: int
    persona_id: int
    topic: str
    stance_id: int
    essay_id: int
    created_at: datetime
```

## Key Features

### Persona Reuse System
The PersonaRepository enables sophisticated persona reuse:
- **Topic Compatibility**: Scores personas based on interest alignment
- **Usage History**: Tracks which personas have been used for topics
- **Attribute Queries**: Find personas by specific characteristics
- **Diversity Management**: Ensures varied persona usage across essays

### Performance Optimization
- Indexed columns for fast queries
- JSON field extraction for attribute searches
- Optimized foreign key relationships
- Batch operations for efficiency

### Migration System
- Automatic schema updates
- Backward compatibility
- Data preservation during upgrades
- Error recovery mechanisms

## Usage Examples

### Basic Operations
```python
# Initialize database
db = DatabaseManager('synthetic_essays.db')

# Save a persona
with db.get_session() as session:
    persona = Persona(
        background="international student",
        strengths=["cross-cultural perspective", "research skills"],
        weaknesses=["grammar issues"],
        interests=["global politics", "cultural studies"]
    )
    session.add(persona)
```

### Persona Repository
```python
repo = PersonaRepository(db)

# Find by background
stem_personas = repo.find_by_background("STEM major taking humanities")

# Find by attributes
analytical = repo.find_by_attributes(
    strengths=["analytical skills"],
    interests=["technology ethics"],
    require_all=True
)

# Find compatible personas for topic
compatible = repo.find_compatible_for_topic(
    "AI ethics in healthcare",
    used_personas=[1, 2, 3],  # Exclude these
    min_compatibility_score=0.5
)

# Track usage
usage_count = repo.get_usage_count(persona_id=1)
recent_usage = repo.get_usage_history(
    persona_id=1,
    limit=5
)
```

## Database Schema

The database uses these key relationships:
- Essay → Persona (many-to-one)
- Essay → Stance (many-to-one)
- Essay → Quality (many-to-one)
- PersonaUsage → Persona (many-to-one)
- PersonaUsage → Essay (one-to-one)

## Files

- `schema.py`: All SQLAlchemy models
- `manager.py`: Database operations and session management
- `persona_repository.py`: Advanced persona querying
- `migration.py`: Prompt table migration
- `migrate_persona_usage.py`: Usage tracking migration
- `add_indexes.py`: Performance optimization script

## Configuration

Database settings in `config/settings.yaml`:
```yaml
database:
  path: synthetic_essays.db
  echo: false
  pool_size: 5
```

## Recent Updates

The feat/persona-reuse branch adds:
1. Advanced persona querying capabilities
2. Topic compatibility scoring
3. Usage history tracking
4. Performance optimizations
5. Persona reuse examples

## Testing

Run tests with:
```bash
pytest tests/test_persona_repository.py
```

## Migration Commands

```bash
# Run migrations
python database/migration.py

# Add persona usage tracking
python database/migrate_persona_usage.py

# Add performance indexes
python database/add_indexes.py
```