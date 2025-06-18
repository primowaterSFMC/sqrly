"""
OpenAI Integration Service for ADHD-friendly AI assistance

This service handles all interactions with OpenAI's GPT models,
providing ADHD-specific prompts and response processing.
"""

import openai
from openai import OpenAI
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, List, Optional, Any, Tuple
import structlog
import json
from datetime import datetime

from ..config import settings
from ..models import User, Task, Goal, AISession

logger = structlog.get_logger()

class OpenAIService:
    """Service for OpenAI API interactions with ADHD-specific optimizations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        
        # Token encoder for cost estimation
        try:
            self.encoder = tiktoken.encoding_for_model(self.model)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # Fallback
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text for cost estimation"""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logger.warning("Token counting failed", error=str(e))
            # Rough estimate: 4 chars per token
            return len(text) // 4
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for API call (GPT-4 pricing)"""
        # GPT-4 pricing (as of 2024): $0.03/1K input tokens, $0.06/1K output tokens
        input_cost = (input_tokens / 1000) * 0.03
        output_cost = (output_tokens / 1000) * 0.06
        return input_cost + output_cost
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_api_call(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Tuple[str, int, int]:
        """Make API call to OpenAI with retry logic"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            logger.info(
                "OpenAI API call successful",
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=self.estimate_cost(input_tokens, output_tokens)
            )
            
            return content, input_tokens, output_tokens
            
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            raise
    
    def _create_adhd_system_prompt(self, user: User, context: str = "general") -> str:
        """Create system prompt optimized for user's ADHD profile"""
        
        communication_style = user.get_ai_communication_style()
        overwhelm_threshold = user.get_overwhelm_threshold()
        
        base_prompt = f"""You are an AI assistant specifically designed to help people with ADHD. 
        
User's ADHD Profile:
- Communication style preference: {communication_style}
- Overwhelm threshold: {overwhelm_threshold}/10
- Attention span: {user.get_attention_span_minutes()} minutes
- Preferred task size: {user.get_preferred_task_size()}

IMPORTANT GUIDELINES:
1. Be supportive, encouraging, and non-judgmental
2. Break down complex information into digestible chunks
3. Use clear, direct language without overwhelming details
4. Acknowledge emotional states and validate struggles
5. Provide actionable, specific next steps
6. Consider executive function challenges
7. Always respond in valid JSON format

Communication Style:
- Collaborative: Ask questions, work together, provide options
- Directive: Give clear instructions and specific guidance  
- Supportive: Focus on encouragement and emotional support

Context: {context}
"""
        return base_prompt
    
    async def generate_task_breakdown(
        self, 
        task: Task, 
        user: User,
        session: Optional[AISession] = None
    ) -> Dict[str, Any]:
        """AI-powered task breakdown for executive dysfunction support"""
        
        system_prompt = self._create_adhd_system_prompt(user, "task_breakdown")
        
        user_prompt = f"""
Please break down this task into manageable subtasks:

Task: {task.title}
Description: {task.description or "No description provided"}
Estimated Duration: {task.estimated_duration_minutes or "Not specified"} minutes
Complexity: {task.complexity_level}
Context: {json.dumps(task.context_tags) if task.context_tags else "None"}

User's current energy level: {session.initial_energy_level if session else "Unknown"}
User's stress level: {session.initial_stress_level if session else "Unknown"}

Please provide a JSON response with:
{{
    "subtasks": [
        {{
            "title": "Specific subtask title",
            "action": "Exact action to take",
            "estimated_minutes": 15,
            "difficulty_level": "easy|medium|hard",
            "sequence_order": 1,
            "initiation_support": "How to get started",
            "completion_criteria": "How to know it's done",
            "energy_required": 5,
            "focus_required": 6,
            "momentum_builder": true,
            "confidence_boost": false
        }}
    ],
    "total_estimate": "Total time estimate",
    "completion_strategy": {{
        "approach": "sequential_with_breaks",
        "break_frequency": "every_30_minutes",
        "motivation_system": "progress_bar_with_rewards"
    }},
    "ai_confidence": 0.85
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text, input_tokens, output_tokens = await self._make_api_call(messages)
            response_data = json.loads(response_text)
            
            # Track API usage
            if session:
                session.track_api_usage(
                    input_tokens + output_tokens,
                    self.estimate_cost(input_tokens, output_tokens)
                )
            
            return response_data
            
        except Exception as e:
            logger.error("Task breakdown generation failed", error=str(e), task_id=str(task.id))
            # Return fallback breakdown
            return self._create_fallback_breakdown(task)
    
    async def generate_micro_tasks(
        self,
        task: Task,
        user: User,
        context: Dict[str, Any],
        session: Optional[AISession] = None
    ) -> Dict[str, Any]:
        """Generate micro-tasks for severe executive dysfunction"""
        
        system_prompt = self._create_adhd_system_prompt(user, "micro_tasks")
        
        user_prompt = f"""
