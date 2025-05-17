import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from output.markdown import MarkdownExporter


class TestMarkdownExporter:
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_essays(self):
        """Create sample essay data for testing."""
        return [
            {
                'content': 'This is the first essay content about AI ethics.',
                'model_name': 'ChatGPT 4o',
                'temperature': 0.8,
                'word_count': 8,
                'metadata': {
                    'seed': {'angle': 'economic impact', 'sources': ['source1', 'source2']},
                    'stance': {'name': 'strongly_for', 'position': 1.0},
                    'persona': {'background': 'engineering student'},
                    'evidence': {'primary_type': 'empirical'},
                    'style': {
                        'formality': 0.7,
                        'complexity': 0.6,
                        'emotionality': 0.3,
                        'confidence': 0.8
                    },
                    'quality': {'grade': 'A', 'thesis_clarity': 0.9}
                }
            },
            {
                'content': 'This is the second essay content about AI regulation.',
                'model_name': 'Gemini 2.5 Pro',
                'temperature': 0.7,
                'word_count': 8,
                'metadata': {
                    'seed': {'angle': 'ethical concerns', 'sources': ['source3']},
                    'stance': {'name': 'slightly_against', 'position': -0.5},
                    'persona': {'background': 'philosophy major'},
                    'evidence': {'primary_type': 'theoretical'},
                    'style': {
                        'formality': 0.8,
                        'complexity': 0.7,
                        'emotionality': 0.5,
                        'confidence': 0.6
                    },
                    'quality': {'grade': 'B', 'thesis_clarity': 0.7}
                }
            }
        ]
    
    def test_export_essays_with_topic(self, temp_dir, sample_essays):
        """Test that export_essays correctly includes the topic in index.md."""
        exporter = MarkdownExporter(temp_dir)
        run_id = "test-run-123"
        topic = """
        Analyze the ethical implications of generative AI in creative industries 
        (e.g., writing, visual arts, music). Consider its impact on originality, 
        copyright, the role of human artists, and the potential for misuse.
        """
        
        # Export essays with topic
        exported_files = exporter.export_essays(sample_essays, run_id, topic)
        
        # Check that files were created
        run_dir = Path(temp_dir) / run_id
        assert run_dir.exists()
        assert len(exported_files) == len(sample_essays)
        
        # Check that index.md was created and contains the topic
        index_file = run_dir / "index.md"
        assert index_file.exists()
        
        content = index_file.read_text()
        
        # Verify the topic is included
        assert "## Essay Prompt" in content
        assert "Analyze the ethical implications of generative AI" in content
        assert "creative industries" in content
        assert "impact on originality" in content
        
        # Verify other required sections exist
        assert "## Run Information" in content
        assert f"Run ID**: {run_id}" in content
        assert "Total Essays**: 2" in content
        assert "## Essays by Quality Grade" in content
        assert "## Essays by Stance" in content
    
    def test_export_essays_without_topic(self, temp_dir, sample_essays):
        """Test that export_essays works when topic is not provided."""
        exporter = MarkdownExporter(temp_dir)
        run_id = "test-run-456"
        
        # Export essays without topic
        exported_files = exporter.export_essays(sample_essays, run_id)
        
        # Check that index.md was created
        index_file = Path(temp_dir) / run_id / "index.md"
        assert index_file.exists()
        
        content = index_file.read_text()
        
        # Verify the prompt section shows "Not provided"
        assert "## Essay Prompt" in content
        assert "Not provided" in content
    
    def test_export_essays_with_empty_topic(self, temp_dir, sample_essays):
        """Test that export_essays handles empty topic string."""
        exporter = MarkdownExporter(temp_dir)
        run_id = "test-run-789"
        
        # Export essays with empty topic
        exported_files = exporter.export_essays(sample_essays, run_id, "")
        
        # Check that index.md was created
        index_file = Path(temp_dir) / run_id / "index.md"
        assert index_file.exists()
        
        content = index_file.read_text()
        
        # Verify the prompt section shows "Not provided" for empty string
        assert "## Essay Prompt" in content
        assert "Not provided" in content
    
    def test_index_file_structure(self, temp_dir, sample_essays):
        """Test the overall structure of the index.md file."""
        exporter = MarkdownExporter(temp_dir)
        run_id = "test-run-999"
        topic = "Test essay prompt"
        
        exported_files = exporter.export_essays(sample_essays, run_id, topic)
        
        index_file = Path(temp_dir) / run_id / "index.md"
        content = index_file.read_text()
        
        # Check the order of sections
        lines = content.split('\n')
        section_order = []
        for line in lines:
            if line.startswith('## '):
                section_order.append(line)
        
        expected_order = [
            '## Run Information',
            '## Essay Prompt',
            '## Essays by Quality Grade',
            '## Essays by Stance'
        ]
        
        assert section_order == expected_order
        
        # Check that essay links are properly formatted
        assert "- [essay_001_strongly_for_A_ChatGPT_4o.md]" in content
        assert "- [essay_002_slightly_against_B_Gemini_2.5_Pro.md]" in content
        
        # Check grouping by grade
        assert "### Grade A (1 essays)" in content
        assert "### Grade B (1 essays)" in content
        
        # Check grouping by stance
        assert "### strongly_for (1 essays)" in content
        assert "### slightly_against (1 essays)" in content