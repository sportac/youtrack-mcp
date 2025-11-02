# YouTrack MCP Server Makefile
# Provides convenient commands for building and testing

.PHONY: help build test-create test-update get-issue clean

# Default target
help:
	@echo "YouTrack MCP Server Commands:"
	@echo ""
	@echo "Build Commands:"
	@echo "  build          - Build Docker image with latest code changes"
	@echo "  clean          - Remove Docker images"
	@echo ""
	@echo "Test Commands:"
	@echo "  test-create    - Create a test issue with default data"
	@echo "  test-update     - Update custom field (usage: make test-update ID=DEMO-50 FIELD=Component VALUE=Python)"
	@echo "  get-issue      - Get issue details (usage: make get-issue ID=DEMO-50)"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make test-create"
	@echo "  make get-issue ID=DEMO-50"
	@echo "  make test-update ID=DEMO-50 FIELD=Component VALUE=Python"
	@echo "  make test-update ID=DEMO-51 FIELD=Priority VALUE=High"

# Build Docker image with latest code changes
build:
	@echo "🔨 Building YouTrack MCP Docker image with latest changes..."
	docker build -t youtrack-mcp:latest .
	@echo "✅ Build complete! Image tagged as youtrack-mcp:latest"

# Create a test issue with default data
test-create:
	@echo "📝 Creating test issue with default data..."
	mcp-tools-cli --config mcp_config.json --mcp-name youtrack call-tool --tool-name create_issue --tool-args '{"args": "DEMO", "kwargs": "{\"summary\": \"Test Issue Created via Makefile\", \"description\": \"This is a test issue created using the Makefile command. It includes default data for testing purposes.\"}"}'

# Get issue details by ID
# Usage: make get-issue ID=DEMO-50
get-issue:
	@if [ -z "$(ID)" ]; then \
		echo "❌ Error: ID parameter is required"; \
		echo "Usage: make get-issue ID=DEMO-50"; \
		exit 1; \
	fi
	@echo "📋 Getting details for issue '$(ID)'..."
	mcp-tools-cli --config mcp_config.json --mcp-name youtrack call-tool --tool-name get_issue --tool-args '{"args": "$(ID)", "kwargs": "{}"}'

# Update custom field on an issue
# Usage: make test-update ID=DEMO-50 FIELD=Component VALUE=Python
test-update:
	@if [ -z "$(ID)" ]; then \
		echo "❌ Error: ID parameter is required"; \
		echo "Usage: make test-update ID=DEMO-50 FIELD=Component VALUE=Python"; \
		exit 1; \
	fi
	@if [ -z "$(FIELD)" ]; then \
		echo "❌ Error: FIELD parameter is required"; \
		echo "Usage: make test-update ID=DEMO-50 FIELD=Component VALUE=Python"; \
		exit 1; \
	fi
	@if [ -z "$(VALUE)" ]; then \
		echo "❌ Error: VALUE parameter is required"; \
		echo "Usage: make test-update ID=DEMO-50 FIELD=Component VALUE=Python"; \
		exit 1; \
	fi
	@echo "🔧 Updating custom field '$(FIELD)' to '$(VALUE)' on issue '$(ID)'..."
	mcp-tools-cli --config mcp_config.json --mcp-name youtrack call-tool --tool-name update_custom_fields --tool-args '{"args": "$(ID)", "kwargs": "{\"custom_fields\": {\"$(FIELD)\": \"$(VALUE)\"}}"}'

# Clean up Docker images
clean:
	@echo "🧹 Cleaning up Docker images..."
	docker rmi youtrack-mcp:latest 2>/dev/null || true
	docker rmi youtrack-mcp-local:1.17.3-wip 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Show current Docker images
images:
	@echo "📦 Current YouTrack MCP Docker images:"
	docker images | grep youtrack-mcp || echo "No YouTrack MCP images found"
