# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository appears to be focused on synthetic essay generation for educational demonstrations. It contains a Markdown file documenting a conversation about creating diverse, AI-generated student essays for an English 202/Critical Thinking course.

The project incorporates multiple LLMs (Language Learning Models) using the litellm SDK for concurrent model comparison and diverse essay generation.

## Key Components

### Synethic_Essays.md

- Contains a comprehensive conversation about generating synthetic student essays
- Includes a complete Python framework for creating diverse AI-generated essays
- Discusses strategies for ensuring diversity in synthetic content
- Covers technical implementation details for a Canvas LMS integration

## Common Development Tasks

The main Python script in the Markdown file requires:
- Setting up API keys as environment variables (e.g., `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`)
- Installing necessary libraries:
  - `pip install litellm` (unified SDK for multiple LLM providers)  
  - `pip install openai` (if using OpenAI directly)
  - `pip install google-generativeai` (for Gemini models)
  - `pip install python-dotenv` (for environment variable management)
- Running the generation script: `python your_script_name.py`

### Multi-LLM Benchmark Approach

Based on the `benchmark.py` pattern from the AI education project:
- Uses litellm SDK for unified access to multiple LLM providers
- Supports concurrent model queries using ThreadPoolExecutor
- Configures models with specific temperature settings and parameters
- Handles authentication via API keys loaded from environment or files

## Architecture Notes

### Synthetic Essay Generation Framework

The Python framework follows this structure:
1. Configuration variables defining assignment prompts, student archetypes, and LLM settings
2. Helper functions for prompt construction and LLM API calls
3. Main orchestration logic to generate diverse essays based on different archetypes
4. Output handling for both individual essay files and consolidated JSON export

Key design elements:
- Uses "archetypes" to ensure diversity (different student profiles, writing qualities, perspectives)
- Research snippets generated via Perplexity API for authentic content variation and diversity
- Configurable LLM parameters (temperature, max tokens, model selection)
- Batch generation with metadata tracking for Canvas LMS integration

### Research Seeding with Perplexity

The framework uses Perplexity API to generate research snippets that seed the essay generation process:

1. **Generate Diverse Research Context**:
   - Query Perplexity for current information about the essay topic
   - Extract multiple viewpoints, statistics, and recent developments
   - Create 5-10 unique research snippets per assignment prompt

2. **Integrate with Essay Generation**:
   ```python
   # Example research snippet generation
   research_snippets = perplexity_search(MAIN_ASSIGNMENT_PROMPT)
   # Each snippet provides unique context for essay variety
   ```

3. **Benefits for Synthetic Data**:
   - Introduces real-world, timely information
   - Creates authentic diversity in arguments and evidence
   - Prevents models from generating similar content
   - Simulates actual student research patterns

### Essay Diversity Framework

The synthetic essay generation uses a multi-dimensional tree model to maximize diversity across all outputs. Each branching level introduces specific variations:

#### 1. Root Level: Topic Seeding (Perplexity-driven)
- **Research Angles**: Current debates, controversial aspects, future implications, historical context, economic impacts, social justice perspectives, technological aspects, environmental considerations
- **Extracted Elements**: Facts, quotes, sources, statistics, expert opinions
- **Diversity Goal**: 8-10 unique research seeds per main topic

#### 2. Branch Level 1: Argument Stances
```python
STANCE_VARIATIONS = {
    'strongly_for': {'position': 1.0, 'certainty': 'absolute'},
    'moderately_for': {'position': 0.7, 'certainty': 'confident'},
    'slightly_for': {'position': 0.5, 'certainty': 'tentative'},
    'neutral': {'position': 0.0, 'certainty': 'exploratory'},
    'slightly_against': {'position': -0.5, 'certainty': 'cautious'},
    'moderately_against': {'position': -0.7, 'certainty': 'firm'},
    'strongly_against': {'position': -1.0, 'certainty': 'vehement'},
    'nuanced': {'position': 'varies', 'certainty': 'analytical'}
}
```

#### 3. Branch Level 2: Student Personas
- **Backgrounds**: First-generation college, international student, returning adult learner, honors program, student athlete, STEM major in humanities, humanities major in sciences
- **Writing Strengths**: Analytical skills, creative expression, methodical structure, passionate argumentation, research integration
- **Writing Weaknesses**: Grammar struggles, organization issues, citation problems, over-generalization, weak transitions, limited vocabulary, missing counter-arguments

#### 4. Branch Level 3: Evidence Types
```python
EVIDENCE_PATTERNS = {
    'empirical': ['statistics', 'studies', 'data'],
    'anecdotal': ['personal experience', 'case studies', 'examples'],
    'theoretical': ['philosophical arguments', 'logical reasoning', 'hypotheticals'],
    'authoritative': ['expert quotes', 'institutional positions', 'regulations'],
    'comparative': ['historical parallels', 'cross-cultural analysis', 'analogies']
}
```

#### 5. Leaf Level: Writing Style Variations
- **Formality**: Scale 0-1 (casual to very formal), normally distributed around 0.7
- **Complexity**: Sentence structure complexity, normally distributed around 0.6
- **Emotionality**: Logical vs passionate tone, uniformly distributed 0.1-0.8
- **Confidence**: Hedging vs assertive language, normally distributed around 0.65

#### 6. Quality Injection Patterns
- **Grade A**: Clear thesis (1.0), strong evidence integration (0.9), includes counter-arguments, sophisticated transitions
- **Grade B**: Good thesis (0.8), decent evidence (0.7), may include counter-arguments, standard transitions
- **Grade C**: Adequate thesis (0.6), basic evidence (0.5), no counter-arguments, basic transitions
- **Grade D**: Weak thesis (0.4), poor evidence (0.3), logical fallacies, weak transitions, conceptual errors

#### 7. Multi-LLM Diversity Layer
- Use different models (GPT-4, Gemini, Claude) with varied temperature settings
- Each model brings its own stylistic tendencies and knowledge patterns
- Concurrent generation for efficiency using ThreadPoolExecutor

### Multi-LLM Integration

To incorporate multiple LLMs (following the pattern from benchmark.py):

1. **Define Models Configuration**: 
   ```python
   MODELS = [
       {"name": "ChatGPT 4o", "model": "gpt-4o", "provider": "openai", "temperature": 0.8},
       {"name": "Gemini 2.5 Pro", "model": "gemini-2.5-pro-preview", "provider": "gemini", "temperature": 0.8},
       {"name": "Claude 3.7 Sonnet", "model": "claude-3-7-sonnet", "provider": "anthropic", "temperature": 1.0},
   ]
   ```

2. **Use litellm for Unified API Access**:
   - Handle provider-specific authentication
   - Support concurrent model queries
   - Configure model-specific parameters (e.g., thinking mode for Claude)

3. **Parallel Generation**:
   - Use ThreadPoolExecutor for concurrent requests
   - Generate essays from multiple models for each archetype
   - Compare responses across models for diversity analysis

4. **Token Usage Tracking**:
   - Monitor token consumption across different models
   - Track response times and success rates