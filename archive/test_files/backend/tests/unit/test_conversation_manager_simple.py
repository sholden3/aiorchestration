"""
Unit Tests for Conversation Manager - Simplified Version
Tests core conversation functionality matching actual implementation
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
from ai_orchestration_engine import AIOrchestrationEngine, AITask


class TestConversationManager:
    """Test suite for ConversationManager core functionality"""
    
    @pytest.fixture
    def orchestrator_mock(self):
        """Create mock orchestration engine"""
        mock = Mock(spec=AIOrchestrationEngine)
        mock.submit_task = AsyncMock(return_value="task_123")
        mock.get_task_status = Mock(return_value={
            "status": "completed",
            "result": {"response": "Generated response"}
        })
        mock.completed_tasks = {}  # Add completed_tasks attribute
        return mock
    
    @pytest.fixture
    def conversation_manager(self, orchestrator_mock):
        """Create conversation manager instance for testing"""
        return ConversationManager(orchestrator_mock)
    
    # Basic Conversation Tests
    @pytest.mark.asyncio
    async def test_create_single_turn_conversation(self, conversation_manager):
        """Test creating a single-turn conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.SINGLE_TURN,
            title="Single Turn Test"
        )
        
        assert conv_id is not None
        assert conv_id.startswith("conv_")
        assert conv_id in conversation_manager.conversations
        conv = conversation_manager.conversations[conv_id]
        assert conv.title == "Single Turn Test"
        assert conv.conversation_type == ConversationType.SINGLE_TURN
    
    @pytest.mark.asyncio
    async def test_create_multi_turn_conversation(self, conversation_manager):
        """Test creating a multi-turn conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.MULTI_TURN,
            title="Multi Turn Test"
        )
        
        conv = conversation_manager.conversations[conv_id]
        assert conv.conversation_type == ConversationType.MULTI_TURN
        assert conv.title == "Multi Turn Test"
    
    @pytest.mark.asyncio
    async def test_create_collaborative_conversation(self, conversation_manager):
        """Test creating a collaborative conversation"""
        conv_id = await conversation_manager.create_conversation(
            conversation_type=ConversationType.COLLABORATIVE,
            title="Collaborative Test"
        )
        
        conv = conversation_manager.conversations[conv_id]
        assert conv.conversation_type == ConversationType.COLLABORATIVE
    
    # Message Handling Tests
    @pytest.mark.asyncio
    async def test_add_user_message(self, conversation_manager):
        """Test adding a user message to conversation"""
        # Create conversation
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Message Test"
        )
        
        # Add message
        message = await conversation_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Test user message"
        )
        
        assert message is not None
        conv = conversation_manager.conversations[conv_id]
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Test user message"
        assert conv.messages[0].role == MessageRole.USER
    
    @pytest.mark.asyncio
    async def test_add_assistant_message(self, conversation_manager):
        """Test adding an assistant message"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Assistant Message Test"
        )
        
        message = await conversation_manager.add_message(
            conversation_id=conv_id,
            role="assistant",
            content="AI response message"
        )
        
        conv = conversation_manager.conversations[conv_id]
        assert conv.messages[0].role == MessageRole.ASSISTANT
        assert conv.messages[0].content == "AI response message"
    
    @pytest.mark.asyncio
    async def test_add_message_to_nonexistent_conversation(self, conversation_manager):
        """Test error handling when adding message to non-existent conversation"""
        with pytest.raises(ValueError, match="Conversation not found"):
            await conversation_manager.add_message(
                conversation_id="nonexistent",
                role="user",
                content="Test"
            )
    
    # Context Management Tests
    @pytest.mark.asyncio
    async def test_add_context_to_conversation(self, conversation_manager):
        """Test adding context to a conversation"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Context Test"
        )
        
        context_data = {
            "user_preference": "technical",
            "expertise_level": "advanced"
        }
        
        success = await conversation_manager.add_context(
            conversation_id=conv_id,
            context_type="user_preferences",
            context_data=context_data
        )
        
        assert success == True
        conv = conversation_manager.conversations[conv_id]
        assert len(conv.contexts) > 0
    
    # AI Processing Tests
    @pytest.mark.asyncio
    async def test_generate_ai_response(self, conversation_manager, orchestrator_mock):
        """Test generating AI response for user message"""
        # Create conversation
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "AI Response Test"
        )
        
        # Add user message
        await conversation_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="What is machine learning?"
        )
        
        # Generate response
        response = await conversation_manager.generate_response(
            conversation_id=conv_id
        )
        
        assert response is not None
        assert orchestrator_mock.submit_task.called
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, conversation_manager, orchestrator_mock):
        """Test AI response generation with context"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Context Response Test"
        )
        
        # Add context
        await conversation_manager.add_context(
            conversation_id=conv_id,
            context_type="domain",
            context_data={"field": "data_science"}
        )
        
        # Add message
        await conversation_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Explain neural networks"
        )
        
        # Generate response
        response = await conversation_manager.generate_response(
            conversation_id=conv_id
        )
        
        assert response is not None
        assert orchestrator_mock.submit_task.called
    
    # Conversation Summary Tests
    @pytest.mark.asyncio
    async def test_create_conversation_summary(self, conversation_manager):
        """Test creating a conversation summary"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Summary Test"
        )
        
        # Add multiple messages
        await conversation_manager.add_message(conv_id, "user", "First question")
        await conversation_manager.add_message(conv_id, "assistant", "First answer")
        await conversation_manager.add_message(conv_id, "user", "Second question")
        await conversation_manager.add_message(conv_id, "assistant", "Second answer")
        
        # Create summary
        summary = await conversation_manager.create_summary(
            conversation_id=conv_id,
            summary_type="full"
        )
        
        assert summary is not None
        conv = conversation_manager.conversations[conv_id]
        assert len(conv.summaries) > 0
    
    # Conversation Retrieval Tests
    def test_get_active_conversations(self, conversation_manager):
        """Test retrieving active conversations"""
        active_convs = conversation_manager.get_active_conversations()
        
        assert isinstance(active_convs, list)
        for conv in active_convs:
            assert conv.status == ConversationStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, conversation_manager):
        """Test retrieving conversation by ID"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Get By ID Test"
        )
        
        conv = conversation_manager.get_conversation(conv_id)
        
        assert conv is not None
        assert conv.conversation_id == conv_id
        assert conv.title == "Get By ID Test"
    
    def test_get_nonexistent_conversation(self, conversation_manager):
        """Test retrieving non-existent conversation"""
        conv = conversation_manager.get_conversation("nonexistent")
        
        assert conv is None
    
    # Token Usage Tests
    @pytest.mark.asyncio
    async def test_track_token_usage(self, conversation_manager):
        """Test token usage tracking"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Token Test"
        )
        
        # Add message with token count
        await conversation_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Test message",
            token_count=10
        )
        
        await conversation_manager.add_message(
            conversation_id=conv_id,
            role="assistant",
            content="Response message",
            token_count=15
        )
        
        total_tokens = conversation_manager.get_conversation_tokens(conv_id)
        
        assert total_tokens == 25
    
    # Conversation Status Tests
    @pytest.mark.asyncio
    async def test_pause_conversation(self, conversation_manager):
        """Test pausing a conversation"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Pause Test"
        )
        
        success = await conversation_manager.pause_conversation(conv_id)
        
        assert success == True
        conv = conversation_manager.conversations[conv_id]
        assert conv.status == ConversationStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_resume_conversation(self, conversation_manager):
        """Test resuming a paused conversation"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.MULTI_TURN,
            "Resume Test"
        )
        
        # Pause first
        await conversation_manager.pause_conversation(conv_id)
        
        # Then resume
        success = await conversation_manager.resume_conversation(conv_id)
        
        assert success == True
        conv = conversation_manager.conversations[conv_id]
        assert conv.status == ConversationStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_complete_conversation(self, conversation_manager):
        """Test completing a conversation"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "Complete Test"
        )
        
        success = await conversation_manager.complete_conversation(conv_id)
        
        assert success == True
        conv = conversation_manager.conversations[conv_id]
        assert conv.status == ConversationStatus.COMPLETED
    
    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_generate_response_without_messages(self, conversation_manager):
        """Test generating response when no messages exist"""
        conv_id = await conversation_manager.create_conversation(
            ConversationType.SINGLE_TURN,
            "No Message Test"
        )
        
        response = await conversation_manager.generate_response(conv_id)
        
        # Should handle gracefully
        assert response is None or "error" in response


