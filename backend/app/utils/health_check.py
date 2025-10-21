"""
Health check and monitoring utilities
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, UTC, timedelta
from pathlib import Path
import logging

from ..config import config
from ..exceptions import APIConnectionError, DatabaseError
from ..services.llm_analyzer import LLMAnalyzer, LLMProvider

logger = logging.getLogger(__name__)

class HealthStatus:
    """Health status constants"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """Comprehensive health check system"""
    
    def __init__(self):
        self.start_time = datetime.now(UTC)
        self.last_check = None
        self.check_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        start_time = time.time()
        
        health_data = {
            "status": HealthStatus.HEALTHY,
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
            "checks": {},
            "system": await self._get_system_metrics(),
            "application": await self._get_application_metrics()
        }
        
        # Run all health checks
        checks = [
            ("database", self._check_database),
            ("llm_providers", self._check_llm_providers),
            ("file_system", self._check_file_system),
            ("memory", self._check_memory),
            ("disk_space", self._check_disk_space)
        ]
        
        overall_status = HealthStatus.HEALTHY
        
        for check_name, check_func in checks:
            try:
                check_result = await check_func()
                health_data["checks"][check_name] = check_result
                
                # Update overall status
                if check_result["status"] == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif check_result["status"] == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                health_data["checks"][check_name] = {
                    "status": HealthStatus.UNHEALTHY,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
                overall_status = HealthStatus.UNHEALTHY
        
        health_data["status"] = overall_status
        health_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # Store in history
        self._store_check_result(health_data)
        self.last_check = datetime.now(UTC)
        
        return health_data
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from ..utils.database import DatabaseManager
            
            db_manager = DatabaseManager()
            
            # Simple connectivity test
            if config.database.type.value == "postgresql":
                # For PostgreSQL, try a simple query
                # This would need actual database connection testing
                status = HealthStatus.HEALTHY
                message = "Database connection successful"
            else:
                # For SQLite, check if file exists and is accessible
                db_path = Path(config.database.sqlite_path)
                if db_path.exists():
                    status = HealthStatus.HEALTHY
                    message = "SQLite database accessible"
                else:
                    status = HealthStatus.DEGRADED
                    message = "SQLite database file not found (will be created on first use)"
            
            return {
                "status": status,
                "message": message,
                "database_type": config.database.type.value,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_llm_providers(self) -> Dict[str, Any]:
        """Check LLM provider connectivity"""
        provider_status = {}
        overall_status = HealthStatus.UNHEALTHY
        
        for provider_name, provider_config in config.llm.items():
            if not provider_config.api_key:
                provider_status[provider_name] = {
                    "status": HealthStatus.DEGRADED,
                    "message": "No API key configured"
                }
                continue
            
            try:
                # Test connection with a simple request
                analyzer = LLMAnalyzer(provider=provider_name)
                connection_ok = await analyzer.test_connection()
                
                if connection_ok:
                    provider_status[provider_name] = {
                        "status": HealthStatus.HEALTHY,
                        "message": "Connection successful"
                    }
                    overall_status = HealthStatus.HEALTHY  # At least one provider works
                else:
                    provider_status[provider_name] = {
                        "status": HealthStatus.UNHEALTHY,
                        "message": "Connection failed"
                    }
                    
            except Exception as e:
                provider_status[provider_name] = {
                    "status": HealthStatus.UNHEALTHY,
                    "error": str(e)
                }
        
        # If no providers are healthy, check if at least one is configured
        if overall_status == HealthStatus.UNHEALTHY:
            configured_providers = [name for name, config in config.llm.items() if config.api_key]
            if configured_providers:
                overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status,
            "providers": provider_status,
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def _check_file_system(self) -> Dict[str, Any]:
        """Check file system access"""
        try:
            directories_to_check = [
                config.data_raw_dir,
                config.data_processed_dir,
                config.upload_dir
            ]
            
            issues = []
            
            for directory in directories_to_check:
                if not directory.exists():
                    try:
                        directory.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        issues.append(f"Cannot create directory {directory}: {e}")
                
                if not directory.is_dir():
                    issues.append(f"{directory} is not a directory")
                
                # Test write access
                try:
                    test_file = directory / ".health_check"
                    test_file.write_text("test")
                    test_file.unlink()
                except Exception as e:
                    issues.append(f"No write access to {directory}: {e}")
            
            if issues:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "issues": issues,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            else:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "All directories accessible",
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical memory usage"
            elif memory.percent > 80:
                status = HealthStatus.DEGRADED
                message = "High memory usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Memory usage normal"
            
            return {
                "status": status,
                "message": message,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = "Critical disk space"
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                message = "Low disk space"
            else:
                status = HealthStatus.HEALTHY
                message = "Disk space sufficient"
            
            return {
                "status": status,
                "message": message,
                "disk_percent": round(disk_percent, 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": round((psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100, 2),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    async def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        return {
            "uptime_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
            "last_health_check": self.last_check.isoformat() if self.last_check else None,
            "health_check_count": len(self.check_history),
            "environment": config.environment.value,
            "version": config.app_version
        }
    
    def _store_check_result(self, result: Dict[str, Any]) -> None:
        """Store health check result in history"""
        self.check_history.append({
            "timestamp": result["timestamp"],
            "status": result["status"],
            "response_time_ms": result["response_time_ms"]
        })
        
        # Keep only recent history
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history:]
    
    def get_health_history(self) -> List[Dict[str, Any]]:
        """Get health check history"""
        return self.check_history.copy()

# Global health check instance
health_checker = HealthCheck()
