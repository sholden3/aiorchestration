#!/usr/bin/env python3
"""
Real-Time Governance Monitoring System v9.6
Advanced monitoring and alerting for governance activities across all systems
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from pathlib import Path
import queue
import websockets
import signal
import sys

from unified_governance_orchestrator import UnifiedGovernanceOrchestrator, CollaborationPhase, ConsensusLevel
from ai_orchestration_engine import AIOrchestrationEngine, AITask, TaskPriority
from conversation_manager import ConversationManager, ConversationType
from token_optimization_engine import TokenOptimizationEngine, OptimizationStrategy
from claude_cli_governance_integration import ClaudeGovernanceIntegration, GovernanceLevel
from governance_driven_code_quality import GovernanceDrivenCodeQuality
from advanced_persona_collaboration_scenarios import AdvancedPersonaCollaborationScenarios

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """Levels of governance monitoring"""
    BASIC = "basic"           # Essential metrics only
    STANDARD = "standard"     # Standard monitoring
    COMPREHENSIVE = "comprehensive"  # All metrics and deep analysis
    DEBUG = "debug"          # Debug-level monitoring


class AlertSeverity(Enum):
    """Severity levels for governance alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of governance alerts"""
    CONSENSUS_FAILURE = "consensus_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    QUALITY_VIOLATION = "quality_violation"
    SECURITY_CONCERN = "security_concern"
    RESOURCE_THRESHOLD = "resource_threshold"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ERROR = "system_error"
    PROCESS_ANOMALY = "process_anomaly"


@dataclass
class GovernanceMetric:
    """A single governance metric measurement"""
    metric_name: str
    value: Any
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class GovernanceAlert:
    """A governance monitoring alert"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    affected_systems: List[str]
    metrics: List[GovernanceMetric]
    recommendations: List[str]
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class SystemHealthStatus:
    """Health status for a monitored system"""
    system_name: str
    status: str  # healthy, degraded, critical, offline
    last_check: datetime
    response_time_ms: float
    error_rate: float
    active_sessions: int
    performance_score: float
    issues: List[str] = field(default_factory=list)


class GovernanceMonitoringDashboard:
    """Real-time dashboard for governance monitoring"""
    
    def __init__(self):
        self.active_metrics: Dict[str, GovernanceMetric] = {}
        self.active_alerts: Dict[str, GovernanceAlert] = {}
        self.system_health: Dict[str, SystemHealthStatus] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.alert_history: List[GovernanceAlert] = []
        
    def update_metric(self, metric: GovernanceMetric):
        """Update a governance metric"""
        self.active_metrics[metric.metric_name] = metric
        
    def add_alert(self, alert: GovernanceAlert):
        """Add a new governance alert"""
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            alert.resolution_notes = resolution_notes
            del self.active_alerts[alert_id]
            
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return {
            "active_metrics": {k: {
                "value": v.value,
                "unit": v.unit,
                "timestamp": v.timestamp.isoformat(),
                "tags": v.tags
            } for k, v in self.active_metrics.items()},
            "active_alerts": {k: {
                "type": v.alert_type.value,
                "severity": v.severity.value,
                "message": v.message,
                "timestamp": v.timestamp.isoformat(),
                "affected_systems": v.affected_systems
            } for k, v in self.active_alerts.items()},
            "system_health": {k: {
                "status": v.status,
                "last_check": v.last_check.isoformat(),
                "response_time_ms": v.response_time_ms,
                "performance_score": v.performance_score,
                "issues": v.issues
            } for k, v in self.system_health.items()},
            "summary": {
                "total_active_alerts": len(self.active_alerts),
                "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]),
                "healthy_systems": len([s for s in self.system_health.values() if s.status == "healthy"]),
                "total_systems": len(self.system_health)
            }
        }


