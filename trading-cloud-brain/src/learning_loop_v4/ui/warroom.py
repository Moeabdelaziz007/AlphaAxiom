"""
Dialectic War Room UI for AlphaAxiom v1.0
Real-time visualization of the internal debate and decision-making process.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class DialecticWarRoom:
    """
    Real-time React-based dashboard that visualizes the internal debate 
    of the UnifiedDialecticModel, rendering the "Thinking Machine" transparent.
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.event_listeners = []
    
    def register_event_listener(self, listener_callback):
        """
        Register a callback to receive real-time dialectic events.
        
        Args:
            listener_callback: Function to call when events occur
        """
        self.event_listeners.append(listener_callback)
    
    def broadcast_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Broadcast a dialectic event to all registered listeners.
        
        Args:
            event_type: Type of event (CORE_TOKEN, SHADOW_TOKEN, 
                         DECISION, etc.)            payload: Event data
        """
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Error broadcasting to listener: {e}")
    
    def start_dialectic_session(self, session_id: str, 
                              market_context: Dict[str, Any]):
        """
        Start a new dialectic session visualization.
        
        Args:
            session_id: Unique identifier for the session
            market_context: Initial market data
        """
        self.active_sessions[session_id] = {
            "started_at": datetime.now().isoformat(),
            "market_context": market_context,
            "core_thesis": "",
            "shadow_critique": "",
            "events": []
        }
        
        self.broadcast_event("SESSION_STARTED", {
            "session_id": session_id,
            "market_context": market_context
        })
    
    def update_core_stream(self, session_id: str, token: str):
        """
        Update the core thesis stream visualization.
        
        Args:
            session_id: Session identifier
            token: New token from core agent
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["core_thesis"] += token
            self.active_sessions[session_id]["events"].append({
                "type": "CORE_TOKEN",
                "content": token,
                "timestamp": datetime.now().isoformat()
            })
            
            self.broadcast_event("CORE_TOKEN", {
                "session_id": session_id,
                "token": token
            })
    
    def update_shadow_stream(self, session_id: str, token: str):
        """
        Update the shadow critique stream visualization.
        
        Args:
            session_id: Session identifier
            token: New token from shadow agent
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["shadow_critique"] += token
            self.active_sessions[session_id]["events"].append({
                "type": "SHADOW_TOKEN",
                "content": token,
                "timestamp": datetime.now().isoformat()
            })
            
            self.broadcast_event("SHADOW_TOKEN", {
                "session_id": session_id,
                "token": token
            })
    
    def complete_dialectic_cycle(self, session_id: str, 
                               synthesis: Dict[str, Any]):
        """
        Complete a dialectic cycle and visualize the final decision.
        
        Args:
            session_id: Session identifier
            synthesis: Final synthesis from the dialectic process
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["synthesis"] = synthesis
            self.active_sessions[session_id]["completed_at"] = \
                datetime.now().isoformat()
            
            self.broadcast_event("DECISION_MADE", {
                "session_id": session_id,
                "synthesis": synthesis
            })
            
            # Clean up old sessions (keep only last 100)
            if len(self.active_sessions) > 100:
                oldest_session = min(
                    self.active_sessions.keys(), 
                    key=lambda k: self.active_sessions[k]["started_at"]
                )
                del self.active_sessions[oldest_session]
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a dialectic session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs.
        
        Returns:
            List of active session identifiers
        """
        return list(self.active_sessions.keys())


# Example React Component (TypeScript/JSX representation)
REACT_COMPONENT_EXAMPLE = """
// DialecticWarRoom.tsx - Frontend React Component
import React, { useState, useEffect } from 'react';

interface DebateEvent {
  type: string;
  payload: any;
  timestamp: string;
}

interface SessionStatus {
  core_thesis: string;
  shadow_critique: string;
  synthesis?: any;
}

const DialecticWarRoom: React.FC = () => {
  const [debateStream, setDebateStream] = useState<DebateEvent[]>([]);
  const [currentSession, setCurrentSession] = useState<SessionStatus>({
    core_thesis: '',
    shadow_critique: ''
  });
  const [confidenceMetrics, setConfidenceMetrics] = useState({
    core: 0,
    shadow: 0
  });

  // Connect to Server-Sent Events
  useEffect(() => {
    const eventSource = new EventSource('/api/dialectic/stream');
    
    eventSource.onmessage = (event) => {
      const data: DebateEvent = JSON.parse(event.data);
      setDebateStream(prev => [...prev, data]);
      
      // Update visualization based on event type
      switch (data.type) {
        case 'CORE_TOKEN':
          setCurrentSession(prev => ({
            ...prev,
            core_thesis: prev.core_thesis + data.payload.token
          }));
          break;
        case 'SHADOW_TOKEN':
          setCurrentSession(prev => ({
            ...prev,
            shadow_critique: prev.shadow_critique + data.payload.token
          }));
          break;
        case 'DECISION_MADE':
          // Update confidence metrics when decision is made
          setConfidenceMetrics({
            core: data.payload.synthesis.core_confidence || 0,
            shadow: data.payload.synthesis.shadow_regret || 0
          });
          break;
      }
    };
    
    return () => eventSource.close();
  }, []);

  return (
    <div className="war-room">
      <div className="visualization-panel">
        {/* Real-time Debate Visualization */}
        <div className="debate-stream">
          <div className="core-stream">
            <h3>Core Agent (Thesis)</h3>
            <div className="typewriter-text core-color">
              {currentSession.core_thesis}
            </div>
          </div>
          
          <div className="shadow-stream">
            <h3>Shadow Agent (Antithesis)</h3>
            <div className="typewriter-text shadow-color">
              {currentSession.shadow_critique}
            </div>
          </div>
        </div>
        
        {/* Confidence Gauges */}
        <div className="gauges">
          <div className="gauge core-gauge">
            <h4>Core Confidence</h4>
            <div className="gauge-value">
              {(confidenceMetrics.core * 100).toFixed(1)}%
            </div>
          </div>
          
          <div className="gauge shadow-gauge">
            <h4>Shadow Regret</h4>
            <div className="gauge-value">
              {(confidenceMetrics.shadow * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
      
      {/* Event History */}
      <div className="event-history">
        <h3>Event Timeline</h3>
        <ul>
          {debateStream.map((event, index) => (
            <li key={index} className={`event-${event.type.toLowerCase()}`}>
              [{new Date(event.timestamp).toLocaleTimeString()}] 
              {event.type}: {JSON.stringify(event.payload)}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default DialecticWarRoom;
"""

if __name__ == "__main__":
    # Example usage
    war_room = DialecticWarRoom()
    print("Dialectic War Room initialized")
    
    # Simulate a session
    session_id = "TEST_SESSION_001"
    market_data = {"symbol": "BTCUSDT", "price": 95000, "volume": 1000}
    
    war_room.start_dialectic_session(session_id, market_data)
    print(f"Started session: {session_id}")
    
    # Simulate streaming tokens
    war_room.update_core_stream(session_id, "Analyzing market conditions...")
    war_room.update_shadow_stream(session_id, 
                                 "Warning: High volatility detected...")
    
    # Simulate completion
    synthesis = {
        "core_confidence": 0.85,
        "shadow_regret": 0.30,
        "decision": "BUY",
        "execution_weight": 0.75
    }
    war_room.complete_dialectic_cycle(session_id, synthesis)
    
    # Check session status
    status = war_room.get_session_status(session_id)
    print(f"Session status: {json.dumps(status, indent=2)}")