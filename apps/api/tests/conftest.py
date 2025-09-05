"""
@fileoverview Pytest configuration and fixtures
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - Configuration
@business_logic Shared test fixtures and configuration
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Base
from database.database import get_db

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test_async.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def test_app() -> FastAPI:
    """Create a test FastAPI application with minimal configuration"""
    from fastapi import FastAPI
    from api import rules, practices, templates, sessions
    
    # Create app with test configuration
    app = FastAPI(
        title="Test API",
        docs_url=None,  # Disable docs in tests
        redoc_url=None  # Disable redoc in tests
    )
    
    # Include routers
    app.include_router(rules.router)
    app.include_router(practices.router)
    app.include_router(templates.router)
    app.include_router(sessions.router)
    
    return app

@pytest.fixture(scope="function")
def client(test_app, test_session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(test_app) as c:
        yield c

@pytest.fixture(scope="function")
def test_app_with_governance() -> FastAPI:
    """Create a test app with governance features enabled"""
    import os
    os.environ["TESTING"] = "true"
    os.environ["GOVERNANCE_LEVEL"] = "MONITOR"  # Less strict for testing
    
    # Import after setting env vars
    from main import AIBackendService
    
    # Create service with test config
    service = AIBackendService()
    
    # Disable background tasks that cause issues in tests
    service._initialization_complete = True  # Skip initialization
    service._initialization_error = None
    
    return service.app

@pytest.fixture(scope="function")
async def async_client(test_app_with_governance, test_session):
    """Create an async test client for testing with full app features"""
    from httpx import AsyncClient
    
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    test_app_with_governance.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=test_app_with_governance, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_rule_data():
    """Sample rule data for testing"""
    return {
        "name": "test_rule",
        "description": "Test rule description",
        "category": "testing",
        "severity": "warning",
        "status": "active",
        "condition": '{"key": "value"}',
        "action": "block",
        "parameters": {"threshold": 10}
    }

@pytest.fixture
def sample_practice_data():
    """Sample practice data for testing"""
    return {
        "name": "Test Practice",
        "category": "testing",
        "description": "A test practice",
        "rationale": "Why this is important",
        "examples": ["Example 1", "Example 2"],
        "anti_patterns": ["Don't do this"],
        "score_weight": 1.5
    }

@pytest.fixture
def sample_template_data():
    """Sample template data for testing"""
    return {
        "name": "Test Template",
        "type": "code",
        "category": "testing",
        "template_content": "Hello {{name}}, welcome to {{project}}!",
        "description": "A test template",
        "variables": {
            "name": {"type": "string", "required": True},
            "project": {"type": "string", "required": True}
        }
    }

@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "session_id": "test_session_123",
        "architects": ["Test User"],
        "status": "active",
        "environment": {"test": True}
    }