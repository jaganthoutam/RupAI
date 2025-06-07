"""
Enterprise MCP Payments - Monitoring Background Tasks

Background tasks for system health monitoring, performance tracking, and alerting.
Provides comprehensive monitoring of all system components and services.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from app.tasks.celery_app import app
from app.tasks.utils import async_task, get_db_session, handle_task_error, check_task_health
from app.services.monitoring_service import MonitoringService
from app.services.notification_service import NotificationService
from app.utils.monitoring import track_performance, log_event

logger = logging.getLogger(__name__)

@app.task(bind=True, name='app.tasks.monitoring_tasks.system_health_check')
@async_task
@track_performance
async def system_health_check(self) -> Dict[str, Any]:
    """Perform comprehensive system health check"""
    try:
        async with get_db_session() as session:
            monitoring_service = MonitoringService(session)
            notification_service = NotificationService()
            
            # Check various system components
            health_checks = {
                'database': await monitoring_service.check_database_health(),
                'redis': await monitoring_service.check_redis_health(),
                'rabbitmq': await monitoring_service.check_rabbitmq_health(),
                'external_apis': await monitoring_service.check_external_api_health(),
                'disk_space': await monitoring_service.check_disk_space(),
                'memory_usage': await monitoring_service.check_memory_usage(),
                'cpu_usage': await monitoring_service.check_cpu_usage(),
                'network': await monitoring_service.check_network_connectivity(),
                'tasks': await check_task_health()
            }
            
            # Calculate overall health score
            healthy_components = sum(
                1 for check in health_checks.values()
                if check.get('status') == 'healthy'
            )
            
            total_components = len(health_checks)
            health_score = (healthy_components / total_components) * 100
            
            # Determine overall status
            if health_score >= 95:
                overall_status = 'healthy'
            elif health_score >= 80:
                overall_status = 'warning'
            else:
                overall_status = 'critical'
            
            health_results = {
                'check_timestamp': datetime.utcnow().isoformat(),
                'overall_status': overall_status,
                'health_score': health_score,
                'healthy_components': healthy_components,
                'total_components': total_components,
                'component_checks': health_checks,
                'alerts': []
            }
            
            # Generate alerts for unhealthy components
            for component, check in health_checks.items():
                if check.get('status') != 'healthy':
                    alert = {
                        'component': component,
                        'status': check.get('status'),
                        'message': check.get('message', ''),
                        'severity': check.get('severity', 'medium')
                    }
                    health_results['alerts'].append(alert)
                    
                    # Send notification for critical issues
                    if check.get('severity') == 'critical':
                        await notification_service.send_system_alert(
                            component, check.get('message'), 'critical'
                        )
            
            # Store health check results
            await monitoring_service.store_health_check_results(health_results)
            
            log_event('system_health_checked', {
                'overall_status': overall_status,
                'health_score': health_score,
                'alerts_count': len(health_results['alerts'])
            })
            
            return health_results
            
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.monitoring_tasks.collect_performance_metrics')
@async_task
@track_performance
async def collect_performance_metrics(self) -> Dict[str, Any]:
    """Collect and store performance metrics"""
    try:
        async with get_db_session() as session:
            monitoring_service = MonitoringService(session)
            
            # Collect various performance metrics
            metrics = {
                'api_performance': await monitoring_service.collect_api_metrics(),
                'database_performance': await monitoring_service.collect_database_metrics(),
                'queue_performance': await monitoring_service.collect_queue_metrics(),
                'payment_metrics': await monitoring_service.collect_payment_metrics(),
                'user_activity': await monitoring_service.collect_user_activity_metrics(),
                'system_resources': await monitoring_service.collect_system_resource_metrics()
            }
            
            # Calculate performance scores
            performance_scores = await monitoring_service.calculate_performance_scores(metrics)
            
            metrics_results = {
                'collection_timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'performance_scores': performance_scores,
                'overall_performance': sum(performance_scores.values()) / len(performance_scores)
            }
            
            # Store metrics
            await monitoring_service.store_performance_metrics(metrics_results)
            
            log_event('performance_metrics_collected', {
                'overall_performance': metrics_results['overall_performance'],
                'api_performance': performance_scores.get('api_performance', 0),
                'db_performance': performance_scores.get('database_performance', 0)
            })
            
            return metrics_results
            
    except Exception as e:
        logger.error(f"Performance metrics collection failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.monitoring_tasks.check_service_availability')
@async_task
@track_performance
async def check_service_availability(self) -> Dict[str, Any]:
    """Check availability of all services and endpoints"""
    try:
        async with get_db_session() as session:
            monitoring_service = MonitoringService(session)
            
            # Check internal services
            service_checks = {
                'analytics_service': await monitoring_service.check_analytics_service(),
                'payment_service': await monitoring_service.check_payment_service(),
                'wallet_service': await monitoring_service.check_wallet_service(),
                'compliance_service': await monitoring_service.check_compliance_service(),
                'notification_service': await monitoring_service.check_notification_service(),
                'mcp_server': await monitoring_service.check_mcp_server()
            }
            
            # Check external dependencies
            external_checks = {
                'stripe_api': await monitoring_service.check_stripe_connectivity(),
                'razorpay_api': await monitoring_service.check_razorpay_connectivity(),
                'email_service': await monitoring_service.check_email_service(),
                'sms_service': await monitoring_service.check_sms_service()
            }
            
            # Calculate availability metrics
            all_checks = {**service_checks, **external_checks}
            available_services = sum(
                1 for check in all_checks.values()
                if check.get('available', False)
            )
            
            total_services = len(all_checks)
            availability_percentage = (available_services / total_services) * 100
            
            availability_results = {
                'check_timestamp': datetime.utcnow().isoformat(),
                'availability_percentage': availability_percentage,
                'available_services': available_services,
                'total_services': total_services,
                'internal_services': service_checks,
                'external_services': external_checks,
                'unavailable_services': [
                    name for name, check in all_checks.items()
                    if not check.get('available', False)
                ]
            }
            
            # Store availability data
            await monitoring_service.store_availability_metrics(availability_results)
            
            log_event('service_availability_checked', {
                'availability_percentage': availability_percentage,
                'available_services': available_services,
                'total_services': total_services
            })
            
            return availability_results
            
    except Exception as e:
        logger.error(f"Service availability check failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.monitoring_tasks.generate_monitoring_report')
@async_task
@track_performance
async def generate_monitoring_report(self, period_hours: int = 24) -> Dict[str, Any]:
    """Generate comprehensive monitoring report"""
    try:
        async with get_db_session() as session:
            monitoring_service = MonitoringService(session)
            
            # Define time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Generate report sections
            health_summary = await monitoring_service.generate_health_summary(start_time, end_time)
            performance_summary = await monitoring_service.generate_performance_summary(start_time, end_time)
            availability_summary = await monitoring_service.generate_availability_summary(start_time, end_time)
            incident_summary = await monitoring_service.generate_incident_summary(start_time, end_time)
            
            monitoring_report = {
                'report_period_hours': period_hours,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'health_summary': health_summary,
                'performance_summary': performance_summary,
                'availability_summary': availability_summary,
                'incident_summary': incident_summary,
                'key_metrics': {
                    'avg_health_score': health_summary.get('avg_health_score', 0),
                    'avg_performance_score': performance_summary.get('avg_performance_score', 0),
                    'avg_availability': availability_summary.get('avg_availability', 0),
                    'total_incidents': incident_summary.get('total_incidents', 0)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Store monitoring report
            await monitoring_service.store_monitoring_report(monitoring_report)
            
            log_event('monitoring_report_generated', {
                'period_hours': period_hours,
                'avg_health_score': health_summary.get('avg_health_score', 0),
                'total_incidents': incident_summary.get('total_incidents', 0)
            })
            
            return monitoring_report
            
    except Exception as e:
        logger.error(f"Monitoring report generation failed: {e}")
        await handle_task_error(self, e, {'period_hours': period_hours})
        raise

@app.task(bind=True, name='app.tasks.monitoring_tasks.cleanup_old_monitoring_data')
@async_task
@track_performance
async def cleanup_old_monitoring_data(self, retention_days: int = 90) -> Dict[str, Any]:
    """Clean up old monitoring data beyond retention period"""
    try:
        async with get_db_session() as session:
            monitoring_service = MonitoringService(session)
            
            # Clean up different types of monitoring data
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            cleanup_results = {
                'health_checks': await monitoring_service.cleanup_old_health_checks(cutoff_date),
                'performance_metrics': await monitoring_service.cleanup_old_performance_metrics(cutoff_date),
                'availability_data': await monitoring_service.cleanup_old_availability_data(cutoff_date),
                'monitoring_reports': await monitoring_service.cleanup_old_monitoring_reports(cutoff_date)
            }
            
            # Calculate total cleanup statistics
            total_deleted = sum(
                result.get('records_deleted', 0) for result in cleanup_results.values()
            )
            
            cleanup_summary = {
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                'cleanup_details': cleanup_results,
                'total_records_deleted': total_deleted,
                'cleanup_timestamp': datetime.utcnow().isoformat()
            }
            
            log_event('monitoring_data_cleaned', {
                'retention_days': retention_days,
                'records_deleted': total_deleted
            })
            
            return cleanup_summary
            
    except Exception as e:
        logger.error(f"Monitoring data cleanup failed: {e}")
        await handle_task_error(self, e, {'retention_days': retention_days})
        raise 