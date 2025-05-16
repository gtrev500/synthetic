import asyncio
from datetime import datetime
from typing import Dict, List

from database.manager import DatabaseManager
from diversity.manager import DiversityManager
from generation.llm_manager import LLMManager

class EssayGenerator:
    def __init__(self, models_config: List[Dict], db_manager: DatabaseManager, base_tokens: int = 1500):
        self.llm_manager = LLMManager(models_config, base_tokens)
        self.db_manager = db_manager
        self.diversity_manager = DiversityManager()
    
    async def generate_essays(self, combinations: List[Dict], batch_size: int = 5) -> List[Dict]:
        """Generate essays from combinations, managing database interactions."""
        all_essays = []
        
        # Process in batches to manage memory and API rate limits
        for i in range(0, len(combinations), batch_size):
            batch = combinations[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(combinations) + batch_size - 1)//batch_size}")
            
            # Create prompts for this batch
            prompts = []
            for combo in batch:
                prompt_data = self.diversity_manager.create_composite_prompt(combo)
                prompts.append(prompt_data)
            
            # Generate essays for this batch
            batch_essays = await self.llm_manager.generate_batch(prompts)
            
            # Process and save each essay
            for essay in batch_essays:
                if essay is None:
                    continue
                
                # Extract metadata components
                metadata = essay['metadata']
                
                # Save components to database if they don't exist
                stance = self.db_manager.get_or_create_stance(metadata['stance'])
                persona = self.db_manager.save_persona(metadata['persona'])
                evidence = self.db_manager.save_evidence_pattern(metadata['evidence'])
                style = self.db_manager.save_style_parameters(metadata['style'])
                quality = self.db_manager.save_quality_level(metadata['quality'])
                
                # Prepare essay data for database while preserving metadata
                essay_data = {
                    'content': essay['content'],
                    'seed_id': metadata['seed']['id'] if 'id' in metadata['seed'] else None,
                    'stance_id': stance.id,
                    'persona_id': persona.id,
                    'evidence_id': evidence.id,
                    'style_id': style.id,
                    'quality_id': quality.id,
                    'model_name': essay['model_name'],
                    'temperature': essay['temperature'],
                    'prompt_hash': essay['prompt_hash'],
                    'metadata': metadata  # Preserve original metadata for export
                }
                
                all_essays.append(essay_data)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(combinations):
                await asyncio.sleep(1)
        
        return all_essays
    
    async def generate_with_diversity_report(self, combinations: List[Dict], 
                                          batch_size: int = 5) -> Dict:
        """Generate essays and include a diversity report."""
        
        # Generate diversity report before starting
        diversity_report = self.diversity_manager.get_diversity_report(combinations)
        
        # Generate essays
        essays = await self.generate_essays(combinations, batch_size)
        
        # Add generation statistics to report
        generation_stats = {
            'total_requested': len(combinations),
            'total_generated': len(essays),
            'success_rate': len(essays) / len(combinations) if combinations else 0,
            'models_used': list(set(e['model_name'] for e in essays)),
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'essays': essays,
            'diversity_report': diversity_report,
            'generation_stats': generation_stats
        }