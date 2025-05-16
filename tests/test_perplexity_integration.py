import pytest
import os
import json
from dotenv import load_dotenv

from research.perplexity import PerplexityClient
from research.seed_generator import ResearchSeedGenerator
from research.models import ResearchData
from pydantic import ValidationError

# Load environment variables
load_dotenv()


@pytest.fixture
def perplexity_api_key():
    """Fixture to get Perplexity API key"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        pytest.skip("PERPLEXITY_API_KEY not found in environment variables")
    return api_key


@pytest.fixture
def perplexity_client(perplexity_api_key):
    """Fixture to create PerplexityClient instance"""
    return PerplexityClient(perplexity_api_key)


@pytest.fixture
def research_seed_generator(perplexity_api_key):
    """Fixture to create ResearchSeedGenerator instance"""
    return ResearchSeedGenerator(perplexity_api_key)


@pytest.mark.asyncio
async def test_perplexity_client_structured_output(perplexity_client):
    """Test the PerplexityClient with structured JSON output"""
    # Test query
    query = """
    Research the topic of free college education.
    
    Please provide a structured JSON response with:
    1. facts: A list of 5-7 specific, relevant facts about free college education
    2. quotes: A list of 2-3 quotes from experts or studies, with proper attribution
    3. sources: A list of credible sources and references with full citations
    """
    
    # Send request to Perplexity API
    response = await perplexity_client.search(query)
    
    # Verify response structure
    assert response is not None
    assert 'choices' in response
    assert len(response['choices']) > 0
    assert 'message' in response['choices'][0]
    assert 'content' in response['choices'][0]['message']
    
    # Parse structured response
    parsed_data = perplexity_client.parse_structured_response(response)
    
    # Verify parsed data
    assert 'facts' in parsed_data
    assert 'quotes' in parsed_data
    assert 'sources' in parsed_data
    assert isinstance(parsed_data['facts'], list)
    assert isinstance(parsed_data['quotes'], list)
    assert isinstance(parsed_data['sources'], list)
    assert len(parsed_data['facts']) > 0
    assert len(parsed_data['quotes']) > 0
    assert len(parsed_data['sources']) > 0


@pytest.mark.asyncio
async def test_pydantic_validation(perplexity_client):
    """Test that response validates with Pydantic model"""
    query = """
    Research the topic of climate change.
    
    Please provide a structured JSON response with:
    1. facts: A list of 5-7 specific, relevant facts about climate change
    2. quotes: A list of 2-3 quotes from experts or studies, with proper attribution
    3. sources: A list of credible sources and references with full citations
    """
    
    response = await perplexity_client.search(query)
    
    # Extract content and validate with Pydantic
    content = response['choices'][0]['message']['content']
    
    # Should not raise ValidationError
    research_data = ResearchData.model_validate_json(content)
    
    # Verify Pydantic model data
    assert len(research_data.facts) >= 1
    assert len(research_data.quotes) >= 1
    assert len(research_data.sources) >= 1
    assert all(isinstance(fact, str) for fact in research_data.facts)
    assert all(isinstance(quote, str) for quote in research_data.quotes)
    assert all(isinstance(source, str) for source in research_data.sources)


@pytest.mark.asyncio
async def test_research_seed_generator(research_seed_generator):
    """Test the ResearchSeedGenerator with multiple angles"""
    topic = "artificial intelligence in education"
    num_seeds = 3
    
    # Generate seeds
    seeds = await research_seed_generator.generate_seeds(topic, num_seeds)
    
    # Verify we got the expected number of seeds
    assert len(seeds) == num_seeds
    
    # Verify each seed has the required structure
    for seed in seeds:
        assert 'angle' in seed
        assert 'topic' in seed
        assert 'facts' in seed
        assert 'quotes' in seed
        assert 'sources' in seed
        assert isinstance(seed['facts'], list)
        assert isinstance(seed['quotes'], list)
        assert isinstance(seed['sources'], list)
        assert len(seed['facts']) > 0
        assert len(seed['quotes']) > 0
        assert len(seed['sources']) > 0
        
        # Verify it's not fallback data
        assert not seed['facts'][0].startswith("General fact")
        assert not seed['quotes'][0].startswith("Expert opinion")


@pytest.mark.asyncio
async def test_error_handling(perplexity_api_key):
    """Test error handling with invalid API key"""
    # Create client with invalid API key
    invalid_client = PerplexityClient("invalid_api_key")
    
    query = "Test query"
    
    # Should raise an exception
    with pytest.raises(Exception) as exc_info:
        await invalid_client.search(query)
    
    assert "Perplexity API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_seed_generator_fallback(research_seed_generator):
    """Test that seed generator provides fallback data on error"""
    # Mock the client's search method to raise an error
    original_search = research_seed_generator.client.search
    
    async def mock_search(*args, **kwargs):
        raise Exception("Simulated API error")
    
    research_seed_generator.client.search = mock_search
    
    # Generate seed with error
    seed = await research_seed_generator._generate_seed("test angle", "test topic")
    
    # Verify fallback data
    assert seed['angle'] == "test angle"
    assert seed['topic'] == "test topic"
    assert seed['facts'][0] == "General fact about test angle"
    assert seed['quotes'][0] == "Expert opinion on test angle"
    assert seed['sources'][0] == "Academic source"
    
    # Restore original method
    research_seed_generator.client.search = original_search


@pytest.mark.asyncio
async def test_json_decode_error_handling(perplexity_client):
    """Test handling of invalid JSON in response"""
    # Create a mock response with invalid JSON
    mock_response = {
        "choices": [{
            "message": {
                "content": "This is not valid JSON"
            }
        }]
    }
    
    # Parse should handle the error gracefully
    parsed_data = perplexity_client.parse_structured_response(mock_response)
    
    # Should return fallback data
    assert parsed_data['facts'][0] == "Unable to extract facts from research"
    assert parsed_data['quotes'][0] == "Unable to extract quotes from research"
    assert parsed_data['sources'][0] == "Unable to extract sources from research"