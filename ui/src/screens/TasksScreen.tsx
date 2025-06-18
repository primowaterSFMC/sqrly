import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { Text, Chip, FAB, Searchbar, SegmentedButtons } from 'react-native-paper';
import { colors } from '../theme';
import TaskCard from '../components/TaskCard';
import QuadrantView from '../components/QuadrantView';
import AIAssistantModal from '../components/AIAssistantModal';

const { width } = Dimensions.get('window');

export default function TasksScreen({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('list');
  const [filterQuadrant, setFilterQuadrant] = useState('all');
  const [showAIModal, setShowAIModal] = useState(false);

  const filters = [
    { value: 'all', label: 'All Tasks' },
    { value: 'focus', label: 'Focus', color: colors.accent },
    { value: 'schedule', label: 'Schedule', color: colors.primary },
    { value: 'delegate', label: 'Delegate', color: colors.secondary },
    { value: 'eliminate', label: 'Eliminate', color: colors.textSecondary },
  ];

  // Mock data - replace with context/API data
  const tasks = [
    {
      id: '1',
      title: 'Review project proposal and provide feedback',
      quadrant: 'focus',
      energy_level: 4,
      time_estimate: 45,
      difficulty_level: 3,
      completed: false,
      has_ai_breakdown: true,
    },
    {
      id: '2',
      title: 'Schedule dentist appointment',
      quadrant: 'schedule',
      energy_level: 2,
      time_estimate: 10,
      difficulty_level: 1,
      completed: false,
      has_ai_breakdown: false,
    },
    {
      id: '3',
      title: 'Prepare weekly team meeting agenda',
      quadrant: 'focus',
      energy_level: 3,
      time_estimate: 30,
      difficulty_level: 2,
      completed: false,
      has_ai_breakdown: true,
    },
  ];

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesQuadrant = filterQuadrant === 'all' || task.quadrant === filterQuadrant;
    return matchesSearch && matchesQuadrant;
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Searchbar
          placeholder="Search tasks..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchBar}
          iconColor={colors.textSecondary}
          placeholderTextColor={colors.textSecondary}
        />

        <SegmentedButtons
          value={viewMode}
          onValueChange={setViewMode}
          buttons={[
            { value: 'list', label: 'List', icon: 'format-list-bulleted' },
            { value: 'quadrant', label: 'Quadrants', icon: 'view-grid' },
          ]}
          style={styles.viewToggle}
        />
      </View>

      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.filterContainer}
      >
        {filters.map((filter) => (
          <Chip
            key={filter.value}
            mode="flat"
            selected={filterQuadrant === filter.value}
            onPress={() => setFilterQuadrant(filter.value)}
            style={[
              styles.filterChip,
              filterQuadrant === filter.value && {
                backgroundColor: (filter.color || colors.primary) + '20',
              }
            ]}
            textStyle={[
              styles.filterChipText,
              filterQuadrant === filter.value && {
                color: filter.color || colors.primary,
              }
            ]}
          >
            {filter.label}
          </Chip>
        ))}
      </ScrollView>

      {viewMode === 'list' ? (
        <ScrollView style={styles.taskList} showsVerticalScrollIndicator={false}>
          {filteredTasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onPress={() => navigation.navigate('TaskDetail', { taskId: task.id })}
            />
          ))}
          {filteredTasks.length === 0 && (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No tasks found</Text>
              <Text style={styles.emptySubtext}>
                Try adjusting your filters or add a new task
              </Text>
            </View>
          )}
        </ScrollView>
      ) : (
        <QuadrantView 
          tasks={filteredTasks}
          onTaskPress={(taskId) => navigation.navigate('TaskDetail', { taskId })}
        />
      )}

      <FAB.Group
        open={false}
        visible
        icon="plus"
        actions={[
          {
            icon: 'robot',
            label: 'AI Breakdown',
            onPress: () => setShowAIModal(true),
            color: colors.primary,
            style: { backgroundColor: colors.surface },
          },
          {
            icon: 'lightning-bolt',
            label: 'Quick Add',
            onPress: () => navigation.navigate('QuickCapture'),
            color: colors.accent,
            style: { backgroundColor: colors.surface },
          },
          {
            icon: 'text',
            label: 'Full Task',
            onPress: () => navigation.navigate('AddTask'),
            color: colors.text,
            style: { backgroundColor: colors.surface },
          },
        ]}
        fabStyle={{ backgroundColor: colors.primary }}
        color="#FFFFFF"
      />

      <AIAssistantModal
        visible={showAIModal}
        onDismiss={() => setShowAIModal(false)}
        onTaskCreated={(task) => {
          setShowAIModal(false);
          // Handle task creation
        }}
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
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 8,
  },
  searchBar: {
    marginBottom: 12,
    backgroundColor: colors.surface,
    elevation: 0,
  },
  viewToggle: {
    marginBottom: 8,
  },
  filterContainer: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    maxHeight: 50,
  },
  filterChip: {
    marginRight: 8,
    backgroundColor: colors.surfaceVariant,
  },
  filterChipText: {
    color: colors.textSecondary,
  },
  taskList: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});