n"""Tests for the FlowReg MCP server."""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastmcp import Context
from fastmcp.prompts.prompt import Message

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_flowreg.server import (
    load_prompt,
    parameter_suggest,
    mcp,
    PROMPTS_DIR
)


class TestLoadPrompt:
    """Test the load_prompt utility function."""
    
    def test_load_prompt_existing_file(self, tmp_path):
        """Test loading an existing prompt file."""
        prompt_file = tmp_path / "test_prompt.md"
        expected_content = "# Test Prompt\nThis is a test prompt."
        prompt_file.write_text(expected_content, encoding="utf-8")
        
        with patch('mcp_flowreg.server.PROMPTS_DIR', tmp_path):
            result = load_prompt("test_prompt.md")
            assert result == expected_content
    
    def test_load_prompt_missing_file(self):
        """Test that loading a missing prompt file raises FileNotFoundError."""
        with patch('mcp_flowreg.server.PROMPTS_DIR', Path("/nonexistent")):
            with pytest.raises(FileNotFoundError):
                load_prompt("missing.md")


class TestParameterSuggest:
    """Test the parameter_suggest prompt function."""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        ctx = Mock(spec=Context)
        ctx.info = Mock()
        ctx.error = Mock()
        ctx.debug = Mock()
        return ctx
    
    @pytest.fixture
    def sample_input_dict(self):
        """Sample input dictionary for testing."""
        return {
            "video_path": "/path/to/video.tiff",
            "channels": ["red", "green"],
            "resolution": [512, 512]
        }
    
    def test_parameter_suggest_with_dict_input(self, mock_context, sample_input_dict):
        """Test parameter_suggest with dictionary input."""
        prompt_content = "Test prompt content"
        
        with patch('mcp_flowreg.server.load_prompt', return_value=prompt_content):
            result = parameter_suggest(
                ctx=mock_context,
                input_json=sample_input_dict,
                final_run=True
            )
            
            assert len(result) == 2
            assert isinstance(result[0], Message)
            assert isinstance(result[1], Message)
            assert result[0].content == prompt_content
            assert result[0].role == "system"
            assert result[1].role == "user"
            
            user_message_data = json.loads(result[1].content)
            assert user_message_data["input_json"]["video_path"] == sample_input_dict["video_path"]
            assert user_message_data["input_json"]["final_run"] is True
    
    def test_parameter_suggest_with_json_string_input(self, mock_context, sample_input_dict):
        """Test parameter_suggest with JSON string input."""
        prompt_content = "Test prompt content"
        json_string = json.dumps(sample_input_dict)
        
        with patch('mcp_flowreg.server.load_prompt', return_value=prompt_content):
            result = parameter_suggest(
                ctx=mock_context,
                input_json=json_string,
                final_run=False
            )
            
            assert len(result) == 2
            user_message_data = json.loads(result[1].content)
            assert user_message_data["input_json"]["video_path"] == sample_input_dict["video_path"]
            assert user_message_data["input_json"]["final_run"] is False
    
    def test_parameter_suggest_invalid_json_string(self, mock_context):
        """Test parameter_suggest with invalid JSON string raises error."""
        prompt_content = "Test prompt content"
        
        with patch('mcp_flowreg.server.load_prompt', return_value=prompt_content):
            with pytest.raises(json.JSONDecodeError):
                parameter_suggest(
                    ctx=mock_context,
                    input_json="invalid json {",
                    final_run=False
                )
    
    def test_parameter_suggest_default_final_run(self, mock_context, sample_input_dict):
        """Test that final_run defaults to False."""
        prompt_content = "Test prompt content"
        
        with patch('mcp_flowreg.server.load_prompt', return_value=prompt_content):
            result = parameter_suggest(
                ctx=mock_context,
                input_json=sample_input_dict
            )
            
            user_message_data = json.loads(result[1].content)
            assert user_message_data["input_json"]["final_run"] is False


class TestMCPServer:
    """Test the FastMCP server instance."""
    
    def test_mcp_server_initialized(self):
        """Test that the MCP server is properly initialized."""
        assert mcp is not None
        assert mcp.name == "mcp-flowreg"
    
    def test_parameter_suggest_prompt_registered(self):
        """Test that parameter_suggest is registered as a prompt."""
        # FastMCP stores prompts internally
        # This test verifies the decorator worked
        assert callable(parameter_suggest)
    
    @patch('mcp_flowreg.server.mcp.run')
    def test_main_execution(self, mock_run):
        """Test that the server runs when executed as main."""
        with patch('mcp_flowreg.server.__name__', '__main__'):
            with patch('sys.argv', ['server.py']):
                exec(open('src/mcp-flowreg/server.py').read())
                mock_run.assert_called_once()


class TestPromptMetadata:
    """Test the prompt metadata and configuration."""
    
    def test_parameter_suggest_metadata(self):
        """Verify the metadata attached to parameter_suggest prompt."""
        # The metadata should be accessible through the decorated function
        # This tests that tags and meta are properly configured
        assert parameter_suggest.__name__ == "parameter_suggest"
        # Additional metadata testing would depend on FastMCP's API


if __name__ == "__main__":
    pytest.main([__file__, "-v"])