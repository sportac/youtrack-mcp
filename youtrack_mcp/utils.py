"""
Utility functions for YouTrack MCP server.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Union


def convert_timestamp_to_iso8601(timestamp_ms: int) -> str:
    """
    Convert YouTrack epoch timestamp (in milliseconds) to ISO8601 format in UTC.

    Args:
        timestamp_ms: Timestamp in milliseconds since Unix epoch

    Returns:
        ISO8601 formatted timestamp string in UTC timezone
    """
    try:
        # Convert milliseconds to seconds
        timestamp_seconds = timestamp_ms / 1000
        # Create datetime object in UTC and format as ISO8601
        dt = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, OSError, OverflowError):
        # Return original timestamp as string if conversion fails
        return str(timestamp_ms)


def add_iso8601_timestamps(
    data: Union[Dict, List, Any],
) -> Union[Dict, List, Any]:
    """
    Recursively add ISO8601 formatted timestamps to YouTrack data.

    This function looks for timestamp fields (created, updated) that contain
    epoch timestamps in milliseconds and adds corresponding ISO8601 fields.

    Args:
        data: The data structure to process (dict, list, or other)

    Returns:
        The data structure with ISO8601 timestamps added
    """
    if isinstance(data, dict):
        # Create a copy to avoid modifying the original
        result = data.copy()

        # Process timestamp fields
        timestamp_fields = ["created", "updated"]
        for field in timestamp_fields:
            if field in result and isinstance(result[field], int):
                iso_field = f"{field}_iso8601"
                result[iso_field] = convert_timestamp_to_iso8601(result[field])

        # Recursively process nested dictionaries and lists
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                result[key] = add_iso8601_timestamps(value)

        return result

    elif isinstance(data, list):
        # Process each item in the list
        return [add_iso8601_timestamps(item) for item in data]

    else:
        # Return unchanged for other types
        return data


def format_json_response(data: Any) -> str:
    """
    Format data as JSON string with ISO8601 timestamps added.

    Args:
        data: The data to format

    Returns:
        JSON string with ISO8601 timestamps added
    """
    # Add ISO8601 timestamps to the data
    enhanced_data = add_iso8601_timestamps(data)

    # Return formatted JSON
    return json.dumps(enhanced_data, indent=2)


def create_enhanced_tool_description(
    action: str,
    use_when: str,
    returns: str,
    important: str,
    example: str
) -> str:
    """
    Generate consistent enhanced tool description for MCP tools.
    
    Creates a lightweight but comprehensive description that helps LLM agents
    use tools correctly on the first try by providing clear usage context,
    expected returns, and concrete examples.
    
    Args:
        action: Brief action-oriented summary of what the tool does
        use_when: Specific situations when this tool should be used
        returns: What the agent receives back from the tool
        important: Critical notes about format, common mistakes, or requirements
        example: Concrete usage example with actual parameter values
    
    Returns:
        Formatted tool description string with emojis for visual scanning
    
    Example:
        >>> create_enhanced_tool_description(
        ...     action="Get allowed values for a custom field",
        ...     use_when="Need to see valid options before setting field values",
        ...     returns="List of allowed values with name, id, and description",
        ...     important="Use project SHORT NAME like 'AI' not full name",
        ...     example='get_custom_field_allowed_values(project_id="AI", field_name="Type")'
        ... )
    """
    return f"""{action}

🎯 USE WHEN: {use_when}
✅ RETURNS: {returns}
⚠️ IMPORTANT: {important}

Example: {example}"""
