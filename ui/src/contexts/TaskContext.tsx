import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

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
  subtasks?: Task[];
  executive_difficulty?: number;
  initiation_difficulty?: number;
  completion_difficulty?: number;
}

interface TaskContextType {
  tasks: Task[];
  todaysTasks: Task[];
  completedToday: Task[];
  isLoading: boolean;
  addTask: (task: Omit<Task, 'id' | 'created_at'>) => Promise<void>;
  updateTask: (id: string, taskData: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  completeTask: (id: string) => Promise<void>;
  getTodaysTasks: () => Task[];
  getTasksByQuadrant: (quadrant: string) => Task[];
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

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const storedTasks = await AsyncStorage.getItem('tasks');
      if (storedTasks) {
        setTasks(JSON.parse(storedTasks));
      } else {
        // Initialize with some mock data
        const mockTasks: Task[] = [
          {
            id: '1',
            title: 'Review project proposal and provide feedback',
            description: 'Go through the new project proposal document and provide detailed feedback',
            quadrant: 'focus',
            energy_level: 4,
            time_estimate: 45,
            difficulty_level: 3,
            completed: false,
            created_at: new Date().toISOString(),
            has_ai_breakdown: true,
            executive_difficulty: 3,
            initiation_difficulty: 2,
            completion_difficulty: 4,
          },
          {
            id: '2',
            title: 'Schedule dentist appointment',
            quadrant: 'schedule',
            energy_level: 2,
            time_estimate: 10,
            difficulty_level: 1,
            completed: false,
            created_at: new Date().toISOString(),
            has_ai_breakdown: false,
            executive_difficulty: 1,
            initiation_difficulty: 3,
            completion_difficulty: 1,
          },
          {
            id: '3',
            title: 'Organize desk workspace',
            quadrant: 'delegate',
            energy_level: 3,
            time_estimate: 30,
            difficulty_level: 2,
            completed: true,
            created_at: new Date().toISOString(),
            has_ai_breakdown: false,
            executive_difficulty: 2,
            initiation_difficulty: 4,
            completion_difficulty: 2,
          },
        ];
        setTasks(mockTasks);
        await AsyncStorage.setItem('tasks', JSON.stringify(mockTasks));
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveTasks = async (updatedTasks: Task[]) => {
    try {
      await AsyncStorage.setItem('tasks', JSON.stringify(updatedTasks));
    } catch (error) {
      console.error('Error saving tasks:', error);
    }
  };

  const addTask = async (taskData: Omit<Task, 'id' | 'created_at'>) => {
    const newTask: Task = {
      ...taskData,
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
    };

    const updatedTasks = [...tasks, newTask];
    setTasks(updatedTasks);
    await saveTasks(updatedTasks);
  };

  const updateTask = async (id: string, taskData: Partial<Task>) => {
    const updatedTasks = tasks.map(task =>
      task.id === id ? { ...task, ...taskData } : task
    );
    setTasks(updatedTasks);
    await saveTasks(updatedTasks);
  };

  const deleteTask = async (id: string) => {
    const updatedTasks = tasks.filter(task => task.id !== id);
    setTasks(updatedTasks);
    await saveTasks(updatedTasks);
  };

  const completeTask = async (id: string) => {
    await updateTask(id, { completed: true });
  };

  const getTodaysTasks = () => {
    const today = new Date().toDateString();
    return tasks.filter(task => {
      const taskDate = new Date(task.created_at).toDateString();
      return taskDate === today || task.due_date === today;
    });
  };

  const getTasksByQuadrant = (quadrant: string) => {
    return tasks.filter(task => task.quadrant === quadrant);
  };

  const todaysTasks = getTodaysTasks();
  const completedToday = todaysTasks.filter(task => task.completed);

  const value: TaskContextType = {
    tasks,
    todaysTasks,
    completedToday,
    isLoading,
    addTask,
    updateTask,
    deleteTask,
    completeTask,
    getTodaysTasks,
    getTasksByQuadrant,
  };

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}