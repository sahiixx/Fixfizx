"""
Pytest Configuration and Fixtures
"""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import os

# Test database name
TEST_DB_NAME = "nowhereai_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database connection"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client[TEST_DB_NAME]
    
    yield db
    
    # Cleanup: drop test database after all tests
    await client.drop_database(TEST_DB_NAME)
    client.close()

@pytest.fixture(autouse=True)
async def clean_db(test_db):
    """Clean database before each test"""
    # Drop all collections before each test
    for collection_name in await test_db.list_collection_names():
        await test_db[collection_name].delete_many({})
    
    yield
    
    # Optional: Clean after test as well
    # for collection_name in await test_db.list_collection_names():
    #     await test_db[collection_name].delete_many({})

@pytest.fixture
async def test_client():
    """Create test HTTP client"""
    from server import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_contact_data():
    """Sample contact form data"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+971501234567",
        "service": "web_dev",
        "message": "This is a test message"
    }

@pytest.fixture
def sample_user_data():
    """Sample user data"""
    return {
        "email": "testuser@example.com",
        "password": "SecureP@ssw0rd",
        "name": "Test User",
        "role": "user"
    }
