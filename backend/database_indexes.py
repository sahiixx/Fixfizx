"""
Database Indexes Configuration
Creates indexes for optimal query performance
"""
import asyncio
import logging
from database import get_database

logger = logging.getLogger(__name__)

async def create_all_indexes():
    """Create all necessary database indexes"""
    try:
        db = get_database()
        
        # Contacts Collection Indexes
        await db.contacts.create_index([("email", 1)], unique=True)
        await db.contacts.create_index([("created_at", -1)])
        await db.contacts.create_index([("service", 1)])
        logger.info("✅ Contacts collection indexes created")
        
        # Analytics Collection Indexes
        await db.analytics.create_index([("date", 1)])
        await db.analytics.create_index([("metric", 1)])
        await db.analytics.create_index([("date", 1), ("metric", 1)])
        logger.info("✅ Analytics collection indexes created")
        
        # Tenants Collection Indexes (White Label)
        await db.tenants.create_index([("config.domain", 1)], unique=True)
        await db.tenants.create_index([("config.status", 1)])
        await db.tenants.create_index([("config.subscription_tier", 1)])
        logger.info("✅ Tenants collection indexes created")
        
        # Chat Sessions Indexes
        await db.chat_sessions.create_index([("session_id", 1)], unique=True)
        await db.chat_sessions.create_index([("user_id", 1)])
        await db.chat_sessions.create_index([("created_at", -1)])
        await db.chat_sessions.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✅ Chat sessions collection indexes created")
        
        # AI Agent Tasks Indexes
        await db.agent_tasks.create_index([("task_id", 1)], unique=True)
        await db.agent_tasks.create_index([("agent_id", 1)])
        await db.agent_tasks.create_index([("status", 1)])
        await db.agent_tasks.create_index([("created_at", -1)])
        await db.agent_tasks.create_index([("agent_id", 1), ("status", 1)])
        logger.info("✅ Agent tasks collection indexes created")
        
        # Security Audit Logs Indexes
        await db.audit_logs.create_index([("user_id", 1)])
        await db.audit_logs.create_index([("action", 1)])
        await db.audit_logs.create_index([("timestamp", -1)])
        await db.audit_logs.create_index([("tenant_id", 1), ("timestamp", -1)])
        logger.info("✅ Audit logs collection indexes created")
        
        # Performance Metrics Indexes
        await db.performance_metrics.create_index([("timestamp", -1)])
        await db.performance_metrics.create_index([("metric_type", 1)])
        await db.performance_metrics.create_index([("metric_type", 1), ("timestamp", -1)])
        logger.info("✅ Performance metrics collection indexes created")
        
        logger.info("🎉 All database indexes created successfully")
        return {"success": True, "message": "All indexes created"}
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

async def drop_all_indexes():
    """Drop all custom indexes (for testing/reset)"""
    try:
        db = get_database()
        
        collections = [
            "contacts", "analytics", "tenants", "chat_sessions",
            "agent_tasks", "audit_logs", "performance_metrics"
        ]
        
        for collection in collections:
            if collection in await db.list_collection_names():
                await db[collection].drop_indexes()
                logger.info(f"Dropped indexes for {collection}")
        
        logger.info("🎉 All custom indexes dropped")
        return {"success": True, "message": "All indexes dropped"}
        
    except Exception as e:
        logger.error(f"❌ Error dropping indexes: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

async def check_indexes():
    """Check existing indexes"""
    try:
        db = get_database()
        
        collections = [
            "contacts", "analytics", "tenants", "chat_sessions",
            "agent_tasks", "audit_logs", "performance_metrics"
        ]
        
        indexes_info = {}
        
        for collection in collections:
            if collection in await db.list_collection_names():
                indexes = await db[collection].index_information()
                indexes_info[collection] = indexes
        
        return {"success": True, "indexes": indexes_info}
        
    except Exception as e:
        logger.error(f"❌ Error checking indexes: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

async def main():
    """Main function to create indexes"""
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import after path is set
    from database import get_database, client
    
    # Ensure connection is established
    try:
        await client.admin.command('ping')
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    result = await create_all_indexes()
    if result["success"]:
        logger.info("✅ Database indexes setup complete")
    else:
        logger.error(f"❌ Failed to create indexes: {result.get('error')}")

if __name__ == "__main__":
    # Run directly to create indexes
    asyncio.run(main())
