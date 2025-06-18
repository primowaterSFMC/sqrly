from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base, DatabaseMixin

class SessionType(str, enum.Enum):
    COLLABORATION = "collaboration"
    TASK_BREAKDOWN = "task_breakdown"
    OVERWHELM_SUPPORT = "overwhelm_support"
    GOAL_PLANNING = "goal_planning"
    NATURAL_INPUT = "natural_input"

class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"

class CollaborationMode(str, enum.Enum):
    CONSULTATIVE = "consultative"  # AI asks questions and provides guidance
    DIRECTIVE = "directive"        # AI takes more control and provides specific instructions
    SUPPORTIVE = "supportive"      # AI provides emotional support and encouragement

class AISession(Base, DatabaseMixin):
    __tablename__ = "ai_sessions"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_type = Column(String(30), default=SessionType.COLLABORATION)
    collaboration_mode = Column(String(20), default=CollaborationMode.CONSULTATIVE)
    status = Column(String(20), default=SessionStatus.ACTIVE)
    
    # Context
    initial_user_input = Column(Text, nullable=True)
    session_goal = Column(String(255), nullable=True)
    context_data = Column(JSON, nullable=True)  # User state, tasks, energy level, etc.
    
    # AI configuration for this session
    ai_personality = Column(String(50), default="supportive")
    communication_style = Column(String(50), nullable=True)
    detail_level = Column(String(20), default="moderate")
    
    # Conversation tracking
    conversation_history = Column(JSON, nullable=True)  # Array of messages
    total_messages = Column(Integer, default=0)
    
    # Session metrics
    session_progress = Column(Float, default=0.0)  # 0-1 scale
    user_satisfaction = Column(Integer, nullable=True)  # 1-10 rating
    ai_confidence_avg = Column(Float, nullable=True)  # Average AI confidence
    
    # User state tracking
    initial_energy_level = Column(Integer, nullable=True)
    initial_stress_level = Column(Integer, nullable=True)
    final_energy_level = Column(Integer, nullable=True)
    final_stress_level = Column(Integer, nullable=True)
    
    # Outcomes
    tasks_created = Column(Integer, default=0)
    goals_created = Column(Integer, default=0)
    insights_generated = Column(JSON, nullable=True)
    action_items = Column(JSON, nullable=True)
    
    # OpenAI API tracking
    tokens_used = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ai_sessions")
    
    def __repr__(self):
        return f"<AISession(id={self.id}, type={self.session_type}, status={self.status})>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate session duration in minutes"""
        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.created_at
        return int(duration.total_seconds() / 60)
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.status == SessionStatus.ACTIVE
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add a message to the conversation history"""
        if self.conversation_history is None:
            self.conversation_history = []
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(message)
        self.total_messages = len(self.conversation_history)
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_user_message(self, content: str, user_state: dict = None):
        """Add user message with optional state information"""
        metadata = {}
        if user_state:
            metadata["user_state"] = user_state
        
        self.add_message("user", content, metadata)
    
    def add_ai_message(self, content: str, confidence: float = None, suggestions: list = None):
        """Add AI message with confidence and suggestions"""
        metadata = {}
        if confidence is not None:
            metadata["confidence"] = confidence
        if suggestions:
            metadata["suggestions"] = suggestions
        
        self.add_message("assistant", content, metadata)
        
        # Update average confidence
        if confidence is not None:
            if self.ai_confidence_avg is None:
                self.ai_confidence_avg = confidence
            else:
                # Running average
                total_ai_messages = len([m for m in self.conversation_history if m["role"] == "assistant"])
                self.ai_confidence_avg = ((self.ai_confidence_avg * (total_ai_messages - 1)) + confidence) / total_ai_messages
    
    def update_progress(self, progress: float):
        """Update session progress (0-1 scale)"""
        self.session_progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.utcnow()
    
    def complete_session(self, user_satisfaction: int = None):
        """Mark session as completed"""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if user_satisfaction:
            self.user_satisfaction = user_satisfaction
    
    def add_insight(self, insight_type: str, content: str, confidence: float = None):
        """Add AI-generated insight"""
        if self.insights_generated is None:
            self.insights_generated = []
        
        insight = {
            "type": insight_type,
            "content": content,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.insights_generated.append(insight)
        self.updated_at = datetime.utcnow()
    
    def add_action_item(self, action: str, priority: str = "medium"):
        """Add action item from the session"""
        if self.action_items is None:
            self.action_items = []
        
        action_item = {
            "action": action,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.action_items.append(action_item)
        self.updated_at = datetime.utcnow()
    
    def track_api_usage(self, tokens: int, cost: float):
        """Track OpenAI API usage"""
        self.tokens_used += tokens
        self.api_calls_made += 1
        self.total_cost += cost
        self.updated_at = datetime.utcnow()
    
    def get_conversation_summary(self, max_messages: int = 10) -> list:
        """Get recent conversation messages"""
        if not self.conversation_history:
            return []
        
        # Return last max_messages messages
        return self.conversation_history[-max_messages:]
    
    def should_check_overwhelm(self) -> bool:
        """Check if we should assess user for overwhelm based on session length"""
        return (
            self.duration_minutes > 30 or 
            self.total_messages > 20 or
            (self.initial_stress_level and self.initial_stress_level > 6)
        )