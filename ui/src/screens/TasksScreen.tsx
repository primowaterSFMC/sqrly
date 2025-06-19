import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Dimensions, ActivityIndicator } from 'react-native';
import { Text, Chip, FAB, Searchbar, SegmentedButtons } from 'react-native-paper';
import { colors } from '../theme';
import { useTask } from '../contexts/TaskContext';
import { TasksScreenProps } from '../types/navigation';
import TaskCard from '../components/TaskCard';
import QuadrantView from '../components/QuadrantView';
import AIAssistantModal from '../components/AIAssistantModal';

const { width } = Dimensions.get('window');

export default function TasksScreen({ navigation }: TasksScreenProps) {
  const { tasks, isLoading, error, getTasksByQuadrant } = useTask();
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('list');
  const [filterQuadrant, setFilterQuadrant] = useState('all');
  const [showAIModal, setShowAIModal] = useState(false);
  const [fabOpen, setFabOpen] = useState(false);

  const filters = [
    { value: 'all', label: 'All Tasks' },
    { value: 'focus', label: 'Focus', color: colors.accent },
    { value: 'schedule', label: 'Schedule', color: colors.primary },
    { value: 'delegate', label: 'Delegate', color: colors.secondary },
    { value: 'eliminate', label: 'Eliminate', color: colors.textSecondary },
  ];

  // Get filtered tasks based on current filter
  const getFilteredTasks = () => {
    let filteredTasks = tasks;

    // Filter by quadrant
    if (filterQuadrant !== 'all') {
      filteredTasks = filteredTasks.filter(task => task.quadrant === filterQuadrant);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      filteredTasks = filteredTasks.filter(task =>
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    return filteredTasks;
  };

  const filteredTasks = getFilteredTasks();

  // Show loading state
  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading tasks...</Text>
      </View>
    );
  }

  // Show error state
  if (error) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Error loading tasks</Text>
        <Text style={styles.errorSubtext}>{error}</Text>
      </View>
    );
  }

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
              onPress={() => {
                // TODO: Implement task detail modal or navigation
                console.log('Task pressed:', task.id);
              }}
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
          onTaskPress={(taskId) => {
            // TODO: Implement task detail modal or navigation
            console.log('Task pressed:', taskId);
          }}
        />
      )}

      <FAB.Group
        open={fabOpen}
        visible
        icon={fabOpen ? 'close' : 'plus'}
        onStateChange={({ open }) => setFabOpen(open)}
        actions={[
          {
            icon: 'robot',
            label: 'AI Breakdown',
            onPress: () => {
              setShowAIModal(true);
              setFabOpen(false);
            },
            color: colors.primary,
            style: { backgroundColor: colors.surface },
          },
          {
            icon: 'lightning-bolt',
            label: 'Quick Add',
            onPress: () => {
              // TODO: Implement quick task creation modal
              console.log('Quick add pressed');
              setFabOpen(false);
            },
            color: colors.accent,
            style: { backgroundColor: colors.surface },
          },
          {
            icon: 'text',
            label: 'Full Task',
            onPress: () => {
              // TODO: Implement full task creation modal
              console.log('Full task pressed');
              setFabOpen(false);
            },
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
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: colors.textSecondary,
  },
  errorText: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.error,
    marginBottom: 8,
  },
  errorSubtext: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
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