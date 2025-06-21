#!/usr/bin/env python3
"""Script to create demo essay files from the database."""

import sqlite3
import json
import os

def create_essay_markdown(essay_data):
    """Create markdown content for a single essay."""
    
    # Unpack all the data
    (essay_id, stance, grade, persona, model, word_count, created_at, temperature, prompt_hash,
     prompt_id, seed_id, stance_id, persona_id, evidence_id, style_id, quality_id,
     position, certainty, thesis_clarity, evidence_integration, counter_arguments,
     transitions, conclusion_type, errors, strengths, weaknesses, interests,
     ev_primary, ev_secondary, ev_ratio, ev_patterns,
     formality, complexity, emotionality, confidence,
     angle, facts, quotes, sources, content) = essay_data
    
    # Parse JSON fields
    errors_list = json.loads(errors) if errors else []
    strengths_list = json.loads(strengths) if strengths else []
    weaknesses_list = json.loads(weaknesses) if weaknesses else []
    interests_list = json.loads(interests) if interests else []
    ev_patterns_list = json.loads(ev_patterns) if ev_patterns else []
    facts_list = json.loads(facts) if facts else []
    quotes_list = json.loads(quotes) if quotes else []
    sources_list = json.loads(sources) if sources else []
    
    # Clean model name for filename
    model_clean = model.replace(' ', '_').replace('.', '')
    
    markdown = f"""# Essay {essay_id}: {stance} - Grade {grade} - {model}

## Full Metadata

### Database IDs
- **Essay ID**: {essay_id}
- **Prompt ID**: {prompt_id}
- **Seed ID**: {seed_id}
- **Stance ID**: {stance_id}
- **Persona ID**: {persona_id}
- **Evidence Pattern ID**: {evidence_id}
- **Style Parameters ID**: {style_id}
- **Quality Level ID**: {quality_id}
- **Created**: {created_at}

### Model Information
- **Model**: {model}
- **Temperature**: {temperature}
- **Prompt Hash**: {prompt_hash}

### Diversity Dimensions

#### Stance: {stance} (ID: {stance_id})
- **Position**: {position}
- **Certainty**: {certainty}

#### Quality Level: Grade {grade} (ID: {quality_id})
- **Thesis Clarity**: {thesis_clarity}
- **Evidence Integration**: {evidence_integration}
- **Counter Arguments**: {'Yes' if counter_arguments else 'No'}
- **Transitions**: {transitions}
- **Conclusion Type**: {conclusion_type}
- **Common Errors**: {json.dumps(errors_list)}

#### Persona: {persona} (ID: {persona_id})
- **Background**: {persona}
- **Strengths**: {json.dumps(strengths_list)}
- **Weaknesses**: {json.dumps(weaknesses_list)}
- **Interests**: {json.dumps(interests_list)}

#### Evidence Pattern (ID: {evidence_id})
- **Primary Type**: {ev_primary}
- **Secondary Type**: {ev_secondary}
- **Primary Ratio**: {ev_ratio}
- **Patterns**: {json.dumps(ev_patterns_list)}

#### Style Parameters (ID: {style_id})
- **Formality**: {formality}
- **Complexity**: {complexity}
- **Emotionality**: {emotionality}
- **Confidence**: {confidence}

### Research Seed (ID: {seed_id})
- **Angle**: {angle}
- **Key Facts**: {json.dumps(facts_list)}
- **Quotes**: {json.dumps(quotes_list)}
- **Sources**: {json.dumps(sources_list)}

## Essay Content

**Word Count**: {word_count}

---

{content}
"""
    
    filename = f"essay_{essay_id:03d}_{stance}_{grade}_{model_clean}.md"
    return filename, markdown

def main():
    # Connect to database
    conn = sqlite3.connect('synthetic_essays.db')
    cursor = conn.cursor()
    
    # Essay IDs to export
    essay_ids = [1, 2, 3, 10, 11, 12, 22, 23, 24]
    
    for essay_id in essay_ids:
        # Get all essay data
        cursor.execute("""
            SELECT 
                e.id, s.name, q.grade, p.background, e.model_name, 
                e.word_count, e.created_at, e.temperature, e.prompt_hash,
                e.prompt_id, e.seed_id, s.id, p.id, ev.id, sp.id, q.id,
                s.position, s.certainty,
                q.thesis_clarity, q.evidence_integration, q.counter_arguments, 
                q.transitions, q.conclusion_type, q.errors,
                p.strengths, p.weaknesses, p.interests,
                ev.primary_type, ev.secondary_type, ev.primary_ratio, ev.patterns,
                sp.formality, sp.complexity, sp.emotionality, sp.confidence,
                rs.angle, rs.facts, rs.quotes, rs.sources,
                e.content
            FROM essays e 
            JOIN stances s ON e.stance_id = s.id
            JOIN quality_levels q ON e.quality_id = q.id
            JOIN personas p ON e.persona_id = p.id
            JOIN evidence_patterns ev ON e.evidence_id = ev.id
            JOIN style_parameters sp ON e.style_id = sp.id
            JOIN research_seeds rs ON e.seed_id = rs.id
            WHERE e.id = ?
        """, (essay_id,))
        
        essay_data = cursor.fetchone()
        if essay_data:
            filename, markdown = create_essay_markdown(essay_data)
            filepath = os.path.join('demo', 'essays', filename)
            
            with open(filepath, 'w') as f:
                f.write(markdown)
            
            print(f"Created {filepath}")
    
    conn.close()

if __name__ == "__main__":
    main()