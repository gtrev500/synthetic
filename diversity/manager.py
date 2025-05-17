import random
from typing import Dict, List

from diversity.stances import StanceManager
from diversity.personas import PersonaManager
from diversity.evidence import EvidenceManager
from diversity.styles import StyleManager
from diversity.quality import QualityManager

class DiversityManager:
    def __init__(self):
        self.stance_manager = StanceManager()
        self.persona_manager = PersonaManager()
        self.evidence_manager = EvidenceManager()
        self.style_manager = StyleManager()
        self.quality_manager = QualityManager()
    
    def generate_combinations(self, seeds: List[Dict], num_essays: int) -> List[Dict]:
        """Generate diverse combinations of all parameters for essay generation."""
        combinations = []
        
        # Get all possible stances
        stances = self.stance_manager.get_all_stances()
        
        # Calculate how many essays per seed (roughly)
        essays_per_seed = max(1, num_essays // len(seeds))
        
        # Generate combinations
        for i in range(num_essays):
            # Rotate through seeds
            seed = seeds[i % len(seeds)]
            
            # Rotate through stances with some randomization
            stance_index = i % len(stances)
            if random.random() < 0.3:  # 30% chance to pick random stance
                stance_index = random.randint(0, len(stances) - 1)
            stance = stances[stance_index]
            
            # Generate other parameters
            persona = self.persona_manager.generate_persona()
            evidence = self.evidence_manager.generate_evidence_pattern()
            style = self.style_manager.generate_style_parameters()
            quality = self.quality_manager.generate_quality_with_distribution()
            
            combination = {
                'seed': seed,
                'stance': stance,
                'persona': persona,
                'evidence': evidence,
                'style': style,
                'quality': quality,
                'combination_id': f"combo_{i:04d}"
            }
            
            combinations.append(combination)
        
        return combinations
    
    def create_composite_prompt(self, combination: Dict) -> Dict:
        """Create a comprehensive prompt from all diversity parameters."""
        
        # Extract components
        seed = combination['seed']
        stance = combination['stance']
        persona = combination['persona']
        evidence = combination['evidence']
        style = combination['style']
        quality = combination['quality']
        
        # Build prompts for each component
        stance_prompt = self.stance_manager.create_stance_prompt(stance)
        persona_prompt = self.persona_manager.create_persona_prompt(persona)
        evidence_prompt = self.evidence_manager.create_evidence_prompt(evidence)
        style_prompt = self.style_manager.create_style_prompt(style)
        quality_prompt = self.quality_manager.create_quality_prompt(quality)
        
        # Create base prompt (research context and general requirements)
        base_prompt = f"""You are writing an essay for an English 202 Critical Thinking course.

RESEARCH CONTEXT:
Topic Angle: {seed['angle']}
Key Facts to Consider:
{chr(10).join(f'- {fact}' for fact in seed['facts'][:5])}

Expert Perspectives:
{chr(10).join(f'- {quote}' for quote in seed['quotes'][:3])}

ESSAY REQUIREMENTS:
Write ONLY the essay text itself. Do not include any meta-commentary, titles, or headers. Begin directly with your introduction paragraph.

The essay should be approximately 750-1000 words."""
        
        # Create modulated prompt (base + diversity components)
        modulated_prompt = f"""{base_prompt}

{stance_prompt}

{persona_prompt}

{evidence_prompt}

{style_prompt}

{quality_prompt}"""
        
        # Create prompt metadata
        prompt_metadata = {
            'stance': stance_prompt,
            'persona': persona_prompt,
            'evidence': evidence_prompt,
            'style': style_prompt,
            'quality': quality_prompt
        }
        
        return {
            'prompt': modulated_prompt,  # The full prompt for the LLM
            'base_prompt': base_prompt,  # The base prompt without diversity
            'prompt_metadata': prompt_metadata,  # Breakdown of diversity components
            'metadata': combination  # Original combination data
        }
    
    def get_diversity_report(self, combinations: List[Dict]) -> Dict:
        """Generate a report on the diversity of the combinations."""
        report = {
            'total_combinations': len(combinations),
            'stance_distribution': {},
            'quality_distribution': {},
            'evidence_patterns': {},
            'persona_backgrounds': {},
            'unique_seeds': len(set(c['seed']['angle'] for c in combinations))
        }
        
        # Count distributions
        for combo in combinations:
            stance_name = combo['stance']['name']
            quality_grade = combo['quality']['grade']
            evidence_primary = combo['evidence']['primary_type']
            persona_bg = combo['persona']['background']
            
            report['stance_distribution'][stance_name] = report['stance_distribution'].get(stance_name, 0) + 1
            report['quality_distribution'][quality_grade] = report['quality_distribution'].get(quality_grade, 0) + 1
            report['evidence_patterns'][evidence_primary] = report['evidence_patterns'].get(evidence_primary, 0) + 1
            report['persona_backgrounds'][persona_bg] = report['persona_backgrounds'].get(persona_bg, 0) + 1
        
        return report