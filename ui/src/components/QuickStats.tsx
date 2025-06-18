import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Surface } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';

export default function QuickStats() {
  const stats = [
    {
      icon: 'fire',
      label: 'Streak',
      value: '3 days',
      color: colors.accent,
    },
    {
      icon: 'target',
      label: 'Focus Time',
      value: '2h 15m',
      color: colors.focusHighlight,
    },
    {
      icon: 'checkbox-marked-circle',
      label: 'Completed',
      value: '12 tasks',
      color: colors.success,
    },
  ];

  return (
    <View style={styles.container}>
      {stats.map((stat, index) => (
        <Surface key={index} style={styles.statCard} elevation={1}>
          <MaterialCommunityIcons 
            name={stat.icon as any} 
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