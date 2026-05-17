#!/usr/bin/env python
"""Continuous monitoring demo - generates events for dashboard display"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.monitoring import get_dashboard, EventType, Severity
import time


async def main():
    """Generate continuous monitoring data"""
    dashboard = get_dashboard()
    
    print("=" * 60)
    print("Continuous Monitoring Demo")
    print("=" * 60)
    print("\n Generating monitoring data for dashboard...")
    print("Keep this running to see live data in the dashboard")
    print("Press Ctrl+C to stop\n")
    
    session_id = "live_demo_session"
    session = dashboard.create_session(session_id)
    
    event_counter = 0
    try:
        while True:
            # Log different types of events
            events = [
                (EventType.NAVIGATION, Severity.INFO, "Navigated to admin panel"),
                (EventType.WAIT, Severity.INFO, "Waiting for data to load"),
                (EventType.CLICK, Severity.INFO, "Clicked export button"),
                (EventType.INPUT, Severity.INFO, "Entered filter criteria"),
                (EventType.WAIT, Severity.INFO, "Processing request"),
                (EventType.SCREENSHOT, Severity.INFO, "Captured page screenshot"),
                (EventType.CONVERSATION, Severity.INFO, "Agent analyzing results"),
            ]
            
            for event_type, severity, message in events:
                event_counter += 1
                session.log_event(event_type=event_type, severity=severity, message=message)
                print(f"[{event_counter}] {event_type.name:15} | {message}")
                await asyncio.sleep(0.5)
            
            # Occasionally add an error
            if event_counter % 7 == 0:
                session.log_event(event_type=EventType.ERROR, severity=Severity.WARNING, message="Detected timeout - retrying")
                print(f"[{event_counter}] ERROR           | Detected timeout - retrying")
            
            print(f"   Total events: {len(session.events)}")
            print()
            await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print(" Demo stopped")
        print("=" * 60)
        metrics = session.get_metrics()
        print(f"\n Final Session Metrics:")
        print(f"  Session ID: {metrics.session_id}")
        print(f"  Total Events: {metrics.total_events}")
        print(f"  Errors: {metrics.errors}")
        print(f"  Warnings: {metrics.warnings}")
        print(f"  Success Rate: {metrics.success_rate:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
