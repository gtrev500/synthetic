import random
from typing import Dict, List

class QualityManager:
    def __init__(self):
        self.quality_levels = {
            'A': {
                'grade': 'A',
                'thesis_clarity': 1.0,
                'evidence_integration': 0.9,
                'counter_arguments': True,
                'transitions': 'sophisticated',
                'conclusion_type': 'synthesizing',
                'errors': [],
                'description': 'Excellent essay with clear thesis, strong evidence, and sophisticated analysis'
            },
            'B': {
                'grade': 'B',
                'thesis_clarity': 0.8,
                'evidence_integration': 0.7,
                'counter_arguments': random.choice([True, False]),
                'transitions': 'standard',
                'conclusion_type': 'summarizing',
                'errors': ['minor grammatical issues'],
                'description': 'Good essay with solid arguments but some minor weaknesses'
            },
            'C': {
                'grade': 'C',
                'thesis_clarity': 0.6,
                'evidence_integration': 0.5,
                'counter_arguments': False,
                'transitions': 'basic',
                'conclusion_type': 'repetitive',
                'errors': ['organization issues', 'some unclear points'],
                'description': 'Adequate essay that meets basic requirements but lacks depth'
            },
            'D': {
                'grade': 'D',
                'thesis_clarity': 0.4,
                'evidence_integration': 0.3,
                'counter_arguments': False,
                'transitions': 'weak',
                'conclusion_type': 'abrupt',
                'errors': ['significant grammar errors', 'unclear thesis', 'poor organization'],
                'description': 'Below average essay with significant weaknesses'
            },
            'F': {
                'grade': 'F',
                'thesis_clarity': 0.2,
                'evidence_integration': 0.1,
                'counter_arguments': False,
                'transitions': 'absent',
                'conclusion_type': 'missing',
                'errors': ['off-topic', 'major comprehension issues', 'incoherent arguments'],
                'description': 'Failing essay that does not meet basic requirements'
            }
        }
        
        self.error_patterns = {
            'conceptual': [
                'misunderstand key concepts',
                'confuse correlation with causation',
                'overgeneralize from limited examples',
                'present opinions as facts'
            ],
            'structural': [
                'lack clear paragraph structure',
                'jump between topics without transitions',
                'include irrelevant tangents',
                'fail to support claims with evidence'
            ],
            'grammatical': [
                'use inconsistent verb tenses',
                'have subject-verb disagreement',
                'misuse punctuation',
                'create run-on sentences'
            ],
            'citation': [
                'forget to cite sources',
                'use improper citation format',
                'fail to distinguish quotes from paraphrases',
                'rely too heavily on one source'
            ]
        }
    
    def get_quality_level(self, grade: str) -> Dict:
        return self.quality_levels.get(grade, self.quality_levels['C'])
    
    def generate_quality_with_distribution(self, weights: Dict[str, float] = None) -> Dict:
        if weights is None:
            weights = {'A': 0.15, 'B': 0.35, 'C': 0.35, 'D': 0.12, 'F': 0.03}
        
        grades = list(weights.keys())
        probabilities = list(weights.values())
        
        selected_grade = random.choices(grades, weights=probabilities)[0]
        quality = self.quality_levels[selected_grade].copy()
        
        # Add specific errors for lower grades
        if selected_grade in ['C', 'D', 'F']:
            num_error_types = {'C': 1, 'D': 2, 'F': 3}[selected_grade]
            error_types = random.sample(list(self.error_patterns.keys()), num_error_types)
            
            specific_errors = []
            for error_type in error_types:
                errors = random.sample(self.error_patterns[error_type], k=random.randint(1, 2))
                specific_errors.extend(errors)
            
            quality['errors'] = specific_errors
        
        return quality
    
    def create_quality_prompt(self, quality: Dict) -> str:
        grade = quality['grade']
        
        if grade == 'A':
            prompt = """Write an excellent essay that:
- Presents a crystal-clear, sophisticated thesis
- Integrates evidence seamlessly and effectively
- Addresses counter-arguments thoughtfully
- Uses sophisticated transitions between ideas
- Concludes by synthesizing arguments into new insights
- Demonstrates mastery of grammar and style"""
        
        elif grade == 'B':
            prompt = """Write a good essay that:
- Has a clear thesis with minor ambiguities
- Uses evidence well but occasionally could integrate it better
- May or may not address counter-arguments
- Uses standard transitions effectively
- Concludes by summarizing main points
- Has minor grammatical issues that don't impede understanding"""
        
        elif grade == 'C':
            prompt = f"""Write an adequate essay that:
- Has a thesis that is somewhat unclear or too broad
- Uses evidence but doesn't always integrate it smoothly
- Ignores potential counter-arguments
- Uses basic transitions like "first," "second," "finally"
- Concludes by simply repeating the introduction
- Shows these specific issues: {', '.join(quality['errors'])}"""
        
        elif grade == 'D':
            prompt = f"""Write a below-average essay that:
- Has a weak or confused thesis statement
- Poorly integrates evidence or uses inappropriate sources
- Completely ignores opposing viewpoints
- Has weak or missing transitions between paragraphs
- Ends abruptly without proper conclusion
- Contains these problems: {', '.join(quality['errors'])}"""
        
        else:  # F
            prompt = f"""Write a failing essay that:
- Lacks a clear thesis or completely misunderstands the prompt
- Fails to use evidence effectively or at all
- Shows no awareness of complexity in the topic
- Has no clear organizational structure
- May not even have a conclusion
- Exhibits these major flaws: {', '.join(quality['errors'])}"""
        
        return prompt
    
    def get_grade_distribution(self) -> Dict[str, float]:
        return {'A': 0.15, 'B': 0.35, 'C': 0.35, 'D': 0.12, 'F': 0.03}