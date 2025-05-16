import asyncio
import sys
from datetime import datetime
from pathlib import Path
import uuid
import argparse

from config.settings import Settings
from database.manager import DatabaseManager
from research.seed_generator import ResearchSeedGenerator
from diversity.manager import DiversityManager
from generation.generator import EssayGenerator
from generation.llm_manager import LLMManager
from output.markdown import MarkdownExporter
from output.analytics import AnalyticsGenerator

class SyntheticEssaySystem:
    def __init__(self, config_path: str = None):
        self.settings = Settings(config_path)
        self.db = DatabaseManager(self.settings.db_path)
        self.research = ResearchSeedGenerator(self.settings.perplexity_api_key)
        self.diversity = DiversityManager()
        self.llm_manager = LLMManager(self.settings.models)
        self.generator = EssayGenerator(self.settings.models, self.db)
        self.exporter = MarkdownExporter(self.settings.output_dir)
        self.analytics = AnalyticsGenerator(self.settings.output_dir)
    
    async def generate_essay_corpus(self, topic: str, num_essays: int = None):
        """Generate a diverse corpus of synthetic essays."""
        if num_essays is None:
            num_essays = self.settings.default_num_essays
        
        run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        print(f"Starting essay generation run: {run_id}")
        print(f"Topic: {topic}")
        print(f"Target essays: {num_essays}")
        print()
        
        # Check API keys
        print("Checking API keys...")
        key_status = self.llm_manager.validate_api_keys()
        for provider, has_key in key_status.items():
            status = "" if has_key else ""
            print(f"  {provider}: {status}")
        print()
        
        # 1. Generate research seeds
        print(f"Generating research seeds...")
        seeds = await self.research.generate_seeds(topic, num_seeds=10)
        
        # Save seeds to database
        saved_seeds = self.db.save_research_seeds(seeds)
        for seed, saved in zip(seeds, saved_seeds):
            seed['id'] = saved.id
        
        print(f"  Generated {len(seeds)} research seeds")
        print()
        
        # 2. Create diversity combinations
        print("Creating diversity combinations...")
        combinations = self.diversity.generate_combinations(seeds, num_essays)
        print(f"  Created {len(combinations)} unique combinations")
        print()
        
        # 3. Generate essays
        print(f"Generating essays...")
        result = await self.generator.generate_with_diversity_report(
            combinations, 
            batch_size=self.settings.batch_size
        )
        
        essays = result['essays']
        diversity_report = result['diversity_report']
        generation_stats = result['generation_stats']
        
        print(f"  Generated {len(essays)} essays")
        print()
        
        # 4. Save essays to database
        print("Saving to database...")
        saved_essays = self.db.save_essays(essays, run_id)
        print(f"  Saved {len(saved_essays)} essays")
        print()
        
        # 5. Export as markdown
        print("Exporting markdown files...")
        self.exporter.export_essays(essays, run_id)
        print(f"  Exported to: {self.settings.output_dir}/{run_id}/")
        print()
        
        # 6. Generate analytics
        print("Generating analytics...")
        self.analytics.generate_analytics(
            essays, diversity_report, generation_stats, run_id
        )
        print(f"  Analytics saved to: {self.settings.output_dir}/{run_id}/analytics.json")
        print()
        
        # 7. Save generation run metadata
        duration = (datetime.now() - start_time).total_seconds()
        self.db.save_generation_run(
            run_id, topic, len(essays), duration,
            config={'num_requested': num_essays, 'batch_size': self.settings.batch_size}
        )
        
        print(f"Generation complete!")
        print(f"Run ID: {run_id}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Success rate: {generation_stats['success_rate']:.1%}")
        print(f"Output directory: {self.settings.output_dir}/{run_id}/")
        
        return run_id

async def main():
    parser = argparse.ArgumentParser(description='Generate synthetic essays for educational demos')
    parser.add_argument('--topic', type=str, help='Essay topic/prompt')
    parser.add_argument('--num-essays', type=int, default=60, help='Number of essays to generate')
    parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    # Default topic if not provided
    if not args.topic:
        args.topic = """
        Analyze the ethical implications of generative AI in creative industries 
        (e.g., writing, visual arts, music). Consider its impact on originality, 
        copyright, the role of human artists, and the potential for misuse.
        """
    
    system = SyntheticEssaySystem(args.config)
    
    try:
        await system.generate_essay_corpus(args.topic, args.num_essays)
    except KeyboardInterrupt:
        print("\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())