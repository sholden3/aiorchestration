"""
Unit Tests for Conversation Manager
Tests conversation lifecycle, message handling, and context management
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any
import uuid

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from conversation_manager import (
    ConversationManager,
    AIConversation,
    ConversationType,
    ConversationMessage,
    MessageRole,
    ConversationStatus,
    ConversationContext,
    ConversationSummary
)
from ai_orchestration_engine import AIOrchestrationEngine


class TestConversationManager:
    """Test suite for ConversationManager"""
    
    @pytest.fixture
    def orchestrator_mock(self):
        """Create mock orchestration engine"""
        mock = Mock(spec=AIOrchestrationEngine)
        mock.submit_task = AsyncMock(return_value="task_123")
        mock.get_task_status = Mock(return_value={
            "status": "completed",
            "result": {"response": "Generated response"}
        })
        return mock
    
    @pytest.fixture
    def conversation_manager(self, orchestrator_mock):
        """Create conversation manager instance for testing"""
        return ConversationManager(orchestrator_mock)
    
    @pytest.fixture
    def sample_conversation(self):
        """Create sample conversation for testing"""
        return AIAIConversation(
            conversation_id=str(uuid.uuid4()),
            conversation_type=ConversationType.SINGLE_TURN,
            title="Test Conversation",
            description="Test conversation for unit testing",
            status=ConversationStatus.ACTIVE,
            context=ConversationContext(
                user_preferences={"language": "en"},
                session_data={"session_id": "test_session"},
                domain="testing"
            ),
            messages=[],
            created_at=datetime.now()
        )
    
    # Conversation Lifecycle Tests
    @pytest.mark.asyncio
    async def test_create_conversation(self, conversation_manager):
        """Test creating a new conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.SINGLE_TURN,
            title="New Test Conversation",
            description="Testing conversation creation"
        )
        
        assert conv_id is not None
        assert conv_id in conversation_manager.conversations
        conv = conversation_manager.conversations[conv_id]
        assert conv.title == "New Test Conversation"
        assert conv.conversation_type == ConversationType.SINGLE_TURN
    
    @pytest.mark.asyncio
    async def test_create_multi_turn_conversation(self, conversation_manager):
        """Test creating multi-turn conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.MULTI_TURN,
            title="Multi-turn Test",
            description="Testing multi-turn conversation",
            initial_context={
                "max_turns": 10,
                "maintain_history": True
            }
        )
        
        conv = conversation_manager.conversations[conv_id]
        assert conv.conversation_type == ConversationType.MULTI_TURN
        assert conv.context["max_turns"] == 10
        assert conv.context["maintain_history"] == True
    
    @pytest.mark.asyncio
    async def test_create_collaborative_conversation(self, conversation_manager):
        """Test creating collaborative conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.COLLABORATIVE,
            title="Collaborative Test",
            description="Testing collaborative conversation",
            initial_context={
                "participants": ["user1", "ai_assistant"],
                "collaboration_mode": "pair_programming"
            }
        )
        
        conv = conversation_manager.conversations[conv_id]
        assert conv.conversation_type == ConversationType.COLLABORATIVE
        assert "participants" in conv.context
        assert len(conv.context["participants"]) == 2
    
    @pytest.mark.asyncio
    async def test_end_conversation(self, conversation_manager, sample_conversation):
        """Test ending a conversation"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        success = await conversation_manager.end_conversation(conv_id)
        
        assert success == True
        assert conversation_manager.conversations[conv_id].status == ConversationStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, conversation_manager, sample_conversation):
        """Test deleting a conversation"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        success = await conversation_manager.delete_conversation(conv_id)
        
        assert success == True
        assert conv_id not in conversation_manager.conversations
    
    # ConversationMessage Handling Tests
    @pytest.mark.asyncio
    async def test_add_message(self, conversation_manager, sample_conversation):
        """Test adding message to conversation"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        message_id = await conversation_manager.add_message(
            conversation_id=conv_id,
            role=MessageRole.USER,
            content="Test message content"
        )
        
        assert message_id is not None
        assert len(sample_conversation.messages) == 1
        assert sample_conversation.messages[0].content == "Test message content"
        assert sample_conversation.messages[0].role == MessageRole.USER
    
    @pytest.mark.asyncio
    async def test_add_message_with_metadata(self, conversation_manager, sample_conversation):
        """Test adding message with metadata"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source": "web_interface",
            "confidence": 0.95
        }
        
        message_id = await conversation_manager.add_message(
            conversation_id=conv_id,
            role=MessageRole.ASSISTANT,
            content="Response with metadata",
            metadata=metadata
        )
        
        message = sample_conversation.messages[0]
        assert message.metadata == metadata
        assert message.metadata["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, conversation_manager, sample_conversation):
        """Test retrieving conversation history"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        # Add multiple messages
        await conversation_manager.add_message(conv_id, MessageRole.USER, "First message")
        await conversation_manager.add_message(conv_id, MessageRole.ASSISTANT, "First response")
        await conversation_manager.add_message(conv_id, MessageRole.USER, "Second message")
        
        history = conversation_manager.get_conversation_history(conv_id)
        
        assert len(history) == 3
        assert history[0]["content"] == "First message"
        assert history[1]["role"] == "assistant"
        assert history[2]["content"] == "Second message"
    
    @pytest.mark.asyncio
    async def test_get_last_n_messages(self, conversation_manager, sample_conversation):
        """Test getting last N messages from conversation"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        # Add 5 messages
        for i in range(5):
            await conversation_manager.add_message(
                conv_id,
                MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                f"ConversationMessage {i+1}"
            )
        
        last_3 = conversation_manager.get_last_n_messages(conv_id, 3)
        
        assert len(last_3) == 3
        assert last_3[0]["content"] == "ConversationMessage 3"
        assert last_3[2]["content"] == "ConversationMessage 5"
    
    # Context Management Tests
    @pytest.mark.asyncio
    async def test_update_context(self, conversation_manager, sample_conversation):
        """Test updating conversation context"""
        conv_id = sample_conversation.conversation_id
        conversation_manager.conversations[conv_id] = sample_conversation
        
        new_context = {
            "topic": "AI development",
            "expertise_level": "intermediate"
        }
        
        success = await conversation_manager.update_context(conv_id, new_context)
        
        assert success == True
        assert sample_conversation.context["topic"] == "AI development"
        assert sample_conversation.context["expertise_level"] == "intermediate"
    
    @pytest.mark.asyncio
    async def test_merge_context(self, conversation_manager, sample_conversation):
        """Test merging context without overwriting existing values"""
        conv_id = sample_conversation.conversation_id
        sample_conversation.context = {"existing": "value", "key": "old"}
        conversation_manager.conversations[conv_id] = sample_conversation
        
        new_context = {"key": "new", "additional": "data"}
        success = await conversation_manager.update_context(
            conv_id,
            new_context,
            merge=True
        )
        
        assert success == True
        assert sample_conversation.context["existing"] == "value"
        assert sample_conversation.context["key"] == "new"
        assert sample_conversation.context["additional"] == "data"
    
    @pytest.mark.asyncio
    async def test_get_conversation_context(self, conversation_manager, sample_conversation):
        """Test retrieving conversation context"""
        conv_id = sample_conversation.conversation_id
        sample_conversation.context = {
            "user_id": "test_user",
            "preferences": {"theme": "dark"}
        }
        conversation_manager.conversations[conv_id] = sample_conversation
        
        context = conversation_manager.get_conversation_context(conv_id)
        
        assert context is not None
        assert context["user_id"] == "test_user"
        assert context["preferences"]["theme"] == "dark"
    
    # AI Processing Tests
    @pytest.mark.asyncio
    async def test_process_ai_response(self, conversation_manager, orchestrator_mock):
        """Test processing AI response for user message"""
        # Create conversation
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "AI Response Test"
        )
        
        # Process AI response
        response = await conversation_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="What is machine learning?"
        )
        
        assert response is not None
        assert "response" in response
        assert orchestrator_mock.submit_task.called
    
    @pytest.mark.asyncio
    async def test_process_ai_response_with_context(self, conversation_manager, orchestrator_mock):
        """Test AI response with context enhancement"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Context Test",
            initial_context={"domain": "data_science"}
        )
        
        response = await conversation_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="Explain neural networks",
            context_enhancement=True
        )
        
        assert response is not None
        assert orchestrator_mock.submit_task.called
        # Verify context was included in task
        call_args = orchestrator_mock.submit_task.call_args
        assert call_args is not None
    
    @pytest.mark.asyncio
    async def test_process_ai_response_with_governance(self, conversation_manager, orchestrator_mock):
        """Test AI response with governance validation"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.COLLABORATIVE,
            "Governance Test"
        )
        
        response = await conversation_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="Deploy to production",
            use_governance=True
        )
        
        assert response is not None
        assert "governance_used" in response or "response" in response
    
    # Conversation Search Tests
    @pytest.mark.asyncio
    async def test_search_conversations_by_status(self, conversation_manager):
        """Test searching conversations by status"""
        # Create multiple conversations
        active_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Active Conv"
        )
        
        paused_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Paused Conv"
        )
        conversation_manager.conversations[paused_id].status = ConversationStatus.PAUSED
        
        active_convs = conversation_manager.search_conversations(
            status=ConversationStatus.ACTIVE
        )
        
        assert len(active_convs) >= 1
        assert any(c.conversation_id == active_id for c in active_convs)
        assert not any(c.conversation_id == paused_id for c in active_convs)
    
    @pytest.mark.asyncio
    async def test_search_conversations_by_type(self, conversation_manager):
        """Test searching conversations by type"""
        single_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Single Turn"
        )
        
        multi_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Multi Turn"
        )
        
        multi_convs = conversation_manager.search_conversations(
            conversation_type=ConversationType.MULTI_TURN
        )
        
        assert len(multi_convs) >= 1
        assert any(c.conversation_id == multi_id for c in multi_convs)
        assert not any(c.conversation_id == single_id for c in multi_convs)
    
    @pytest.mark.asyncio
    async def test_search_conversations_by_date_range(self, conversation_manager):
        """Test searching conversations by date range"""
        # Create conversation
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Date Test"
        )
        
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        results = conversation_manager.search_conversations(
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(results) >= 1
        assert any(c.conversation_id == conv_id for c in results)
    
    # Metrics Tests
    def test_get_conversation_metrics(self, conversation_manager, sample_conversation):
        """Test getting conversation metrics"""
        conv_id = sample_conversation.conversation_id
        sample_conversation.messages = [
            ConversationMessage("msg1", MessageRole.USER, "User message", {}),
            ConversationMessage("msg2", MessageRole.ASSISTANT, "AI response", {}),
            ConversationMessage("msg3", MessageRole.USER, "Follow up", {})
        ]
        conversation_manager.conversations[conv_id] = sample_conversation
        
        metrics = conversation_manager.get_conversation_metrics(conv_id)
        
        assert metrics is not None
        assert metrics["message_count"] == 3
        assert metrics["user_messages"] == 2
        assert metrics["assistant_messages"] == 1
    
    def test_get_global_metrics(self, conversation_manager):
        """Test getting global conversation metrics"""
        # Create multiple conversations
        for i in range(3):
            conv = AIConversation(
                conversation_id=f"conv_{i}",
                conversation_type=ConversationType.SINGLE_TURN,
                title=f"Conv {i}",
                description="Test",
                status=ConversationStatus.ACTIVE if i < 2 else ConversationStatus.COMPLETED,
                context={},
                messages=[],
                created_at=datetime.now()
            )
            conversation_manager.conversations[f"conv_{i}"] = conv
        
        metrics = conversation_manager.get_global_metrics()
        
        assert metrics["total_conversations"] == 3
        assert metrics["active_conversations"] == 2
        assert metrics["completed_conversations"] == 1
    
    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_add_message_to_nonexistent_conversation(self, conversation_manager):
        """Test adding message to non-existent conversation"""
        result = await conversation_manager.add_message(
            conversation_id="nonexistent",
            role=MessageRole.USER,
            content="Test"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_conversation(self, conversation_manager):
        """Test deleting non-existent conversation"""
        success = await conversation_manager.delete_conversation("nonexistent")
        
        assert success == False
    
    @pytest.mark.asyncio
    async def test_process_ai_response_with_failed_task(self, conversation_manager, orchestrator_mock):
        """Test AI response when task fails"""
        orchestrator_mock.get_task_status = Mock(return_value={
            "status": "failed",
            "error": "Task execution failed"
        })
        
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Failure Test"
        )
        
        response = await conversation_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="Test message"
        )
        
        assert response is not None
        assert "error" in response or "status" in response