class TestConversationTypes:
    """Test suite for conversation type enums"""
    
    def test_conversation_type_values(self):
        """Test ConversationType enum values"""
        assert ConversationType.SINGLE_TURN.value == "single_turn"
        assert ConversationType.MULTI_TURN.value == "multi_turn"
        assert ConversationType.COLLABORATIVE.value == "collaborative"
    
    def test_message_role_values(self):
        """Test MessageRole enum values"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"
    
    def test_conversation_status_values(self):
        """Test ConversationStatus enum values"""
        assert ConversationStatus.ACTIVE.value == "active"
        assert ConversationStatus.PAUSED.value == "paused"
        assert ConversationStatus.COMPLETED.value == "completed"
        assert ConversationStatus.ARCHIVED.value == "archived"


class TestConversationMessage:
    """Test suite for ConversationMessage class"""
    
    def test_message_creation_with_required_fields(self):
        """Test creating message with required fields"""
        message = ConversationMessage(
            message_id="msg_123",
            conversation_id="conv_456",
            role=MessageRole.USER,
            content="Test message"
        )
        
        assert message.message_id == "msg_123"
        assert message.conversation_id == "conv_456"
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
    
    def test_message_timestamp_auto_set(self):
        """Test that timestamp is automatically set"""
        message = ConversationMessage(
            message_id="msg_124",
            conversation_id="conv_456",
            role=MessageRole.ASSISTANT,
            content="Response"
        )
        
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_message_with_metadata(self):
        """Test message creation with metadata"""
        metadata = {"source": "web", "confidence": 0.95}
        message = ConversationMessage(
            message_id="msg_125",
            conversation_id="conv_456",
            role=MessageRole.USER,
            content="Test",
            metadata=metadata
        )
        
        assert message.metadata == metadata
        assert message.metadata["confidence"] == 0.95


class TestAIConversation:
    """Test suite for AIConversation class"""
    
    def test_conversation_creation(self):
        """Test AIConversation creation"""
        conv = AIConversation(
            conversation_id="conv_123",
            conversation_type=ConversationType.MULTI_TURN,
            title="Test Conversation",
            description="Test description"
        )
        
        assert conv.conversation_id == "conv_123"
        assert conv.conversation_type == ConversationType.MULTI_TURN
        assert conv.title == "Test Conversation"
        assert conv.status == ConversationStatus.ACTIVE
    
    def test_conversation_default_values(self):
        """Test AIConversation default values"""
        conv = AIConversation(
            conversation_id="conv_124",
            conversation_type=ConversationType.SINGLE_TURN,
            title="Test",
            description="Test"
        )
        
        assert len(conv.messages) == 0
        assert len(conv.contexts) == 0
        assert len(conv.summaries) == 0
        assert conv.status == ConversationStatus.ACTIVE


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])