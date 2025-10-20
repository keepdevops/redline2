#!/usr/bin/env python3
"""
REDLINE Background Task Manager
Manages asynchronous task processing using Celery.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import uuid

try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    Celery = None
    AsyncResult = None
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages background task processing."""
    
    def __init__(self, app=None):
        """Initialize task manager."""
        self.app = app
        self.celery_app = None
        self.task_registry = {}
        
        if CELERY_AVAILABLE:
            self._initialize_celery()
        else:
            logger.warning("Celery not available. Background tasks will run synchronously.")
    
    def _initialize_celery(self):
        """Initialize Celery application."""
        try:
            # Create Celery app
            self.celery_app = Celery('redline')
            
            # Configure Celery
            self.celery_app.conf.update(
                broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=30 * 60,  # 30 minutes
                task_soft_time_limit=25 * 60,  # 25 minutes
                worker_prefetch_multiplier=1,
                task_acks_late=True,
                worker_disable_rate_limits=False,
                task_routes={
                    'redline.background.tasks.*': {'queue': 'redline_tasks'},
                },
                task_default_queue='redline_tasks',
                task_default_exchange='redline_tasks',
                task_default_exchange_type='direct',
                task_default_routing_key='redline_tasks',
            )
            
            # Import tasks
            from . import tasks
            
            logger.info("Celery initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Celery: {str(e)}")
            self.celery_app = None
    
    def submit_task(self, task_name: str, args: tuple = (), kwargs: dict = None, 
                   queue: str = None, priority: int = 5) -> str:
        """Submit a background task."""
        if kwargs is None:
            kwargs = {}
        
        task_id = str(uuid.uuid4())
        
        if self.celery_app and CELERY_AVAILABLE:
            try:
                # Submit task to Celery
                task = self.celery_app.send_task(
                    task_name,
                    args=args,
                    kwargs=kwargs,
                    queue=queue or 'redline_tasks',
                    priority=priority
                )
                
                # Store task info
                task_info = {
                    'task_id': task.id,
                    'task_name': task_name,
                    'args': args,
                    'kwargs': kwargs,
                    'status': 'PENDING',
                    'submitted_at': datetime.utcnow().isoformat(),
                    'queue': queue or 'redline_tasks',
                    'priority': priority
                }
                
                self.task_registry[task.id] = task_info
                
                logger.info(f"Submitted task {task_name} with ID {task.id}")
                return task.id
                
            except Exception as e:
                logger.error(f"Failed to submit task {task_name}: {str(e)}")
                # Fallback to synchronous execution
                return self._execute_sync(task_name, args, kwargs)
        else:
            # Fallback to synchronous execution
            return self._execute_sync(task_name, args, kwargs)
    
    def _execute_sync(self, task_name: str, args: tuple, kwargs: dict) -> str:
        """Execute task synchronously as fallback."""
        task_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Executing task {task_name} synchronously")
            
            # Import and execute task function
            from . import tasks
            task_func = getattr(tasks, task_name, None)
            
            if task_func:
                result = task_func(*args, **kwargs)
                
                # Store result
                task_info = {
                    'task_id': task_id,
                    'task_name': task_name,
                    'args': args,
                    'kwargs': kwargs,
                    'status': 'SUCCESS',
                    'submitted_at': datetime.utcnow().isoformat(),
                    'completed_at': datetime.utcnow().isoformat(),
                    'result': result,
                    'execution_mode': 'synchronous'
                }
                
                self.task_registry[task_id] = task_info
                
                logger.info(f"Task {task_name} completed synchronously")
                return task_id
            else:
                raise ValueError(f"Task function {task_name} not found")
                
        except Exception as e:
            logger.error(f"Failed to execute task {task_name} synchronously: {str(e)}")
            
            # Store error
            task_info = {
                'task_id': task_id,
                'task_name': task_name,
                'args': args,
                'kwargs': kwargs,
                'status': 'FAILURE',
                'submitted_at': datetime.utcnow().isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'error': str(e),
                'execution_mode': 'synchronous'
            }
            
            self.task_registry[task_id] = task_info
            return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and result."""
        if task_id in self.task_registry:
            task_info = self.task_registry[task_id].copy()
            
            # Update status from Celery if available
            if self.celery_app and CELERY_AVAILABLE:
                try:
                    result = AsyncResult(task_id, app=self.celery_app)
                    
                    if result.state == 'PENDING':
                        task_info['status'] = 'PENDING'
                    elif result.state == 'PROGRESS':
                        task_info['status'] = 'PROGRESS'
                        task_info['progress'] = result.info
                    elif result.state == 'SUCCESS':
                        task_info['status'] = 'SUCCESS'
                        task_info['result'] = result.result
                        task_info['completed_at'] = datetime.utcnow().isoformat()
                    elif result.state == 'FAILURE':
                        task_info['status'] = 'FAILURE'
                        task_info['error'] = str(result.info)
                        task_info['completed_at'] = datetime.utcnow().isoformat()
                    
                    # Update registry
                    self.task_registry[task_id] = task_info
                    
                except Exception as e:
                    logger.error(f"Failed to get task status from Celery: {str(e)}")
            
            return task_info
        else:
            return {'error': 'Task not found'}
    
    def get_task_result(self, task_id: str) -> Any:
        """Get task result."""
        status = self.get_task_status(task_id)
        
        if status.get('status') == 'SUCCESS':
            return status.get('result')
        elif status.get('status') == 'FAILURE':
            raise Exception(status.get('error', 'Task failed'))
        else:
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if self.celery_app and CELERY_AVAILABLE:
            try:
                self.celery_app.control.revoke(task_id, terminate=True)
                
                # Update registry
                if task_id in self.task_registry:
                    self.task_registry[task_id]['status'] = 'REVOKED'
                    self.task_registry[task_id]['completed_at'] = datetime.utcnow().isoformat()
                
                logger.info(f"Task {task_id} cancelled")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cancel task {task_id}: {str(e)}")
                return False
        else:
            return False
    
    def list_tasks(self, status_filter: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List tasks with optional status filter."""
        tasks = list(self.task_registry.values())
        
        if status_filter:
            tasks = [t for t in tasks if t.get('status') == status_filter]
        
        # Sort by submitted_at descending
        tasks.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        return tasks[:limit]
    
    def cleanup_old_tasks(self, days: int = 7):
        """Clean up old completed tasks."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        tasks_to_remove = []
        for task_id, task_info in self.task_registry.items():
            submitted_at = task_info.get('submitted_at', '')
            if submitted_at:
                try:
                    submitted_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    if submitted_date < cutoff_date:
                        tasks_to_remove.append(task_id)
                except ValueError:
                    continue
        
        for task_id in tasks_to_remove:
            del self.task_registry[task_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        if self.celery_app and CELERY_AVAILABLE:
            try:
                inspect = self.celery_app.control.inspect()
                
                stats = {
                    'active_tasks': len(inspect.active() or {}),
                    'scheduled_tasks': len(inspect.scheduled() or {}),
                    'reserved_tasks': len(inspect.reserved() or {}),
                    'registered_tasks': len(inspect.registered() or {}),
                    'worker_stats': inspect.stats()
                }
                
                return stats
                
            except Exception as e:
                logger.error(f"Failed to get queue stats: {str(e)}")
                return {'error': str(e)}
        else:
            return {
                'active_tasks': 0,
                'scheduled_tasks': 0,
                'reserved_tasks': 0,
                'registered_tasks': 0,
                'worker_stats': {},
                'mode': 'synchronous'
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check background task system health."""
        health = {
            'celery_available': CELERY_AVAILABLE,
            'celery_connected': False,
            'queue_stats': {},
            'registry_size': len(self.task_registry),
            'status': 'healthy'
        }
        
        if self.celery_app and CELERY_AVAILABLE:
            try:
                # Test connection
                self.celery_app.control.ping()
                health['celery_connected'] = True
                health['queue_stats'] = self.get_queue_stats()
                
            except Exception as e:
                health['status'] = 'unhealthy'
                health['error'] = str(e)
                logger.error(f"Celery health check failed: {str(e)}")
        
        return health

# Global task manager instance
task_manager = TaskManager()
