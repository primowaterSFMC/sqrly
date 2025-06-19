/**
 * API Service for Sqrly ADHD Planner
 * 
 * Centralized API communication with the FastAPI backend
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // Development - standard backend port
  : 'https://api.sqrly.com'; // Production

// Mock mode for development when backend is not available
const MOCK_MODE = false; // Backend is running, use real API

interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

interface Subtask {
  id: string;
  task_id: string;
  title: string;
  action?: string;
  completion_criteria?: string;
  sequence_order: number;
  depends_on_subtask_ids?: string[];
  subtask_type: 'preparation' | 'execution' | 'review' | 'micro';
  difficulty_level: 'easy' | 'medium' | 'hard';
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  estimated_minutes: number;
  actual_minutes?: number;
  energy_required: number;
  focus_required: number;
  initiation_support?: string;
  success_indicators?: string[];
  dopamine_reward?: string;
  preparation_steps?: string[];
  materials_needed?: string[];
  momentum_builder: boolean;
  confidence_boost: boolean;
  ai_generated: boolean;
  ai_confidence?: number;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
  is_blocked?: boolean;
  can_start?: boolean;
}

interface Task {
  id: string;
  title: string;
  description?: string;
  quadrant: 'focus' | 'schedule' | 'delegate' | 'eliminate';
  energy_level: number;
  time_estimate: number;
  difficulty_level: number;
  completed: boolean;
  created_at: string;
  due_date?: string;
  has_ai_breakdown: boolean;
  subtasks?: Subtask[];
  executive_difficulty?: number;
  initiation_difficulty?: number;
  completion_difficulty?: number;
}

// Backend task response interface (matches the actual API response)
interface BackendTask {
  id: string;
  title: string;
  description?: string;
  fc_quadrant?: number;
  required_energy_level: number;
  estimated_duration_minutes?: number;
  complexity_level: string;
  status: string;
  created_at: string;
  due_date?: string;
  executive_difficulty?: number;
  initiation_difficulty?: number;
  completion_difficulty?: number;
  progress_percentage?: number;
}

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar_url?: string | null;
  provider: string;
  onboarding_completed: boolean;
  subscription_tier: string;
  adhd_preferences?: any;
  created_at: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Mock data for development
const MOCK_TASKS: Task[] = [
  {
    id: '1',
    title: 'Complete project proposal presentation',
    description: 'Finalize slides for the Q1 project proposal presentation to the executive team',
    quadrant: 'focus',
    energy_level: 4,
    time_estimate: 90,
    difficulty_level: 3,
    completed: false,
    created_at: new Date().toISOString(),
    due_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
    has_ai_breakdown: true,
    executive_difficulty: 6,
    initiation_difficulty: 4,
    completion_difficulty: 7,
  },
  {
    id: '2',
    title: 'Review and respond to client feedback',
    description: 'Address urgent client concerns about the recent deliverable',
    quadrant: 'focus',
    energy_level: 3,
    time_estimate: 45,
    difficulty_level: 2,
    completed: false,
    created_at: new Date().toISOString(),
    due_date: new Date().toISOString(), // Today
    has_ai_breakdown: false,
    executive_difficulty: 5,
    initiation_difficulty: 3,
    completion_difficulty: 6,
  },
  {
    id: '3',
    title: 'Schedule annual health checkups',
    description: 'Book appointments with doctor, dentist, and eye doctor',
    quadrant: 'schedule',
    energy_level: 2,
    time_estimate: 15,
    difficulty_level: 1,
    completed: false,
    created_at: new Date().toISOString(),
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
    has_ai_breakdown: false,
    executive_difficulty: 4,
    initiation_difficulty: 6,
    completion_difficulty: 2,
  },
  {
    id: '4',
    title: 'Organize desk workspace',
    description: 'Clean and organize desk area for better focus and productivity',
    quadrant: 'delegate',
    energy_level: 3,
    time_estimate: 30,
    difficulty_level: 2,
    completed: true,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
    has_ai_breakdown: false,
    executive_difficulty: 3,
    initiation_difficulty: 4,
    completion_difficulty: 2,
  },
  {
    id: '5',
    title: 'Clean out old email folders',
    description: 'Archive or delete emails from 2022 and earlier',
    quadrant: 'eliminate',
    energy_level: 2,
    time_estimate: 45,
    difficulty_level: 2,
    completed: false,
    created_at: new Date().toISOString(),
    due_date: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days
    has_ai_breakdown: false,
    executive_difficulty: 4,
    initiation_difficulty: 5,
    completion_difficulty: 3,
  },
];

const MOCK_USER: User = {
  id: '1',
  email: 'jwhiteprimo@gmail.com',
  first_name: 'J',
  last_name: 'White',
  avatar_url: null,
  provider: 'email',
  onboarding_completed: false,
  subscription_tier: 'free',
  created_at: new Date().toISOString(),
  adhd_preferences: {
    energy_tracking_enabled: true,
    overwhelm_notifications: true,
    break_reminders: true,
  },
};

// Transform backend task to frontend format
function transformBackendTask(backendTask: BackendTask): Task {
  // Map fc_quadrant (1-4) to quadrant names
  const quadrantMap: { [key: number]: 'focus' | 'schedule' | 'delegate' | 'eliminate' } = {
    1: 'focus',      // Important & Urgent
    2: 'schedule',   // Important & Not Urgent
    3: 'delegate',   // Not Important & Urgent
    4: 'eliminate'   // Not Important & Not Urgent
  };

  // Map complexity level to difficulty level (1-3)
  const difficultyMap: { [key: string]: number } = {
    'micro': 1,
    'simple': 1,
    'medium': 2,
    'complex': 3
  };

  return {
    id: backendTask.id,
    title: backendTask.title,
    description: backendTask.description,
    quadrant: quadrantMap[backendTask.fc_quadrant || 1] || 'focus',
    energy_level: Math.min(5, Math.ceil((backendTask.required_energy_level || 5) / 2)), // Convert 1-10 to 1-5
    time_estimate: backendTask.estimated_duration_minutes || 30,
    difficulty_level: difficultyMap[backendTask.complexity_level] || 2,
    completed: backendTask.status === 'completed',
    created_at: backendTask.created_at,
    due_date: backendTask.due_date,
    has_ai_breakdown: false, // TODO: Add this field to backend response
    executive_difficulty: backendTask.executive_difficulty,
    initiation_difficulty: backendTask.initiation_difficulty,
    completion_difficulty: backendTask.completion_difficulty
  };
}

class ApiService {
  private baseURL: string;
  private authToken: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.loadAuthToken();
  }

  private async loadAuthToken(): Promise<void> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      this.authToken = token;
    } catch (error) {
      console.error('Error loading auth token:', error);
    }
  }

  private async saveAuthToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('auth_token', token);
      this.authToken = token;
    } catch (error) {
      console.error('Error saving auth token:', error);
    }
  }

  private async clearAuthToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem('auth_token');
      this.authToken = null;
    } catch (error) {
      console.error('Error clearing auth token:', error);
    }
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, clear it
          await this.clearAuthToken();
          throw new Error('Authentication required');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Authentication methods
  async login(email: string, password: string): Promise<User> {
    if (MOCK_MODE) {
      // Mock authentication
      if (email === 'jwhiteprimo@gmail.com' && password === 'SecuredPassword123') {
        await this.saveAuthToken('mock-jwt-token');
        return MOCK_USER;
      } else {
        throw new Error('Invalid credentials');
      }
    }

    const response = await this.makeRequest<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    await this.saveAuthToken(response.access_token);

    // Get user profile
    return this.getCurrentUser();
  }

  async register(firstName: string, lastName: string, email: string, password: string): Promise<User> {
    if (MOCK_MODE) {
      // Mock registration
      const mockUser: User = {
        id: '1',
        email: email,
        first_name: firstName,
        last_name: lastName,
        avatar_url: null,
        provider: 'email',
        onboarding_completed: false,
        subscription_tier: 'free',
        created_at: new Date().toISOString(),
      };
      await this.saveAuthToken('mock-jwt-token');
      return mockUser;
    }

    const response = await this.makeRequest<AuthTokens>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }),
    });

    await this.saveAuthToken(response.access_token);

    // Get user profile
    return this.getCurrentUser();
  }

  async logout(): Promise<void> {
    if (!MOCK_MODE) {
      try {
        await this.makeRequest('/auth/logout', {
          method: 'POST',
        });
      } catch (error) {
        // Logout endpoint might fail, but we still want to clear local tokens
        console.warn('Logout request failed:', error);
      }
    }
    await this.clearAuthToken();
  }

  async getCurrentUser(): Promise<User> {
    if (MOCK_MODE) {
      return MOCK_USER;
    }
    return this.makeRequest<User>('/auth/me');
  }

  // Task methods
  async getTasks(): Promise<Task[]> {
    if (MOCK_MODE) {
      return [...MOCK_TASKS];
    }
    const response = await this.makeRequest<{tasks: BackendTask[]}>('/tasks');
    return (response.tasks || []).map(transformBackendTask);
  }

  async getTask(id: string): Promise<Task> {
    const backendTask = await this.makeRequest<BackendTask>(`/tasks/${id}`);
    return transformBackendTask(backendTask);
  }

  async createTask(taskData: Omit<Task, 'id' | 'created_at'>): Promise<Task> {
    // Transform frontend task data to backend format
    const backendTaskData = {
      title: taskData.title,
      description: taskData.description,
      fc_quadrant: taskData.quadrant === 'focus' ? 1 : taskData.quadrant === 'schedule' ? 2 : taskData.quadrant === 'delegate' ? 3 : 4,
      required_energy_level: taskData.energy_level * 2, // Convert 1-5 to 1-10
      estimated_duration_minutes: taskData.time_estimate,
      complexity_level: taskData.difficulty_level === 1 ? 'simple' : taskData.difficulty_level === 2 ? 'medium' : 'complex',
      executive_difficulty: taskData.executive_difficulty,
      initiation_difficulty: taskData.initiation_difficulty,
      completion_difficulty: taskData.completion_difficulty
    };

    const backendTask = await this.makeRequest<BackendTask>('/tasks', {
      method: 'POST',
      body: JSON.stringify(backendTaskData),
    });
    return transformBackendTask(backendTask);
  }

  async updateTask(id: string, taskData: Partial<Task>): Promise<Task> {
    // Transform frontend task data to backend format
    const backendTaskData: any = {};
    if (taskData.title) backendTaskData.title = taskData.title;
    if (taskData.description) backendTaskData.description = taskData.description;
    if (taskData.quadrant) {
      backendTaskData.fc_quadrant = taskData.quadrant === 'focus' ? 1 : taskData.quadrant === 'schedule' ? 2 : taskData.quadrant === 'delegate' ? 3 : 4;
    }
    if (taskData.energy_level) backendTaskData.required_energy_level = taskData.energy_level * 2;
    if (taskData.time_estimate) backendTaskData.estimated_duration_minutes = taskData.time_estimate;
    if (taskData.difficulty_level) {
      backendTaskData.complexity_level = taskData.difficulty_level === 1 ? 'simple' : taskData.difficulty_level === 2 ? 'medium' : 'complex';
    }
    if (taskData.completed !== undefined) {
      backendTaskData.status = taskData.completed ? 'completed' : 'pending';
    }

    const backendTask = await this.makeRequest<BackendTask>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(backendTaskData),
    });
    return transformBackendTask(backendTask);
  }

  async deleteTask(id: string): Promise<void> {
    await this.makeRequest(`/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async completeTask(id: string): Promise<Task> {
    if (MOCK_MODE) {
      const taskIndex = MOCK_TASKS.findIndex(task => task.id === id);
      if (taskIndex !== -1) {
        MOCK_TASKS[taskIndex] = { ...MOCK_TASKS[taskIndex], completed: true };
        return MOCK_TASKS[taskIndex];
      }
      throw new Error('Task not found');
    }
    const backendTask = await this.makeRequest<BackendTask>(`/tasks/${id}/complete`, {
      method: 'POST',
    });
    return transformBackendTask(backendTask);
  }

  async getTodaysTasks(): Promise<Task[]> {
    if (MOCK_MODE) {
      const today = new Date().toDateString();
      return MOCK_TASKS.filter(task => {
        const dueDate = task.due_date ? new Date(task.due_date).toDateString() : null;
        return dueDate === today;
      });
    }
    const response = await this.makeRequest<{tasks: BackendTask[]}>('/tasks/today');
    return (response.tasks || []).map(transformBackendTask);
  }

  async getTasksByQuadrant(quadrant: string): Promise<Task[]> {
    const response = await this.makeRequest<{tasks: BackendTask[]}>(`/tasks/quadrant/${quadrant}`);
    return (response.tasks || []).map(transformBackendTask);
  }

  // Focus session methods
  async createFocusSession(sessionData: any): Promise<any> {
    if (MOCK_MODE) {
      // Mock focus session creation
      return {
        id: Date.now().toString(),
        ...sessionData,
        created_at: new Date().toISOString()
      };
    }
    return this.makeRequest('/focus-sessions', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async getFocusStats(timeframe: string = 'today'): Promise<any> {
    if (MOCK_MODE) {
      // Mock focus statistics
      return {
        completedSessions: 3,
        totalFocusTime: 4500, // 75 minutes
        averageSessionLength: 1500, // 25 minutes
        hyperfocusWarnings: 1,
        streak: 5
      };
    }
    return this.makeRequest(`/focus-sessions/stats?timeframe=${timeframe}`);
  }

  // AI methods
  async analyzeTask(description: string): Promise<any> {
    return this.makeRequest('/ai/analyze-task', {
      method: 'POST',
      body: JSON.stringify({ description }),
    });
  }

  async getAIInsights(): Promise<any> {
    return this.makeRequest('/ai/insights');
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.makeRequest('/health');
  }

  // Subtask methods
  async getSubtasksForTask(taskId: string): Promise<Subtask[]> {
    // Temporarily use mock mode for subtasks to test UI
    if (MOCK_MODE || true) {
      // Return mock subtasks for the task
      return [
        {
          id: '1',
          task_id: taskId,
          title: 'Review project requirements',
          action: 'Read through the project specification document',
          completion_criteria: 'All requirements understood and noted',
          sequence_order: 1,
          subtask_type: 'preparation',
          difficulty_level: 'easy',
          status: 'pending',
          estimated_minutes: 15,
          energy_required: 3,
          focus_required: 4,
          momentum_builder: true,
          confidence_boost: false,
          ai_generated: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_blocked: false,
          can_start: true
        },
        {
          id: '2',
          task_id: taskId,
          title: 'Create outline structure',
          action: 'Draft the main sections and subsections',
          completion_criteria: 'Clear outline with all major points',
          sequence_order: 2,
          subtask_type: 'execution',
          difficulty_level: 'medium',
          status: 'pending',
          estimated_minutes: 30,
          energy_required: 5,
          focus_required: 6,
          momentum_builder: false,
          confidence_boost: true,
          ai_generated: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_blocked: false,
          can_start: true
        }
      ];
    }
    const response = await this.makeRequest<Subtask[]>(`/subtasks/task/${taskId}`);
    return response;
  }

  async createSubtask(subtaskData: Omit<Subtask, 'id' | 'created_at' | 'updated_at' | 'is_blocked' | 'can_start'>): Promise<Subtask> {
    if (MOCK_MODE || true) {
      const newSubtask: Subtask = {
        ...subtaskData,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_blocked: false,
        can_start: true
      };
      return newSubtask;
    }
    return this.makeRequest<Subtask>('/subtasks', {
      method: 'POST',
      body: JSON.stringify(subtaskData),
    });
  }

  async updateSubtask(id: string, subtaskData: Partial<Subtask>): Promise<Subtask> {
    if (MOCK_MODE) {
      // Mock update
      return {
        id,
        ...subtaskData,
        updated_at: new Date().toISOString()
      } as Subtask;
    }
    return this.makeRequest<Subtask>(`/subtasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(subtaskData),
    });
  }

  async deleteSubtask(id: string): Promise<void> {
    if (MOCK_MODE) {
      return;
    }
    await this.makeRequest(`/subtasks/${id}`, {
      method: 'DELETE',
    });
  }

  async performSubtaskAction(id: string, action: string, notes?: string, actualMinutes?: number): Promise<Subtask> {
    if (MOCK_MODE || true) {
      // Mock action
      return {
        id,
        task_id: 'mock-task-id',
        title: 'Mock Subtask',
        sequence_order: 1,
        subtask_type: 'execution',
        difficulty_level: 'medium',
        status: action === 'complete' ? 'completed' : action === 'start' ? 'in_progress' : 'skipped',
        estimated_minutes: 15,
        energy_required: 5,
        focus_required: 5,
        momentum_builder: false,
        confidence_boost: false,
        ai_generated: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_blocked: false,
        can_start: true,
        ...(action === 'complete' && { completed_at: new Date().toISOString() }),
        ...(action === 'start' && { started_at: new Date().toISOString() }),
        ...(actualMinutes && { actual_minutes: actualMinutes })
      } as Subtask;
    }
    return this.makeRequest<Subtask>(`/subtasks/${id}/action`, {
      method: 'POST',
      body: JSON.stringify({
        action,
        notes,
        actual_minutes: actualMinutes
      }),
    });
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (MOCK_MODE) {
      return !!this.authToken;
    }
    return !!this.authToken;
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export types
export type { Task, Subtask, User, AuthTokens, ApiResponse };

export default apiService;
