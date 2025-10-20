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
    """Represents an active agent session with multiple installations"""
    agent_id: str
    phone_number: str
    current_job_id: Optional[str] = None
    current_step: int = 0  # 0 = awaiting DR, -1 = awaiting location, 1-12 = photo steps
    completed_steps: Dict[int, str] = None
    session_start: datetime = None
    last_activity: datetime = None
    status: str = "active"  # active, completed, abandoned
    dr_number: Optional[str] = None
    location_verified: bool = False
    location_data: Optional[Dict] = None
    # Multi-installation support
    installations: Dict[str, Dict] = None  # DR_number -> installation_data
    current_dr: Optional[str] = None  # Currently active DR number
    awaiting_dr_input: bool = True

    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = {}
        if self.session_start is None:
            self.session_start = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.installations is None:
            self.installations = {}
        if self.location_data is None:
            self.location_data = {}

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
                current_step=0,  # Start with DR collection
                completed_steps={},
                session_start=datetime.now(),
                last_activity=datetime.now(),
                status="active",
                dr_number=None,
                location_verified=False,
                location_data={},
                installations={},
                current_dr=None,
                awaiting_dr_input=True
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
            if session.current_step > 12:
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
            session.current_step = 0  # Start with DR collection
            session.completed_steps = {}
            session.session_start = datetime.now()
            session.last_activity = datetime.now()
            session.status = "active"
            session.dr_number = None
            session.location_verified = False
            session.location_data = {}
            session.installations = {}
            session.current_dr = None
            session.awaiting_dr_input = True

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

    def switch_to_dr(self, phone_number: str, dr_number: str) -> bool:
        """Switch to or create installation with specific DR number"""
        phone_number = self._normalize_phone_number(phone_number)
        dr_number = dr_number.strip().upper()
        
        if phone_number not in self.sessions:
            return False
            
        session = self.sessions[phone_number]
        
        # Check installation limit (10 max)
        if dr_number not in session.installations and len(session.installations) >= 10:
            logger.warning(f"Installation limit reached for {phone_number}")
            return False
        
        # Save current installation state if exists (and not switching to same DR)
        if session.current_dr and session.current_dr != dr_number:
            session.installations[session.current_dr] = {
                "job_id": session.current_job_id,
                "current_step": session.current_step,
                "completed_steps": session.completed_steps.copy(),
                "dr_number": session.dr_number,
                "location_verified": session.location_verified,
                "location_data": session.location_data.copy(),
                "status": session.status,
                "last_activity": datetime.now().isoformat()
            }
        
        # Switch to or create new installation
        if dr_number in session.installations:
            # Load existing installation
            install = session.installations[dr_number]
            session.current_job_id = install["job_id"]
            session.current_step = install["current_step"]
            session.completed_steps = install["completed_steps"].copy()
            session.dr_number = install["dr_number"]
            session.location_verified = install["location_verified"]
            session.location_data = install["location_data"].copy()
            session.status = install["status"]
        else:
            # Create new installation
            job_id = self._generate_job_id(session.agent_id, dr_number)
            session.current_job_id = job_id
            session.current_step = -1  # Awaiting location
            session.completed_steps = {}
            session.dr_number = dr_number
            session.location_verified = False
            session.location_data = {}
            session.status = "active"
            
        session.current_dr = dr_number
        session.awaiting_dr_input = False
        session.last_activity = datetime.now()
        self._save_sessions()
        
        logger.info(f"Switched to DR {dr_number} for {phone_number}")
        return True
    
    def get_installation_list(self, phone_number: str) -> List[Dict]:
        """Get list of all installations for an agent"""
        phone_number = self._normalize_phone_number(phone_number)
        
        if phone_number not in self.sessions:
            return []
            
        session = self.sessions[phone_number]
        installations = []
        
        # Add current installation if it exists
        if session.current_dr:
            current_install = {
                "dr_number": session.current_dr,
                "job_id": session.current_job_id,
                "current_step": session.current_step,
                "completed_count": len(session.completed_steps),
                "progress_percent": (len(session.completed_steps) / 12) * 100,
                "status": session.status,
                "is_current": True
            }
            installations.append(current_install)
        
        # Add other installations
        for dr, install_data in session.installations.items():
            if dr != session.current_dr:  # Don't duplicate current
                install_info = {
                    "dr_number": dr,
                    "job_id": install_data["job_id"],
                    "current_step": install_data["current_step"],
                    "completed_count": len(install_data["completed_steps"]),
                    "progress_percent": (len(install_data["completed_steps"]) / 12) * 100,
                    "status": install_data["status"],
                    "is_current": False
                }
                installations.append(install_info)
                
        return sorted(installations, key=lambda x: x["dr_number"])
    
    def _generate_job_id(self, agent_id: str, dr_number: str = None) -> str:
        """Generate unique job ID with optional DR number"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if dr_number:
            return f"JOB_{timestamp}_{agent_id}_{dr_number}"
        return f"JOB_{timestamp}_{agent_id}"

    def _get_average_steps_completed(self) -> float:
        """Calculate average number of steps completed across all sessions"""
        if not self.sessions:
            return 0

        total_steps = sum(len(session.completed_steps) for session in self.sessions.values())
        return round(total_steps / len(self.sessions), 1)
