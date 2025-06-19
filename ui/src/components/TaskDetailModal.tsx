import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Modal,
  Portal,
  Text,
  Surface,
  IconButton,
  Button,
  Chip,
  Divider,
  TextInput,
  List,
  Checkbox,
  ProgressBar,
  Menu,
  FAB,
} from 'react-native-paper';
import { colors } from '../theme';
import { Task, Subtask } from '../services/api';
import { useTask } from '../contexts/TaskContext';
import apiService from '../services/api';

const { width, height } = Dimensions.get('window');

interface TaskDetailModalProps {
  visible: boolean;
  task: Task | null;
  onDismiss: () => void;
}

const quadrantColors = {
  focus: colors.accent,
  schedule: colors.primary,
  delegate: colors.secondary,
  eliminate: colors.textSecondary,
};

const quadrantLabels = {
  focus: 'Focus',
  schedule: 'Schedule',
  delegate: 'Delegate',
  eliminate: 'Eliminate',
};

export default function TaskDetailModal({
  visible,
  task,
  onDismiss,
}: TaskDetailModalProps) {
  const { updateTask, deleteTask, completeTask, getSubtasksForTask, addSubtask, toggleSubtask } = useTask();
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('');
  const [showMenu, setShowMenu] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [subtasks, setSubtasks] = useState<Subtask[]>([]);
  const [isLoadingSubtasks, setIsLoadingSubtasks] = useState(false);

  // Initialize edit fields when task changes
  React.useEffect(() => {
    if (task) {
      setEditedTitle(task.title);
      setEditedDescription(task.description || '');
    }
  }, [task]);

  // Fetch subtasks when task changes
  React.useEffect(() => {
    if (task && visible) {
      fetchSubtasks();
    }
  }, [task, visible]);

  const fetchSubtasks = async () => {
    if (!task) return;

    setIsLoadingSubtasks(true);
    try {
      const fetchedSubtasks = await getSubtasksForTask(task.id);
      setSubtasks(fetchedSubtasks);
    } catch (error) {
      console.error('Error fetching subtasks:', error);
      // Don't show error to user, just use empty subtasks
      // This prevents the modal from breaking when subtask API fails
      setSubtasks([]);
    } finally {
      setIsLoadingSubtasks(false);
    }
  };

  if (!task) return null;

  const handleSaveEdit = async () => {
    try {
      await updateTask(task.id, {
        title: editedTitle,
        description: editedDescription,
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const handleComplete = async () => {
    try {
      await completeTask(task.id);
      onDismiss();
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteTask(task.id);
      onDismiss();
    } catch (error) {
      console.error('Error deleting task:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleAddSubtask = async () => {
    if (!newSubtaskTitle.trim() || !task) return;

    try {
      const newSubtaskData = {
        task_id: task.id,
        title: newSubtaskTitle,
        subtask_type: 'execution' as const,
        difficulty_level: 'medium' as const,
        status: 'pending' as const,
        estimated_minutes: 15,
        energy_required: 5,
        focus_required: 5,
        sequence_order: subtasks.length + 1,
        momentum_builder: false,
        confidence_boost: false,
        ai_generated: false,
      };

      const createdSubtask = await addSubtask(newSubtaskData);
      setSubtasks(prev => [...prev, createdSubtask]);
      setNewSubtaskTitle('');
    } catch (error) {
      console.error('Error adding subtask:', error);
    }
  };

  const handleToggleSubtask = async (subtaskId: string) => {
    try {
      const subtask = subtasks.find(st => st.id === subtaskId);
      if (!subtask) return;

      const action = subtask.status === 'completed' ? 'start' : 'complete';
      const updatedSubtask = await apiService.performSubtaskAction(subtaskId, action);

      setSubtasks(prev =>
        prev.map(st => st.id === subtaskId ? updatedSubtask : st)
      );
    } catch (error) {
      console.error('Error toggling subtask:', error);
    }
  };

  const completedSubtasks = subtasks.filter(st => st.status === 'completed').length;
  const totalSubtasks = subtasks.length;
  const progress = totalSubtasks > 0 ? completedSubtasks / totalSubtasks : 0;

  return (
    <Portal>
      <Modal
        visible={visible}
        onDismiss={onDismiss}
        contentContainerStyle={styles.modal}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardAvoid}
        >
          <Surface style={styles.container}>
            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Header */}
              <View style={styles.header}>
                <View style={styles.headerLeft}>
                  <Chip
                    mode="flat"
                    style={[
                      styles.quadrantChip,
                      { backgroundColor: quadrantColors[task.quadrant] + '20' },
                    ]}
                    textStyle={[
                      styles.quadrantChipText,
                      { color: quadrantColors[task.quadrant] },
                    ]}
                  >
                    {quadrantLabels[task.quadrant]}
                  </Chip>
                  {task.completed && (
                    <Chip
                      mode="flat"
                      style={styles.completedChip}
                      textStyle={styles.completedChipText}
                    >
                      Completed
                    </Chip>
                  )}
                </View>
                <View style={styles.headerRight}>
                  <IconButton
                    icon={isEditing ? 'close' : 'pencil'}
                    size={24}
                    onPress={() => setIsEditing(!isEditing)}
                  />
                  <Menu
                    visible={showMenu}
                    onDismiss={() => setShowMenu(false)}
                    anchor={
                      <IconButton
                        icon="dots-vertical"
                        size={24}
                        onPress={() => setShowMenu(true)}
                      />
                    }
                  >
                    <Menu.Item
                      onPress={() => {
                        setShowMenu(false);
                        handleDelete();
                      }}
                      title="Delete Task"
                      leadingIcon="delete"
                    />
                  </Menu>
                </View>
              </View>

              {/* Title and Description */}
              <View style={styles.content}>
                {isEditing ? (
                  <>
                    <TextInput
                      value={editedTitle}
                      onChangeText={setEditedTitle}
                      style={styles.titleInput}
                      placeholder="Task title"
                      mode="outlined"
                      outlineColor={colors.surface}
                      activeOutlineColor={colors.primary}
                    />
                    <TextInput
                      value={editedDescription}
                      onChangeText={setEditedDescription}
                      style={styles.descriptionInput}
                      placeholder="Add description..."
                      mode="outlined"
                      outlineColor={colors.surface}
                      activeOutlineColor={colors.primary}
                      multiline
                      numberOfLines={3}
                    />
                    <Button
                      mode="contained"
                      onPress={handleSaveEdit}
                      style={styles.saveButton}
                    >
                      Save Changes
                    </Button>
                  </>
                ) : (
                  <>
                    <Text style={styles.title}>{task.title}</Text>
                    {task.description && (
                      <Text style={styles.description}>{task.description}</Text>
                    )}
                  </>
                )}
              </View>

              {/* Task Metadata */}
              <View style={styles.metadata}>
                <View style={styles.metaItem}>
                  <IconButton icon="clock-outline" size={20} />
                  <Text style={styles.metaText}>
                    {task.time_estimate} min
                  </Text>
                </View>
                <View style={styles.metaItem}>
                  <IconButton icon="lightning-bolt" size={20} />
                  <Text style={styles.metaText}>
                    Energy: {task.energy_level}/5
                  </Text>
                </View>
                <View style={styles.metaItem}>
                  <IconButton icon="speedometer" size={20} />
                  <Text style={styles.metaText}>
                    Difficulty: {task.difficulty_level}/5
                  </Text>
                </View>
              </View>

              {/* ADHD Support Metrics */}
              {(task.executive_difficulty || task.initiation_difficulty || task.completion_difficulty) && (
                <>
                  <Divider style={styles.divider} />
                  <View style={styles.adhdMetrics}>
                    <Text style={styles.sectionTitle}>ADHD Support</Text>
                    {task.executive_difficulty && (
                      <View style={styles.metricItem}>
                        <Text style={styles.metricLabel}>Executive Function</Text>
                        <ProgressBar
                          progress={task.executive_difficulty / 10}
                          color={colors.primary}
                          style={styles.progressBar}
                        />
                      </View>
                    )}
                    {task.initiation_difficulty && (
                      <View style={styles.metricItem}>
                        <Text style={styles.metricLabel}>Getting Started</Text>
                        <ProgressBar
                          progress={task.initiation_difficulty / 10}
                          color={colors.accent}
                          style={styles.progressBar}
                        />
                      </View>
                    )}
                    {task.completion_difficulty && (
                      <View style={styles.metricItem}>
                        <Text style={styles.metricLabel}>Finishing</Text>
                        <ProgressBar
                          progress={task.completion_difficulty / 10}
                          color={colors.secondary}
                          style={styles.progressBar}
                        />
                      </View>
                    )}
                  </View>
                </>
              )}

              {/* Subtasks */}
              <Divider style={styles.divider} />
              <View style={styles.subtasksSection}>
                <View style={styles.subtasksHeader}>
                  <Text style={styles.sectionTitle}>Subtasks</Text>
                  {totalSubtasks > 0 && (
                    <Text style={styles.subtaskProgress}>
                      {completedSubtasks}/{totalSubtasks}
                    </Text>
                  )}
                </View>
                
                {totalSubtasks > 0 && (
                  <ProgressBar
                    progress={progress}
                    color={colors.primary}
                    style={styles.subtaskProgressBar}
                  />
                )}

                {isLoadingSubtasks ? (
                  <Text style={styles.loadingText}>Loading subtasks...</Text>
                ) : (
                  <List.Section>
                    {subtasks.map((subtask) => (
                      <List.Item
                        key={subtask.id}
                        title={subtask.title}
                        description={subtask.action}
                        titleStyle={[
                          styles.subtaskTitle,
                          subtask.status === 'completed' && styles.completedSubtask,
                        ]}
                        left={(props) => (
                          <Checkbox
                            status={subtask.status === 'completed' ? 'checked' : 'unchecked'}
                            onPress={() => handleToggleSubtask(subtask.id)}
                          />
                        )}
                        right={(props) => (
                          <View style={styles.subtaskMeta}>
                            <Text style={styles.subtaskTime}>
                              {subtask.estimated_minutes}min
                            </Text>
                            <Text style={styles.subtaskEnergy}>
                              E:{subtask.energy_required}
                            </Text>
                          </View>
                        )}
                      />
                    ))}
                  </List.Section>
                )}

                <View style={styles.addSubtask}>
                  <TextInput
                    value={newSubtaskTitle}
                    onChangeText={setNewSubtaskTitle}
                    placeholder="Add a subtask..."
                    mode="outlined"
                    outlineColor={colors.surface}
                    activeOutlineColor={colors.primary}
                    style={styles.subtaskInput}
                    onSubmitEditing={handleAddSubtask}
                  />
                  <IconButton
                    icon="plus"
                    size={24}
                    onPress={handleAddSubtask}
                    disabled={!newSubtaskTitle.trim()}
                  />
                </View>
              </View>

              {/* Action Buttons */}
              <View style={styles.actions}>
                <Button
                  mode="outlined"
                  onPress={onDismiss}
                  style={styles.actionButton}
                >
                  Close
                </Button>
                {!task.completed && (
                  <Button
                    mode="contained"
                    onPress={handleComplete}
                    style={[styles.actionButton, styles.completeButton]}
                  >
                    Mark Complete
                  </Button>
                )}
              </View>
            </ScrollView>
          </Surface>
        </KeyboardAvoidingView>
      </Modal>
    </Portal>
  );
}

const styles = StyleSheet.create({
  modal: {
    margin: 20,
    marginTop: 60,
    marginBottom: 60,
  },
  keyboardAvoid: {
    flex: 1,
  },
  container: {
    borderRadius: 16,
    backgroundColor: colors.surface,
    maxHeight: height - 120,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  quadrantChip: {
    height: 28,
  },
  quadrantChipText: {
    fontSize: 12,
    fontWeight: '600',
  },
  completedChip: {
    height: 28,
    backgroundColor: colors.success + '20',
  },
  completedChipText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.success,
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  titleInput: {
    marginBottom: 12,
    backgroundColor: colors.background,
  },
  descriptionInput: {
    marginBottom: 12,
    backgroundColor: colors.background,
  },
  saveButton: {
    marginTop: 8,
  },
  metadata: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 10,
    gap: 16,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  divider: {
    marginVertical: 16,
    marginHorizontal: 20,
  },
  adhdMetrics: {
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
  },
  metricItem: {
    marginBottom: 16,
  },
  metricLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.surface,
  },
  subtasksSection: {
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  subtasksHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  subtaskProgress: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  subtaskProgressBar: {
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.surface,
    marginBottom: 16,
  },
  subtaskTitle: {
    fontSize: 16,
    color: colors.text,
  },
  completedSubtask: {
    textDecorationLine: 'line-through',
    color: colors.textSecondary,
  },
  addSubtask: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  subtaskInput: {
    flex: 1,
    backgroundColor: colors.background,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
  completeButton: {
    backgroundColor: colors.success,
  },
  loadingText: {
    textAlign: 'center',
    color: colors.textSecondary,
    fontStyle: 'italic',
    marginVertical: 16,
  },
  subtaskMeta: {
    alignItems: 'flex-end',
    justifyContent: 'center',
    paddingRight: 8,
  },
  subtaskTime: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  subtaskEnergy: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
  },
});