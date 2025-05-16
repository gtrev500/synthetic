import numpy as np
from typing import Dict, List

class StyleManager:
    def __init__(self):
        self.style_dimensions = {
            'formality': {
                'low': 'conversational and informal',
                'medium': 'professional but accessible',
                'high': 'highly formal and academic'
            },
            'complexity': {
                'low': 'simple, clear sentences',
                'medium': 'varied sentence structure',
                'high': 'complex, multi-clause sentences'
            },
            'emotionality': {
                'low': 'purely logical and objective',
                'medium': 'balanced logic and emotion',
                'high': 'passionate and emotionally charged'
            },
            'confidence': {
                'low': 'heavily hedged with qualifiers',
                'medium': 'appropriately cautious',
                'high': 'assertive and definitive'
            }
        }
    
    def generate_style_parameters(self) -> Dict:
        # Use normal distribution for natural variation
        style = {
            'formality': np.clip(np.random.normal(0.7, 0.15), 0, 1),
            'complexity': np.clip(np.random.normal(0.6, 0.2), 0, 1),
            'emotionality': np.random.uniform(0.1, 0.8),
            'confidence': np.clip(np.random.normal(0.65, 0.15), 0, 1)
        }
        
        return style
    
    def _get_level(self, value: float) -> str:
        if value < 0.33:
            return 'low'
        elif value < 0.67:
            return 'medium'
        else:
            return 'high'
    
    def create_style_prompt(self, style: Dict) -> str:
        formality_desc = self.style_dimensions['formality'][self._get_level(style['formality'])]
        complexity_desc = self.style_dimensions['complexity'][self._get_level(style['complexity'])]
        emotionality_desc = self.style_dimensions['emotionality'][self._get_level(style['emotionality'])]
        confidence_desc = self.style_dimensions['confidence'][self._get_level(style['confidence'])]
        
        prompt = f"""Apply the following writing style:
        
Tone: {formality_desc}
Sentence Structure: {complexity_desc}
Emotional Content: {emotionality_desc}
Assertion Level: {confidence_desc}

Specific parameters (0-1 scale):
- Formality: {style['formality']:.2f}
- Complexity: {style['complexity']:.2f}
- Emotionality: {style['emotionality']:.2f}
- Confidence: {style['confidence']:.2f}

Let these style parameters naturally influence your word choice, sentence construction, and rhetorical approach."""
        
        return prompt
    
    def get_random_styles(self, count: int) -> List[Dict]:
        return [self.generate_style_parameters() for _ in range(count)]