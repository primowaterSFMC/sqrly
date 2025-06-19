import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { Modal, Text, TextInput, Button, Surface, IconButton, Chip, ProgressBar } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';

interface AIAssistantModalProps {
  visible: boolean;
  onDismiss: () => void;
  onTaskCreated: (task: any) => void;
}

export default function AIAssistantModal({ visible, onDismiss, onTaskCreated }: AIAssistantModalProps) {
  const [step, setStep] = useState(1);
  const [taskDescription, setTaskDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [breakdown, setBreakdown] = useState<any>(null);
  const [selectedSubtasks, setSelectedSubtasks] = useState<string[]>([]);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => {
      setBreakdown({
        mainTask: {
          title: taskDescription,
          time_estimate: 60,
          energy_level: 3,
          difficulty_level: 2,
          quadrant: 'focus',
        },
        subtasks: [
          {
            id: '1',
            title: 'Research best practices',
            time_estimate: 20,
            energy_level: 2,
          },
          {
            id: '2',
            title: 'Create initial outline',
            time_estimate: 15,
            energy_level: 3,
          },
          {
            id: '3',
            title: 'Write first draft',
            time_estimate: 25,
            energy_level: 4,
          },
        ],
        insights: {
          bestTime: 'Morning (9-11 AM)',
          totalTime: '60 minutes',
          difficulty: 'Moderate',
          tips: [
            'Break into 25-minute focus sessions',
            'Start with the research phase when energy is lower',
          ],
        },
      });
      setIsAnalyzing(false);
      setStep(2);
    }, 2000);
  };

  const toggleSubtask = (id: string) => {
    setSelectedSubtasks(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleCreate = () => {
    if (!breakdown) return;

    onTaskCreated({
      ...breakdown.mainTask,
      subtasks: breakdown.subtasks.filter((st: any) => selectedSubtasks.includes(st.id)),
    });
  };

  const reset = () => {
    setStep(1);
    setTaskDescription('');
    setBreakdown(null);
    setSelectedSubtasks([]);
  };

  return (
    <Modal
      visible={visible}
      onDismiss={() => {
        onDismiss();
        reset();
      }}
      contentContainerStyle={styles.modal}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <Surface style={styles.content} elevation={0}>
          <View style={styles.header}>
            <View style={styles.titleRow}>
              <MaterialCommunityIcons name="robot" size={24} color={colors.primary} />
              <Text style={styles.title}>AI Task Assistant</Text>
            </View>
            <IconButton
              icon="close"
              size={24}
              onPress={() => {
                onDismiss();
                reset();
              }}
            />
          </View>

          <ProgressBar
            progress={step / 2}
            color={colors.primary}
            style={styles.progressBar}
          />

          {step === 1 ? (
            <>
              <Text style={styles.stepTitle}>What do you need to do?</Text>
              <Text style={styles.stepDescription}>
                Describe your task and I'll help break it down into manageable steps
              </Text>

              <TextInput
                mode="outlined"
                label="Task description"
                value={taskDescription}
                onChangeText={setTaskDescription}
                multiline
                numberOfLines={4}
                style={styles.input}
                placeholder="e.g., Write a report on quarterly sales performance"
                outlineColor={colors.surfaceVariant}
                activeOutlineColor={colors.primary}
              />

              <View style={styles.suggestions}>
                <Text style={styles.suggestionsTitle}>Tips for better results:</Text>
                <View style={styles.tip}>
                  <MaterialCommunityIcons name="check" size={16} color={colors.success} />
                  <Text style={styles.tipText}>Be specific about the outcome</Text>
                </View>
                <View style={styles.tip}>
                  <MaterialCommunityIcons name="check" size={16} color={colors.success} />
                  <Text style={styles.tipText}>Include any constraints or deadlines</Text>
                </View>
                <View style={styles.tip}>
                  <MaterialCommunityIcons name="check" size={16} color={colors.success} />
                  <Text style={styles.tipText}>Mention if it's new or familiar work</Text>
                </View>
              </View>

              <Button
                mode="contained"
                onPress={handleAnalyze}
                loading={isAnalyzing}
                disabled={!taskDescription.trim() || isAnalyzing}
                style={styles.button}
                contentStyle={styles.buttonContent}
              >
                Analyze Task
              </Button>
            </>
          ) : (
            <ScrollView showsVerticalScrollIndicator={false}>
              <Text style={styles.stepTitle}>Task Breakdown</Text>
              <Text style={styles.stepDescription}>
                Select which subtasks you'd like to create
              </Text>

              {breakdown && (
                <Surface style={styles.mainTaskCard} elevation={1}>
                  <Text style={styles.mainTaskTitle}>{breakdown.mainTask.title}</Text>
                  <View style={styles.taskMeta}>
                    <Chip
                      mode="flat"
                      style={[styles.chip, { backgroundColor: colors.accent + '20' }]}
                      textStyle={[styles.chipText, { color: colors.accent }]}
                    >
                      {breakdown.mainTask.quadrant}
                    </Chip>
                    <Text style={styles.metaText}>
                      {breakdown.mainTask.time_estimate} min • Energy {breakdown.mainTask.energy_level}/5
                    </Text>
                  </View>
                </Surface>
              )}

              <Text style={styles.sectionTitle}>Suggested Subtasks</Text>
              {breakdown?.subtasks?.map((subtask: any) => (
                <TouchableOpacity
                  key={subtask.id}
                  onPress={() => toggleSubtask(subtask.id)}
                  style={[
                    styles.subtaskCard,
                    selectedSubtasks.includes(subtask.id) && styles.selectedSubtask,
                  ]}
                >
                  <MaterialCommunityIcons
                    name={selectedSubtasks.includes(subtask.id) ? 'checkbox-marked' : 'checkbox-blank-outline'}
                    size={24}
                    color={selectedSubtasks.includes(subtask.id) ? colors.primary : colors.textSecondary}
                  />
                  <View style={styles.subtaskContent}>
                    <Text style={styles.subtaskTitle}>{subtask.title}</Text>
                    <Text style={styles.subtaskMeta}>
                      {subtask.time_estimate} min • Energy {subtask.energy_level}/5
                    </Text>
                  </View>
                </TouchableOpacity>
              )) || []}

              {breakdown?.insights && (
                <Surface style={styles.insightsCard} elevation={1}>
                  <Text style={styles.insightsTitle}>AI Insights</Text>
                  <View style={styles.insight}>
                    <MaterialCommunityIcons name="clock-outline" size={20} color={colors.focusHighlight} />
                    <View style={styles.insightContent}>
                      <Text style={styles.insightLabel}>Best time to work</Text>
                      <Text style={styles.insightValue}>{breakdown.insights.bestTime}</Text>
                    </View>
                  </View>
                  <View style={styles.insight}>
                    <MaterialCommunityIcons name="timer" size={20} color={colors.primary} />
                    <View style={styles.insightContent}>
                      <Text style={styles.insightLabel}>Total time needed</Text>
                      <Text style={styles.insightValue}>{breakdown.insights.totalTime}</Text>
                    </View>
                  </View>
                  {breakdown.insights.tips?.map((tip: string, index: number) => (
                    <View key={index} style={styles.tipRow}>
                      <MaterialCommunityIcons name="lightbulb-outline" size={16} color={colors.secondary} />
                      <Text style={styles.tipText}>{tip}</Text>
                    </View>
                  )) || []}
                </Surface>
              )}

              <View style={styles.actions}>
                <Button
                  mode="outlined"
                  onPress={() => setStep(1)}
                  style={styles.secondaryButton}
                >
                  Back
                </Button>
                <Button
                  mode="contained"
                  onPress={handleCreate}
                  disabled={selectedSubtasks.length === 0}
                  style={styles.primaryButton}
                  contentStyle={styles.buttonContent}
                >
                  Create Tasks ({selectedSubtasks.length})
                </Button>
              </View>
            </ScrollView>
          )}
        </Surface>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modal: {
    padding: 20,
    justifyContent: 'center',
  },
  keyboardView: {
    maxHeight: '90%',
  },
  content: {
    borderRadius: 20,
    backgroundColor: colors.surface,
    maxHeight: '100%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 0,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
  },
  progressBar: {
    height: 4,
    marginHorizontal: 20,
    marginTop: 16,
    marginBottom: 24,
    borderRadius: 2,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginHorizontal: 20,
    marginBottom: 8,
  },
  stepDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginHorizontal: 20,
    marginBottom: 20,
  },
  input: {
    marginHorizontal: 20,
    marginBottom: 20,
    backgroundColor: colors.surface,
  },
  suggestions: {
    marginHorizontal: 20,
    marginBottom: 24,
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 8,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  tipText: {
    fontSize: 13,
    color: colors.textSecondary,
    flex: 1,
  },
  button: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  mainTaskCard: {
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 16,
    borderRadius: 12,
    backgroundColor: colors.surfaceVariant,
  },
  mainTaskTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 8,
  },
  taskMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  chip: {
    height: 24,
  },
  chipText: {
    fontSize: 12,
  },
  metaText: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginHorizontal: 20,
    marginBottom: 12,
  },
  subtaskCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginHorizontal: 20,
    marginBottom: 8,
    padding: 12,
    borderRadius: 8,
    backgroundColor: colors.surfaceVariant,
  },
  selectedSubtask: {
    backgroundColor: colors.primary + '15',
    borderWidth: 1,
    borderColor: colors.primary + '30',
  },
  subtaskContent: {
    flex: 1,
  },
  subtaskTitle: {
    fontSize: 14,
    color: colors.text,
    marginBottom: 4,
  },
  subtaskMeta: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  insightsCard: {
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 24,
    padding: 16,
    borderRadius: 12,
    backgroundColor: colors.focusHighlight + '10',
  },
  insightsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
  },
  insight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  insightContent: {
    flex: 1,
  },
  insightLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  insightValue: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
  },
  tipRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    marginTop: 8,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    marginHorizontal: 20,
    marginBottom: 20,
  },
  secondaryButton: {
    flex: 1,
  },
  primaryButton: {
    flex: 2,
  },
});