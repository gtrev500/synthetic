from typing import Dict, List

class StanceManager:
    def __init__(self):
        self.stances = {
            'strongly_for': {
                'name': 'strongly_for',
                'position': 1.0,
                'certainty': 'absolute',
                'description': 'Strongly advocates for the topic with unwavering conviction'
            },
            'moderately_for': {
                'name': 'moderately_for',
                'position': 0.7,
                'certainty': 'confident',
                'description': 'Generally supports the topic with reasonable confidence'
            },
            'slightly_for': {
                'name': 'slightly_for',
                'position': 0.5,
                'certainty': 'tentative',
                'description': 'Leans toward supporting but acknowledges uncertainties'
            },
            'neutral': {
                'name': 'neutral',
                'position': 0.0,
                'certainty': 'exploratory',
                'description': 'Explores multiple perspectives without taking a firm position'
            },
            'slightly_against': {
                'name': 'slightly_against',
                'position': -0.5,
                'certainty': 'cautious',
                'description': 'Questions aspects of the topic with measured skepticism'
            },
            'moderately_against': {
                'name': 'moderately_against',
                'position': -0.7,
                'certainty': 'firm',
                'description': 'Clearly opposes with well-reasoned arguments'
            },
            'strongly_against': {
                'name': 'strongly_against',
                'position': -1.0,
                'certainty': 'vehement',
                'description': 'Vehemently opposes with strong conviction'
            },
            'nuanced': {
                'name': 'nuanced',
                'position': 'varies',
                'certainty': 'analytical',
                'description': 'Takes a complex position that varies by aspect'
            }
        }
    
    def get_stance(self, name: str) -> Dict:
        return self.stances.get(name, self.stances['neutral'])
    
    def get_all_stances(self) -> List[Dict]:
        return list(self.stances.values())
    
    def create_stance_prompt(self, stance: Dict) -> str:
        if stance['name'] == 'nuanced':
            return f"""Take a nuanced, analytical approach that:
- Acknowledges multiple valid perspectives
- Weighs pros and cons carefully
- Arrives at a sophisticated, context-dependent conclusion
- Shows deep critical thinking"""
        
        direction = "supporting" if stance['position'] > 0 else "opposing" if stance['position'] < 0 else "neutral about"
        strength = abs(stance['position'])
        
        if strength == 1.0:
            intensity = "very strongly"
        elif strength >= 0.7:
            intensity = "clearly"
        elif strength >= 0.5:
            intensity = "somewhat"
        else:
            intensity = "neutrally examining"
        
        return f"""Write an essay {intensity} {direction} the topic.
Your tone should be {stance['certainty']} and your arguments should reflect a {stance['description']}.
Make sure your thesis and conclusion align with this stance."""