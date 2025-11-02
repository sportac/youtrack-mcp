#!/bin/bash

# Manual testing script for YouTrack MCP Server
# Provides an interactive menu to test the 9 most-used tools

CONFIG_FILE="mcp_config.json"
MCP_NAME="youtrack"

# Color codes for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}YouTrack MCP Manual Testing Tool${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

echo -e "${GREEN}Select a tool to test:${NC}"
echo "  1) get_custom_fields"
echo "  2) get_custom_field_allowed_values"
echo "  3) create_issue"
echo "  4) get_issue"
echo "  5) get_issue_raw"
echo "  6) update_issue_type"
echo "  7) update_custom_fields"
echo "  8) get_available_custom_field_values"
echo "  9) add_tag_to_issue"
echo ""
read -p "Enter your choice (1-9): " choice

case $choice in
    1)
            # get_custom_fields
            read -p "Enter project ID (e.g., AI, DEMO): " project_id
            
            TOOL_ARGS="{\"args\": \"$project_id\", \"kwargs\": \"{}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name get_custom_fields --tool-args '$TOOL_ARGS'"
            ;;
        2)
            # get_custom_field_allowed_values
            read -p "Enter project ID (e.g., AI, DEMO): " project_id
            read -p "Enter field name (e.g., Type, Priority): " field_name
            
            TOOL_ARGS="{\"args\": \"$project_id\", \"kwargs\": \"{\\\"field_name\\\": \\\"$field_name\\\"}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name get_custom_field_allowed_values --tool-args '$TOOL_ARGS'"
            ;;
        3)
            # create_issue
            read -p "Enter project ID (e.g., AI, DEMO): " project_id
            read -p "Enter issue summary: " summary
            read -p "Enter issue description (optional, press Enter to skip): " description
            
            if [ -z "$description" ]; then
                TOOL_ARGS="{\"args\": \"$project_id\", \"kwargs\": \"{\\\"summary\\\": \\\"$summary\\\"}\"}"
            else
                TOOL_ARGS="{\"args\": \"$project_id\", \"kwargs\": \"{\\\"summary\\\": \\\"$summary\\\", \\\"description\\\": \\\"$description\\\"}\"}"
            fi
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name create_issue --tool-args '$TOOL_ARGS'"
            ;;
        4)
            # get_issue
            read -p "Enter issue ID (e.g., AI-2375): " issue_id
            
            TOOL_ARGS="{\"args\": \"$issue_id\", \"kwargs\": \"{}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name get_issue --tool-args '$TOOL_ARGS'"
            ;;
        5)
            # get_issue_raw
            read -p "Enter issue ID (e.g., AI-2375): " issue_id
            
            TOOL_ARGS="{\"args\": \"$issue_id\", \"kwargs\": \"{}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name get_issue_raw --tool-args '$TOOL_ARGS'"
            ;;
        6)
            # update_issue_type
            read -p "Enter issue ID (e.g., AI-2375): " issue_id
            read -p "Enter issue type (e.g., Task, Bug, Feature): " issue_type
            
            TOOL_ARGS="{\"args\": \"$issue_id\", \"kwargs\": \"{\\\"issue_type\\\": \\\"$issue_type\\\"}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name update_issue_type --tool-args '$TOOL_ARGS'"
            ;;
        7)
            # update_custom_fields
            read -p "Enter issue ID (e.g., AI-2375): " issue_id
            read -p "Enter field name (e.g., Team, Priority): " field_name
            read -p "Enter field value (e.g., Python, High): " field_value
            
            TOOL_ARGS="{\"args\": \"$issue_id\", \"kwargs\": \"{\\\"custom_fields\\\": {\\\"$field_name\\\": \\\"$field_value\\\"}}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name update_custom_fields --tool-args '$TOOL_ARGS'"
            ;;
        8)
            # get_available_custom_field_values
            read -p "Enter project ID (e.g., AI, DEMO): " project_id
            read -p "Enter field name (e.g., Type, Priority): " field_name
            
            TOOL_ARGS="{\"args\": \"$project_id\", \"kwargs\": \"{\\\"field_name\\\": \\\"$field_name\\\"}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name get_available_custom_field_values --tool-args '$TOOL_ARGS'"
            ;;
        9)
            # add_tag_to_issue
            read -p "Enter issue ID (e.g., AI-2375): " issue_id
            read -p "Enter tag name (e.g., refinement, urgent): " tag_name
            
            TOOL_ARGS="{\"args\": \"$issue_id\", \"kwargs\": \"{\\\"tag_name\\\": \\\"$tag_name\\\"}\"}"
            CMD="mcp-tools-cli --config $CONFIG_FILE --mcp-name $MCP_NAME call-tool --tool-name add_tag_to_issue --tool-args '$TOOL_ARGS'"
            ;;
    *)
        echo -e "${RED}Invalid choice. Please enter a number between 1 and 9.${NC}"
        exit 1
        ;;
