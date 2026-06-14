# AI-KungFU East Africa MCP Server
# Glama-compatible Dockerfile for remit-mcp
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/remit-mcp"
LABEL org.opencontainers.image.description="remit-mcp — East Africa AI Coordination Infrastructure"
LABEL org.opencontainers.image.licenses="MIT"

RUN pip install --no-cache-dir remit-mcp

CMD ["remit-mcp"]
