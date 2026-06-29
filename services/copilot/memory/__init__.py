import time
from typing import Dict, List, Any

class CopilotMemoryManager:
    def __init__(self):
        # Maps session_id to list of message dicts
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """
        Appends a conversation message to the session's memory.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # Keep only the last 10 messages to limit context size
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Returns recent messages from the session.
        """
        return self.sessions.get(session_id, [])

    def clear(self, session_id: str):
        """
        Resets conversation memory.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
