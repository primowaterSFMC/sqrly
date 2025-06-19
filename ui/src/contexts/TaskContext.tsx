import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService, { Task, Subtask } from '../services/api';

// Task interface is now imported from api service

interface TaskContextType {
  tasks: Task[];
  todaysTasks: Task[];
  completedToday: Task[];
  isLoading: boolean;
  error: string | null;
  addTask: (task: Omit<Task, 'id' | 'created_at'>) => Promise<void>;
  updateTask: (id: string, taskData: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  completeTask: (id: string) => Promise<void>;
  getTodaysTasks: () => Task[];
  getTasksByQuadrant: (quadrant: string) => Task[];
  refreshTasks: () => Promise<void>;
  // Subtask management
  getSubtasksForTask: (taskId: string) => Promise<Subtask[]>;
  addSubtask: (subtaskData: Omit<Subtask, 'id' | 'created_at' | 'updated_at' | 'is_blocked' | 'can_start'>) => Promise<Subtask>;
  updateSubtask: (id: string, subtaskData: Partial<Subtask>) => Promise<Subtask>;
  deleteSubtask: (id: string) => Promise<void>;
  toggleSubtask: (id: string) => Promise<Subtask>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export function useTask() {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
}

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);

      if (apiService.isAuthenticated()) {
        const fetchedTasks = await apiService.getTasks();
        setTasks(fetchedTasks);
      } else {
        // If not authenticated, use empty array or redirect to login
        setTasks([]);
        setError('Authentication required');
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
      setError(error instanceof Error ? error.message : 'Failed to load tasks');

      // Fallback to empty array on error
      setTasks([]);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshTasks = async () => {
    await loadTasks();
  };

  const addTask = async (taskData: Omit<Task, 'id' | 'created_at'>) => {
    try {
      const newTask = await apiService.createTask(taskData);
      setTasks(prevTasks => [...prevTasks, newTask]);
    } catch (error) {
      console.error('Error adding task:', error);
      setError(error instanceof Error ? error.message : 'Failed to add task');
      throw error;
    }
  };

  const updateTask = async (id: string, taskData: Partial<Task>) => {
    try {
      const updatedTask = await apiService.updateTask(id, taskData);
      setTasks(prevTasks =>
        prevTasks.map(task => task.id === id ? updatedTask : task)
      );
    } catch (error) {
      console.error('Error updating task:', error);
      setError(error instanceof Error ? error.message : 'Failed to update task');
      throw error;
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await apiService.deleteTask(id);
      setTasks(prevTasks => prevTasks.filter(task => task.id !== id));
    } catch (error) {
      console.error('Error deleting task:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete task');
      throw error;
    }
  };

  const completeTask = async (id: string) => {
    try {
      const completedTask = await apiService.completeTask(id);
      setTasks(prevTasks =>
        prevTasks.map(task => task.id === id ? completedTask : task)
      );
    } catch (error) {
      console.error('Error completing task:', error);
      setError(error instanceof Error ? error.message : 'Failed to complete task');
      throw error;
    }
  };

  const getTodaysTasks = () => {
    if (!Array.isArray(tasks)) return [];

    const today = new Date().toDateString();
    return tasks.filter(task => {
      const taskDate = new Date(task.created_at).toDateString();
      return taskDate === today || task.due_date === today;
    });
  };

  const getTasksByQuadrant = (quadrant: string) => {
    if (!Array.isArray(tasks)) return [];

    return tasks.filter(task => task.quadrant === quadrant);
  };

  const todaysTasks = getTodaysTasks();
  const completedToday = todaysTasks.filter(task => task.completed);

  // Subtask management functions
  const getSubtasksForTask = async (taskId: string): Promise<Subtask[]> => {
    try {
      return await apiService.getSubtasksForTask(taskId);
    } catch (error) {
      console.error('Error fetching subtasks:', error);
      // Don't set global error for subtask failures to avoid breaking the UI
      // Return empty array as fallback
      return [];
    }
  };

  const addSubtask = async (subtaskData: Omit<Subtask, 'id' | 'created_at' | 'updated_at' | 'is_blocked' | 'can_start'>): Promise<Subtask> => {
    try {
      const newSubtask = await apiService.createSubtask(subtaskData);
      return newSubtask;
    } catch (error) {
      console.error('Error adding subtask:', error);
      setError(error instanceof Error ? error.message : 'Failed to add subtask');
      throw error;
    }
  };

  const updateSubtask = async (id: string, subtaskData: Partial<Subtask>): Promise<Subtask> => {
    try {
      const updatedSubtask = await apiService.updateSubtask(id, subtaskData);
      return updatedSubtask;
    } catch (error) {
      console.error('Error updating subtask:', error);
      setError(error instanceof Error ? error.message : 'Failed to update subtask');
      throw error;
    }
  };

  const deleteSubtask = async (id: string): Promise<void> => {
    try {
      await apiService.deleteSubtask(id);
    } catch (error) {
      console.error('Error deleting subtask:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete subtask');
      throw error;
    }
  };

  const toggleSubtask = async (id: string): Promise<Subtask> => {
    try {
      // Get current subtask to determine action
      const subtasks = await apiService.getSubtasksForTask(''); // This will need the task ID
      const subtask = subtasks.find(st => st.id === id);
      if (!subtask) throw new Error('Subtask not found');

      const action = subtask.status === 'completed' ? 'start' : 'complete';
      return await apiService.performSubtaskAction(id, action);
    } catch (error) {
      console.error('Error toggling subtask:', error);
      setError(error instanceof Error ? error.message : 'Failed to toggle subtask');
      throw error;
    }
  };

  const value: TaskContextType = {
    tasks,
    todaysTasks,
    completedToday,
    isLoading,
    error,
    addTask,
    updateTask,
    deleteTask,
    completeTask,
    getTodaysTasks,
    getTasksByQuadrant,
    refreshTasks,
    getSubtasksForTask,
    addSubtask,
    updateSubtask,
    deleteSubtask,
    toggleSubtask,
  };

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}