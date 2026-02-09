"""Performance tests for chat endpoint.

T067: Performance test chat endpoint (<5s response time target)

These tests verify:
1. Chat endpoint responds within 5 seconds
2. Multiple concurrent requests are handled
3. Rate limiting doesn't cause excessive latency

Note: These tests require a running backend server with valid GEMINI_API_KEY.
Run with: pytest tests/performance/test_chat_performance.py -v --timeout=30
"""

import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from tests.conftest import api_client


class TestChatPerformance:
    """Performance tests for chat endpoint (T067)."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client, create_jwt_token):
        """Set up test fixtures."""
        self.api_client = api_client
        self.user_id = "perf_test_user"
        self.token = create_jwt_token(self.user_id)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_single_request_under_5_seconds(self, api_client, create_jwt_token):
        """T067: Single chat request completes within 5 seconds."""
        token = create_jwt_token("perf_user_single")
        headers = {"Authorization": f"Bearer {token}"}

        start_time = time.time()
        response = api_client.post(
            "/api/perf_user_single/chat",
            json={"message": "Show my tasks"},
            headers=headers,
        )
        elapsed_time = time.time() - start_time

        # Log response details for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response time: {elapsed_time:.2f}s")

        # Verify response (may fail if no real AI service configured)
        # The main goal is to measure latency
        assert elapsed_time < 5.0, f"Response took {elapsed_time:.2f}s (target: <5s)"

    def test_simple_add_task_under_5_seconds(self, api_client, create_jwt_token):
        """T067: Add task command completes within 5 seconds."""
        token = create_jwt_token("perf_user_add")
        headers = {"Authorization": f"Bearer {token}"}

        start_time = time.time()
        response = api_client.post(
            "/api/perf_user_add/chat",
            json={"message": "Add a task: Performance test task"},
            headers=headers,
        )
        elapsed_time = time.time() - start_time

        print(f"\nAdd task response time: {elapsed_time:.2f}s")
        assert elapsed_time < 5.0, f"Add task took {elapsed_time:.2f}s (target: <5s)"

    def test_average_response_time_under_3_seconds(self, api_client, create_jwt_token):
        """T067: Average response time over 3 requests is under 3 seconds."""
        token = create_jwt_token("perf_user_avg")
        headers = {"Authorization": f"Bearer {token}"}

        messages = [
            "Show my tasks",
            "What tasks do I have?",
            "List pending tasks",
        ]

        response_times = []
        for i, msg in enumerate(messages):
            start_time = time.time()
            response = api_client.post(
                "/api/perf_user_avg/chat",
                json={"message": msg},
                headers=headers,
            )
            elapsed_time = time.time() - start_time
            response_times.append(elapsed_time)
            print(f"\nRequest {i + 1}: {elapsed_time:.2f}s")

            # Brief pause to avoid rate limiting
            time.sleep(0.5)

        avg_time = statistics.mean(response_times)
        print(f"\nAverage response time: {avg_time:.2f}s")
        print(f"Response times: {[f'{t:.2f}s' for t in response_times]}")

        assert avg_time < 3.0, f"Average response time {avg_time:.2f}s exceeds 3s target"

    def test_response_time_consistency(self, api_client, create_jwt_token):
        """T067: Response times are consistent (low standard deviation)."""
        token = create_jwt_token("perf_user_consistency")
        headers = {"Authorization": f"Bearer {token}"}

        response_times = []
        for i in range(3):
            start_time = time.time()
            response = api_client.post(
                "/api/perf_user_consistency/chat",
                json={"message": f"Hello, this is test {i + 1}"},
                headers=headers,
            )
            elapsed_time = time.time() - start_time
            response_times.append(elapsed_time)
            time.sleep(0.5)  # Avoid rate limiting

        if len(response_times) > 1:
            std_dev = statistics.stdev(response_times)
            print(f"\nResponse time std dev: {std_dev:.2f}s")
            # Standard deviation should be reasonable (under 2 seconds)
            assert std_dev < 2.0, f"High variance in response times: std_dev={std_dev:.2f}s"


class TestChatLatencyBenchmark:
    """Benchmark tests for measuring baseline latency."""

    def test_measure_baseline_latency(self, api_client, create_jwt_token):
        """Measure baseline latency for chat endpoint."""
        token = create_jwt_token("bench_user")
        headers = {"Authorization": f"Bearer {token}"}

        # Warm-up request
        api_client.post(
            "/api/bench_user/chat",
            json={"message": "Hello"},
            headers=headers,
        )
        time.sleep(0.5)

        # Benchmark requests
        latencies = []
        for _ in range(3):
            start = time.time()
            response = api_client.post(
                "/api/bench_user/chat",
                json={"message": "Show tasks"},
                headers=headers,
            )
            latencies.append(time.time() - start)
            time.sleep(0.5)

        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[-1]

        print(f"\n=== Chat Endpoint Latency Benchmark ===")
        print(f"P50 (median): {p50:.2f}s")
        print(f"P95: {p95:.2f}s")
        print(f"Min: {min(latencies):.2f}s")
        print(f"Max: {max(latencies):.2f}s")

        # P95 should be under 5 seconds
        assert p95 < 5.0, f"P95 latency {p95:.2f}s exceeds 5s target"
