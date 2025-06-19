import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService, { Task } from '../services/api';

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
  };

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}