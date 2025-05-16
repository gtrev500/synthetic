import random
from typing import Dict, List

class EvidenceManager:
    def __init__(self):
        self.evidence_types = {
            'empirical': {
                'patterns': ['statistics', 'studies', 'data', 'research findings', 'surveys'],
                'description': 'Uses quantitative data and research studies'
            },
            'anecdotal': {
                'patterns': ['personal experience', 'case studies', 'examples', 'stories', 'observations'],
                'description': 'Relies on personal stories and specific examples'
            },
            'theoretical': {
                'patterns': ['philosophical arguments', 'logical reasoning', 'hypotheticals', 'thought experiments', 'principles'],
                'description': 'Employs abstract reasoning and theoretical frameworks'
            },
            'authoritative': {
                'patterns': ['expert quotes', 'institutional positions', 'regulations', 'official statements', 'scholarly opinions'],
                'description': 'Cites experts and authoritative sources'
            },
            'comparative': {
                'patterns': ['historical parallels', 'cross-cultural analysis', 'analogies', 'contrasts', 'comparative studies'],
                'description': 'Draws comparisons across time, cultures, or domains'
            }
        }
    
    def generate_evidence_pattern(self) -> Dict:
        # Choose primary and secondary evidence types
        types = list(self.evidence_types.keys())
        primary_type = random.choice(types)
        remaining_types = [t for t in types if t != primary_type]
        secondary_type = random.choice(remaining_types)
        
        # Determine ratio (how much primary vs secondary)
        primary_ratio = random.uniform(0.6, 0.85)
        
        pattern = {
            'primary_type': primary_type,
            'secondary_type': secondary_type,
            'patterns': {
                'primary': self.evidence_types[primary_type]['patterns'],
                'secondary': self.evidence_types[secondary_type]['patterns']
            },
            'primary_ratio': primary_ratio
        }
        
        return pattern
    
    def create_evidence_prompt(self, pattern: Dict) -> str:
        primary = pattern['primary_type']
        secondary = pattern['secondary_type']
        ratio = pattern['primary_ratio']
        
        primary_desc = self.evidence_types[primary]['description']
        secondary_desc = self.evidence_types[secondary]['description']
        
        primary_percent = int(ratio * 100)
        secondary_percent = 100 - primary_percent
        
        prompt = f"""Structure your evidence as follows:
        
Primary Evidence Type ({primary_percent}%): {primary} - {primary_desc}
Use elements like: {', '.join(pattern['patterns']['primary'][:3])}

Secondary Evidence Type ({secondary_percent}%): {secondary} - {secondary_desc}
Include some: {', '.join(pattern['patterns']['secondary'][:3])}

Blend these evidence types naturally throughout your essay, with the primary type dominating your argumentation."""
        
        return prompt
    
    def get_random_patterns(self, count: int) -> List[Dict]:
        return [self.generate_evidence_pattern() for _ in range(count)]