# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a sophisticated system for generating diverse, authentic-looking student essays for educational demonstrations. It uses multiple LLMs via litellm and a multi-dimensional diversity framework to create realistic essay corpora.

## Commands

### Running the System
```bash
# Generate essays with default settings (60 essays on default topic)
python main.py

# Generate essays with custom topic
python main.py --topic "Analyze the ethics of AI in healthcare"

# Generate specific number of essays
python main.py --num-essays 100

# Full example
python main.py --topic "Discuss climate change solutions" --num-essays 50
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_llm_query.py

# Run test script to verify system components
python test_system.py
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file template and add API keys
cp .env.example .env
```

## High-Level Architecture

### Core Flow
```
main.py
├─> ResearchSeedGenerator (research/)
│   └─> Queries Perplexity API for research seeds
├─> DiversityManager (diversity/)
│   └─> Manages all diversity dimensions
├─> EssayGenerator (generation/)
│   └─> Orchestrates LLM calls via litellm
├─> DatabaseManager (database/)
│   └─> Persists all data to SQLite
└─> MarkdownExporter (output/)
    └─> Exports essays and analytics
```

### Key Modules

**research/**
- `seed_generator.py`: Integrates Perplexity API to generate research seeds
- Provides real-world information and multiple viewpoints for essay topics

**diversity/**
- `manager.py`: Central diversity orchestration
- `stances.py`: 8 argument positions (strongly_for → strongly_against)
- `personas.py`: 12+ student backgrounds and characteristics
- `evidence.py`: 5 evidence pattern types
- `styles.py`: Writing style variations (formality, complexity, etc.)
- `quality.py`: 5 grade levels (A-F) with realistic error patterns

**generation/**
- `generator.py`: Main essay generation logic
- `llm_manager.py`: Multi-LLM orchestration with litellm
- `prompt_builder.py`: Constructs prompts from diversity dimensions
- `token_calculator.py`: Manages token limits per model

**database/**
- `manager.py`: SQLAlchemy database interface
- `schema.py`: All database models (Research, Essays, Runs, etc.)

**output/**
- `markdown.py`: Exports essays as markdown files
- `analytics.py`: Generates diversity reports and statistics

### Configuration

All settings in `config/settings.yaml`:
- Model configurations with token multipliers
- API settings
- Database paths
- Batch sizes
- Output directories

### Environment Variables

Required API keys in `.env`:
```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
PERPLEXITY_API_KEY=
```

### Output Structure
```
output/<run-id>/
├── index.md                    # Overview of all essays
├── analytics.json              # Detailed analytics
├── summary_report.md           # Human-readable summary
└── essay_XXX_[stance]_[grade]_[model].md  # Individual essays
```

## Model Configuration

Models are configured with specific temperature and token settings:
- GPT-4o: temperature=0.8, token_multiplier=1.0
- Gemini 2.5 Pro: temperature=0.8, token_multiplier=2.0 (for thinking tokens)
- Claude 3.7 Sonnet: temperature=1.0, token_multiplier=1.2

Base token limit: 3000 (adjusted by model multipliers)

## Rate Limiting

The system includes sophisticated rate limiting:
- Automatic backoff for API limits
- Concurrent request management
- Intelligent retry logic with exponential backoff