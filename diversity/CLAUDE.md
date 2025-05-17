# Diversity Framework

This module implements a sophisticated multi-dimensional diversity system for generating authentic student essays.

## Architecture

The diversity framework operates through six orthogonal dimensions that combine to create unique essay instances:

### 1. Research Seeds (External Knowledge)
- **Purpose**: Provides factual grounding and real-world context
- **Source**: Perplexity API generates research angles, facts, quotes, and sources
- **Impact**: Ensures essays contain accurate, varied information rather than hallucinated content
- **Diversity**: Multiple seeds per topic create different factual foundations

### 2. Personas (Student Identity)
- **Purpose**: Defines WHO is writing the essay
- **Components**:
  - Background (12 types): "first-generation student", "international student", etc.
  - Strengths (1-3 from 10): "research integration", "creative expression", etc.
  - Weaknesses (1-3 from 13): "grammar struggles", "weak transitions", etc.
  - Interests (1-3 from 10): "social justice", "technology ethics", etc.
- **Impact**: Shapes perspective, examples, and writing patterns
- **Diversity**: ~100,000+ unique combinations possible

### 3. Stances (Argumentative Position)
- **Purpose**: Defines the writer's position on the topic
- **Range**: 8 positions from strongly_for to strongly_against
- **Components**: Position value + certainty level
- **Impact**: Determines argument direction and conviction
- **Diversity**: Same persona can argue different sides

### 4. Evidence Patterns (Argumentation Style)
- **Purpose**: Defines HOW arguments are constructed
- **Types**: Statistical, anecdotal, theoretical, historical, empirical
- **Structure**: Primary type (60-80%) + secondary type
- **Impact**: Shapes the nature of supporting evidence
- **Diversity**: Different evidence approaches for same stance

### 5. Style Parameters (Writing Characteristics)
- **Purpose**: Defines the writing voice and tone
- **Dimensions**:
  - Formality (0.0-1.0): casual → academic
  - Complexity (0.0-1.0): simple → sophisticated
  - Emotionality (0.0-1.0): detached → passionate
  - Confidence (0.0-1.0): tentative → assertive
- **Impact**: Controls sentence structure, vocabulary, expression
- **Diversity**: Continuous values create subtle variations

### 6. Quality Levels (Academic Performance)
- **Purpose**: Simulates realistic grade distributions
- **Grades**: A through F with specific characteristics
- **Components**:
  - Thesis clarity
  - Evidence integration
  - Counter-arguments
  - Transitions
  - Conclusion type
  - Error patterns
- **Impact**: Introduces realistic flaws and limitations
- **Diversity**: Same persona can perform at different levels

## Combinatorial Power

The framework's strength lies in its multiplicative diversity:
- 10 research seeds × 
- ~100,000 persona combinations ×
- 8 stances ×
- 20 evidence patterns ×
- Continuous style space ×
- 5 quality levels ×
- 3-5 LLM models

= Millions of unique essay possibilities per topic

## Design Philosophy

1. **Orthogonality**: Each dimension is independent, preventing conflation
2. **Authenticity**: Combinations reflect real student diversity
3. **Consistency**: Internal coherence within each essay
4. **Scalability**: Easy to add new options to any dimension
5. **Realism**: Flaws and strengths distribute naturally

## Module Structure

- `manager.py`: Central orchestration of all diversity dimensions
- `personas.py`: Student identity generation (background, abilities, interests)
- `stances.py`: Argument position management (for/against spectrum)
- `evidence.py`: Evidence pattern selection (statistical, anecdotal, etc.)
- `styles.py`: Writing style parameters (formality, complexity, etc.)
- `quality.py`: Academic quality levels (A-F with associated characteristics)

## Key Relationships

In the database, each essay references these dimensions through foreign keys:
- `persona_id`: Links to student identity
- `stance_id`: Links to argumentative position
- `evidence_id`: Links to evidence approach
- `style_id`: Links to writing characteristics
- `quality_id`: Links to grade level
- `seed_id`: Links to research content (from research module)

These dimensions combine during essay generation to create authentic, diverse student writing that maintains internal consistency while exhibiting natural variation.