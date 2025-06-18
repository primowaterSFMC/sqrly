import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Text, Chip, Surface } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';

interface TaskCardProps {
  task: {
    id: string;
    title: string;
    quadrant: string;
    energy_level: number;
    time_estimate: number;
    difficulty_level: number;
    completed: boolean;
    has_ai_breakdown: boolean;
  };
  onPress: () => void;
}

const quadrantColors = {
  'focus': colors.accent,
  'schedule': colors.primary,
  'delegate': colors.secondary,
  'eliminate': colors.textSecondary,
};

const difficultyIcons = {
  1: 'leaf',
  2: 'sprout',
  3: 'tree',
};

export default function TaskCard({ task, onPress }: TaskCardProps) {
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8}>
      <Surface style={styles.card} elevation={1}>
        <View style={styles.header}>
          <View style={styles.titleRow}>
            <Text style={styles.title} numberOfLines={2}>
              {task.title}
            </Text>
            {task.has_ai_breakdown && (
              <MaterialCommunityIcons 
                name="robot" 
                size={16} 
                color={colors.primary}
                style={styles.aiIcon}
              />
            )}
          </View>
          <View style={styles.badges}>
            <Chip 
              mode="flat" 
              style={[styles.quadrantChip, { backgroundColor: quadrantColors[task.quadrant] + '20' }]}
              textStyle={[styles.chipText, { color: quadrantColors[task.quadrant] }]}
            >
              {task.quadrant.charAt(0).toUpperCase() + task.quadrant.slice(1)}
            </Chip>
          </View>
        </View>

        <View style={styles.details}>
          <View style={styles.detail}>
            <MaterialCommunityIcons name="clock-outline" size={16} color={colors.textSecondary} />
            <Text style={styles.detailText}>{task.time_estimate} min</Text>
          </View>
          
          <View style={styles.detail}>
            <MaterialCommunityIcons name="lightning-bolt" size={16} color={colors.textSecondary} />
            <Text style={styles.detailText}>Energy {task.energy_level}/5</Text>
          </View>

          <View style={styles.detail}>
            <MaterialCommunityIcons 
              name={difficultyIcons[task.difficulty_level] || 'tree'} 
              size={16} 
              color={colors.textSecondary} 
            />
            <Text style={styles.detailText}>Level {task.difficulty_level}</Text>
          </View>
        </View>
      </Surface>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    marginBottom: 12,
    borderRadius: 12,
    backgroundColor: colors.surface,
    padding: 16,
  },
  header: {
    marginBottom: 12,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.text,
    flex: 1,
    lineHeight: 22,
  },
  aiIcon: {
    marginLeft: 8,
    marginTop: 2,
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
  },
  quadrantChip: {
    height: 24,
  },
  chipText: {
    fontSize: 12,
    fontWeight: '500',
  },
  details: {
    flexDirection: 'row',
    gap: 16,
  },
  detail: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 13,
    color: colors.textSecondary,
  },
});