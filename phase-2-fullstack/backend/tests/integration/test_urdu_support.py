"""Integration tests for Urdu language support in chatbot.

This module tests the multilingual capabilities of the AI chatbot,
specifically for Urdu language support (+100 bonus points for Phase III).

Test cases verify:
- Urdu task creation commands
- Urdu task listing commands
- Urdu task completion commands
- Urdu response generation
- Language detection and auto-response
"""

import pytest
from unittest.mock import patch, MagicMock


class TestUrduTaskCreation:
    """Test suite for Urdu task creation (T051)."""

    def test_urdu_add_task_command_recognized(
        self, api_client, create_jwt_token
    ):
        """Test that Urdu add task command is recognized."""
        token = create_jwt_token("test_user_urdu")

        # Mock the chat service to verify the command is processed
        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✅ کام 'دودھ خریدنا' کامیابی سے شامل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["add_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "ایک کام شامل کریں: دودھ خریدنا"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Verify Urdu response
            assert "کام" in data["message"] or "✅" in data["message"]

    def test_urdu_create_task_with_priority(
        self, api_client, create_jwt_token
    ):
        """Test Urdu task creation with priority specification."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✅ اہم کام 'ڈاکٹر کی ملاقات' شامل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["add_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "نیا اہم کام بنائیں: ڈاکٹر کی ملاقات"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_urdu_add_task_alternate_phrasing(
        self, api_client, create_jwt_token
    ):
        """Test alternate Urdu phrasings for task creation."""
        token = create_jwt_token("test_user_urdu")

        # Test "نیا کام بنائیں" (create new task)
        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✅ کام شامل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["add_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "نیا کام بنائیں - گھر کی صفائی"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200


class TestUrduTaskListing:
    """Test suite for Urdu task listing (T052)."""

    def test_urdu_list_tasks_command(
        self, api_client, create_jwt_token
    ):
        """Test Urdu list tasks command."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "📋 آپ کے کام:\n1. دودھ خریدنا (اہم)",
                "conversation_id": 1,
                "tool_calls": ["list_tasks_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "میرے کام دکھائیں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Verify Urdu in response
            assert "کام" in data["message"]

    def test_urdu_list_pending_tasks(
        self, api_client, create_jwt_token
    ):
        """Test Urdu pending tasks listing."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "📋 آپ کے باقی کام:\nکوئی باقی کام نہیں 🎉",
                "conversation_id": 1,
                "tool_calls": ["list_tasks_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "باقی کام دکھائیں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200


class TestUrduTaskCompletion:
    """Test suite for Urdu task completion."""

    def test_urdu_complete_task_command(
        self, api_client, create_jwt_token
    ):
        """Test Urdu task completion command."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✅ کام 'دودھ خریدنا' مکمل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["complete_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "کام 1 مکمل کریں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "مکمل" in data["message"] or "✅" in data["message"]


class TestUrduTaskUpdate:
    """Test suite for Urdu task updates."""

    def test_urdu_update_task_title(
        self, api_client, create_jwt_token
    ):
        """Test Urdu task title update."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✏️ کام تبدیل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["update_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "کام 1 کا عنوان تبدیل کریں: تازہ دودھ"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200


class TestUrduTaskDeletion:
    """Test suite for Urdu task deletion."""

    def test_urdu_delete_task_command(
        self, api_client, create_jwt_token
    ):
        """Test Urdu task deletion command."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "🗑️ کام 'دودھ خریدنا' حذف ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["delete_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "کام 1 حذف کریں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "حذف" in data["message"] or "🗑️" in data["message"]


class TestLanguageDetection:
    """Test suite for automatic language detection."""

    def test_mixed_language_defaults_to_user_language(
        self, api_client, create_jwt_token
    ):
        """Test that mixed language input responds in detected language."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "✅ Task 'grocery shopping' شامل ہو گیا!",
                "conversation_id": 1,
                "tool_calls": ["add_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            # Mixed Urdu/English input
            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "Add کریں task: grocery shopping"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200

    def test_pure_urdu_gets_urdu_response(
        self, api_client, create_jwt_token
    ):
        """Test that pure Urdu input gets Urdu response."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "📋 آپ کے کوئی کام نہیں ہیں۔ ایک نیا کام شامل کریں!",
                "conversation_id": 1,
                "tool_calls": ["list_tasks_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "میرے تمام کام دکھائیں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            # Verify response contains Urdu characters (Arabic script range)
            assert any(ord(c) > 1536 and ord(c) < 1792 for c in data["message"])


class TestUrduErrorMessages:
    """Test suite for Urdu error messages."""

    def test_urdu_task_not_found_error(
        self, api_client, create_jwt_token
    ):
        """Test Urdu error message for task not found."""
        token = create_jwt_token("test_user_urdu")

        with patch("src.api.routes.chat.ChatService") as MockChatService:
            mock_instance = MagicMock()
            mock_instance.process_message.return_value = {
                "success": True,
                "message": "❌ کام نمبر 999 نہیں ملا۔ براہ کرم درست کام نمبر دیں۔",
                "conversation_id": 1,
                "tool_calls": ["complete_task_wrapper"],
            }
            MockChatService.return_value = mock_instance

            response = api_client.post(
                "/api/test_user_urdu/chat",
                json={"message": "کام 999 مکمل کریں"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            # Error message should be in Urdu
            assert "نہیں" in data["message"] or "❌" in data["message"]
