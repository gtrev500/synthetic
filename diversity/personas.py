import random
from typing import Dict, List
from datetime import datetime

class PersonaManager:
    def __init__(self):
        self.backgrounds = [
            "first-generation college student",
            "international student from Asia",
            "international student from Europe",
            "returning adult learner",
            "honors program student",
            "student athlete",
            "STEM major taking humanities",
            "humanities major exploring sciences",
            "working parent pursuing degree",
            "military veteran student",
            "transfer student from community college",
            "graduate student instructor"
        ]
        
        self.writing_strengths = [
            "strong analytical skills",
            "creative expression",
            "methodical structure",
            "passionate argumentation",
            "research integration",
            "clear thesis development",
            "engaging introductions",
            "persuasive rhetoric",
            "comparative analysis",
            "synthesis of complex ideas"
        ]
        
        self.writing_weaknesses = [
            "grammar struggles",
            "organization issues",
            "citation problems",
            "over-generalization",
            "weak transitions",
            "limited vocabulary",
            "missing counter-arguments",
            "repetitive phrasing",
            "unclear thesis",
            "abrupt conclusions",
            "informal tone when inappropriate",
            "difficulty with complex sentences",
            "tendency to summarize rather than analyze"
        ]
        
        self.interests = [
            "social justice",
            "technology ethics",
            "environmental sustainability",
            "economic policy",
            "healthcare reform",
            "education equality",
            "cultural preservation",
            "scientific innovation",
            "artistic expression",
            "political theory"
        ]
    
    def generate_persona(self) -> Dict:
        num_strengths = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        num_weaknesses = random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0]
        num_interests = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
        
        persona = {
            'background': random.choice(self.backgrounds),
            'strengths': random.sample(self.writing_strengths, num_strengths),
            'weaknesses': random.sample(self.writing_weaknesses, num_weaknesses),
            'interests': random.sample(self.interests, num_interests),
            'created_at': datetime.now()
        }
        
        return persona
    
    def create_persona_prompt(self, persona: Dict) -> str:
        background = persona['background']
        strengths = ", ".join(persona['strengths'])
        weaknesses = ", ".join(persona['weaknesses'])
        interests = ", ".join(persona['interests'])
        
        prompt = f"""Write this essay as a {background} with the following characteristics:
        
Writing Strengths: {strengths}
Writing Weaknesses: {weaknesses}
Academic Interests: {interests}

Incorporate these characteristics naturally into your writing style. 
Your strengths should be evident in the essay's best aspects.
Your weaknesses should manifest as occasional flaws or limitations.
Your background and interests should subtly influence your perspective and examples."""
        
        return prompt
    
    def get_random_personas(self, count: int) -> List[Dict]:
        return [self.generate_persona() for _ in range(count)]