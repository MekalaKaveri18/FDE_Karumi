"""Streamlit Dashboard for Session Monitoring"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import streamlit as st
import json
from datetime import datetime
import pandas as pd
from src.monitoring import get_dashboard, Severity, EventType


def create_demo_session(dashboard):
    """Create a demo session with sample events"""
    demo_session = dashboard.create_session("demo_session")
    
    # Add sample events
    events_data = [
        (EventType.NAVIGATION, Severity.INFO, "Navigated to application dashboard"),
        (EventType.WAIT, Severity.INFO, "Waiting for page load (2.3s)"),
        (EventType.CLICK, Severity.INFO, "Clicked 'Run Report' button"),
        (EventType.INPUT, Severity.INFO, "Entered date range filter"),
        (EventType.WAIT, Severity.INFO, "Processing report request"),
        (EventType.SCREENSHOT, Severity.INFO, "Captured report preview"),
        (EventType.CLICK, Severity.INFO, "Clicked 'Export' button"),
        (EventType.ERROR, Severity.WARNING, "Network timeout - retrying request"),
        (EventType.WAIT, Severity.INFO, "Retrying with exponential backoff"),
        (EventType.SCREENSHOT, Severity.INFO, "Export completed successfully"),
        (EventType.CONVERSATION, Severity.INFO, "Agent: 'Report exported to PDF format'"),
    ]
    
    for event_type, severity, message in events_data:
        demo_session.log_event(event_type=event_type, severity=severity, message=message)
    
    return demo_session


def main():
    st.set_page_config(page_title="Karumi Monitoring Dashboard", layout="wide")
    
    st.title(" Karumi Monitoring Dashboard")
    st.markdown("Real-time monitoring for AI agent deployment sessions")
    
    dashboard = get_dashboard()
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 60, 5)
    
    # Get all sessions
    sessions = dashboard.get_all_sessions()
    
    if not sessions:
        st.warning(" No active sessions detected. Displaying demo data...")
        # Create demo session
        demo_session = create_demo_session(dashboard)
        sessions = dashboard.get_all_sessions()
    
    # Session selector
    selected_session = st.sidebar.selectbox("Select Session", sessions)
    
    if selected_session:
        session = dashboard.get_session(selected_session)
        
        # Summary section
        st.header("Session Summary")
        metrics = session.get_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", metrics.total_events)
        with col2:
            st.metric("Errors", metrics.errors)
        with col3:
            st.metric("Warnings", metrics.warnings)
        with col4:
            st.metric("Success Rate", f"{metrics.success_rate:.1%}")
        
        # Events timeline
        st.header("Events Timeline")
        
        recent_events = session.get_recent_events(limit=20)
        
        event_data = []
        for event in recent_events:
            event_data.append({
                "Time": event.timestamp,
                "Type": event.event_type.value,
                "Severity": event.severity.value,
                "Message": event.message,
                "Suggestion": event.suggestion or "N/A"
            })
        
        if event_data:
            df = pd.DataFrame(event_data)
            
            # Color code by severity
            def color_severity(val):
                if val == "error":
                    return "background-color: #ffcccc"
                elif val == "warning":
                    return "background-color: #ffffcc"
                elif val == "critical":
                    return "background-color: #ff9999"
                return ""
            
            st.dataframe(
                df.style.applymap(color_severity, subset=["Severity"]),
                use_container_width=True
            )
        
        # Error analysis
        st.header("Error Analysis")
        
        error_events = session.get_error_events()
        
        if error_events:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Recent Errors")
                for event in error_events[-5:]:
                    with st.expander(f" {event.message}", expanded=False):
                        st.write(f"**Time**: {event.timestamp}")
                        st.write(f"**Type**: {event.event_type.value}")
                        if event.details:
                            st.json(event.details)
            
            with col2:
                st.subheader("Suggestions")
                for event in error_events[-5:]:
                    if event.suggestion:
                        st.info(f" {event.suggestion}")
        else:
            st.success(" No errors detected!")
        
        # Export data
        st.header("Export")
        
        export_data = session.export_session()
        st.json(export_data)
        
        # Download button
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="Download Session Data",
            data=json_str,
            file_name=f"session_{selected_session}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
