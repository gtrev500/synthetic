from typing import Dict, List

class PromptBuilder:
    def __init__(self):
        self.base_context = """You are writing an essay for an English 202 Critical Thinking course.
This is an academic essay that should demonstrate critical analysis, logical argumentation, and proper essay structure."""
    
    def build_research_section(self, seed: Dict) -> str:
        """Build the research context section of the prompt."""
        research = f"""
RESEARCH CONTEXT:
Topic Angle: {seed['angle']}

Key Facts to Consider:
{self._format_list(seed.get('facts', [])[:5])}

Expert Perspectives:
{self._format_list(seed.get('quotes', [])[:3])}

Relevant Sources:
{self._format_list(seed.get('sources', [])[:3])}
"""
        return research
    
    def build_requirements_section(self, combination: Dict) -> str:
        """Build the requirements section from all diversity parameters."""
        requirements = []
        
        # Add each component's requirements
        if 'stance_prompt' in combination:
            requirements.append(combination['stance_prompt'])
        
        if 'persona_prompt' in combination:
            requirements.append(combination['persona_prompt'])
        
        if 'evidence_prompt' in combination:
            requirements.append(combination['evidence_prompt'])
        
        if 'style_prompt' in combination:
            requirements.append(combination['style_prompt'])
        
        if 'quality_prompt' in combination:
            requirements.append(combination['quality_prompt'])
        
        return "\n\n".join(requirements)
    
    def build_complete_prompt(self, combination: Dict) -> str:
        """Build the complete prompt from all components."""
        seed = combination['seed']
        
        prompt_parts = [
            self.base_context,
            self.build_research_section(seed),
            "ESSAY REQUIREMENTS:",
            self.build_requirements_section(combination),
            self._get_closing_instructions()
        ]
        
        return "\n\n".join(prompt_parts)
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as bullet points."""
        if not items:
            return "- No specific items provided"
        return "\n".join(f"- {item}" for item in items)
    
    def _get_closing_instructions(self) -> str:
        """Get the closing instructions for the essay."""
        return """
IMPORTANT INSTRUCTIONS:
1. Write ONLY the essay text itself
2. Do not include any meta-commentary, titles, or headers
3. Begin directly with your introduction paragraph
4. Aim for approximately 750-1000 words
5. Ensure your essay has:
   - A clear introduction with thesis statement
   - Body paragraphs with topic sentences
   - Supporting evidence and analysis
   - A conclusive ending that reinforces your argument
   
Remember to write authentically as a student with the specified characteristics, not as an AI assistant."""