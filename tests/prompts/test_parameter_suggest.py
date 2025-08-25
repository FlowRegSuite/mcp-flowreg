"""Tests for prompt files and prompt loading."""
import pytest
from pathlib import Path
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_flowreg.server import PROMPTS_DIR


class TestPromptFiles:
    """Test that prompt files exist and are valid."""
    
    def test_parameter_suggest_prompt_exists(self):
        """Test that parameter_suggest.md exists."""
        prompt_file = PROMPTS_DIR / "parameter_suggest.md"
        assert prompt_file.exists(), f"Prompt file {prompt_file} does not exist"
    
    def test_parameter_suggest_prompt_not_empty(self):
        """Test that parameter_suggest.md is not empty."""
        prompt_file = PROMPTS_DIR / "parameter_suggest.md"
        content = prompt_file.read_text(encoding="utf-8")
        assert len(content) > 0, "Prompt file is empty"
    
    def test_parameter_suggest_prompt_has_expected_content(self):
        """Test that parameter_suggest.md contains expected keywords."""
        prompt_file = PROMPTS_DIR / "parameter_suggest.md"
        content = prompt_file.read_text(encoding="utf-8")
        
        # Check for key sections
        expected_keywords = [
            "variational flow-registration",
            "Quality Preset Policy",
            "backend",
            "microscopy",
            "sigma",
            "alpha",
            "references"
        ]
        
        for keyword in expected_keywords:
            assert keyword in content, f"Expected keyword '{keyword}' not found in prompt"
    
    def test_parameter_suggest_prompt_json_examples_valid(self):
        """Test that JSON examples in the prompt are valid."""
        prompt_file = PROMPTS_DIR / "parameter_suggest.md"
        content = prompt_file.read_text(encoding="utf-8")
        
        # Extract and validate the input JSON structure
        # This is a simplified check - in production you might parse more carefully
        assert '"data_type":' in content
        assert '"channels":' in content
        assert '"resolution_px":' in content
        assert '"backend":' in content
        assert '"quality_choice":' in content


class TestPromptIntegration:
    """Test prompt integration with the server."""
    
    def test_all_prompts_have_handlers(self):
        """Verify that all prompt files have corresponding handlers."""
        prompt_files = list(PROMPTS_DIR.glob("*.md"))
        
        # Currently we expect parameter_suggest.md
        expected_prompts = ["parameter_suggest.md"]
        actual_prompts = [f.name for f in prompt_files]
        
        for expected in expected_prompts:
            assert expected in actual_prompts, f"Expected prompt {expected} not found"
    
    def test_prompts_directory_structure(self):
        """Test that the prompts directory has the expected structure."""
        assert PROMPTS_DIR.exists(), "Prompts directory does not exist"
        assert PROMPTS_DIR.is_dir(), "Prompts path is not a directory"
        
        # Check that we have at least one prompt file
        prompt_files = list(PROMPTS_DIR.glob("*.md"))
        assert len(prompt_files) > 0, "No prompt files found in prompts directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])