import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

db = Database()

class MockResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockCollection:
    async def find_one(self, query):
        return None
    async def insert_one(self, doc):
        return MockResult(inserted_id='mock')
    async def find(self, query=None):
        return []
    async def update_one(self, query, update):
        return MockResult(modified_count=1)
    async def create_index(self, *args, **kwargs):
        pass

class MockDB:
    def __getitem__(self, name):
        return MockCollection()
    async def command(self, cmd):
        return {'ok': 1, 'collections': 2}

class MockClient:
    def __init__(self):
        self.admin = MockAdmin()
    def __getitem__(self, name):
        return MockDB()
    def close(self):
        pass

class MockAdmin:
    async def command(self, cmd):
        return {'ok': 1}

async def connect_to_db():
    """Create database connection (mocked)"""
    try:
        db.client = MockClient()
        db.db = MockDB()
        logger.info("Connected to Mock Database (MongoDB bypassed)")
    except Exception as e:
        logger.error(f"Database setup error: {e}")
        raise

async def close_db_connection():
    """Close database connection"""
    if db.client and hasattr(db.client, 'close'):
        db.client.close()

def get_database():
    return db.db
