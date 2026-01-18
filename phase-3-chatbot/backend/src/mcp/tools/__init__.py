"""MCP tools for AI chatbot task management.

This package contains stateless MCP (Model Context Protocol) tools that are
registered with the OpenAI Agents SDK (Swarm framework) for natural language
task management.

All tools follow the MCP pattern:
- Stateless functions (no server memory)
- Database-backed persistence
- OpenAI function calling compatible signatures
- User isolation via user_id parameter
"""
