"""Monitoring & Troubleshooting Dashboard

Watches running agent sessions, logs actions/browser state/errors, and suggests fixes.
Uses Streamlit for UI and FastAPI for data serving.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)


class EventType(str, Enum):
    """Type of monitoring event"""
    NAVIGATION = "navigation"
    CLICK = "click"
    INPUT = "input"
    WAIT = "wait"
    ERROR = "error"
    SCREENSHOT = "screenshot"
    CONVERSATION = "conversation"


class Severity(str, Enum):
    """Severity level of an event"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MonitoringEvent:
    """Single monitoring event"""
    timestamp: str
    event_type: EventType
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    browser_state: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


@dataclass
class SessionMetrics:
    """Metrics for a monitoring session"""
    session_id: str
    start_time: str
    last_update: str
    total_events: int
    errors: int
    warnings: int
    avg_response_time_ms: float
    success_rate: float


class SessionMonitor:
    """Monitors an active agent session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: List[MonitoringEvent] = []
        self.start_time = datetime.now()
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
    
    def log_event(
        self,
        event_type: EventType,
        message: str,
        severity: Severity = Severity.INFO,
        details: Optional[Dict[str, Any]] = None,
        browser_state: Optional[Dict[str, Any]] = None
    ) -> MonitoringEvent:
        """Log a monitoring event"""
        
        # Generate suggestion based on event
        suggestion = self._generate_suggestion(event_type, message, severity)
        
        event = MonitoringEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            message=message,
            details=details or {},
            browser_state=browser_state,
            suggestion=suggestion
        )
        
        self.events.append(event)
        
        # Track metrics
        if severity == Severity.ERROR:
            self.error_count += 1
        else:
            self.success_count += 1
        
        logger.info(
            "Event logged",
            session=self.session_id,
            event_type=event_type.value,
            severity=severity.value,
            message=message
        )
        
        return event
    
    def _generate_suggestion(
        self,
        event_type: EventType,
        message: str,
        severity: Severity
    ) -> Optional[str]:
        """Generate a suggestion based on the event"""
        
        suggestions = {
            "selector_not_found": "Selector may have changed. Check browser dev tools to find new locator.",
            "timeout": "Element took too long to load. Consider increasing timeout or waiting for a different event.",
            "stale_element": "Element reference is stale. Re-locate the element before interacting.",
            "network_error": "Network request failed. Check browser console for API errors.",
            "auth_failure": "Authentication failed. Verify credentials and check if session expired.",
            "dynamic_modal": "Dynamic modal appeared. Wait for it to load completely before proceeding.",
            "lazy_loading": "Element may not be visible due to lazy loading. Scroll into view first.",
        }
        
        # Try to match message to known issues
        for issue, suggestion in suggestions.items():
            if issue.lower() in message.lower():
                return suggestion
        
        # Default suggestions based on severity
        if severity == Severity.ERROR:
            return "Check browser console for more details and consider adding wait conditions."
        elif severity == Severity.WARNING:
            return "Monitor this closely as it may lead to failures later."
        
        return None
    
    def get_metrics(self) -> SessionMetrics:
        """Get session metrics"""
        duration_seconds = (datetime.now() - self.start_time).total_seconds()
        total_events = len(self.events)
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        success_rate = (self.success_count / (self.success_count + self.error_count)) if (self.success_count + self.error_count) > 0 else 1.0
        
        return SessionMetrics(
            session_id=self.session_id,
            start_time=self.start_time.isoformat(),
            last_update=datetime.now().isoformat(),
            total_events=total_events,
            errors=self.error_count,
            warnings=len([e for e in self.events if e.severity == Severity.WARNING]),
            avg_response_time_ms=avg_response_time,
            success_rate=success_rate
        )
    
    def get_recent_events(self, limit: int = 50) -> List[MonitoringEvent]:
        """Get recent events"""
        return self.events[-limit:]
    
    def get_error_events(self) -> List[MonitoringEvent]:
        """Get all error events"""
        return [e for e in self.events if e.severity.value in ["error", "critical"]]
    
    def export_session(self) -> Dict[str, Any]:
        """Export session data"""
        metrics = self.get_metrics()
        
        return {
            "session_id": self.session_id,
            "metrics": {
                "start_time": metrics.start_time,
                "last_update": metrics.last_update,
                "total_events": metrics.total_events,
                "errors": metrics.errors,
                "warnings": metrics.warnings,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "success_rate": metrics.success_rate
            },
            "events": [
                {
                    "timestamp": e.timestamp,
                    "event_type": e.event_type.value,
                    "severity": e.severity.value,
                    "message": e.message,
                    "details": e.details,
                    "suggestion": e.suggestion
                }
                for e in self.events
            ]
        }


class MonitoringDashboard:
    """Central monitoring dashboard for multiple sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionMonitor] = {}
    
    def create_session(self, session_id: str) -> SessionMonitor:
        """Create a new monitoring session"""
        session = SessionMonitor(session_id)
        self.sessions[session_id] = session
        logger.info("Session created", session_id=session_id)
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionMonitor]:
        """Get a monitoring session"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[str]:
        """Get all session IDs"""
        return list(self.sessions.keys())
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions"""
        all_metrics = [session.get_metrics() for session in self.sessions.values()]
        
        total_errors = sum(m.errors for m in all_metrics)
        total_events = sum(m.total_events for m in all_metrics)
        avg_success_rate = sum(m.success_rate for m in all_metrics) / len(all_metrics) if all_metrics else 0
        
        return {
            "total_sessions": len(self.sessions),
            "total_events": total_events,
            "total_errors": total_errors,
            "avg_success_rate": avg_success_rate,
            "sessions": [
                {
                    "id": m.session_id,
                    "events": m.total_events,
                    "errors": m.errors,
                    "success_rate": m.success_rate
                }
                for m in all_metrics
            ]
        }


# Global dashboard instance
_dashboard = MonitoringDashboard()


def get_dashboard() -> MonitoringDashboard:
    """Get the global dashboard instance"""
    return _dashboard
