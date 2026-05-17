"""FastAPI for Monitoring Data Serving"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.monitoring import get_dashboard, EventType, Severity
from fastapi import Request

app = FastAPI(title="Karumi Monitoring API", version="1.0.0")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Karumi Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "summary": "/api/summary",
            "sessions": "/api/sessions",
            "session": "/api/sessions/{session_id}",
            "events": "/api/sessions/{session_id}/events",
            "metrics": "/api/sessions/{session_id}/metrics",
        }
    }


@app.get("/api/summary")
async def get_summary():
    """Get dashboard summary"""
    dashboard = get_dashboard()
    return dashboard.get_dashboard_summary()


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    dashboard = get_dashboard()
    return {"sessions": dashboard.get_all_sessions()}


@app.post("/api/sessions/import")
async def import_session(request: Request):
    """Import a session JSON payload into the API dashboard"""
    payload = await request.json()
    dashboard = get_dashboard()

    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # Create session and import events
    session = dashboard.create_session(session_id)
    events = payload.get("events", [])
    for e in events:
        try:
            et = EventType(e.get("event_type")) if e.get("event_type") else EventType.NAVIGATION
        except Exception:
            et = EventType.NAVIGATION
        sev = Severity(e.get("severity")) if e.get("severity") else Severity.INFO
        message = e.get("message", "")
        session.log_event(event_type=et, severity=sev, message=message, details=e.get("details", {}))

    return JSONResponse({"status": "imported", "session_id": session_id})


@app.get("/api/sessions/{session_id}")
async def get_session_data(session_id: str):
    """Get session data"""
    dashboard = get_dashboard()
    session = dashboard.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.export_session()


@app.get("/api/sessions/{session_id}/events")
async def get_session_events(session_id: str, limit: int = 50):
    """Get session events"""
    dashboard = get_dashboard()
    session = dashboard.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    events = session.get_recent_events(limit=limit)
    
    return {
        "session_id": session_id,
        "events": [
            {
                "timestamp": e.timestamp,
                "event_type": e.event_type.value,
                "severity": e.severity.value,
                "message": e.message,
                "details": e.details,
                "suggestion": e.suggestion
            }
            for e in events
        ]
    }


@app.get("/api/sessions/{session_id}/metrics")
async def get_session_metrics(session_id: str):
    """Get session metrics"""
    dashboard = get_dashboard()
    session = dashboard.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    metrics = session.get_metrics()
    
    return {
        "session_id": metrics.session_id,
        "start_time": metrics.start_time,
        "last_update": metrics.last_update,
        "total_events": metrics.total_events,
        "errors": metrics.errors,
        "warnings": metrics.warnings,
        "avg_response_time_ms": metrics.avg_response_time_ms,
        "success_rate": metrics.success_rate
    }


@app.get("/api/sessions/{session_id}/errors")
async def get_session_errors(session_id: str):
    """Get session errors"""
    dashboard = get_dashboard()
    session = dashboard.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    errors = session.get_error_events()
    
    return {
        "session_id": session_id,
        "error_count": len(errors),
        "errors": [
            {
                "timestamp": e.timestamp,
                "event_type": e.event_type.value,
                "severity": e.severity.value,
                "message": e.message,
                "suggestion": e.suggestion
            }
            for e in errors
        ]
    }


async def main():
    """Run the API"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
