"""
Enhanced Health Check System
Provides detailed system status and diagnostics
"""
from datetime import datetime, timezone
from typing import Dict, Any
import psutil
import logging
from database import get_database, client

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health check system"""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and stats"""
        try:
            db = get_database()
            # Ping database
            await client.admin.command('ping')
            
            # Get database stats
            stats = await db.command('dbStats')
            
            return {
                "status": "healthy",
                "connected": True,
                "response_time_ms": stats.get("ok", 0),
                "collections": stats.get("collections", 0),
                "data_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
                "index_size_mb": round(stats.get("indexSize", 0) / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system CPU, memory, disk usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                "disk": {
                    "percent": disk.percent,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                }
            }
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    def check_cache(self) -> Dict[str, Any]:
        """Check cache system status"""
        try:
            from cache_manager import cache_manager
            stats = cache_manager.get_stats()
            
            return {
                "status": "healthy",
                "enabled": True,
                "size": stats["size"],
                "max_size": stats["max_size"],
                "hit_rate": stats["hit_rate"],
                "total_requests": stats["total_requests"]
            }
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            return {
                "status": "unknown",
                "enabled": False,
                "error": str(e)
            }
    
    def check_rate_limiter(self) -> Dict[str, Any]:
        """Check rate limiter status"""
        try:
            from rate_limiter import get_rate_limiter_stats
            stats = get_rate_limiter_stats()
            
            return {
                "status": "healthy",
                "enabled": True,
                **stats
            }
        except Exception as e:
            logger.error(f"Rate limiter check failed: {e}")
            return {
                "status": "unknown",
                "enabled": False,
                "error": str(e)
            }
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get application uptime"""
        uptime = datetime.now(timezone.utc) - self.start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "started_at": self.start_time.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s"
        }
    
    async def get_full_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Check all components
        db_status = await self.check_database()
        system_status = self.check_system_resources()
        cache_status = self.check_cache()
        rate_limiter_status = self.check_rate_limiter()
        uptime = self.get_uptime()
        
        # Determine overall status
        overall_status = "healthy"
        if db_status["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif system_status["status"] == "warning":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.1.0",
            "environment": "production",  # Get from config
            "uptime": uptime,
            "components": {
                "database": db_status,
                "system": system_status,
                "cache": cache_status,
                "rate_limiter": rate_limiter_status
            },
            "features": {
                "ai_agents": True,
                "plugin_system": True,
                "white_label": True,
                "multi_tenancy": True,
                "voice_ai": True,
                "vision_ai": True
            }
        }
    
    async def get_basic_status(self) -> Dict[str, Any]:
        """Get basic health status (fast check)"""
        try:
            db = get_database()
            await client.admin.command('ping')
            
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "connected",
                "version": "1.1.0"
            }
        except Exception as e:
            logger.error(f"Basic health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "disconnected",
                "error": str(e)
            }

# Global health checker instance
health_checker = HealthChecker()

async def get_health_status(detailed: bool = False) -> Dict[str, Any]:
    """
    Get health status
    
    Args:
        detailed: If True, return comprehensive status with all components
    
    Returns:
        Health status dictionary
    """
    if detailed:
        return await health_checker.get_full_status()
    return await health_checker.get_basic_status()
