"""Tests for monitoring module"""

import pytest
from src.monitoring import SessionMonitor, EventType, Severity


def test_session_monitor_initialization():
    """Test session monitor creation"""
    monitor = SessionMonitor("test_session_001")
    
    assert monitor.session_id == "test_session_001"
    assert len(monitor.events) == 0
    assert monitor.error_count == 0


def test_log_event():
    """Test event logging"""
    monitor = SessionMonitor("test_session")
    
    event = monitor.log_event(
        event_type=EventType.CLICK,
        message="Clicked submit button",
        severity=Severity.INFO
    )
    
    assert event.message == "Clicked submit button"
    assert event.event_type == EventType.CLICK
    assert len(monitor.events) == 1


def test_metrics_calculation():
    """Test metrics calculation"""
    monitor = SessionMonitor("test_session")
    
    # Log some events
    monitor.log_event(EventType.CLICK, "Click 1", Severity.INFO)
    monitor.log_event(EventType.CLICK, "Click 2", Severity.INFO)
    monitor.log_event(EventType.ERROR, "Error event", Severity.ERROR)
    
    metrics = monitor.get_metrics()
    
    assert metrics.total_events == 3
    assert metrics.errors == 1
    assert metrics.session_id == "test_session"


def test_error_tracking():
    """Test error event tracking"""
    monitor = SessionMonitor("test_session")
    
    monitor.log_event(EventType.ERROR, "Element not found", Severity.ERROR)
    monitor.log_event(EventType.WAIT, "Waiting", Severity.INFO)
    monitor.log_event(EventType.ERROR, "Timeout", Severity.ERROR)
    
    error_events = monitor.get_error_events()
    
    assert len(error_events) == 2
    assert all(e.severity == Severity.ERROR for e in error_events)
