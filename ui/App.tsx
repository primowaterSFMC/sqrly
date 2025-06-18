import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from './src/contexts/AuthContext';
import { TaskProvider } from './src/contexts/TaskContext';
import { theme } from './src/theme';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import TasksScreen from './src/screens/TasksScreen';
import FocusScreen from './src/screens/FocusScreen';
import InsightsScreen from './src/screens/InsightsScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <AuthProvider>
      <TaskProvider>
        <PaperProvider theme={theme}>
          <NavigationContainer>
            <StatusBar style="dark" />
            <Tab.Navigator
              screenOptions={{
                tabBarActiveTintColor: theme.colors.primary,
                tabBarInactiveTintColor: '#888888',
                tabBarStyle: {
                  backgroundColor: theme.colors.background,
                  borderTopWidth: 0,
                  elevation: 20,
                  shadowColor: '#000',
                  shadowOffset: { width: 0, height: -3 },
                  shadowOpacity: 0.1,
                  shadowRadius: 10,
                  height: 85,
                  paddingBottom: 25,
                  paddingTop: 10,
                },
                headerStyle: {
                  backgroundColor: theme.colors.background,
                  elevation: 0,
                  shadowOpacity: 0,
                  borderBottomWidth: 0,
                },
                headerTintColor: theme.colors.text,
                headerTitleStyle: {
                  fontWeight: '600',
                  fontSize: 20,
                },
              }}
            >
              <Tab.Screen
                name="Home"
                component={HomeScreen}
                options={{
                  tabBarLabel: 'Today',
                  tabBarIcon: ({ color, size }) => (
                    <MaterialCommunityIcons name="calendar-today" size={size} color={color} />
                  ),
                }}
              />
              <Tab.Screen
                name="Tasks"
                component={TasksScreen}
                options={{
                  tabBarLabel: 'Tasks',
                  tabBarIcon: ({ color, size }) => (
                    <MaterialCommunityIcons name="checkbox-multiple-marked-outline" size={size} color={color} />
                  ),
                }}
              />
              <Tab.Screen
                name="Focus"
                component={FocusScreen}
                options={{
                  tabBarLabel: 'Focus',
                  tabBarIcon: ({ color, size }) => (
                    <MaterialCommunityIcons name="target" size={size} color={color} />
                  ),
                }}
              />
              <Tab.Screen
                name="Insights"
                component={InsightsScreen}
                options={{
                  tabBarLabel: 'Insights',
                  tabBarIcon: ({ color, size }) => (
                    <MaterialCommunityIcons name="lightbulb-outline" size={size} color={color} />
                  ),
                }}
              />
              <Tab.Screen
                name="Profile"
                component={ProfileScreen}
                options={{
                  tabBarLabel: 'Profile',
                  tabBarIcon: ({ color, size }) => (
                    <MaterialCommunityIcons name="account" size={size} color={color} />
                  ),
                }}
              />
            </Tab.Navigator>
          </NavigationContainer>
        </PaperProvider>
      </TaskProvider>
    </AuthProvider>
  );
}