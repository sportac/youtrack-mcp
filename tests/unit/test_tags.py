"""
Unit tests for YouTrack tag management functionality.
"""

import json
import pytest
from unittest.mock import Mock, patch

from youtrack_mcp.api.issues import IssuesClient
from youtrack_mcp.api.projects import ProjectsClient
from youtrack_mcp.tools.issues.tags import Tags


class TestTags:
    """Test cases for tag management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.issues_api = IssuesClient(self.mock_client)
        self.projects_api = ProjectsClient(self.mock_client)
        self.tags = Tags(self.issues_api, self.projects_api)

    def test_get_available_tags_success(self):
        """Test getting available tags successfully."""
        # Mock API response
        mock_tags = [
            {"id": "6-1", "name": "deploy", "owner": {"id": "1-1", "login": "admin"}},
            {"id": "6-2", "name": "urgent", "owner": {"id": "1-1", "login": "admin"}},
            {"id": "6-3", "name": "bug", "owner": {"id": "1-2", "login": "user"}}
        ]
        self.issues_api.get_tags = Mock(return_value=mock_tags)
        
        result = self.tags.get_available_tags(query="deploy", limit=10)
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert len(result_data) == 3
        assert result_data[0]["name"] == "deploy"
        
        # Verify API was called with correct parameters
        self.issues_api.get_tags.assert_called_once_with(query="deploy", limit=10)

    def test_get_available_tags_error(self):
        """Test error handling when getting available tags fails."""
        self.issues_api.get_tags = Mock(side_effect=Exception("API Error"))
        
        result = self.tags.get_available_tags()
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "API Error" in result_data["error"]

    def test_get_issue_tags_success(self):
        """Test getting tags for an issue successfully."""
        mock_issue_tags = [
            {"id": "6-1", "name": "deploy", "owner": {"id": "1-1", "login": "admin"}},
            {"id": "6-2", "name": "urgent", "owner": {"id": "1-1", "login": "admin"}}
        ]
        self.issues_api.get_issue_tags = Mock(return_value=mock_issue_tags)
        
        result = self.tags.get_issue_tags("DEMO-123")
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert len(result_data) == 2
        assert result_data[0]["name"] == "deploy"
        
        # Verify API was called with correct issue ID
        self.issues_api.get_issue_tags.assert_called_once_with("DEMO-123")

    def test_add_tag_to_issue_success(self):
        """Test adding a tag to an issue successfully."""
        mock_tag = {"id": "6-1", "name": "deploy", "owner": {"id": "1-1", "login": "admin"}}
        mock_issue_result = {
            "id": "DEMO-123",
            "tags": [mock_tag]
        }
        
        self.issues_api.find_tag_by_name = Mock(return_value=mock_tag)
        self.issues_api.add_tag_to_issue = Mock(return_value=mock_issue_result)
        
        result = self.tags.add_tag_to_issue("DEMO-123", "deploy")
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert result_data["id"] == "DEMO-123"
        assert len(result_data["tags"]) == 1
        assert result_data["tags"][0]["name"] == "deploy"
        
        # Verify API calls
        self.issues_api.find_tag_by_name.assert_called_once_with("deploy")
        self.issues_api.add_tag_to_issue.assert_called_once_with("DEMO-123", "6-1")

    def test_add_tag_to_issue_tag_not_found(self):
        """Test adding a tag that doesn't exist."""
        self.issues_api.find_tag_by_name = Mock(return_value=None)
        
        result = self.tags.add_tag_to_issue("DEMO-123", "nonexistent")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Tag 'nonexistent' not found" in result_data["error"]

    def test_remove_tag_from_issue_success(self):
        """Test removing a tag from an issue successfully."""
        mock_tag = {"id": "6-1", "name": "deploy", "owner": {"id": "1-1", "login": "admin"}}
        
        self.issues_api.find_tag_by_name = Mock(return_value=mock_tag)
        self.issues_api.remove_tag_from_issue = Mock(return_value=True)
        
        result = self.tags.remove_tag_from_issue("DEMO-123", "deploy")
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert result_data["success"] is True
        assert "Tag 'deploy' removed" in result_data["message"]
        
        # Verify API calls
        self.issues_api.find_tag_by_name.assert_called_once_with("deploy")
        self.issues_api.remove_tag_from_issue.assert_called_once_with("DEMO-123", "6-1")

    def test_remove_tag_from_issue_tag_not_found(self):
        """Test removing a tag that doesn't exist on the issue."""
        self.issues_api.find_tag_by_name = Mock(return_value=None)
        
        result = self.tags.remove_tag_from_issue("DEMO-123", "nonexistent")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Tag 'nonexistent' not found" in result_data["error"]

    def test_set_issue_tags_success(self):
        """Test setting all tags for an issue successfully."""
        mock_tags = [
            {"id": "6-1", "name": "deploy"},
            {"id": "6-2", "name": "urgent"}
        ]
        mock_issue_result = {
            "id": "DEMO-123",
            "tags": mock_tags
        }
        
        self.issues_api.find_tag_by_name = Mock(side_effect=[
            {"id": "6-1", "name": "deploy"},
            {"id": "6-2", "name": "urgent"}
        ])
        self.issues_api.set_issue_tags = Mock(return_value=mock_issue_result)
        
        result = self.tags.set_issue_tags("DEMO-123", ["deploy", "urgent"])
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert result_data["id"] == "DEMO-123"
        assert len(result_data["tags"]) == 2
        
        # Verify API calls
        assert self.issues_api.find_tag_by_name.call_count == 2
        self.issues_api.set_issue_tags.assert_called_once_with("DEMO-123", ["6-1", "6-2"])

    def test_set_issue_tags_missing_tags(self):
        """Test setting tags when some tags don't exist."""
        self.issues_api.find_tag_by_name = Mock(side_effect=[
            {"id": "6-1", "name": "deploy"},
            None  # Second tag not found
        ])
        
        result = self.tags.set_issue_tags("DEMO-123", ["deploy", "nonexistent"])
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Tags not found: nonexistent" in result_data["error"]

    def test_remove_all_tags_from_issue_success(self):
        """Test removing all tags from an issue successfully."""
        mock_issue_result = {
            "id": "DEMO-123",
            "tags": []
        }
        
        self.issues_api.remove_all_tags_from_issue = Mock(return_value=mock_issue_result)
        
        result = self.tags.remove_all_tags_from_issue("DEMO-123")
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert result_data["id"] == "DEMO-123"
        assert len(result_data["tags"]) == 0
        
        # Verify API call
        self.issues_api.remove_all_tags_from_issue.assert_called_once_with("DEMO-123")

    def test_find_tag_by_name_success(self):
        """Test finding a tag by name successfully."""
        mock_tag = {"id": "6-1", "name": "deploy", "owner": {"id": "1-1", "login": "admin"}}
        
        self.issues_api.find_tag_by_name = Mock(return_value=mock_tag)
        
        result = self.tags.find_tag_by_name("deploy")
        result_data = json.loads(result)
        
        assert "error" not in result_data
        assert result_data["name"] == "deploy"
        assert result_data["id"] == "6-1"
        
        # Verify API call
        self.issues_api.find_tag_by_name.assert_called_once_with("deploy")

    def test_find_tag_by_name_not_found(self):
        """Test finding a tag that doesn't exist."""
        self.issues_api.find_tag_by_name = Mock(return_value=None)
        
        result = self.tags.find_tag_by_name("nonexistent")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Tag 'nonexistent' not found" in result_data["error"]

    def test_get_tool_definitions(self):
        """Test that tool definitions are properly structured."""
        definitions = self.tags.get_tool_definitions()
        
        # Check that all expected tools are defined
        expected_tools = [
            "get_available_tags",
            "get_issue_tags", 
            "add_tag_to_issue",
            "remove_tag_from_issue",
            "set_issue_tags",
            "remove_all_tags_from_issue",
            "find_tag_by_name"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in definitions
            assert "description" in definitions[tool_name]
            assert "parameter_descriptions" in definitions[tool_name]
