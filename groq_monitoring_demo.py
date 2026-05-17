#!/usr/bin/env python
"""Groq-powered monitoring demo - generates intelligent monitoring sessions"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.monitoring import get_dashboard, EventType, Severity
from groq import Groq

# Initialize Groq client from .env
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print(" Error: GROQ_API_KEY not found in .env file")
    sys.exit(1)

client = Groq(api_key=groq_api_key)


def generate_monitoring_scenario(session_number):
    """Use Groq to generate a realistic monitoring scenario"""
    prompt = f"""Generate a realistic AI agent monitoring scenario #{session_number} for a web application. 
    
    Describe a sequence of 5-7 monitoring events that an AI agent would encounter while:
    - Logging into an application
    - Navigating pages
    - Performing actions
    - Handling errors
    
    Format each event on a new line as: [EVENT_TYPE] | [MESSAGE]
    
    Event types can be: NAVIGATION, WAIT, CLICK, INPUT, SCREENSHOT, CONVERSATION, ERROR
    
    Example format:
    NAVIGATION | Navigated to login page
    INPUT | Entered credentials
    WAIT | Waiting for authentication
    CLICK | Clicked submit button
    ERROR | Login timeout, retrying with exponential backoff
    CONVERSATION | Agent: Successfully authenticated
    SCREENSHOT | Captured dashboard view
    
    Generate a NEW unique scenario (not the login example above):"""
    
    try:
        # Groq client may vary; attempt to call a messages API
        if hasattr(client, "messages") and callable(getattr(client, "messages")):
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            scenario_text = message.content[0].text
        elif hasattr(client, "generate") and callable(getattr(client, "generate")):
            # Alternate API surface
            response = client.generate(prompt)
            scenario_text = response.text if hasattr(response, "text") else str(response)
        else:
            raise AttributeError("Groq client does not expose a compatible generation method")

        events = []
        for line in scenario_text.strip().split('\n'):
            if '|' in line:
                try:
                    event_type_str, message_text = line.split('|', 1)
                    event_type_str = event_type_str.strip().upper()
                    message_text = message_text.strip()

                    event_type_map = {
                        'NAVIGATION': EventType.NAVIGATION,
                        'WAIT': EventType.WAIT,
                        'CLICK': EventType.CLICK,
                        'INPUT': EventType.INPUT,
                        'SCREENSHOT': EventType.SCREENSHOT,
                        'CONVERSATION': EventType.CONVERSATION,
                        'ERROR': EventType.ERROR,
                    }

                    event_type = event_type_map.get(event_type_str)
                    if event_type:
                        severity = Severity.WARNING if event_type_str == 'ERROR' else Severity.INFO
                        events.append((event_type, severity, message_text))
                except Exception:
                    continue

        return events
    except Exception as e:
        # Fallback: generate a deterministic local scenario
        print(f" Groq generation failed ({e}). Falling back to local scenario generator.")
        local_events = [
            (EventType.NAVIGATION, Severity.INFO, "Navigated to login page"),
            (EventType.INPUT, Severity.INFO, "Entered username and password"),
            (EventType.WAIT, Severity.INFO, "Waiting for authentication response"),
            (EventType.CLICK, Severity.INFO, "Clicked 'Continue'"),
            (EventType.ERROR, Severity.WARNING, "Authentication delay detected, retrying"),
            (EventType.SCREENSHOT, Severity.INFO, "Captured post-login dashboard"),
            (EventType.CONVERSATION, Severity.INFO, "Agent: 'Login successful, loading user dashboard'"),
        ]
        return local_events


async def main():
    """Generate multiple active monitoring sessions using Groq"""
    dashboard = get_dashboard()
    
    print("=" * 70)
    print("Groq-Powered Monitoring Sessions Generator")
    print("=" * 70)
    print(f"\n Using Groq API to generate intelligent monitoring scenarios")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    sessions_created = []
    
    try:
        # Create 3 active sessions with Groq-generated scenarios
        for session_num in range(1, 4):
            print(f"\n Generating Session {session_num}...")
            print("-" * 70)
            
            # Generate scenario using Groq
            events = generate_monitoring_scenario(session_num)
            
            if events:
                session_id = f"groq_session_{session_num}"
                session = dashboard.create_session(session_id)
                
                print(f" Session created: {session_id}")
                print(f" Generated {len(events)} monitoring events:\n")
                
                # Log events
                for idx, (event_type, severity, message) in enumerate(events, 1):
                    session.log_event(event_type=event_type, severity=severity, message=message)
                    severity_icon = "" if severity == Severity.WARNING else "ℹ"
                    print(f"  {severity_icon} [{idx}] {event_type.name:15} | {message}")
                    await asyncio.sleep(0.2)
                
                metrics = session.get_metrics()
                print(f"\n   Session Metrics:")
                print(f"     - Total Events: {metrics.total_events}")
                print(f"     - Errors: {metrics.errors}")
                print(f"     - Warnings: {metrics.warnings}")
                print(f"     - Success Rate: {metrics.success_rate:.1f}%")
                
                sessions_created.append(session_id)
            else:
                print(f" Failed to generate scenario for session {session_num}")
    
    except KeyboardInterrupt:
        print("\n\n  Stopped by user")
    
    # Final summary
    print("\n" + "=" * 70)
    print(" Monitoring Sessions Ready")
    print("=" * 70)
    print(f"\n Active Sessions Created: {len(sessions_created)}")
    for sess_id in sessions_created:
        print(f"  • {sess_id}")
    
    print(f"\n Dashboard: http://localhost:8502")
    print(f" API: http://localhost:8000/api/summary")
    print(f"\n Dashboard will auto-refresh and display these sessions!")


if __name__ == "__main__":
    asyncio.run(main())