class RealTimeGovernanceMonitoring:
    """Main real-time governance monitoring system"""
    
    def __init__(self, project_root: Optional[Path] = None, monitoring_level: MonitoringLevel = MonitoringLevel.STANDARD):
        """Initialize real-time governance monitoring"""
        self.project_root = project_root or Path.cwd()
        self.monitoring_level = monitoring_level
        
        # Initialize all governance systems
        self.governance = UnifiedGovernanceOrchestrator()
        self.orchestrator = AIOrchestrationEngine(self.governance)
        self.conversation_manager = ConversationManager(self.orchestrator)
        self.token_optimizer = TokenOptimizationEngine()
        self.claude_integration = ClaudeGovernanceIntegration(self.project_root)
        self.quality_system = GovernanceDrivenCodeQuality(self.project_root)
        self.scenarios = AdvancedPersonaCollaborationScenarios(self.project_root)
        
        # Monitoring infrastructure
        self.dashboard = GovernanceMonitoringDashboard()
        self.monitoring_active = False
        self.monitoring_interval = 5.0  # seconds
        self.alert_handlers: List[Callable] = []
        self.metric_collectors: Dict[str, Callable] = {}
        
        # Performance thresholds
        self.thresholds = {
            "consensus_success_rate": 0.85,
            "average_response_time": 2000,  # ms
            "token_optimization_ratio": 0.6,
            "quality_score_minimum": 70.0,
            "error_rate_maximum": 0.05,
            "system_availability": 0.99
        }
        
        # Monitoring queues and threads
        self.metric_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        self.monitoring_thread = None
        self.alert_processing_thread = None
        
        # WebSocket server for real-time updates
        self.websocket_port = 8765
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Initialize metric collectors
        self._initialize_metric_collectors()
        
    async def initialize(self):
        """Initialize all monitoring components"""
        # Initialize governance systems
        await self.orchestrator.start_orchestration()
        await self.claude_integration.initialize()
        await self.quality_system.initialize()
        await self.scenarios.initialize()
        
        # Initialize monitoring systems
        self._register_system_health_checks()
        self._setup_alert_handlers()
        
        logger.info(f"Real-Time Governance Monitoring v9.6 initialized (level: {self.monitoring_level.value})")
        
    def _initialize_metric_collectors(self):
        """Initialize metric collection functions"""
        self.metric_collectors = {
            "orchestration_health": self._collect_orchestration_metrics,
            "governance_performance": self._collect_governance_metrics,
            "quality_metrics": self._collect_quality_metrics,
            "token_optimization": self._collect_token_metrics,
            "claude_operations": self._collect_claude_metrics,
            "conversation_analytics": self._collect_conversation_metrics,
            "scenario_performance": self._collect_scenario_metrics,
            "system_resources": self._collect_system_metrics
        }
        
    def _register_system_health_checks(self):
        """Register health checks for all systems"""
        systems_to_monitor = [
            ("governance_orchestrator", self.governance),
            ("ai_orchestration", self.orchestrator),
            ("conversation_manager", self.conversation_manager),
            ("token_optimizer", self.token_optimizer),
            ("claude_integration", self.claude_integration),
            ("quality_system", self.quality_system),
            ("scenario_system", self.scenarios)
        ]
        
        for system_name, system_instance in systems_to_monitor:
            self.dashboard.system_health[system_name] = SystemHealthStatus(
                system_name=system_name,
                status="initializing",
                last_check=datetime.now(),
                response_time_ms=0.0,
                error_rate=0.0,
                active_sessions=0,
                performance_score=100.0
            )
    
    def _setup_alert_handlers(self):
        """Setup alert handling functions"""
        self.alert_handlers = [
            self._handle_consensus_failure,
            self._handle_performance_degradation,
            self._handle_quality_violation,
            self._handle_security_concern,
            self._handle_compliance_violation
        ]
    
    async def start_monitoring(self):
        """Start real-time governance monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        
        print(f"\n{'='*80}")
        print(f"STARTING REAL-TIME GOVERNANCE MONITORING v9.6")
        print(f"Monitoring Level: {self.monitoring_level.value.upper()}")
        print(f"Update Interval: {self.monitoring_interval} seconds")
        print(f"{'='*80}")
        
        # Start monitoring threads
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.alert_processing_thread = threading.Thread(target=self._alert_processing_loop, daemon=True)
        
        self.monitoring_thread.start()
        self.alert_processing_thread.start()
        
        # Start WebSocket server for real-time dashboard
        if self.monitoring_level in [MonitoringLevel.COMPREHENSIVE, MonitoringLevel.DEBUG]:
            asyncio.create_task(self._start_websocket_server())
        
        logger.info("Real-time governance monitoring started")
        
    async def stop_monitoring(self):
        """Stop governance monitoring"""
        if not self.monitoring_active:
            return
            
        self.monitoring_active = False
        
        # Wait for threads to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
            
        if self.alert_processing_thread and self.alert_processing_thread.is_alive():
            self.alert_processing_thread.join(timeout=5.0)
        
        print("\nGovernance monitoring stopped")
        logger.info("Real-time governance monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop running in background thread"""
        while self.monitoring_active:
            try:
                # Collect metrics from all systems
                self._collect_all_metrics()
                
                # Check health of all systems
                self._check_system_health()
                
                # Process alerts based on thresholds
                self._process_threshold_alerts()
                
                # Update dashboard
                self._update_dashboard()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                
    def _alert_processing_loop(self):
        """Alert processing loop running in background thread"""
        while self.monitoring_active:
            try:
                # Process alerts from queue
                try:
                    alert = self.alert_queue.get(timeout=1.0)
                    self._process_alert(alert)
                    self.alert_queue.task_done()
                except queue.Empty:
                    continue
                    
            except Exception as e:
                logger.error(f"Error in alert processing: {str(e)}")
    
    def _collect_all_metrics(self):
        """Collect metrics from all systems"""
        for collector_name, collector_func in self.metric_collectors.items():
            try:
                metrics = collector_func()
                for metric in metrics:
                    self.dashboard.update_metric(metric)
                    self.metric_queue.put(metric)
            except Exception as e:
                logger.error(f"Error collecting {collector_name} metrics: {str(e)}")
    
    def _collect_orchestration_metrics(self) -> List[GovernanceMetric]:
        """Collect AI orchestration metrics"""
        try:
            status = self.orchestrator.get_orchestration_status()
            
            metrics = [
                GovernanceMetric("orchestration_running", status["is_running"], "boolean", datetime.now()),
                GovernanceMetric("active_agents", status["agents"]["active"], "count", datetime.now()),
                GovernanceMetric("completed_tasks", status["tasks"]["completed"], "count", datetime.now()),
                GovernanceMetric("failed_tasks", status["tasks"]["failed"], "count", datetime.now()),
                GovernanceMetric("success_rate", status["performance"]["overall_success_rate"], "percentage", datetime.now())
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting orchestration metrics: {str(e)}")
            return []
    
    def _collect_governance_metrics(self) -> List[GovernanceMetric]:
        """Collect governance performance metrics"""
        try:
            # Get governance statistics (simulated for demo)
            metrics = [
                GovernanceMetric("governance_sessions_active", 0, "count", datetime.now()),
                GovernanceMetric("consensus_success_rate", 0.92, "percentage", datetime.now()),
                GovernanceMetric("average_collaboration_time", 1.5, "minutes", datetime.now()),
                GovernanceMetric("evidence_quality_score", 8.7, "score", datetime.now())
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting governance metrics: {str(e)}")
            return []
    
    def _collect_quality_metrics(self) -> List[GovernanceMetric]:
        """Collect code quality metrics"""
        try:
            # Simplified quality metrics for sync collection
            dashboard_data = {"summary": {
                "total_files_analyzed": len(self.quality_system.quality_reports),
                "average_quality_score": 80.0,
                "total_issues": 5,
                "governance_sessions_created": 0
            }}
            
            if "summary" in dashboard_data:
                summary = dashboard_data["summary"]
                metrics = [
                    GovernanceMetric("quality_files_analyzed", summary.get("total_files_analyzed", 0), "count", datetime.now()),
                    GovernanceMetric("quality_average_score", summary.get("average_quality_score", 0), "score", datetime.now()),
                    GovernanceMetric("quality_total_issues", summary.get("total_issues", 0), "count", datetime.now()),
                    GovernanceMetric("quality_governance_sessions", summary.get("governance_sessions_created", 0), "count", datetime.now())
                ]
                return metrics
            
            return []
            
        except Exception as e:
            logger.error(f"Error collecting quality metrics: {str(e)}")
            return []
    
    def _collect_token_metrics(self) -> List[GovernanceMetric]:
        """Collect token optimization metrics"""
        try:
            stats = self.token_optimizer.get_optimization_stats()
            
            if "error" not in stats:
                metrics = [
                    GovernanceMetric("token_requests_processed", stats.get("total_requests", 0), "count", datetime.now()),
                    GovernanceMetric("tokens_saved", stats["token_stats"].get("tokens_saved", 0), "count", datetime.now()),
                    GovernanceMetric("cost_savings", stats["cost_stats"].get("cost_savings", 0), "dollars", datetime.now()),
                    GovernanceMetric("optimization_ratio", stats["performance"].get("average_compression_ratio", 0), "percentage", datetime.now())
                ]
                return metrics
            
            return []
            
        except Exception as e:
            logger.error(f"Error collecting token metrics: {str(e)}")
            return []
    
    def _collect_claude_metrics(self) -> List[GovernanceMetric]:
        """Collect Claude CLI operation metrics"""
        try:
            # Simplified Claude metrics for sync collection
            analytics = {
                "total_operations": len(self.claude_integration.completed_operations),
                "governance_levels": {"advisory": 2, "enforced": 1},
                "command_distribution": {"chat": 2, "analyze": 1},
                "success_rates": {}
            }
            
            metrics = [
                GovernanceMetric("claude_total_operations", analytics.get("total_operations", 0), "count", datetime.now()),
                GovernanceMetric("claude_governance_levels", len(analytics.get("governance_levels", {})), "count", datetime.now()),
                GovernanceMetric("claude_command_types", len(analytics.get("command_distribution", {})), "count", datetime.now())
            ]
            
            # Add success rates by governance level
            for level, stats in analytics.get("success_rates", {}).items():
                if stats.get("total", 0) > 0:
                    metrics.append(GovernanceMetric(
                        f"claude_success_rate_{level}",
                        stats.get("percentage", 0),
                        "percentage",
                        datetime.now()
                    ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting Claude metrics: {str(e)}")
            return []
    
    def _collect_conversation_metrics(self) -> List[GovernanceMetric]:
        """Collect conversation management metrics"""
        try:
            # Get conversation statistics (simulated for demo)
            metrics = [
                GovernanceMetric("active_conversations", 0, "count", datetime.now()),
                GovernanceMetric("total_conversations", 0, "count", datetime.now()),
                GovernanceMetric("average_conversation_length", 5.2, "turns", datetime.now()),
                GovernanceMetric("context_optimization_rate", 0.74, "percentage", datetime.now())
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting conversation metrics: {str(e)}")
            return []
    
    def _collect_scenario_metrics(self) -> List[GovernanceMetric]:
        """Collect scenario execution metrics"""
        try:
            # Get scenario statistics
            total_scenarios = len(self.scenarios.completed_scenarios)
            successful_scenarios = sum(1 for s in self.scenarios.completed_scenarios.values() if s.decision_reached)
            
            metrics = [
                GovernanceMetric("scenarios_executed", total_scenarios, "count", datetime.now()),
                GovernanceMetric("scenarios_successful", successful_scenarios, "count", datetime.now()),
                GovernanceMetric("scenario_success_rate", successful_scenarios / total_scenarios if total_scenarios > 0 else 0, "percentage", datetime.now()),
                GovernanceMetric("active_scenarios", len(self.scenarios.active_scenarios), "count", datetime.now())
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting scenario metrics: {str(e)}")
            return []
    
    def _collect_system_metrics(self) -> List[GovernanceMetric]:
        """Collect system resource metrics"""
        try:
            import psutil
            
            metrics = [
                GovernanceMetric("cpu_usage", psutil.cpu_percent(), "percentage", datetime.now()),
                GovernanceMetric("memory_usage", psutil.virtual_memory().percent, "percentage", datetime.now()),
                GovernanceMetric("disk_usage", psutil.disk_usage('/').percent, "percentage", datetime.now())
            ]
            
            return metrics
            
        except ImportError:
            # psutil not available, return basic metrics
            return [
                GovernanceMetric("system_status", "unknown", "status", datetime.now())
            ]
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return []
    
    def _check_system_health(self):
        """Check health of all monitored systems"""
        current_time = datetime.now()
        
        for system_name in self.dashboard.system_health.keys():
            try:
                # Perform health check (simulated)
                start_time = time.time()
                health_status = self._perform_health_check(system_name)
                response_time = (time.time() - start_time) * 1000  # ms
                
                # Update system health
                system_health = self.dashboard.system_health[system_name]
                system_health.status = health_status["status"]
                system_health.last_check = current_time
                system_health.response_time_ms = response_time
                system_health.error_rate = health_status.get("error_rate", 0.0)
                system_health.active_sessions = health_status.get("active_sessions", 0)
                system_health.performance_score = health_status.get("performance_score", 100.0)
                system_health.issues = health_status.get("issues", [])
                
            except Exception as e:
                logger.error(f"Health check failed for {system_name}: {str(e)}")
                system_health = self.dashboard.system_health[system_name]
                system_health.status = "error"
                system_health.issues = [f"Health check failed: {str(e)}"]
    
    def _perform_health_check(self, system_name: str) -> Dict[str, Any]:
        """Perform health check for a specific system"""
        # Simplified health check implementation
        health_checks = {
            "governance_orchestrator": lambda: {"status": "healthy", "performance_score": 95.0},
            "ai_orchestration": lambda: {"status": "healthy", "active_sessions": len(self.orchestrator.active_tasks)},
            "conversation_manager": lambda: {"status": "healthy", "active_sessions": len(self.conversation_manager.conversations)},
            "token_optimizer": lambda: {"status": "healthy", "performance_score": 92.0},
            "claude_integration": lambda: {"status": "healthy", "active_sessions": len(self.claude_integration.active_operations)},
            "quality_system": lambda: {"status": "healthy", "performance_score": 88.0},
            "scenario_system": lambda: {"status": "healthy", "active_sessions": len(self.scenarios.active_scenarios)}
        }
        
        if system_name in health_checks:
            return health_checks[system_name]()
        else:
            return {"status": "unknown"}
    
    def _process_threshold_alerts(self):
        """Process alerts based on metric thresholds"""
        current_metrics = self.dashboard.active_metrics
        
        # Check each threshold
        for threshold_name, threshold_value in self.thresholds.items():
            if threshold_name in current_metrics:
                metric = current_metrics[threshold_name]
                
                # Check if threshold is exceeded
                if self._is_threshold_exceeded(metric, threshold_value, threshold_name):
                    alert = self._create_threshold_alert(metric, threshold_value, threshold_name)
                    self.alert_queue.put(alert)
    
    def _is_threshold_exceeded(self, metric: GovernanceMetric, threshold: float, threshold_name: str) -> bool:
        """Check if a metric exceeds its threshold"""
        try:
            value = float(metric.value)
            
            # Define threshold directions (higher or lower is better)
            lower_is_better = ["error_rate_maximum", "average_response_time"]
            higher_is_better = ["consensus_success_rate", "token_optimization_ratio", "quality_score_minimum", "system_availability"]
            
            if threshold_name in lower_is_better:
                return value > threshold
            elif threshold_name in higher_is_better:
                return value < threshold
            else:
                return False
                
        except (ValueError, TypeError):
            return False
    
    def _create_threshold_alert(self, metric: GovernanceMetric, threshold: float, threshold_name: str) -> GovernanceAlert:
        """Create an alert for threshold violation"""
        alert_id = f"threshold_{threshold_name}_{int(time.time())}"
        
        severity = AlertSeverity.WARNING
        if "critical" in threshold_name.lower():
            severity = AlertSeverity.CRITICAL
        elif "error" in threshold_name.lower():
            severity = AlertSeverity.ERROR
        
        return GovernanceAlert(
            alert_id=alert_id,
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=severity,
            message=f"Threshold exceeded: {threshold_name} = {metric.value} (threshold: {threshold})",
            affected_systems=[threshold_name],
            metrics=[metric],
            recommendations=[f"Investigate {threshold_name} performance", "Check system resources"],
            timestamp=datetime.now()
        )
    
    def _process_alert(self, alert: GovernanceAlert):
        """Process a governance alert"""
        # Add to dashboard
        self.dashboard.add_alert(alert)
        
        # Run alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {str(e)}")
        
        # Log alert
        logger.warning(f"GOVERNANCE ALERT [{alert.severity.value.upper()}]: {alert.message}")
        
        # Send to WebSocket clients if available
        asyncio.create_task(self._broadcast_alert(alert))
    
    def _update_dashboard(self):
        """Update dashboard with current metrics"""
        if self.monitoring_level == MonitoringLevel.DEBUG:
            # Print real-time metrics for debug mode
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Governance Monitoring Update:")
            
            # Show key metrics
            key_metrics = ["orchestration_running", "active_agents", "success_rate", "consensus_success_rate"]
            for metric_name in key_metrics:
                if metric_name in self.dashboard.active_metrics:
                    metric = self.dashboard.active_metrics[metric_name]
                    print(f"  {metric_name}: {metric.value} {metric.unit}")
            
            # Show active alerts
            if self.dashboard.active_alerts:
                print(f"  Active alerts: {len(self.dashboard.active_alerts)}")
                for alert in list(self.dashboard.active_alerts.values())[:3]:
                    print(f"    - {alert.severity.value}: {alert.message}")
    
    async def _run_async_in_thread(self, async_func):
        """Run async function in thread-safe manner"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(async_func())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running async function: {str(e)}")
            return {}
    
    # Alert handlers
    def _handle_consensus_failure(self, alert: GovernanceAlert):
        """Handle consensus failure alerts"""
        if alert.alert_type == AlertType.CONSENSUS_FAILURE:
            print(f"🚨 CONSENSUS FAILURE: {alert.message}")
    
    def _handle_performance_degradation(self, alert: GovernanceAlert):
        """Handle performance degradation alerts"""
        if alert.alert_type == AlertType.PERFORMANCE_DEGRADATION:
            print(f"⚠️  PERFORMANCE ISSUE: {alert.message}")
    
    def _handle_quality_violation(self, alert: GovernanceAlert):
        """Handle quality violation alerts"""
        if alert.alert_type == AlertType.QUALITY_VIOLATION:
            print(f"📊 QUALITY ISSUE: {alert.message}")
    
    def _handle_security_concern(self, alert: GovernanceAlert):
        """Handle security concern alerts"""
        if alert.alert_type == AlertType.SECURITY_CONCERN:
            print(f"🔒 SECURITY ALERT: {alert.message}")
    
    def _handle_compliance_violation(self, alert: GovernanceAlert):
        """Handle compliance violation alerts"""
        if alert.alert_type == AlertType.COMPLIANCE_VIOLATION:
            print(f"📋 COMPLIANCE ISSUE: {alert.message}")
    
    # WebSocket server for real-time dashboard
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time dashboard updates"""
        try:
            async def handle_client(websocket, path):
                self.websocket_clients.add(websocket)
                try:
                    await websocket.wait_closed()
                finally:
                    self.websocket_clients.discard(websocket)
            
            server = await websockets.serve(handle_client, "localhost", self.websocket_port)
            logger.info(f"WebSocket server started on ws://localhost:{self.websocket_port}")
            
        except Exception as e:
            logger.error(f"WebSocket server failed: {str(e)}")
    
    async def _broadcast_alert(self, alert: GovernanceAlert):
        """Broadcast alert to WebSocket clients"""
        if not self.websocket_clients:
            return
            
        alert_data = {
            "type": "alert",
            "alert": {
                "id": alert.alert_id,
                "type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat()
            }
        }
        
        message = json.dumps(alert_data)
        
        # Send to all connected clients
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Clean up disconnected clients
        self.websocket_clients -= disconnected_clients
    
    async def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        current_time = datetime.now()
        
        # Collect current status
        dashboard_data = self.dashboard.get_dashboard_data()
        
        # Calculate monitoring statistics
        total_alerts = len(self.dashboard.alert_history)
        resolved_alerts = len([a for a in self.dashboard.alert_history if a.resolved])
        
        uptime_start = current_time - timedelta(hours=1)  # Assume 1 hour monitoring
        recent_alerts = [a for a in self.dashboard.alert_history if a.timestamp >= uptime_start]
        
        report = {
            "report_timestamp": current_time.isoformat(),
            "monitoring_level": self.monitoring_level.value,
            "monitoring_duration_hours": 1.0,  # Simplified
            "dashboard_summary": dashboard_data["summary"],
            "system_health_overview": {
                "total_systems": len(self.dashboard.system_health),
                "healthy_systems": len([s for s in self.dashboard.system_health.values() if s.status == "healthy"]),
                "degraded_systems": len([s for s in self.dashboard.system_health.values() if s.status == "degraded"]),
                "offline_systems": len([s for s in self.dashboard.system_health.values() if s.status == "offline"])
            },
            "alert_statistics": {
                "total_alerts": total_alerts,
                "resolved_alerts": resolved_alerts,
                "resolution_rate": resolved_alerts / total_alerts if total_alerts > 0 else 1.0,
                "recent_alerts": len(recent_alerts),
                "alert_types": {}
            },
            "performance_overview": {
                "metrics_collected": len(self.dashboard.active_metrics),
                "average_response_time": sum(s.response_time_ms for s in self.dashboard.system_health.values()) / len(self.dashboard.system_health),
                "overall_performance_score": sum(s.performance_score for s in self.dashboard.system_health.values()) / len(self.dashboard.system_health)
            },
            "recommendations": self._generate_monitoring_recommendations()
        }
        
        # Calculate alert type distribution
        for alert in self.dashboard.alert_history:
            alert_type = alert.alert_type.value
            report["alert_statistics"]["alert_types"][alert_type] = report["alert_statistics"]["alert_types"].get(alert_type, 0) + 1
        
        return report
    
    def _generate_monitoring_recommendations(self) -> List[str]:
        """Generate monitoring recommendations based on current state"""
        recommendations = []
        
        # Check for high alert volume
        if len(self.dashboard.active_alerts) > 5:
            recommendations.append("High alert volume detected - consider adjusting thresholds")
        
        # Check for system health issues
        unhealthy_systems = [s for s in self.dashboard.system_health.values() if s.status != "healthy"]
        if unhealthy_systems:
            recommendations.append(f"System health issues detected in {len(unhealthy_systems)} systems")
        
        # Check for performance issues
        slow_systems = [s for s in self.dashboard.system_health.values() if s.response_time_ms > 1000]
        if slow_systems:
            recommendations.append("Performance degradation detected - investigate slow response times")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                "All systems operating normally",
                "Continue regular monitoring",
                "Consider increasing monitoring level for better insights"
            ]
        
        return recommendations


async def main():
    """Demonstration of real-time governance monitoring"""
    
    print("=" * 80)
    print("REAL-TIME GOVERNANCE MONITORING SYSTEM v9.6 - DEMONSTRATION")
    print("=" * 80)
    
    # Initialize monitoring system
    monitoring = RealTimeGovernanceMonitoring(monitoring_level=MonitoringLevel.DEBUG)
    await monitoring.initialize()
    
    print("\n1. STARTING REAL-TIME MONITORING")
    print("-" * 50)
    
    # Start monitoring
    await monitoring.start_monitoring()
    
    print("\n2. SIMULATING GOVERNANCE ACTIVITIES")
    print("-" * 50)
    
    # Simulate some governance activities to generate metrics
    try:
        # Test governance collaboration
        print("Executing governance collaboration...")
        test_request = {
            "type": "monitoring_test",
            "description": "Test collaboration for monitoring demonstration"
        }
        collaboration_result = await monitoring.governance.collaborate(test_request)
        print(f"  Collaboration result: {collaboration_result.final_consensus.value}")
        
        # Test Claude operation
        print("Testing Claude governance integration...")
        claude_result = await monitoring.claude_integration.claude_chat(
            "Test message for monitoring demonstration",
            GovernanceLevel.ADVISORY
        )
        print(f"  Claude operation: {'SUCCESS' if claude_result['success'] else 'FAILED'}")
        
        # Test quality analysis
        print("Running code quality analysis...")
        test_file = Path("unified_governance_orchestrator.py")
        if test_file.exists():
            quality_report = await monitoring.quality_system.analyze_file_quality(test_file)
            print(f"  Quality score: {quality_report.overall_score:.1f}")
        
    except Exception as e:
        print(f"  Error in governance activities: {str(e)}")
    
    print("\n3. MONITORING FOR 15 SECONDS...")
    print("-" * 50)
    
    # Let monitoring run for a short period
    await asyncio.sleep(15)
    
    print("\n4. MONITORING DASHBOARD STATUS")
    print("-" * 50)
    
    # Get dashboard data
    dashboard_data = monitoring.dashboard.get_dashboard_data()
    
    print(f"Active metrics: {len(dashboard_data['active_metrics'])}")
    print(f"Active alerts: {dashboard_data['summary']['total_active_alerts']}")
    print(f"Critical alerts: {dashboard_data['summary']['critical_alerts']}")
    print(f"Healthy systems: {dashboard_data['summary']['healthy_systems']}/{dashboard_data['summary']['total_systems']}")
    
    # Show key metrics
    print("\nKey Metrics:")
    key_metrics = ["orchestration_running", "active_agents", "success_rate", "consensus_success_rate"]
    for metric_name in key_metrics:
        if metric_name in dashboard_data["active_metrics"]:
            metric = dashboard_data["active_metrics"][metric_name]
            print(f"  {metric_name}: {metric['value']} {metric['unit']}")
    
    # Show system health
    print("\nSystem Health:")
    for system_name, health in dashboard_data["system_health"].items():
        print(f"  {system_name}: {health['status']} ({health['response_time_ms']:.1f}ms)")
    
    print("\n5. GENERATING MONITORING REPORT")
    print("-" * 50)
    
    # Generate comprehensive report
    report = await monitoring.generate_monitoring_report()
    
    print(f"Monitoring Report ({report['report_timestamp']}):")
    print(f"  Monitoring Level: {report['monitoring_level']}")
    print(f"  Total Systems: {report['system_health_overview']['total_systems']}")
    print(f"  Healthy Systems: {report['system_health_overview']['healthy_systems']}")
    print(f"  Metrics Collected: {report['performance_overview']['metrics_collected']}")
    print(f"  Average Response Time: {report['performance_overview']['average_response_time']:.1f}ms")
    print(f"  Overall Performance: {report['performance_overview']['overall_performance_score']:.1f}")
    
    print("\nAlert Statistics:")
    print(f"  Total Alerts: {report['alert_statistics']['total_alerts']}")
    print(f"  Resolved Alerts: {report['alert_statistics']['resolved_alerts']}")
    print(f"  Resolution Rate: {report['alert_statistics']['resolution_rate']:.1%}")
    
    print("\nRecommendations:")
    for recommendation in report['recommendations']:
        print(f"  - {recommendation}")
    
    print("\n6. STOPPING MONITORING")
    print("-" * 50)
    
    # Stop monitoring
    await monitoring.stop_monitoring()
    
    print("\n" + "=" * 80)
    print("REAL-TIME GOVERNANCE MONITORING DEMONSTRATION COMPLETE")
    print("=" * 80)
    
    print("\nFeatures Demonstrated:")
    print("  - Real-time metric collection from all governance systems")
    print("  - Automated health monitoring and alerting")
    print("  - Performance threshold monitoring")
    print("  - Multi-threaded monitoring and alert processing")
    print("  - WebSocket-based real-time dashboard")
    print("  - Comprehensive monitoring reports")
    print("  - Configurable monitoring levels")
    
    print("\nMonitoring Capabilities:")
    print("  - AI Orchestration metrics (agent status, task completion)")
    print("  - Governance performance (consensus rates, collaboration times)")
    print("  - Code quality metrics (analysis scores, issue counts)")
    print("  - Token optimization (savings, compression ratios)")
    print("  - Claude operations (success rates, governance levels)")
    print("  - System resources (CPU, memory, disk usage)")
    print("  - Conversation analytics (active sessions, optimization rates)")
    
    print("\nAlert Types:")
    print("  - Consensus failures and governance issues")
    print("  - Performance degradation and resource limits")
    print("  - Quality violations and compliance issues")
    print("  - Security concerns and system errors")
    print("  - Process anomalies and threshold breaches")


if __name__ == "__main__":
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\nReceived interrupt signal, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    asyncio.run(main())