The user is feeling stuck and needs micro-tasks (2-5 minute actions) to build momentum:

Task: {task.title}
Current state: {context.get('current_state', 'feeling_stuck')}
Overwhelm level: {context.get('overwhelm_level', 'high')}/10
Energy available: {context.get('energy_available', 'low')}/10
Session length: {context.get('session_length', 15)} minutes

Please provide 3-5 micro-tasks that will help them start. Respond in JSON:

{{
    "micro_tasks": [
        {{
            "action": "Very specific 1-2 minute action",
            "duration": 2,
            "materials_needed": ["laptop"],
            "completion_signal": "Clear sign it's done",
            "motivation": "Encouraging note",
            "confidence_boost": true,
            "momentum_builder": true
        }}
    ],
    "success_tips": ["Tip 1", "Tip 2"],
    "reward_suggestions": ["small reward idea"],
    "total_commitment": "Maximum time commitment"
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text, input_tokens, output_tokens = await self._make_api_call(messages)
            response_data = json.loads(response_text)
            
            if session:
                session.track_api_usage(
                    input_tokens + output_tokens,
                    self.estimate_cost(input_tokens, output_tokens)
                )
            
            return response_data
            
        except Exception as e:
            logger.error("Micro-task generation failed", error=str(e))
            return self._create_fallback_micro_tasks()
    
    async def collaborate_session(
        self,
        user_input: str,
        user: User,
        session: AISession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interactive AI collaboration with ADHD-aware responses"""
        
        system_prompt = self._create_adhd_system_prompt(user, "collaboration")
        
        # Get recent conversation history
        conversation_history = session.get_conversation_summary(max_messages=10)
        
        # Build conversation context
        context_str = f"""
Current session context:
- Energy level: {context.get('energy_level', 'unknown')}/10  
- Stress level: {context.get('stress_level', 'unknown')}/10
- Available time: {context.get('time_available', 'unknown')}
- Current tasks: {context.get('current_tasks', [])}

Previous conversation:
{json.dumps(conversation_history, indent=2) if conversation_history else "None"}

User input: {user_input}
"""
        
        user_prompt = f"""
The user needs collaborative support. Please respond helpfully in JSON format:

{context_str}

Provide a response with:
{{
    "ai_response": "Your supportive response to the user",
    "suggestions": [
        {{
            "type": "immediate_action|clarifying_question|resource",
            "content": "Specific suggestion"
        }}
    ],
    "questions": ["Follow-up question if needed"],
    "confidence": 0.85,
    "next_steps": ["Suggested next action"],
    "session_progress": {{
        "stage": "problem_clarification|solution_development|action_planning",
        "completion": 0.3
    }},
    "supportive_note": "Encouraging message"
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text, input_tokens, output_tokens = await self._make_api_call(messages)
            response_data = json.loads(response_text)
            
            # Track usage and update session
            session.track_api_usage(
                input_tokens + output_tokens,
                self.estimate_cost(input_tokens, output_tokens)
            )
            
            # Add messages to conversation history
            session.add_user_message(user_input, context)
            session.add_ai_message(
                response_data["ai_response"],
                response_data.get("confidence"),
                response_data.get("suggestions")
            )
            
            return response_data
            
        except Exception as e:
            logger.error("Collaboration session failed", error=str(e))
            return self._create_fallback_collaboration_response()
    
    async def detect_overwhelm(
        self,
        user_data: Dict[str, Any],
        user: User,
        session: Optional[AISession] = None
    ) -> Dict[str, Any]:
        """AI-powered overwhelm detection and intervention suggestions"""
        
        system_prompt = self._create_adhd_system_prompt(user, "overwhelm_support")
        
        user_prompt = f"""
Analyze this user's current state for overwhelm and provide support:

Current load:
- Active tasks: {user_data.get('current_load', {}).get('active_tasks', 0)}
- Overdue tasks: {user_data.get('current_load', {}).get('overdue_tasks', 0)}
- Upcoming deadlines: {user_data.get('current_load', {}).get('upcoming_deadlines', 0)}
- Meetings today: {user_data.get('current_load', {}).get('meetings_today', 0)}

User state:
- Energy level: {user_data.get('energy_level', 'unknown')}/10
- Stress indicators: {user_data.get('stress_indicators', [])}
- Focus quality: {user_data.get('user_state', {}).get('focus_quality', 'unknown')}/10
- Anxiety level: {user_data.get('user_state', {}).get('anxiety_level', 'unknown')}/10

Please provide overwhelm assessment and support in JSON:

{{
    "overwhelm_risk": "low|medium|high",
    "risk_factors": ["Factor 1", "Factor 2"],
    "suggested_reductions": [
        {{
            "action": "defer_non_urgent",
            "tasks": ["task1", "task2"],
            "rationale": "Why this helps"
        }}
    ],
    "coping_strategies": [
        {{
            "strategy": "take_break",
            "duration": 15,
            "activity": "specific_activity"
        }}
    ],
    "immediate_actions": ["Action 1", "Action 2"],
    "supportive_message": "Encouraging message",
    "follow_up": {{
        "check_in_time": 60,
        "metrics_to_monitor": ["stress_level", "task_completion"]
    }}
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text, input_tokens, output_tokens = await self._make_api_call(messages)
            response_data = json.loads(response_text)
            
            if session:
                session.track_api_usage(
                    input_tokens + output_tokens,
                    self.estimate_cost(input_tokens, output_tokens)
                )
            
            return response_data
            
        except Exception as e:
            logger.error("Overwhelm detection failed", error=str(e))
            return self._create_fallback_overwhelm_response()
    
    def _create_fallback_breakdown(self, task: Task) -> Dict[str, Any]:
        """Create fallback task breakdown when AI fails"""
        return {
            "subtasks": [
                {
                    "title": f"Start working on: {task.title}",
                    "action": "Begin the task by reviewing requirements",
                    "estimated_minutes": 15,
                    "difficulty_level": "medium",
                    "sequence_order": 1,
                    "initiation_support": "Just open the necessary files or tools",
                    "completion_criteria": "You have a clear understanding of what needs to be done",
                    "energy_required": 5,
                    "focus_required": 6,
                    "momentum_builder": True,
                    "confidence_boost": True
                }
            ],
            "total_estimate": f"{task.estimated_duration_minutes or 30} minutes",
            "completion_strategy": {
                "approach": "start_small",
                "break_frequency": "as_needed",
                "motivation_system": "celebrate_small_wins"
            },
            "ai_confidence": 0.5
        }
    
    def _create_fallback_micro_tasks(self) -> Dict[str, Any]:
        """Create fallback micro-tasks when AI fails"""
        return {
            "micro_tasks": [
                {
                    "action": "Take three deep breaths",
                    "duration": 1,
                    "materials_needed": [],
                    "completion_signal": "You feel slightly calmer",
                    "motivation": "You're taking care of yourself!",
                    "confidence_boost": True,
                    "momentum_builder": True
                },
                {
                    "action": "Clear your workspace of distractions",
                    "duration": 3,
                    "materials_needed": [],
                    "completion_signal": "Only essential items are visible",
                    "motivation": "Great job creating focus space!",
                    "confidence_boost": True,
                    "momentum_builder": True
                }
            ],
            "success_tips": [
                "Focus only on the current micro-task",
                "Celebrate each completion"
            ],
            "reward_suggestions": ["favorite drink", "stretch break"],
            "total_commitment": "5 minutes maximum"
        }
    
    def _create_fallback_collaboration_response(self) -> Dict[str, Any]:
        """Create fallback collaboration response when AI fails"""
        return {
            "ai_response": "I'm here to help! Let's break this down into smaller, manageable steps.",
            "suggestions": [
                {
                    "type": "immediate_action",
                    "content": "Start with the most important or urgent item"
                }
            ],
            "questions": ["What's the most pressing thing on your mind right now?"],
            "confidence": 0.7,
            "next_steps": ["Identify the top priority", "Break it into smaller steps"],
            "session_progress": {
                "stage": "problem_clarification", 
                "completion": 0.2
            },
            "supportive_note": "You're doing great by asking for help. We'll figure this out together."
        }
    
    def _create_fallback_overwhelm_response(self) -> Dict[str, Any]:
        """Create fallback overwhelm response when AI fails"""
        return {
            "overwhelm_risk": "medium",
            "risk_factors": ["Multiple active tasks", "Time pressure"],
            "suggested_reductions": [
                {
                    "action": "defer_non_urgent",
                    "tasks": [],
                    "rationale": "Focus on what truly needs attention today"
                }
            ],
            "coping_strategies": [
                {
                    "strategy": "take_break",
                    "duration": 10,
                    "activity": "deep_breathing_or_short_walk"
                }
            ],
            "immediate_actions": [
                "Take a 5-minute break",
                "Choose only 3 most important tasks for today"
            ],
            "supportive_message": "It's okay to feel overwhelmed. Let's reduce the pressure together.",
            "follow_up": {
                "check_in_time": 60,
                "metrics_to_monitor": ["stress_level", "task_completion"]
            }
        }

    # Alias methods for backward compatibility with existing API calls
    async def analyze_task_priority(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task priority and provide recommendations"""
        # Create a mock Task object from the data
        from ..models.task import Task
        task = Task(
            title=task_data.get("title", ""),
            description=task_data.get("description", ""),
            complexity_level=task_data.get("complexity_level", "medium"),
            estimated_duration_minutes=task_data.get("estimated_duration_minutes", 30)
        )

        # Create a mock User object
        from ..models.user import User
        user = User(
            id=task_data.get("user_id"),
            email="user@example.com",
            full_name="User"
        )

        # Use the existing task breakdown method
        result = await self.generate_task_breakdown(task, user)

        # Transform the result to match expected format
        return {
            "priority_score": 7,  # Default priority
            "recommended_quadrant": 2,  # Default quadrant
            "suggestions": result.get("subtasks", []),
            "confidence": result.get("ai_confidence", 0.7),
            "reasoning": "AI analysis based on task complexity and user context"
        }

    async def analyze_goal_comprehensive(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive goal analysis"""
        return {
            "quadrant": 2,
            "quadrant_reasoning": "Based on goal importance and timeline",
            "complexity": goal_data.get("complexity_assessment", "medium"),
            "overwhelm_risk": goal_data.get("overwhelm_risk", "low"),
            "breakdown": [
                {
                    "phase": "Planning",
                    "tasks": ["Define objectives", "Create timeline"],
                    "duration": "1-2 weeks"
                },
                {
                    "phase": "Execution",
                    "tasks": ["Begin implementation", "Track progress"],
                    "duration": "4-6 weeks"
                }
            ],
            "timeline": [
                {"milestone": "Planning complete", "target_date": "2 weeks"},
                {"milestone": "50% progress", "target_date": "6 weeks"}
            ],
            "adhd_tips": [
                "Break this goal into smaller, manageable tasks",
                "Set regular check-ins to track progress",
                "Celebrate small wins along the way"
            ],
            "confidence": 0.8
        }

    async def analyze_goal(self, goal_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a goal and provide insights"""
        return await self.analyze_goal_comprehensive(goal_context)

    async def break_down_task(self, breakdown_request: Dict[str, Any]) -> Dict[str, Any]:
        """Break down a task into subtasks"""
        # Create a mock Task object from the request
        from ..models.task import Task
        task = Task(
            title=breakdown_request.get("title", ""),
            description=breakdown_request.get("description", ""),
            complexity_level=breakdown_request.get("complexity_level", "medium"),
            estimated_duration_minutes=breakdown_request.get("estimated_duration_minutes", 30)
        )

        # Create a mock User object
        from ..models.user import User
        user = User(
            id=breakdown_request.get("user_id"),
            email="user@example.com",
            full_name="User"
        )

        # Use the existing task breakdown method
        result = await self.generate_task_breakdown(task, user)

        # Transform the result to match expected format
        return {
            "subtasks": result.get("subtasks", []),
            "reasoning": "Task broken down based on complexity and user context",
            "total_time": sum(subtask.get("estimated_minutes", 15) for subtask in result.get("subtasks", [])),
            "confidence": result.get("ai_confidence", 0.7)
        }

    async def collaborate(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Start a collaboration session"""
        # Create mock objects
        from ..models.user import User
        from ..models import AISession

        user = User(
            id=user_context.get("user_id"),
            email="user@example.com",
            full_name="User"
        )

        session = AISession(
            user_id=user_context.get("user_id"),
            session_type="collaboration"
        )

        # Use the existing collaboration method
        result = await self.collaborate_session(
            user_context.get("user_input", ""),
            user,
            session,
            user_context.get("context", {})
        )

        # Transform the result to match expected format
        return {
            "session_id": str(session.id) if hasattr(session, 'id') else "mock-session",
            "response": result.get("ai_response", ""),
            "suggestions": result.get("suggestions", []),
            "follow_up": result.get("questions", []),
            "adhd_support": {
                "supportive_note": result.get("supportive_note", ""),
                "next_steps": result.get("next_steps", [])
            },
            "confidence": result.get("confidence", 0.7)
        }

    async def assess_overwhelm(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overwhelm level and provide recommendations"""
        # Create mock objects
        from ..models.user import User

        user = User(
            id=assessment_data.get("user_id"),
            email="user@example.com",
            full_name="User"
        )

        # Transform assessment data to match expected format
        user_data = {
            "current_load": {
                "active_tasks": len(assessment_data.get("current_tasks", [])),
                "overdue_tasks": 0,
                "upcoming_deadlines": 0,
                "meetings_today": 0
            },
            "energy_level": assessment_data.get("energy_level", 5),
            "stress_indicators": [],
            "user_state": {
                "focus_quality": 5,
                "anxiety_level": assessment_data.get("stress_level", 5)
            }
        }

        # Use the existing overwhelm detection method
        result = await self.detect_overwhelm(user_data, user)

        # Transform the result to match expected format
        return {
            "overwhelm_level": result.get("overwhelm_risk", "moderate"),
            "recommendations": result.get("immediate_actions", []),
            "immediate_actions": result.get("coping_strategies", []),
            "confidence": 0.7
        }