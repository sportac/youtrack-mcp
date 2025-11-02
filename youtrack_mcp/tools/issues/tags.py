"""
YouTrack Issue Tags Management Module.

This module provides MCP tools for managing tags on YouTrack issues:
- List available tags
- Get tags for an issue
- Add tags to issues
- Remove tags from issues
- Set all tags for an issue
- Find tags by name

These tools integrate with the YouTrack REST API tag endpoints.
"""

import logging
from typing import Any, Dict, List, Optional

from youtrack_mcp.api.issues import IssuesClient
from youtrack_mcp.api.projects import ProjectsClient
from youtrack_mcp.mcp_wrappers import sync_wrapper
from youtrack_mcp.utils import format_json_response, create_enhanced_tool_description

logger = logging.getLogger(__name__)


class Tags:
    """
    YouTrack issue tags management tools.
    
    Provides comprehensive tag management functionality including listing,
    adding, removing, and searching tags on YouTrack issues.
    """

    def __init__(self, issues_api: IssuesClient, projects_api: ProjectsClient):
        """Initialize with API clients."""
        self.issues_api = issues_api
        self.projects_api = projects_api
        self.client = issues_api.client

    @sync_wrapper
    def get_available_tags(self, query: Optional[str] = None, limit: int = 50) -> str:
        """
        Get all available tags that are owned by or shared with the current user.
        
        FORMAT: get_available_tags(query="deploy", limit=20)
        
        Args:
            query: Optional query to filter tags by name
            limit: Maximum number of tags to return (default: 50)
            
        Returns:
            JSON string with available tags
        """
        try:
            tags = self.issues_api.get_tags(query=query, limit=limit)
            return format_json_response(tags)
        except Exception as e:
            logger.exception(f"Error getting available tags")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def get_issue_tags(self, issue_id: str) -> str:
        """
        Get all tags currently assigned to an issue.
        
        FORMAT: get_issue_tags(issue_id="DEMO-123")
        
        Args:
            issue_id: Issue identifier like 'DEMO-123' or 'PROJECT-456'
            
        Returns:
            JSON string with tags assigned to the issue
        """
        try:
            tags = self.issues_api.get_issue_tags(issue_id)
            return format_json_response(tags)
        except Exception as e:
            logger.exception(f"Error getting tags for issue {issue_id}")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def add_tag_to_issue(self, issue_id: str, tag_name: str) -> str:
        """
        Add a tag to an issue by tag name.
        
        FORMAT: add_tag_to_issue(issue_id="DEMO-123", tag_name="deploy")
        
        Args:
            issue_id: Issue identifier like 'DEMO-123' or 'PROJECT-456'
            tag_name: Name of the tag to add
            
        Returns:
            JSON string with updated issue data including tags
        """
        try:
            # First, find the tag by name to get its ID
            tag = self.issues_api.find_tag_by_name(tag_name)
            if not tag:
                return format_json_response({
                    "error": f"Tag '{tag_name}' not found. Use get_available_tags() to see available tags."
                })
            
            # Add the tag to the issue
            result = self.issues_api.add_tag_to_issue(issue_id, tag["id"])
            return format_json_response(result)
        except Exception as e:
            logger.exception(f"Error adding tag '{tag_name}' to issue {issue_id}")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def remove_tag_from_issue(self, issue_id: str, tag_name: str) -> str:
        """
        Remove a specific tag from an issue by tag name.
        
        FORMAT: remove_tag_from_issue(issue_id="DEMO-123", tag_name="deploy")
        
        Args:
            issue_id: Issue identifier like 'DEMO-123' or 'PROJECT-456'
            tag_name: Name of the tag to remove
            
        Returns:
            JSON string with success status
        """
        try:
            # First, find the tag by name to get its ID
            tag = self.issues_api.find_tag_by_name(tag_name)
            if not tag:
                return format_json_response({
                    "error": f"Tag '{tag_name}' not found on this issue."
                })
            
            # Remove the tag from the issue
            success = self.issues_api.remove_tag_from_issue(issue_id, tag["id"])
            if success:
                return format_json_response({"success": True, "message": f"Tag '{tag_name}' removed from issue {issue_id}"})
            else:
                return format_json_response({"error": f"Failed to remove tag '{tag_name}' from issue {issue_id}"})
        except Exception as e:
            logger.exception(f"Error removing tag '{tag_name}' from issue {issue_id}")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def set_issue_tags(self, issue_id: str, tag_names: List[str]) -> str:
        """
        Set all tags for an issue (replaces existing tags).
        
        FORMAT: set_issue_tags(issue_id="DEMO-123", tag_names=["deploy", "urgent"])
        
        Args:
            issue_id: Issue identifier like 'DEMO-123' or 'PROJECT-456'
            tag_names: List of tag names to set
            
        Returns:
            JSON string with updated issue data including tags
        """
        try:
            # Find all tag IDs by name
            tag_ids = []
            missing_tags = []
            
            for tag_name in tag_names:
                tag = self.issues_api.find_tag_by_name(tag_name)
                if tag:
                    tag_ids.append(tag["id"])
                else:
                    missing_tags.append(tag_name)
            
            if missing_tags:
                return format_json_response({
                    "error": f"Tags not found: {', '.join(missing_tags)}. Use get_available_tags() to see available tags."
                })
            
            # Set the tags on the issue
            result = self.issues_api.set_issue_tags(issue_id, tag_ids)
            return format_json_response(result)
        except Exception as e:
            logger.exception(f"Error setting tags for issue {issue_id}")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def remove_all_tags_from_issue(self, issue_id: str) -> str:
        """
        Remove all tags from an issue.
        
        FORMAT: remove_all_tags_from_issue(issue_id="DEMO-123")
        
        Args:
            issue_id: Issue identifier like 'DEMO-123' or 'PROJECT-456'
            
        Returns:
            JSON string with updated issue data (empty tags)
        """
        try:
            result = self.issues_api.remove_all_tags_from_issue(issue_id)
            return format_json_response(result)
        except Exception as e:
            logger.exception(f"Error removing all tags from issue {issue_id}")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def find_tag_by_name(self, tag_name: str) -> str:
        """
        Find a tag by its name.
        
        FORMAT: find_tag_by_name(tag_name="deploy")
        
        Args:
            tag_name: Name of the tag to find
            
        Returns:
            JSON string with tag information if found
        """
        try:
            tag = self.issues_api.find_tag_by_name(tag_name)
            if tag:
                return format_json_response(tag)
            else:
                return format_json_response({"error": f"Tag '{tag_name}' not found"})
        except Exception as e:
            logger.exception(f"Error finding tag '{tag_name}'")
            return format_json_response({"error": str(e)})

    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get tool definitions for tag management functions."""
        return {
            "get_available_tags": {
                "description": "Get all available tags that are owned by or shared with the current user. Example: get_available_tags(query='deploy', limit=20)",
                "parameter_descriptions": {
                    "query": "Optional query to filter tags by name (e.g., 'deploy', 'urgent')",
                    "limit": "Maximum number of tags to return (default: 50)"
                }
            },
            "get_issue_tags": {
                "description": "Get all tags currently assigned to an issue. Example: get_issue_tags(issue_id='DEMO-123')",
                "parameter_descriptions": {
                    "issue_id": "Issue identifier like 'DEMO-123' or 'PROJECT-456'"
                }
            },
            "add_tag_to_issue": {
                "description": create_enhanced_tool_description(
                    action="Add a tag to an issue by tag name",
                    use_when="Need to label/categorize issue with tags like 'refinement', 'urgent', 'deploy', or custom workflow labels",
                    returns="Tag object indicating success with updated issue data showing the new tag added to the issue",
                    important="Tag must already exist in YouTrack. Use exact tag name (case-sensitive). Tag is added, not replaced - existing tags remain.",
                    example='add_tag_to_issue(issue_id="AI-2375", tag_name="refinement")'
                ),
                "parameter_descriptions": {
                    "issue_id": "Full issue identifier like 'AI-2375' or 'DEMO-123' (format: PROJECT-NUMBER)",
                    "tag_name": "Exact tag name to add (e.g., 'refinement', 'urgent', 'deploy'). Tag must exist in YouTrack. Use get_available_tags() to see options."
                }
            },
            "remove_tag_from_issue": {
                "description": "Remove a specific tag from an issue by tag name. Example: remove_tag_from_issue(issue_id='DEMO-123', tag_name='deploy')",
                "parameter_descriptions": {
                    "issue_id": "Issue identifier like 'DEMO-123' or 'PROJECT-456'",
                    "tag_name": "Name of the tag to remove"
                }
            },
            "set_issue_tags": {
                "description": "Set all tags for an issue (replaces existing tags). Example: set_issue_tags(issue_id='DEMO-123', tag_names=['deploy', 'urgent'])",
                "parameter_descriptions": {
                    "issue_id": "Issue identifier like 'DEMO-123' or 'PROJECT-456'",
                    "tag_names": "List of tag names to set (e.g., ['deploy', 'urgent', 'bug'])"
                }
            },
            "remove_all_tags_from_issue": {
                "description": "Remove all tags from an issue. Example: remove_all_tags_from_issue(issue_id='DEMO-123')",
                "parameter_descriptions": {
                    "issue_id": "Issue identifier like 'DEMO-123' or 'PROJECT-456'"
                }
            },
            "find_tag_by_name": {
                "description": "Find a tag by its name. Example: find_tag_by_name(tag_name='deploy')",
                "parameter_descriptions": {
                    "tag_name": "Name of the tag to find"
                }
            }
        }
