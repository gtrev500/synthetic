import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from database.schema import (
    Base, ResearchSeed, Stance, Persona, EvidencePattern,
    StyleParameter, QualityLevel, Essay, GenerationRun
)

class DatabaseManager:
    def __init__(self, db_path: str = "synthetic_essays.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
    
    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_research_seeds(self, seeds: List[Dict]) -> List[ResearchSeed]:
        saved_seeds = []
        with self.get_session() as session:
            for seed_data in seeds:
                seed = ResearchSeed(
                    angle=seed_data['angle'],
                    facts=seed_data['facts'],
                    quotes=seed_data['quotes'],
                    sources=seed_data['sources'],
                    created_at=datetime.now()
                )
                session.add(seed)
                session.flush()
                saved_seeds.append(seed)
        return saved_seeds
    
    def save_stance(self, stance_data: Dict) -> Stance:
        with self.get_session() as session:
            stance = Stance(
                name=stance_data['name'],
                position=stance_data['position'],
                certainty=stance_data['certainty']
            )
            session.add(stance)
            session.flush()
            return stance
    
    def save_persona(self, persona_data: Dict) -> Persona:
        with self.get_session() as session:
            persona = Persona(
                background=persona_data['background'],
                strengths=persona_data['strengths'],
                weaknesses=persona_data['weaknesses'],
                created_at=datetime.now()
            )
            session.add(persona)
            session.flush()
            return persona
    
    def save_evidence_pattern(self, evidence_data: Dict) -> EvidencePattern:
        with self.get_session() as session:
            evidence = EvidencePattern(
                primary_type=evidence_data['primary_type'],
                secondary_type=evidence_data['secondary_type'],
                patterns=evidence_data['patterns'],
                primary_ratio=evidence_data['primary_ratio']
            )
            session.add(evidence)
            session.flush()
            return evidence
    
    def save_style_parameters(self, style_data: Dict) -> StyleParameter:
        with self.get_session() as session:
            style = StyleParameter(
                formality=style_data['formality'],
                complexity=style_data['complexity'],
                emotionality=style_data['emotionality'],
                confidence=style_data['confidence']
            )
            session.add(style)
            session.flush()
            return style
    
    def save_quality_level(self, quality_data: Dict) -> QualityLevel:
        with self.get_session() as session:
            quality = QualityLevel(
                grade=quality_data['grade'],
                thesis_clarity=quality_data['thesis_clarity'],
                evidence_integration=quality_data['evidence_integration'],
                counter_arguments=quality_data['counter_arguments'],
                transitions=quality_data['transitions'],
                conclusion_type=quality_data['conclusion_type'],
                errors=quality_data.get('errors', [])
            )
            session.add(quality)
            session.flush()
            return quality
    
    def save_essay(self, essay_data: Dict, run_id: str) -> Essay:
        with self.get_session() as session:
            essay = Essay(
                content=essay_data['content'],
                word_count=len(essay_data['content'].split()),
                created_at=datetime.now(),
                seed_id=essay_data['seed_id'],
                stance_id=essay_data['stance_id'],
                persona_id=essay_data['persona_id'],
                evidence_id=essay_data['evidence_id'],
                style_id=essay_data['style_id'],
                quality_id=essay_data['quality_id'],
                model_name=essay_data['model_name'],
                temperature=essay_data['temperature'],
                prompt_hash=essay_data['prompt_hash']
            )
            session.add(essay)
            session.flush()
            return essay
    
    def save_essays(self, essays: List[Dict], run_id: str) -> List[Essay]:
        saved_essays = []
        for essay_data in essays:
            saved_essay = self.save_essay(essay_data, run_id)
            saved_essays.append(saved_essay)
        return saved_essays
    
    def save_generation_run(self, run_id: str, main_topic: str, 
                          total_essays: int, duration_seconds: float, 
                          config: Optional[Dict] = None):
        with self.get_session() as session:
            run = GenerationRun(
                run_id=run_id,
                main_topic=main_topic,
                config=config or {},
                total_essays=total_essays,
                duration_seconds=duration_seconds,
                created_at=datetime.now()
            )
            session.add(run)
    
    def get_stance_by_name(self, name: str) -> Optional[Stance]:
        with self.get_session() as session:
            return session.query(Stance).filter_by(name=name).first()
    
    def get_or_create_stance(self, stance_data: Dict) -> Stance:
        existing = self.get_stance_by_name(stance_data['name'])
        if existing:
            return existing
        return self.save_stance(stance_data)