esac

# Display the command
echo ""
echo -e "${YELLOW}Executing command:${NC}"
echo -e "${YELLOW}$CMD${NC}"
echo ""

# Execute command and write output to temp file
TEMP_OUTPUT=$(mktemp)
eval $CMD > "$TEMP_OUTPUT" 2>&1

# Debug: Check if we captured output
if [ ! -s "$TEMP_OUTPUT" ]; then
    echo -e "${RED}ERROR: No output captured from command${NC}"
    rm -f "$TEMP_OUTPUT"
    exit 1
fi

# Extract and format the result
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}RESULT:${NC}"
echo -e "${GREEN}=====================================${NC}"

# Use Python to extract and format the JSON result
python3 << PYTHON_SCRIPT
import sys
import json
import re

# Read the output from temp file
with open('$TEMP_OUTPUT', 'r') as f:
    output = f.read()

# Extract the Result JSON from the output
# Pattern: text='Tool: <toolname>, Result: <JSON>', annotations...
# The JSON can be an object {} or array []
match = re.search(r"Result: ([\{\[].*?[\}\]])'(?:,\s*annotations|')", output, re.DOTALL)

if match:
    json_str = match.group(1)
    try:
        # Decode the string to handle escape sequences properly
        # The string has double-escaped sequences like \\\" which need to become \"
        import codecs
        json_str_decoded = codecs.decode(json_str, 'unicode_escape')
        
        # Parse the result
        data = json.loads(json_str_decoded)
        
        # Check if this is a nested contents structure (from get_issue, get_issue_raw, etc.)
        if isinstance(data, dict) and 'contents' in data:
            contents = data.get('contents', [])
            if contents and isinstance(contents, list) and len(contents) > 0:
                first_content = contents[0]
                if isinstance(first_content, dict) and 'text' in first_content:
                    # Extract the nested JSON from the text field
                    nested_json_str = first_content['text']
                    try:
                        # Parse and pretty print the nested JSON
                        nested_data = json.loads(nested_json_str)
                        print(json.dumps(nested_data, indent=2))
                    except json.JSONDecodeError:
                        # If nested parsing fails, show the original data
                        print(json.dumps(data, indent=2))
                else:
                    print(json.dumps(data, indent=2))
            else:
                print(json.dumps(data, indent=2))
        else:
            # Regular format - just print the data
            print(json.dumps(data, indent=2))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # If decoding fails, try without unicode_escape
        try:
            data = json.loads(json_str)
            print(json.dumps(data, indent=2))
        except:
            print("Failed to parse JSON:")
            print(json_str)
else:
    # Fallback: show relevant output without log lines
    lines = output.split('\n')
    for line in lines:
        if ' - INFO - ' not in line and ' - WARNING - ' not in line and line.strip():
            print(line)
PYTHON_SCRIPT

# Clean up
rm -f "$TEMP_OUTPUT"

echo ""
echo -e "${GREEN}=====================================${NC}"

