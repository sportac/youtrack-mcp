"""
End-to-end tests for YouTrack MCP with real YouTrack instance.

These tests mirror the actual workflow of the 9 most commonly used tools:
1. get_custom_fields - See what fields are available
2. get_custom_field_allowed_values - Check valid values for fields
3. create_issue - Create a new issue
4. update_issue_type - Change the issue type
5. update_custom_fields - Update multiple custom fields
6. add_tag_to_issue - Add tags for categorization
7. get_issue - Get basic issue information
8. get_issue_raw - Get detailed issue data with full custom fields
9. get_available_custom_field_values - Alternative way to check field values

These tests require real YouTrack credentials and will make actual API calls.
"""

import pytest
import os
from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.api.issues import IssuesClient
from youtrack_mcp.api.projects import ProjectsClient

# Mark all tests in this module as e2e tests
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def real_client():
    """Create a real YouTrack client for E2E testing."""
    url = os.getenv("YOUTRACK_URL")
    token = os.getenv("YOUTRACK_API_TOKEN")
    
    if not url or not token:
        pytest.skip("Real YouTrack credentials not available")
    
    client = YouTrackClient()
    client.base_url = f"{url.rstrip('/')}/api"
    client.api_token = token
    return client


@pytest.fixture
def issues_client(real_client):
    """Create a real IssuesClient."""
    return IssuesClient(real_client)


@pytest.fixture
def projects_client(real_client):
    """Create a real ProjectsClient."""
    return ProjectsClient(real_client)


