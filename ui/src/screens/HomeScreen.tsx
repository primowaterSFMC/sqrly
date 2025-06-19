import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { Text, Card, ProgressBar, Chip, FAB, Surface, IconButton } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import { useTask } from '../contexts/TaskContext';
import { HomeScreenProps } from '../types/navigation';
import TaskCard from '../components/TaskCard';
import EnergyTracker from '../components/EnergyTracker';
import QuickStats from '../components/QuickStats';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const { tasks, todaysTasks, completedToday } = useTask();
  const [currentEnergy, setCurrentEnergy] = useState(3);
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  const progressPercentage = todaysTasks.length > 0 
    ? completedToday.length / todaysTasks.length 
    : 0;

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>{greeting}</Text>
            <Text style={styles.subtitle}>Let's make today manageable</Text>
          </View>
          <IconButton
            icon="brain"
            size={28}
            iconColor={colors.primary}
            onPress={() => {
              // TODO: Implement AI Assistant modal
              console.log('AI Assistant pressed');
            }}
            style={styles.aiButton}
          />
        </View>

        <EnergyTracker 
          currentEnergy={currentEnergy}
          onEnergyChange={setCurrentEnergy}
        />

        <Surface style={styles.progressCard} elevation={1}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressTitle}>Today's Progress</Text>
            <Text style={styles.progressText}>
              {completedToday.length} of {todaysTasks.length} tasks
            </Text>
          </View>
          <ProgressBar 
            progress={progressPercentage} 
            color={colors.success}
            style={styles.progressBar}
          />
        </Surface>

        <QuickStats />

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Focus Now</Text>
            <Chip 
              mode="flat" 
              textStyle={styles.chipText}
              style={[styles.energyChip, { backgroundColor: colors.focusHighlight + '20' }]}
            >
              Matches your energy
            </Chip>
          </View>

          {todaysTasks
            .filter(task => !task.completed && task.energy_level <= currentEnergy)
            .slice(0, 3)
            .map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onPress={() => {
                  // TODO: Implement task detail modal
                  console.log('Task pressed:', task.id);
                }}
              />
            ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <Card
              style={styles.actionCard}
              onPress={() => {
                // Navigate to Tasks tab and trigger quick capture
                navigation.navigate('Tasks');
              }}
            >
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons 
                  name="lightning-bolt" 
                  size={24} 
                  color={colors.accent}
                />
                <Text style={styles.actionText}>Quick Capture</Text>
              </Card.Content>
            </Card>

            <Card 
              style={styles.actionCard}
              onPress={() => navigation.navigate('Focus', { mode: 'pomodoro' })}
            >
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons 
                  name="timer" 
                  size={24} 
                  color={colors.focusHighlight}
                />
                <Text style={styles.actionText}>Start Focus</Text>
              </Card.Content>
            </Card>
          </View>
        </View>
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => {
          // Navigate to Tasks tab
          navigation.navigate('Tasks');
        }}
        color="#FFFFFF"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: 4,
  },
  aiButton: {
    backgroundColor: colors.primary + '15',
  },
  progressCard: {
    margin: 20,
    padding: 20,
    borderRadius: 16,
    backgroundColor: colors.surface,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  progressText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.surfaceVariant,
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
  },
  energyChip: {
    height: 28,
  },
  chipText: {
    fontSize: 12,
    color: colors.focusHighlight,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 12,
  },
  actionContent: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: colors.primary,
  },
});