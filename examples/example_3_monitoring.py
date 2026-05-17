"""Example 3: Real-time Monitoring Session"""

import asyncio
import sys
import os

# Add parent directory to path so imports work from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.monitoring import get_dashboard, EventType, Severity


async def main():
    """Demonstrate monitoring dashboard"""
    
    print("=" * 60)
    print("Karumi Monitoring - Example 3")
    print("=" * 60)
    
    # Create dashboard and session
    dashboard = get_dashboard()
    session = dashboard.create_session("monitoring_demo_001")
    
    print(f"\n Monitoring session created: monitoring_demo_001\n")
    
    # Simulate various events
    events_to_log = [
        (EventType.NAVIGATION, "Navigated to dashboard page", Severity.INFO),
        (EventType.WAIT, "Waiting for chart data to load", Severity.INFO),
        (EventType.CLICK, "Clicked filter button", Severity.INFO),
        (EventType.INPUT, "Entered date range filter", Severity.INFO),
        (EventType.WAIT, "Processing filter request", Severity.INFO),
        (EventType.SCREENSHOT, "Captured chart screenshot", Severity.INFO),
        (EventType.ERROR, "Failed to load chart - selector changed", Severity.WARNING),
        (EventType.WAIT, "Retrying with new selector", Severity.INFO),
        (EventType.CONVERSATION, "Agent: 'I'll analyze the Q4 sales data'", Severity.INFO),
        (EventType.SCREENSHOT, "Captured final results", Severity.INFO),
    ]
    
    # Log events
    for event_type, message, severity in events_to_log:
        event = session.log_event(
            event_type=event_type,
            message=message,
            severity=severity,
            details={
                "url": "https://example-saas.com/dashboard",
                "element": "[data-testid='chart']"
            }
        )
        
        # Print event
        icon = {
            Severity.INFO: "ℹ",
            Severity.WARNING: "",
            Severity.ERROR: "",
            Severity.CRITICAL: ""
        }.get(severity, "•")
        
        print(f"{icon} {event_type.value.upper():12} | {message}")
        
        # Small delay between events
        await asyncio.sleep(0.2)
    
    # Get and display metrics
    metrics = session.get_metrics()
    
    print(f"\n" + "=" * 60)
    print(" Session Metrics")
    print("=" * 60)
    print(f"Session ID:           {metrics.session_id}")
    print(f"Start Time:           {metrics.start_time}")
    print(f"Total Events:         {metrics.total_events}")
    print(f"Errors:               {metrics.errors}")
    print(f"Warnings:             {metrics.warnings}")
    print(f"Avg Response Time:    {metrics.avg_response_time_ms:.0f}ms")
    print(f"Success Rate:         {metrics.success_rate:.1%}")
    
    # Get dashboard summary
    print(f"\n" + "=" * 60)
    print(" Dashboard Summary")
    print("=" * 60)
    summary = dashboard.get_dashboard_summary()
    print(f"Active Sessions:      {summary['total_sessions']}")
    print(f"Total Events:         {summary['total_events']}")
    print(f"Total Errors:         {summary['total_errors']}")
    print(f"Avg Success Rate:     {summary['avg_success_rate']:.1%}")
    
    print(f"\n" + "=" * 60)
    print(" Monitoring demo complete!")
    print(" Run 'streamlit run src/monitoring/dashboard.py' to view the UI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
