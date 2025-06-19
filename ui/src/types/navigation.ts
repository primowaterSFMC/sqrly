/**
 * Navigation type definitions for Sqrly ADHD Planner
 * 
 * This file contains all the navigation parameter types for proper TypeScript
 * support throughout the application.
 */

import { NavigationProp, RouteProp } from '@react-navigation/native';

// Root Tab Navigator Parameters
export type RootTabParamList = {
  Home: undefined;
  Tasks: undefined;
  Focus: { mode?: 'pomodoro' | 'custom' };
  Insights: undefined;
  Profile: undefined;
};

// Task Stack Navigator Parameters
export type TaskStackParamList = {
  TaskList: undefined;
  TaskDetail: { taskId: string };
  AddTask: undefined;
  QuickCapture: undefined;
};

// Focus Stack Navigator Parameters
export type FocusStackParamList = {
  FocusHome: { mode?: 'pomodoro' | 'custom' };
  ActiveSession: { 
    mode: 'pomodoro' | 'custom';
    duration?: number;
    taskId?: string;
  };
};

// Combined navigation types for screens
export type HomeScreenNavigationProp = NavigationProp<RootTabParamList, 'Home'>;
export type TasksScreenNavigationProp = NavigationProp<RootTabParamList, 'Tasks'>;
export type FocusScreenNavigationProp = NavigationProp<RootTabParamList, 'Focus'>;
export type InsightsScreenNavigationProp = NavigationProp<RootTabParamList, 'Insights'>;
export type ProfileScreenNavigationProp = NavigationProp<RootTabParamList, 'Profile'>;

// Task-specific navigation types
export type TaskDetailScreenNavigationProp = NavigationProp<TaskStackParamList, 'TaskDetail'>;
export type TaskDetailScreenRouteProp = RouteProp<TaskStackParamList, 'TaskDetail'>;
export type AddTaskScreenNavigationProp = NavigationProp<TaskStackParamList, 'AddTask'>;
export type QuickCaptureScreenNavigationProp = NavigationProp<TaskStackParamList, 'QuickCapture'>;

// Focus-specific navigation types
export type FocusHomeScreenNavigationProp = NavigationProp<FocusStackParamList, 'FocusHome'>;
export type FocusHomeScreenRouteProp = RouteProp<FocusStackParamList, 'FocusHome'>;
export type ActiveSessionScreenNavigationProp = NavigationProp<FocusStackParamList, 'ActiveSession'>;
export type ActiveSessionScreenRouteProp = RouteProp<FocusStackParamList, 'ActiveSession'>;

// Generic navigation props for components that need navigation
export interface NavigationProps {
  navigation: NavigationProp<any>;
}

export interface RouteProps<T = any> {
  route: RouteProp<any, any>;
}

export interface NavigationAndRouteProps<T = any> extends NavigationProps, RouteProps<T> {}

// Screen component props interfaces
export interface HomeScreenProps {
  navigation: HomeScreenNavigationProp;
}

export interface TasksScreenProps {
  navigation: TasksScreenNavigationProp;
}

export interface FocusScreenProps {
  navigation: FocusScreenNavigationProp;
  route: RouteProp<RootTabParamList, 'Focus'>;
}

export interface InsightsScreenProps {
  navigation: InsightsScreenNavigationProp;
}

export interface ProfileScreenProps {
  navigation: ProfileScreenNavigationProp;
}

export interface TaskDetailScreenProps {
  navigation: TaskDetailScreenNavigationProp;
  route: TaskDetailScreenRouteProp;
}

export interface AddTaskScreenProps {
  navigation: AddTaskScreenNavigationProp;
}

export interface QuickCaptureScreenProps {
  navigation: QuickCaptureScreenNavigationProp;
}

// Helper type for screens that need both navigation and route
export type ScreenProps<
  ParamList extends Record<string, object | undefined>,
  RouteName extends keyof ParamList
> = {
  navigation: NavigationProp<ParamList, RouteName>;
  route: RouteProp<ParamList, RouteName>;
};

// Common navigation actions
export interface NavigationActions {
  goBack: () => void;
  navigate: (screen: string, params?: any) => void;
  reset: (state: any) => void;
  setParams: (params: any) => void;
}

// ADHD-specific navigation helpers
export interface ADHDNavigationHelpers {
  // Quick actions for ADHD users
  quickCapture: () => void;
  startFocusSession: (mode?: 'pomodoro' | 'custom') => void;
  viewTaskDetail: (taskId: string) => void;
  openAIAssistant: () => void;
  
  // Context-aware navigation
  navigateBasedOnEnergy: (energyLevel: number) => void;
  suggestNextAction: () => void;
}

export default RootTabParamList;
