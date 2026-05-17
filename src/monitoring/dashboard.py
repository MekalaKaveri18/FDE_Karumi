"""Streamlit Dashboard for Session Monitoring"""

import sys
import os
# Make imports work both locally and on Streamlit Cloud
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import json
from datetime import datetime
import pandas as pd
from src.monitoring import get_dashboard, Severity


def main():
    st.set_page_config(page_title="Karumi Monitoring Dashboard", layout="wide")
    
    st.title("🔍 Karumi Monitoring Dashboard")
    st.markdown("Real-time monitoring for AI agent deployment sessions")
    
    dashboard = get_dashboard()
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    st.sidebar.slider("Refresh interval (seconds)", 1, 60, 5)
    
    # Seed demo data if no sessions exist
    if not dashboard.get_all_sessions():
        from src.monitoring import EventType, Severity as Sev
        session = dashboard.create_session("demo_session")
        demo_events = [
            (EventType.NAVIGATION,   "Navigated to application dashboard",         Sev.INFO),
            (EventType.WAIT,         "Waiting for page load (2.3s)",               Sev.INFO),
            (EventType.CLICK,        "Clicked 'Run Report' button",                Sev.INFO),
            (EventType.INPUT,        "Entered date range filter",                  Sev.INFO),
            (EventType.ERROR,        "no element found matching .export-btn",      Sev.INFO),
            (EventType.ERROR,        "element timed out after 10000ms",            Sev.INFO),
            (EventType.WAIT,         "Retrying with exponential backoff",          Sev.INFO),
            (EventType.ERROR,        "Redirected to /login — 401 unauthorized",    Sev.INFO),
            (EventType.SCREENSHOT,   "Export completed successfully",              Sev.INFO),
            (EventType.CONVERSATION, "Agent: 'Report exported to PDF format'",     Sev.INFO),
        ]
        for event_type, message, severity in demo_events:
            session.log_event(event_type=event_type, message=message, severity=severity)

    sessions = dashboard.get_all_sessions()
    selected_session = st.sidebar.selectbox("Select Session", sessions)
    
    if not selected_session:
        st.info("No active sessions.")
        return

    session = dashboard.get_session(selected_session)
    metrics = session.get_metrics()

    # Metrics row
    st.header("Session Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Events",    metrics.total_events)
    col2.metric("Errors",          metrics.errors)
    col3.metric("Warnings",        metrics.warnings)
    col4.metric("Success Rate",    f"{metrics.success_rate:.1%}")
    col5.metric("Avg Response",    f"{metrics.avg_response_time_ms:.0f}ms")

    # Events timeline
    st.header("Events Timeline")
    recent_events = session.get_recent_events(limit=20)
    event_data = [
        {
            "Time":       e.timestamp.split("T")[1][:8] if "T" in e.timestamp else e.timestamp,
            "Type":       e.event_type.value,
            "Severity":   e.severity.value,
            "Message":    e.message,
            "Fix":        e.suggestion or "—",
        }
        for e in recent_events
    ]
    if event_data:
        df = pd.DataFrame(event_data)

        def color_severity(val):
            if val == "error":    return "background-color: #fee2e2; color: #b91c1c"
            if val == "critical": return "background-color: #fecaca; color: #991b1b"
            if val == "warning":  return "background-color: #fef9c3; color: #92400e"
            return ""

        st.dataframe(
            df.style.map(color_severity, subset=["Severity"]),
            use_container_width=True,
        )

    # Error analysis
    st.header("Error Analysis & Fix Suggestions")
    error_events = session.get_error_events()
    if error_events:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Recent Errors")
            for e in error_events[-5:]:
                with st.expander(f"❌ {e.message[:60]}", expanded=False):
                    st.write(f"**Time:** {e.timestamp}")
                    st.write(f"**Type:** {e.event_type.value}")
                    if e.details:
                        st.json(e.details)
        with col2:
            st.subheader("💡 Fix Suggestions")
            for e in error_events[-5:]:
                if e.suggestion:
                    st.info(e.suggestion)
    else:
        st.success("✅ No errors detected in this session!")

    # Export
    st.header("Export Session Data")
    export_data = session.export_session()
    st.download_button(
        label="⬇ Download JSON",
        data=json.dumps(export_data, indent=2),
        file_name=f"session_{selected_session}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )
    with st.expander("Preview JSON"):
        st.json(export_data)


if __name__ == "__main__":
    main()
