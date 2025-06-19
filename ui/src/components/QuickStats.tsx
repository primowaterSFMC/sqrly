import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Surface } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import { useTask } from '../contexts/TaskContext';

export default function QuickStats() {
  const { tasks, todaysTasks, completedToday } = useTask();

  // Calculate weekly streak
  const calculateWeeklyStreak = (): number => {
    const today = new Date();
    let streak = 0;

    for (let i = 0; i < 7; i++) {
      const checkDate = new Date(today);
      checkDate.setDate(today.getDate() - i);
      const dateString = checkDate.toDateString();

      const dayTasks = tasks.filter(task => {
        const taskDate = new Date(task.created_at).toDateString();
        return taskDate === dateString;
      });

      const completedTasks = dayTasks.filter(task => task.completed);

      if (completedTasks.length > 0) {
        streak++;
      } else if (i === 0) {
        break;
      } else {
        break;
      }
    }

    return streak;
  };

  // Calculate total focus time (estimated)
  const calculateFocusTime = (): string => {
    const totalMinutes = completedToday.reduce((sum, task) => sum + (task.time_estimate || 0), 0);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const weeklyStreak = calculateWeeklyStreak();
  const focusTime = calculateFocusTime();

  const stats = [
    {
      icon: 'fire' as const,
      label: 'Streak',
      value: `${weeklyStreak} ${weeklyStreak === 1 ? 'day' : 'days'}`,
      color: colors.accent,
    },
    {
      icon: 'target' as const,
      label: 'Focus Time',
      value: focusTime,
      color: colors.focusHighlight,
    },
    {
      icon: 'checkbox-marked-circle' as const,
      label: 'Completed',
      value: `${completedToday.length} ${completedToday.length === 1 ? 'task' : 'tasks'}`,
      color: colors.success,
    },
  ];

  return (
    <View style={styles.container}>
      {stats.map((stat, index) => (
        <Surface key={index} style={styles.statCard} elevation={1}>
          <MaterialCommunityIcons
            name={stat.icon}
            size={24}
            color={stat.color}
            style={styles.icon}
          />
          <Text style={styles.value}>{stat.value}</Text>
          <Text style={styles.label}>{stat.label}</Text>
        </Surface>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    backgroundColor: colors.surface,
    alignItems: 'center',
  },
  icon: {
    marginBottom: 8,
  },
  value: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  label: {
    fontSize: 12,
    color: colors.textSecondary,
  },
});