class TestConversationTypes:
    """Test suite for conversation type enums and classes"""
    
    def test_conversation_type_enum(self):
        """Test ConversationType enum values"""
        assert ConversationType.SINGLE_TURN.value == "single_turn"
        assert ConversationType.MULTI_TURN.value == "multi_turn"
        assert ConversationType.COLLABORATIVE.value == "collaborative"
    
    def test_message_role_enum(self):
        """Test MessageRole enum values"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"
    
    def test_conversation_status_enum(self):
        """Test ConversationStatus enum values"""
        assert ConversationStatus.ACTIVE.value == "active"
        assert ConversationStatus.PAUSED.value == "paused"
        assert ConversationStatus.COMPLETED.value == "completed"
        assert ConversationStatus.ARCHIVED.value == "archived"


class TestConversationMessage:
    """Test suite for ConversationMessage class"""
    
    def test_message_creation(self):
        """Test ConversationMessage object creation"""
        message = ConversationMessage(
            message_id="msg_123",
            role=MessageRole.USER,
            content="Test message",
            metadata={"source": "web"}
        )
        
        assert message.message_id == "msg_123"
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
        assert message.metadata["source"] == "web"
    
    def test_message_timestamp(self):
        """Test message timestamp is set"""
        message = ConversationMessage(
            message_id="msg_124",
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata={}
        )
        
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        message = ConversationMessage(
            message_id="msg_125",
            role=MessageRole.USER,
            content="Test",
            metadata={"key": "value"}
        )
        
        msg_dict = message.to_dict()
        
        assert msg_dict["message_id"] == "msg_125"
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Test"
        assert msg_dict["metadata"]["key"] == "value"


class TestAIConversation:
    """Test suite for AIConversation class"""
    
    def test_conversation_creation(self):
        """Test Conversation object creation"""
        conv = AIConversation(
            conversation_id="conv_123",
            conversation_type=ConversationType.MULTI_TURN,
            title="Test Conversation",
            description="Test description",
            status=ConversationStatus.ACTIVE,
            context={"key": "value"},
            messages=[],
            created_at=datetime.now()
        )
        
        assert conv.conversation_id == "conv_123"
        assert conv.conversation_type == ConversationType.MULTI_TURN
        assert conv.title == "Test Conversation"
        assert conv.status == ConversationStatus.ACTIVE
    
    def test_conversation_add_message(self):
        """Test adding message to conversation"""
        conv = AIConversation(
            conversation_id="conv_124",
            conversation_type=ConversationType.SINGLE_TURN,
            title="Test",
            description="Test",
            status=ConversationStatus.ACTIVE,
            context={},
            messages=[],
            created_at=datetime.now()
        )
        
        message = ConversationMessage("msg_1", MessageRole.USER, "Hello", {})
        conv.add_message(message)
        
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"
    
    def test_conversation_get_last_message(self):
        """Test getting last message from conversation"""
        conv = AIConversation(
            conversation_id="conv_125",
            conversation_type=ConversationType.SINGLE_TURN,
            title="Test",
            description="Test",
            status=ConversationStatus.ACTIVE,
            context={},
            messages=[
                ConversationMessage("msg_1", MessageRole.USER, "First", {}),
                ConversationMessage("msg_2", MessageRole.ASSISTANT, "Second", {}),
                ConversationMessage("msg_3", MessageRole.USER, "Last", {})
            ],
            created_at=datetime.now()
        )
        
        last_msg = conv.get_last_message()
        
        assert last_msg is not None
        assert last_msg.content == "Last"
    
    def test_conversation_message_count(self):
        """Test getting message count by role"""
        conv = AIConversation(
            conversation_id="conv_126",
            conversation_type=ConversationType.MULTI_TURN,
            title="Test",
            description="Test",
            status=ConversationStatus.ACTIVE,
            context={},
            messages=[
                ConversationMessage("msg_1", MessageRole.USER, "User 1", {}),
                ConversationMessage("msg_2", MessageRole.ASSISTANT, "AI 1", {}),
                ConversationMessage("msg_3", MessageRole.USER, "User 2", {}),
                ConversationMessage("msg_4", MessageRole.SYSTEM, "System", {})
            ],
            created_at=datetime.now()
        )
        
        assert conv.get_message_count(MessageRole.USER) == 2
        assert conv.get_message_count(MessageRole.ASSISTANT) == 1
        assert conv.get_message_count(MessageRole.SYSTEM) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])