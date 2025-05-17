from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ResearchSeed(Base):
    __tablename__ = 'research_seeds'
    
    id = Column(Integer, primary_key=True)
    angle = Column(String(200))
    facts = Column(JSON)
    quotes = Column(JSON)
    sources = Column(JSON)
    created_at = Column(DateTime)
    
    essays = relationship("Essay", back_populates="seed")

class Stance(Base):
    __tablename__ = 'stances'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    position = Column(Float)
    certainty = Column(String(50))
    
    essays = relationship("Essay", back_populates="stance")

class Persona(Base):
    __tablename__ = 'personas'
    
    id = Column(Integer, primary_key=True)
    background = Column(String(200))
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    interests = Column(JSON)
    created_at = Column(DateTime)
    
    essays = relationship("Essay", back_populates="persona")

class EvidencePattern(Base):
    __tablename__ = 'evidence_patterns'
    
    id = Column(Integer, primary_key=True)
    primary_type = Column(String(50))
    secondary_type = Column(String(50))
    patterns = Column(JSON)
    primary_ratio = Column(Float)
    
    essays = relationship("Essay", back_populates="evidence")

class StyleParameter(Base):
    __tablename__ = 'style_parameters'
    
    id = Column(Integer, primary_key=True)
    formality = Column(Float)
    complexity = Column(Float)
    emotionality = Column(Float)
    confidence = Column(Float)
    
    essays = relationship("Essay", back_populates="style")

class QualityLevel(Base):
    __tablename__ = 'quality_levels'
    
    id = Column(Integer, primary_key=True)
    grade = Column(String(2))
    thesis_clarity = Column(Float)
    evidence_integration = Column(Float)
    counter_arguments = Column(Boolean)
    transitions = Column(String(50))
    conclusion_type = Column(String(50))
    errors = Column(JSON)
    
    essays = relationship("Essay", back_populates="quality")

class Prompt(Base):
    __tablename__ = 'prompts'
    
    id = Column(Integer, primary_key=True)
    base_prompt = Column(Text)
    modulated_prompt = Column(Text)
    prompt_metadata = Column(JSON)  # Store breakdown of prompt components
    hash = Column(String(64))  # SHA-256 hash for deduplication
    created_at = Column(DateTime)
    
    essays = relationship("Essay", back_populates="prompt")

class Essay(Base):
    __tablename__ = 'essays'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    word_count = Column(Integer)
    created_at = Column(DateTime)
    
    # Foreign keys
    seed_id = Column(Integer, ForeignKey('research_seeds.id'))
    stance_id = Column(Integer, ForeignKey('stances.id'))
    persona_id = Column(Integer, ForeignKey('personas.id'))
    evidence_id = Column(Integer, ForeignKey('evidence_patterns.id'))
    style_id = Column(Integer, ForeignKey('style_parameters.id'))
    quality_id = Column(Integer, ForeignKey('quality_levels.id'))
    prompt_id = Column(Integer, ForeignKey('prompts.id'))  # New foreign key
    
    # Additional metadata
    model_name = Column(String(100))
    temperature = Column(Float)
    prompt_hash = Column(String(64))
    
    # Relationships
    seed = relationship("ResearchSeed", back_populates="essays")
    stance = relationship("Stance", back_populates="essays")
    persona = relationship("Persona", back_populates="essays")
    evidence = relationship("EvidencePattern", back_populates="essays")
    style = relationship("StyleParameter", back_populates="essays")
    quality = relationship("QualityLevel", back_populates="essays")
    prompt = relationship("Prompt", back_populates="essays")  # New relationship

class GenerationRun(Base):
    __tablename__ = 'generation_runs'
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(36))
    main_topic = Column(String(500))
    config = Column(JSON)
    total_essays = Column(Integer)
    duration_seconds = Column(Float)
    created_at = Column(DateTime)