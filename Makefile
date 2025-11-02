# YouTrack MCP Server Makefile
# Provides convenient commands for building and testing

.PHONY: help build test test-unit test-integration test-all test-e2e test-manual clean images

# Default target
help:
	@echo "YouTrack MCP Server Commands:"
	@echo ""
	@echo "Build Commands:"
	@echo "  build             - Build Docker image with latest code changes"
	@echo "  clean             - Remove Docker images"
	@echo "  images            - Show current Docker images"
	@echo ""
	@echo "Test Commands:"
	@echo "  test              - Run unit tests (fast, default)"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests"
	@echo "  test-all          - Run all tests (unit + integration)"
	@echo "  test-e2e          - Run end-to-end tests (requires YouTrack credentials)"
	@echo "  test-manual       - Interactive manual testing via mcp-tools-cli"
	@echo ""
	@echo "Examples:"
	@echo "  make build        # Build Docker image"
	@echo "  make test         # Run unit tests"
	@echo "  make test-all     # Run all tests"

# Build Docker image with latest code changes
build:
	@echo "🔨 Building YouTrack MCP Docker image with latest changes..."
	docker build -t youtrack-mcp:latest .
	@echo "✅ Build complete! Image tagged as youtrack-mcp:latest"

# Run unit tests (default test command)
test: test-unit

# Run unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit -m unit -v --tb=short
	@echo "✅ Unit tests completed"

# Run integration tests
test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration -m integration -v --tb=short
	@echo "✅ Integration tests completed"

# Run all tests (unit + integration)
test-all:
	@echo "🧪 Running all tests (unit + integration)..."
	pytest tests/unit tests/integration -v --tb=short
	@echo "✅ All tests completed"

# Run end-to-end tests (requires credentials)
test-e2e:
	@echo "🧪 Running end-to-end tests..."
	@echo "⚠️  Note: E2E tests require YOUTRACK_URL and YOUTRACK_API_TOKEN environment variables"
	@if [ -f .env ]; then \
		echo "📁 Loading environment variables from .env file..."; \
		export $$(cat .env | grep -v '^#' | xargs) && pytest tests/e2e -m e2e -v --tb=short; \
	else \
		echo "⚠️  .env file not found, using existing environment variables"; \
		pytest tests/e2e -m e2e -v --tb=short; \
	fi
	@echo "✅ E2E tests completed"

# Run interactive manual testing script
test-manual:
	@echo "🧪 Starting interactive manual testing..."
	@./scripts/manual_test.sh

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
