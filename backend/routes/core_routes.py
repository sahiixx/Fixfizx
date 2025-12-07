"""
Core API Routes
Basic endpoints: health, contact, analytics
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from models import StandardResponse
from database import get_database
from cache_manager import cached, cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Core"])

# ================================================================================================
# HEALTH CHECK
# ================================================================================================

@router.get("/health", response_model=StandardResponse)
@cached(ttl=60, key_prefix="health")
async def health_check():
    """
    Health check endpoint
    Returns server status and basic system information
    """
    try:
        db = get_database()
        # Ping database
        await db.command('ping')
        
        return StandardResponse(
            success=True,
            message="Server is healthy",
            data={
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "connected",
                "version": "1.0.0"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# ================================================================================================
# CONTACT FORM
# ================================================================================================

@router.post("/contact", response_model=StandardResponse)
async def submit_contact_form(contact_data: Dict[str, Any]):
    """
    Submit contact form
    Stores contact information in database
    """
    try:
        required_fields = ["name", "email", "phone", "service", "message"]
        missing_fields = [field for field in required_fields if field not in contact_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Add metadata
        contact_data["created_at"] = datetime.now(timezone.utc).isoformat()
        contact_data["status"] = "new"
        contact_data["source"] = "website"
        
        # Store in database
        db = get_database()
        result = await db.contacts.insert_one(contact_data)
        
        # Invalidate analytics cache since we have new data
        cache_manager.delete("analytics_summary")
        
        logger.info(f"Contact form submitted: {contact_data.get('email')}")
        
        return StandardResponse(
            success=True,
            message="Contact form submitted successfully",
            data={
                "id": str(result.inserted_id),
                "email": contact_data.get("email")
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting contact form: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to submit contact form")

# ================================================================================================
# ANALYTICS
# ================================================================================================

@router.get("/analytics/summary", response_model=StandardResponse)
@cached(ttl=300, key_prefix="analytics_summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=90, description="Number of days for analytics")
):
    """
    Get analytics summary
    Returns platform usage statistics
    """
    try:
        db = get_database()
        
        # Get contact form submissions
        contacts_count = await db.contacts.count_documents({})
        
        # Get chat sessions count
        sessions_count = await db.chat_sessions.count_documents({})
        
        # Get agent tasks count
        agent_tasks_count = await db.agent_tasks.count_documents({})
        
        # Today's activity
        from datetime import date, timedelta
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        today_contacts = await db.contacts.count_documents({
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        today_sessions = await db.chat_sessions.count_documents({
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        # This week's activity
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        week_contacts = await db.contacts.count_documents({
            "created_at": {"$gte": week_start_dt.isoformat()}
        })
        
        return StandardResponse(
            success=True,
            message="Analytics summary retrieved",
            data={
                "today": {
                    "contacts": today_contacts,
                    "sessions": today_sessions,
                    "date": today.isoformat()
                },
                "this_week": {
                    "contacts": week_contacts,
                    "start_date": week_start.isoformat()
                },
                "total": {
                    "contacts": contacts_count,
                    "sessions": sessions_count,
                    "agent_tasks": agent_tasks_count
                },
                "cache_stats": cache_manager.get_stats()
            }
        )
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

# ================================================================================================
# CONTENT RECOMMENDATIONS
# ================================================================================================

@router.get("/content/recommendations", response_model=StandardResponse)
@cached(ttl=3600, key_prefix="content_recommendations")
async def get_content_recommendations(
    industry: Optional[str] = Query(None, description="Industry filter"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations")
):
    """
    Get AI-powered content recommendations
    Returns recommended services and solutions
    """
    try:
        # In production, this would use AI to generate recommendations
        # For now, return curated recommendations
        
        recommendations = [
            {
                "title": "AI-Powered Customer Service",
                "description": "Automate customer support with intelligent chatbots",
                "category": "ai_automation",
                "relevance_score": 0.95,
                "estimated_roi": "300%",
                "implementation_time": "2-4 weeks"
            },
            {
                "title": "Dubai Market Analysis",
                "description": "Comprehensive market analysis for UAE businesses",
                "category": "analytics",
                "relevance_score": 0.92,
                "estimated_roi": "250%",
                "implementation_time": "1-2 weeks"
            },
            {
                "title": "Social Media Automation",
                "description": "AI-driven social media management and content creation",
                "category": "marketing",
                "relevance_score": 0.88,
                "estimated_roi": "200%",
                "implementation_time": "2-3 weeks"
            },
            {
                "title": "E-commerce Integration",
                "description": "Complete e-commerce platform with AI recommendations",
                "category": "web_development",
                "relevance_score": 0.85,
                "estimated_roi": "400%",
                "implementation_time": "4-6 weeks"
            },
            {
                "title": "Mobile App Development",
                "description": "Native iOS and Android apps with AI features",
                "category": "mobile",
                "relevance_score": 0.80,
                "estimated_roi": "350%",
                "implementation_time": "6-8 weeks"
            }
        ]
        
        # Filter by industry if provided
        if industry:
            recommendations = [
                r for r in recommendations 
                if industry.lower() in r["category"].lower()
            ]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(recommendations)} recommendations",
            data={
                "recommendations": recommendations,
                "total": len(recommendations),
                "industry_filter": industry
            }
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# ================================================================================================
# CACHE MANAGEMENT (Admin)
# ================================================================================================

@router.get("/cache/stats", response_model=StandardResponse)
async def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = cache_manager.get_stats()
        return StandardResponse(
            success=True,
            message="Cache statistics retrieved",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

@router.post("/cache/clear", response_model=StandardResponse)
async def clear_cache(key_prefix: Optional[str] = None):
    """
    Clear cache
    Optionally clear only entries with specific prefix
    """
    try:
        if key_prefix:
            from cache_manager import invalidate_cache
            invalidate_cache(key_prefix)
            message = f"Cache cleared for prefix: {key_prefix}"
        else:
            cache_manager.clear()
            message = "All cache cleared"
        
        logger.info(message)
        
        return StandardResponse(
            success=True,
            message=message,
            data=cache_manager.get_stats()
        )
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")
