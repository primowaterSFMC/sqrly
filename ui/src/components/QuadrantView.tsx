import React from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';
import { Text, Surface } from 'react-native-paper';
import { colors } from '../theme';

const { width, height } = Dimensions.get('window');

interface QuadrantViewProps {
  tasks: Array<{
    id: string;
    title: string;
    quadrant: string;
    energy_level: number;
    time_estimate: number;
  }>;
  onTaskPress: (taskId: string) => void;
}

type QuadrantKey = 'focus' | 'schedule' | 'delegate' | 'eliminate';

const quadrantConfig: Record<QuadrantKey, {
  title: string;
  subtitle: string;
  color: string;
  position: any;
}> = {
  focus: {
    title: 'Focus',
    subtitle: 'Important & Urgent',
    color: colors.accent,
    position: { top: 0, left: 0 },
  },
  schedule: {
    title: 'Schedule',
    subtitle: 'Important & Not Urgent',
    color: colors.primary,
    position: { top: 0, right: 0 },
  },
  delegate: {
    title: 'Delegate',
    subtitle: 'Not Important & Urgent',
    color: colors.secondary,
    position: { bottom: 0, left: 0 },
  },
  eliminate: {
    title: 'Eliminate',
    subtitle: 'Not Important & Not Urgent',
    color: colors.textSecondary,
    position: { bottom: 0, right: 0 },
  },
};

export default function QuadrantView({ tasks, onTaskPress }: QuadrantViewProps) {
  const renderQuadrant = (quadrantKey: QuadrantKey) => {
    const config = quadrantConfig[quadrantKey];
    const quadrantTasks = tasks.filter(task => task.quadrant === quadrantKey);

    return (
      <Surface style={[styles.quadrant, config.position]} elevation={1}>
        <View style={[styles.quadrantHeader, { borderBottomColor: config.color + '40' }]}>
          <Text style={[styles.quadrantTitle, { color: config.color }]}>
            {config.title}
          </Text>
          <Text style={styles.quadrantSubtitle}>{config.subtitle}</Text>
          <View style={[styles.taskCount, { backgroundColor: config.color + '20' }]}>
            <Text style={[styles.taskCountText, { color: config.color }]}>
              {quadrantTasks.length}
            </Text>
          </View>
        </View>

        <ScrollView style={styles.taskList} showsVerticalScrollIndicator={false}>
          {quadrantTasks.map(task => (
            <TouchableOpacity
              key={task.id}
              onPress={() => onTaskPress(task.id)}
              style={[styles.taskItem, { borderLeftColor: config.color }]}
            >
              <Text style={styles.taskTitle} numberOfLines={2}>
                {task.title}
              </Text>
              <View style={styles.taskMeta}>
                <Text style={styles.taskMetaText}>{task.time_estimate}m</Text>
                <View style={styles.dot} />
                <Text style={styles.taskMetaText}>Energy {task.energy_level}/5</Text>
              </View>
            </TouchableOpacity>
          ))}
          {quadrantTasks.length === 0 && (
            <Text style={styles.emptyText}>No tasks in this quadrant</Text>
          )}
        </ScrollView>
      </Surface>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        {renderQuadrant('focus')}
        {renderQuadrant('schedule')}
      </View>
      <View style={styles.row}>
        {renderQuadrant('delegate')}
        {renderQuadrant('eliminate')}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  row: {
    flex: 1,
    flexDirection: 'row',
    gap: 10,
  },
  quadrant: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 16,
    margin: 5,
    padding: 12,
  },
  quadrantHeader: {
    borderBottomWidth: 1,
    paddingBottom: 12,
    marginBottom: 12,
  },
  quadrantTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  quadrantSubtitle: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  taskCount: {
    position: 'absolute',
    top: 0,
    right: 0,
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  taskCountText: {
    fontSize: 12,
    fontWeight: '600',
  },
  taskList: {
    flex: 1,
  },
  taskItem: {
    marginBottom: 8,
    paddingLeft: 8,
    paddingVertical: 8,
    borderLeftWidth: 3,
  },
  taskTitle: {
    fontSize: 14,
    color: colors.text,
    marginBottom: 4,
    lineHeight: 18,
  },
  taskMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskMetaText: {
    fontSize: 11,
    color: colors.textSecondary,
  },
  dot: {
    width: 3,
    height: 3,
    borderRadius: 2,
    backgroundColor: colors.textSecondary,
    marginHorizontal: 6,
  },
  emptyText: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 20,
  },
});