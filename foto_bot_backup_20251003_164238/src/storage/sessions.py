import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from ..config import Config

logger = logging.getLogger(__name__)

@dataclass
class AgentSession:
    """Represents an active agent session"""
    agent_id: str
    phone_number: str
    current_job_id: Optional[str] = None
    current_step: int = 1
    completed_steps: Dict[int, str] = None
    session_start: datetime = None
    last_activity: datetime = None
    status: str = "active"  # active, completed, abandoned

    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = {}
        if self.session_start is None:
            self.session_start = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['session_start'] = self.session_start.isoformat() if self.session_start else None
        data['last_activity'] = self.last_activity.isoformat() if self.last_activity else None
        return data

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary with datetime parsing"""
        if data.get('session_start'):
            data['session_start'] = datetime.fromisoformat(data['session_start'])
        if data.get('last_activity'):
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

class SessionManager:
    """Manages agent sessions and installation jobs"""

    def __init__(self, session_file: Optional[str] = None):
        self.session_file = session_file or Config.SESSION_FILE_PATH
        self.sessions: Dict[str, AgentSession] = {}
        self._load_sessions()

    def _load_sessions(self):
        """Load sessions from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    for phone_number, session_data in data.items():
                        self.sessions[phone_number] = AgentSession.from_dict(session_data)
                logger.info(f"Loaded {len(self.sessions)} sessions from file")
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.sessions = {}

    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)

            with open(self.session_file, 'w') as f:
                data = {
                    phone_number: session.to_dict()
                    for phone_number, session in self.sessions.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")

    def get_or_create_session(self, phone_number: str, agent_id: Optional[str] = None) -> AgentSession:
        """Get existing session or create new one"""
        phone_number = self._normalize_phone_number(phone_number)

        if phone_number not in self.sessions:
            # Clean up old sessions
            self._cleanup_old_sessions()

            # Create new session
            agent_id = agent_id or self._generate_agent_id(phone_number)
            job_id = self._generate_job_id(agent_id)

            self.sessions[phone_number] = AgentSession(
                agent_id=agent_id,
                phone_number=phone_number,
                current_job_id=job_id,
                current_step=1,
                completed_steps={},
                session_start=datetime.now(),
                last_activity=datetime.now(),
                status="active"
            )

            logger.info(f"Created new session for {phone_number}")
            self._save_sessions()

        # Update last activity
        session = self.sessions[phone_number]
        session.last_activity = datetime.now()
        self._save_sessions()

        return session

    def get_session(self, phone_number: str) -> Optional[AgentSession]:
        """Get existing session if exists"""
        phone_number = self._normalize_phone_number(phone_number)
        return self.sessions.get(phone_number)

    def update_session(self, phone_number: str, **kwargs):
        """Update session with new values"""
        phone_number = self._normalize_phone_number(phone_number)

        if phone_number in self.sessions:
            session = self.sessions[phone_number]
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.last_activity = datetime.now()
            self._save_sessions()
            logger.info(f"Updated session for {phone_number}")

    def complete_step(self, phone_number: str, step: int, photo_path: str):
        """Mark a step as completed"""
        phone_number = self._normalize_phone_number(phone_number)

        if phone_number in self.sessions:
            session = self.sessions[phone_number]
            session.completed_steps[step] = photo_path

            # Move to next step if this is the current step
            if session.current_step == step:
                session.current_step = step + 1

            # Check if installation is complete
            if session.current_step > 14:
                session.status = "completed"
                logger.info(f"Installation {session.current_job_id} completed for {phone_number}")

            session.last_activity = datetime.now()
            self._save_sessions()

    def reset_session(self, phone_number: str):
        """Reset session to start new installation"""
        phone_number = self._normalize_phone_number(phone_number)

        if phone_number in self.sessions:
            session = self.sessions[phone_number]
            agent_id = session.agent_id
            job_id = self._generate_job_id(agent_id)

            # Reset session but keep agent info
            session.current_job_id = job_id
            session.current_step = 1
            session.completed_steps = {}
            session.session_start = datetime.now()
            session.last_activity = datetime.now()
            session.status = "active"

            logger.info(f"Reset session for {phone_number} with new job {job_id}")
            self._save_sessions()

    def get_active_sessions(self) -> List[AgentSession]:
        """Get all active sessions"""
        return [
            session for session in self.sessions.values()
            if session.status == "active"
        ]

    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        total_sessions = len(self.sessions)
        active_sessions = len(self.get_active_sessions())
        completed_sessions = len([
            s for s in self.sessions.values() if s.status == "completed"
        ])

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "average_steps_completed": self._get_average_steps_completed()
        }

    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number format"""
        # Remove WhatsApp prefix and normalize format
        normalized = phone_number.replace('whatsapp:', '').replace('+', '')
        return f"+{normalized}" if not normalized.startswith('+') else normalized

    def _generate_agent_id(self, phone_number: str) -> str:
        """Generate agent ID from phone number"""
        return phone_number.replace('+', '').replace('whatsapp:', '')

    def _generate_job_id(self, agent_id: str) -> str:
        """Generate unique job ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"JOB_{timestamp}_{agent_id}"

    def _cleanup_old_sessions(self):
        """Remove sessions older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=Config.MAX_SESSION_DURATION_HOURS)
        old_sessions = [
            phone for phone, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]

        for phone in old_sessions:
            session = self.sessions[phone]
            session.status = "abandoned"
            logger.info(f"Marked session for {phone} as abandoned")

        if old_sessions:
            self._save_sessions()

    def _get_average_steps_completed(self) -> float:
        """Calculate average number of steps completed across all sessions"""
        if not self.sessions:
            return 0

        total_steps = sum(len(session.completed_steps) for session in self.sessions.values())
        return round(total_steps / len(self.sessions), 1)