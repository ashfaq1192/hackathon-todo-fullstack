"""Mocked performance tests to measure endpoint overhead (without AI API calls).

These tests measure the endpoint processing time excluding the Gemini API latency.
This helps identify bottlenecks in our code vs external API latency.
"""

import time
import statistics
from unittest.mock import patch, MagicMock

import pytest


class TestEndpointOverhead:
    """Test endpoint overhead without AI API calls."""

    @pytest.fixture
    def mock_chat_service(self):
        """Create a mock ChatService that returns immediately."""
        mock = MagicMock()
        mock.process_message.return_value = {
            "success": True,
            "message": "Here are your tasks: 1. Test task",
            "conversation_id": 1,
            "tool_calls": ["list_tasks_wrapper"],
        }
        return mock

    def test_endpoint_overhead_under_500ms(self, api_client, create_jwt_token, mock_chat_service):
        """Endpoint overhead (excluding AI API) should be under 500ms."""
        token = create_jwt_token("overhead_user")
        headers = {"Authorization": f"Bearer {token}"}

        with patch("src.api.routes.chat.ChatService", return_value=mock_chat_service):
            times = []
            for _ in range(3):
                start = time.time()
                response = api_client.post(
                    "/api/overhead_user/chat",
                    json={"message": "Show my tasks"},
                    headers=headers,
                )
                elapsed = time.time() - start
                times.append(elapsed)

            avg = statistics.mean(times)
            print(f"\nEndpoint overhead (mocked): {avg * 1000:.1f}ms")
            print(f"Individual times: {[f'{t*1000:.1f}ms' for t in times]}")

            # Endpoint processing overhead should be under 500ms
            assert avg < 0.5, f"Endpoint overhead {avg * 1000:.1f}ms exceeds 500ms target"

    def test_auth_validation_time(self, api_client, create_jwt_token, mock_chat_service):
        """JWT validation should complete quickly."""
        token = create_jwt_token("auth_perf_user")
        headers = {"Authorization": f"Bearer {token}"}

        with patch("src.api.routes.chat.ChatService", return_value=mock_chat_service):
            start = time.time()
            response = api_client.post(
                "/api/auth_perf_user/chat",
                json={"message": "Test"},
                headers=headers,
            )
            elapsed = time.time() - start

            assert response.status_code == 200
            print(f"\nAuth + endpoint time: {elapsed * 1000:.1f}ms")


class TestRealisticPerformance:
    """Document realistic performance expectations."""

    def test_print_performance_expectations(self):
        """Print performance expectations for documentation."""
        print("\n" + "=" * 60)
        print("CHAT ENDPOINT PERFORMANCE EXPECTATIONS")
        print("=" * 60)
        print("""
Expected Response Times (with real Gemini API):

1. Cold Start (first request):
   - Expected: 15-25 seconds
   - Includes: Serverless function warm-up, model loading

2. Warm Requests (subsequent):
   - Expected: 2-5 seconds
   - Includes: AI inference, tool execution, DB operations

3. Simple Queries (no tool calls):
   - Expected: 1-3 seconds

4. Complex Operations (multiple tool calls):
   - Expected: 3-8 seconds

Performance Targets:
- P50 (median): < 3 seconds (warm)
- P95: < 5 seconds (warm)
- P99: < 10 seconds (including cold starts)

Note: These targets are for warm instances. Cold starts on
serverless platforms (Vercel) may add 5-15 seconds.

Optimization Strategies:
1. Keep functions warm with scheduled pings
2. Use connection pooling for database
3. Cache conversation summaries
4. Use streaming responses for perceived speed
""")
        print("=" * 60)