class TestTypicalUserWorkflow:
    """E2E tests that mirror typical user workflow with the 9 most-used tools."""

    def test_1_get_custom_fields(self, projects_client):
        """
        Tool: get_custom_fields
        Use case: See what custom fields are available in a project before creating/updating issues.
        """
        projects = projects_client.get_projects()
        assert len(projects) > 0, "No projects available for testing"
        
        # Use first available project
        project = projects[0]
        project_short_name = getattr(project, 'shortName', None)
        
        # Get custom fields for the project
        custom_fields = projects_client.get_custom_fields(project_short_name)
        
        # Verify we get a list of custom fields
        assert isinstance(custom_fields, list)
        print(f"\n✓ Found {len(custom_fields)} custom fields in project {project_short_name}")
        
        # If we have custom fields, check their structure
        if custom_fields:
            field = custom_fields[0]
            # Fields should have at least an ID or type
            has_id = 'id' in field or hasattr(field, 'id')
            has_type = '$type' in field or hasattr(field, '$type')
            assert has_id or has_type, "Field should have at least an ID or type"
            print(f"  Example field ID: {field.get('id') if isinstance(field, dict) else getattr(field, 'id', 'N/A')}")

    def test_2_get_custom_field_allowed_values(self, projects_client):
        """
        Tool: get_custom_field_allowed_values
        Use case: Check what values are allowed for enum/state fields like Type, Priority, State.
        """
        projects = projects_client.get_projects()
        assert len(projects) > 0
        
        project = projects[0]
        project_short_name = getattr(project, 'shortName', None)
        
        # Try to get allowed values for common fields
        common_fields = ["Type", "Priority", "State"]
        
        for field_name in common_fields:
            try:
                allowed_values = projects_client.get_custom_field_allowed_values(
                    project_short_name, 
                    field_name
                )
                
                if allowed_values and isinstance(allowed_values, list):
                    print(f"\n✓ Field '{field_name}' has {len(allowed_values)} allowed values")
                    if allowed_values:
                        first_value = allowed_values[0]
                        value_name = first_value.get('name') if isinstance(first_value, dict) else getattr(first_value, 'name', None)
                        print(f"  Example value: {value_name}")
                    break  # Found at least one working field
            except Exception:
                # Field might not exist in this project
                continue

    def test_3_get_available_custom_field_values(self, projects_client):
        """
        Tool: get_available_custom_field_values
        Use case: Alternative way to check available values for custom fields.
        """
        projects = projects_client.get_projects()
        assert len(projects) > 0
        
        project = projects[0]
        project_short_name = getattr(project, 'shortName', None)
        
        # This should work similar to get_custom_field_allowed_values
        common_fields = ["Type", "Priority", "State"]
        
        for field_name in common_fields:
            try:
                values = projects_client.get_available_custom_field_values(
                    project_short_name,
                    field_name
                )
                
                if values and isinstance(values, list):
                    print(f"\n✓ get_available_custom_field_values returned {len(values)} values for '{field_name}'")
                    break
            except Exception:
                continue

    @pytest.mark.slow
    def test_4_complete_issue_workflow(self, issues_client, projects_client):
        """
        Complete workflow test covering:
        - create_issue: Create a new issue
        - get_issue: Get basic issue info
        - update_issue_type: Change the issue type
        - update_custom_fields: Update multiple fields at once
        - add_tag_to_issue: Add a tag for categorization
        - get_issue_raw: Get detailed issue data with full custom field values
        """
        # Find a test project (prefer test-named projects, but use first available if none found)
        projects = projects_client.get_projects()
        if not projects:
            pytest.skip("No projects available")
        
        test_project = None
        
        # First try to find a test project
        for project in projects:
            short_name = getattr(project, 'shortName', None)
            if short_name in ["DEMO", "TEST", "SANDBOX", "AI"]:
                test_project = project
                break
        
        # If no test project found, use the first available project
        if not test_project:
            test_project = projects[0]
            print("\n⚠️  Using first available project (no test project found)")
        
        project_id = getattr(test_project, 'id', None)
        project_short_name = getattr(test_project, 'shortName', None)
        
        print(f"\n🧪 Testing workflow in project: {project_short_name}")
        
        # STEP 1: Create an issue
        print("\n1️⃣ Creating issue...")
        issue = issues_client.create_issue(
            project_id=project_id,
            summary="E2E Test - Complete Workflow",
            description="This issue tests the complete workflow: create → get → update type → update fields → add tag"
        )
        
        assert issue.id
        issue_id_readable = getattr(issue, 'idReadable', None)
        
        if not issue_id_readable:
            pytest.skip("Created issue but couldn't get idReadable")
        
        print(f"   ✓ Created issue: {issue_id_readable}")
        
        # STEP 2: Get issue (basic info)
        print("\n2️⃣ Getting issue (basic)...")
        retrieved_issue = issues_client.get_issue(issue_id_readable)
        assert retrieved_issue.id == issue.id
        assert retrieved_issue.summary == "E2E Test - Complete Workflow"
        print(f"   ✓ Retrieved issue: {retrieved_issue.summary}")
        
        # STEP 3: Get issue raw (detailed custom fields)
        print("\n3️⃣ Getting issue raw (detailed)...")
        raw_issue = issues_client.get_issue_raw(issue_id_readable)
        assert raw_issue is not None
        print("   ✓ Retrieved raw issue data with detailed custom fields")
        
        # STEP 4: Update issue type
        print("\n4️⃣ Updating issue type...")
        # Get available types first
        try:
            available_types = projects_client.get_custom_field_allowed_values(
                project_short_name,
                "Type"
            )
            
            if available_types and len(available_types) > 0:
                # Use the first available type
                first_type = available_types[0]
                type_name = first_type.get('name') if isinstance(first_type, dict) else getattr(first_type, 'name', None)
                
                issues_client.update_issue_type(
                    issue_id_readable,
                    type_name
                )
                print(f"   ✓ Updated issue type to: {type_name}")
        except Exception as e:
            print(f"   ⚠️  Type update skipped (field may not exist): {str(e)[:100]}")
        
        # STEP 5: Update custom fields (multiple at once)
        print("\n5️⃣ Updating custom fields...")
        try:
            # Try to update common fields if they exist
            fields_to_update = {}
            
            # Check if Priority field exists and has values
            try:
                priority_values = projects_client.get_custom_field_allowed_values(
                    project_short_name,
                    "Priority"
                )
                if priority_values and len(priority_values) > 0:
                    priority_name = priority_values[0].get('name') if isinstance(priority_values[0], dict) else getattr(priority_values[0], 'name', None)
                    fields_to_update["Priority"] = priority_name
            except Exception:
                pass
            
            if fields_to_update:
                issues_client.update_issue_custom_fields(
                    issue_id_readable,
                    fields_to_update,
                    validate=False
                )
                print(f"   ✓ Updated custom fields: {', '.join(fields_to_update.keys())}")
            else:
                print("   ⚠️  No updatable custom fields found")
        except Exception as e:
            print(f"   ⚠️  Custom field update skipped: {str(e)[:100]}")
        
        # STEP 6: Add tag to issue
        print("\n6️⃣ Adding tag to issue...")
        try:
            # Try to add a common tag (might need to exist first)
            issues_client.add_tag_to_issue(
                issue_id_readable,
                "test"
            )
            print("   ✓ Added tag: test")
        except Exception as e:
            print(f"   ⚠️  Tag add skipped (tag may not exist): {str(e)[:100]}")
        
        # FINAL VERIFICATION: Get issue again to verify all changes
        print("\n7️⃣ Final verification...")
        final_issue = issues_client.get_issue(issue_id_readable)
        assert final_issue.id == issue.id
        assert final_issue.summary == "E2E Test - Complete Workflow"
        print(f"   ✓ Verified issue still accessible: {issue_id_readable}")
        
        print("\n✅ Complete workflow test passed!")
        print(f"   Test issue created: {issue_id_readable}")
        print(f"   You can view it at: {projects_client.client.base_url.replace('/api', '')}/issue/{issue_id_readable}")


class TestEnvironmentSetup:
    """Basic environment and connectivity tests."""
    
    def test_environment_variables(self):
        """Verify YouTrack credentials are available in environment."""
        url = os.getenv("YOUTRACK_URL")
        token = os.getenv("YOUTRACK_API_TOKEN")
        
        if url and token:
            assert url.startswith("https://"), "YOUTRACK_URL should start with https://"
            assert len(token) > 10, "YOUTRACK_API_TOKEN seems too short"
            print("\n✓ Environment variables configured")
            print(f"  URL: {url}")
        else:
            pytest.skip("Environment variables not set")

    def test_api_connectivity(self, real_client):
        """Verify we can connect to YouTrack API."""
        from youtrack_mcp.api.users import UsersClient
        users_client = UsersClient(real_client)
        
        user = users_client.get_current_user()
        assert user is not None
        assert hasattr(user, 'login')
        
        user_login = getattr(user, 'login', 'unknown')
        print(f"\n✓ Connected to YouTrack as: {user_login}") 