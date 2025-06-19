import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, ScrollView, Animated, Alert, AppState } from 'react-native';
import { Text, Button, Surface, ProgressBar, IconButton, Chip, Card, Modal, Portal } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import { useTask } from '../contexts/TaskContext';
import { FocusScreenProps } from '../types/navigation';
import CircularProgress from '../components/CircularProgress';
import apiService from '../services/api';

export default function FocusScreen({ navigation, route }: FocusScreenProps) {
  const { tasks, todaysTasks } = useTask();
  const [mode, setMode] = useState(route.params?.mode || 'pomodoro');
  const [isRunning, setIsRunning] = useState(false);
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [sessions, setSessions] = useState(0);
  const [currentTask, setCurrentTask] = useState<any>(null);
  const [sessionStats, setSessionStats] = useState({
    completedSessions: 0,
    totalFocusTime: 0,
    averageSessionLength: 0,
    hyperfocusWarnings: 0
  });
  const [showHyperfocusWarning, setShowHyperfocusWarning] = useState(false);
  const [showBreakReminder, setShowBreakReminder] = useState(false);
  const [isBreakTime, setIsBreakTime] = useState(false);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const animatedValue = useRef(new Animated.Value(0)).current;

  const focusModes = {
    pomodoro: {
      work: 25 * 60,
      break: 5 * 60,
      longBreak: 15 * 60,
      sessionsUntilLong: 4,
      name: 'Pomodoro',
      description: 'Classic 25-min focus sessions',
      adhdBenefit: 'Perfect for sustained attention'
    },
    deepWork: {
      work: 90 * 60,
      break: 20 * 60,
      name: 'Deep Work',
      description: '90-min hyperfocus sessions',
      adhdBenefit: 'Harness hyperfocus periods'
    },
    microSession: {
      work: 10 * 60,
      break: 2 * 60,
      name: 'Micro Focus',
      description: '10-min quick bursts',
      adhdBenefit: 'Low commitment, easy start'
    },
    adhdCustom: {
      work: 15 * 60,
      break: 3 * 60,
      name: 'ADHD Optimized',
      description: '15-min with gentle breaks',
      adhdBenefit: 'Designed for ADHD brains'
    },
  };

  const currentMode = focusModes[mode];
  const totalTime = currentMode.work;
  const progress = (totalTime - timeLeft) / totalTime;

  useEffect(() => {
    let interval;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handleSessionComplete();
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  // Load focus stats on component mount
  useEffect(() => {
    const loadFocusStats = async () => {
      try {
        const stats = await apiService.getFocusStats('today');
        setSessionStats(stats);
      } catch (error) {
        console.error('Failed to load focus stats:', error);
      }
    };

    loadFocusStats();
  }, []);

  const handleSessionComplete = async () => {
    setIsRunning(false);
    setSessions(prev => prev + 1);

    // Calculate session duration
    const sessionDuration = sessionStartTime
      ? Math.floor((Date.now() - sessionStartTime.getTime()) / 1000)
      : currentMode.work;

    // Update session stats
    setSessionStats(prev => ({
      completedSessions: prev.completedSessions + 1,
      totalFocusTime: prev.totalFocusTime + sessionDuration,
      averageSessionLength: Math.floor((prev.totalFocusTime + sessionDuration) / (prev.completedSessions + 1)),
      hyperfocusWarnings: prev.hyperfocusWarnings
    }));

    // Save session to backend
    try {
      await apiService.createFocusSession({
        task_id: currentTask?.id,
        session_type: mode,
        planned_duration: currentMode.work,
        actual_duration: sessionDuration,
        completed: true,
        hyperfocus_detected: sessionDuration > currentMode.work * 1.5
      });
    } catch (error) {
      console.error('Failed to save focus session:', error);
    }

    // Check for hyperfocus
    if (sessionDuration > currentMode.work * 1.5) {
      setShowHyperfocusWarning(true);
      setSessionStats(prev => ({ ...prev, hyperfocusWarnings: prev.hyperfocusWarnings + 1 }));
    } else {
      // Show break reminder for normal sessions
      setIsBreakTime(true);
      setShowBreakReminder(true);
      setTimeLeft(currentMode.break);
    }
  };

  const toggleTimer = () => {
    if (!isRunning) {
      // Starting a new session
      setSessionStartTime(new Date());
      setIsBreakTime(false);
      if (!currentTask) {
        Alert.alert(
          'Select a Task',
          'Choose a task to focus on for better productivity tracking.',
          [
            { text: 'Skip', onPress: () => setIsRunning(true) },
            { text: 'Choose Task', onPress: () => navigation.navigate('Tasks') }
          ]
        );
        return;
      }
    }
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft(isBreakTime ? currentMode.break : currentMode.work);
    setSessionStartTime(null);
  };

  const skipBreak = () => {
    setIsBreakTime(false);
    setShowBreakReminder(false);
    setTimeLeft(currentMode.work);
  };

  const selectTaskForFocus = (task: any) => {
    setCurrentTask(task);
    // Auto-adjust timer based on task energy level and estimated time
    if (task.time_estimate && task.time_estimate < currentMode.work / 60) {
      const adjustedTime = Math.max(task.time_estimate * 60, 10 * 60); // Minimum 10 minutes
      setTimeLeft(adjustedTime);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEnergyColor = (level: number) => {
    if (level <= 2) return colors.error;
    if (level <= 3) return colors.warning;
    return colors.success;
  };

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Focus Mode</Text>
          <View style={styles.modeSelector}>
            {Object.keys(focusModes).map((modeKey) => (
              <Chip
                key={modeKey}
                mode="flat"
                selected={mode === modeKey}
                onPress={() => {
                  setMode(modeKey);
                  setTimeLeft(focusModes[modeKey].work);
                  setIsRunning(false);
                }}
                style={[
                  styles.modeChip,
                  mode === modeKey && styles.selectedModeChip,
                ]}
                textStyle={[
                  styles.modeChipText,
                  mode === modeKey && styles.selectedModeChipText,
                ]}
              >
                {modeKey.charAt(0).toUpperCase() + modeKey.slice(1).replace(/([A-Z])/g, ' $1')}
              </Chip>
            ))}
          </View>
        </View>

        <View style={styles.timerContainer}>
          <CircularProgress
            size={280}
            strokeWidth={12}
            progress={progress}
            color={colors.primary}
            backgroundColor={colors.surfaceVariant}
          >
            <Text style={styles.timeText}>{formatTime(timeLeft)}</Text>
            <Text style={styles.sessionText}>
              {sessions > 0 ? `Session ${sessions}` : 'Ready to focus'}
            </Text>
          </CircularProgress>
        </View>

        {currentTask ? (
          <Surface style={styles.taskCard} elevation={1}>
            <Text style={styles.taskLabel}>Focusing on:</Text>
            <Text style={styles.taskTitle}>{currentTask.title}</Text>
            {currentTask.energy_level && (
              <View style={styles.taskMeta}>
                <Chip
                  mode="flat"
                  style={[styles.energyChip, { backgroundColor: getEnergyColor(currentTask.energy_level) + '20' }]}
                  textStyle={{ color: getEnergyColor(currentTask.energy_level) }}
                >
                  Energy: {currentTask.energy_level}/5
                </Chip>
                {currentTask.time_estimate && (
                  <Chip mode="flat" style={styles.timeChip}>
                    ~{currentTask.time_estimate}min
                  </Chip>
                )}
              </View>
            )}
            <Button
              mode="text"
              onPress={() => setCurrentTask(null)}
              style={styles.changeTaskButton}
            >
              Change Task
            </Button>
          </Surface>
        ) : (
          <Surface style={styles.selectTaskCard} elevation={1}>
            <MaterialCommunityIcons
              name="checkbox-marked-circle-outline"
              size={24}
              color={colors.textSecondary}
            />
            <Text style={styles.selectTaskText}>Select a task to focus on</Text>
            <Text style={styles.selectTaskSubtext}>
              Choose from your energy-matched tasks
            </Text>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Tasks')}
              style={styles.selectButton}
            >
              Choose Task
            </Button>

            {/* Quick task suggestions */}
            {todaysTasks.filter(task => !task.completed && task.energy_level <= 3).slice(0, 2).map(task => (
              <Card
                key={task.id}
                style={styles.quickTaskCard}
                onPress={() => selectTaskForFocus(task)}
              >
                <Card.Content style={styles.quickTaskContent}>
                  <Text style={styles.quickTaskTitle}>{task.title}</Text>
                  <Text style={styles.quickTaskMeta}>
                    {task.energy_level}/5 energy • {task.time_estimate || 25}min
                  </Text>
                </Card.Content>
              </Card>
            ))}
          </Surface>
        )}

        <View style={styles.controls}>
          <IconButton
            icon="restart"
            size={32}
            onPress={resetTimer}
            disabled={!isRunning && timeLeft === currentMode.work}
            iconColor={colors.textSecondary}
          />
          <Button
            mode="contained"
            onPress={toggleTimer}
            style={styles.mainButton}
            contentStyle={styles.mainButtonContent}
            icon={isRunning ? 'pause' : 'play'}
          >
            {isRunning ? 'Pause' : 'Start'}
          </Button>
          <IconButton
            icon="skip-next"
            size={32}
            onPress={() => setTimeLeft(0)}
            disabled={!isRunning}
            iconColor={colors.textSecondary}
          />
        </View>

        <Surface style={styles.statsCard} elevation={1}>
          <Text style={styles.statsTitle}>Today's Focus Stats</Text>
          <View style={styles.stats}>
            <View style={styles.stat}>
              <MaterialCommunityIcons
                name="fire"
                size={24}
                color={colors.accent}
              />
              <Text style={styles.statValue}>{sessionStats.completedSessions}</Text>
              <Text style={styles.statLabel}>Sessions</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons
                name="clock-check"
                size={24}
                color={colors.success}
              />
              <Text style={styles.statValue}>
                {Math.floor(sessionStats.totalFocusTime / 60)}m
              </Text>
              <Text style={styles.statLabel}>Total Focus</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons
                name="brain"
                size={24}
                color={colors.focusHighlight}
              />
              <Text style={styles.statValue}>
                {sessionStats.averageSessionLength ? Math.floor(sessionStats.averageSessionLength / 60) : 0}m
              </Text>
              <Text style={styles.statLabel}>Avg Session</Text>
            </View>
          </View>

          {/* ADHD-specific insights */}
          {sessionStats.hyperfocusWarnings > 0 && (
            <View style={styles.adhdInsight}>
              <MaterialCommunityIcons
                name="lightbulb-outline"
                size={16}
                color={colors.warning}
              />
              <Text style={styles.insightText}>
                {sessionStats.hyperfocusWarnings} hyperfocus session{sessionStats.hyperfocusWarnings > 1 ? 's' : ''} today.
                Remember to take breaks!
              </Text>
            </View>
          )}
        </Surface>

        <Surface style={styles.tipsCard} elevation={1}>
          <Text style={styles.tipsTitle}>Focus Tips</Text>
          <View style={styles.tip}>
            <MaterialCommunityIcons 
              name="water" 
              size={20} 
              color={colors.focusHighlight}
            />
            <Text style={styles.tipText}>
              Stay hydrated - keep water nearby
            </Text>
          </View>
          <View style={styles.tip}>
            <MaterialCommunityIcons 
              name="cellphone-off" 
              size={20} 
              color={colors.focusHighlight}
            />
            <Text style={styles.tipText}>
              Enable Do Not Disturb mode
            </Text>
          </View>
          <View style={styles.tip}>
            <MaterialCommunityIcons 
              name="music" 
              size={20} 
              color={colors.focusHighlight}
            />
            <Text style={styles.tipText}>
              Try focus music or white noise
            </Text>
          </View>
        </Surface>
      </ScrollView>

      {/* ADHD-Specific Modals */}
      <Portal>
        {/* Hyperfocus Warning Modal */}
        <Modal
          visible={showHyperfocusWarning}
          onDismiss={() => setShowHyperfocusWarning(false)}
          contentContainerStyle={styles.modalContainer}
        >
          <Surface style={styles.modalContent} elevation={3}>
            <MaterialCommunityIcons
              name="alert-circle"
              size={48}
              color={colors.warning}
              style={styles.modalIcon}
            />
            <Text style={styles.modalTitle}>Hyperfocus Detected!</Text>
            <Text style={styles.modalText}>
              You've been focusing for longer than planned. This is great, but remember to take care of yourself.
            </Text>
            <Text style={styles.modalSubtext}>
              • Stretch your body{'\n'}
              • Hydrate{'\n'}
              • Check in with your energy
            </Text>
            <View style={styles.modalButtons}>
              <Button
                mode="outlined"
                onPress={() => {
                  setShowHyperfocusWarning(false);
                  setIsBreakTime(true);
                  setTimeLeft(currentMode.break);
                }}
                style={styles.modalButton}
              >
                Take Break
              </Button>
              <Button
                mode="contained"
                onPress={() => setShowHyperfocusWarning(false)}
                style={styles.modalButton}
              >
                Continue
              </Button>
            </View>
          </Surface>
        </Modal>

        {/* Break Reminder Modal */}
        <Modal
          visible={showBreakReminder}
          onDismiss={() => setShowBreakReminder(false)}
          contentContainerStyle={styles.modalContainer}
        >
          <Surface style={styles.modalContent} elevation={3}>
            <MaterialCommunityIcons
              name="coffee"
              size={48}
              color={colors.success}
              style={styles.modalIcon}
            />
            <Text style={styles.modalTitle}>Great Work! Time for a Break</Text>
            <Text style={styles.modalText}>
              You've completed a focus session. Taking breaks helps maintain your energy and prevents overwhelm.
            </Text>
            <Text style={styles.modalSubtext}>
              Break suggestions:{'\n'}
              • Walk around{'\n'}
              • Deep breathing{'\n'}
              • Gentle stretching{'\n'}
              • Hydrate
            </Text>
            <View style={styles.modalButtons}>
              <Button
                mode="outlined"
                onPress={skipBreak}
                style={styles.modalButton}
              >
                Skip Break
              </Button>
              <Button
                mode="contained"
                onPress={() => {
                  setShowBreakReminder(false);
                  setIsRunning(true);
                }}
                style={styles.modalButton}
              >
                Start Break
              </Button>
            </View>
          </Surface>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: 20,
    paddingBottom: 0,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 16,
  },
  modeSelector: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  modeChip: {
    backgroundColor: colors.surfaceVariant,
  },
  selectedModeChip: {
    backgroundColor: colors.primary + '20',
  },
  modeChipText: {
    color: colors.textSecondary,
    fontSize: 12,
  },
  selectedModeChipText: {
    color: colors.primary,
  },
  timerContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  timeText: {
    fontSize: 48,
    fontWeight: '300',
    color: colors.text,
    letterSpacing: 2,
  },
  sessionText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: 8,
  },
  taskCard: {
    marginHorizontal: 20,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.surface,
    alignItems: 'center',
  },
  taskLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.text,
    textAlign: 'center',
    marginBottom: 12,
  },
  changeTaskButton: {
    marginTop: 4,
  },
  selectTaskCard: {
    marginHorizontal: 20,
    padding: 24,
    borderRadius: 12,
    backgroundColor: colors.surface,
    alignItems: 'center',
  },
  selectTaskText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginVertical: 12,
  },
  selectButton: {
    marginTop: 8,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 32,
    gap: 16,
  },
  mainButton: {
    minWidth: 140,
  },
  mainButtonContent: {
    paddingVertical: 8,
  },
  statsCard: {
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  statsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 16,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  adhdInsight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 16,
    padding: 12,
    backgroundColor: colors.warning + '10',
    borderRadius: 8,
  },
  insightText: {
    fontSize: 12,
    color: colors.text,
    flex: 1,
    lineHeight: 16,
  },
  tipsCard: {
    marginHorizontal: 20,
    marginBottom: 40,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.focusHighlight + '10',
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 16,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: colors.text,
    flex: 1,
  },
  // ADHD-specific styles
  taskMeta: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
    marginBottom: 8,
  },
  energyChip: {
    backgroundColor: colors.surfaceVariant,
  },
  timeChip: {
    backgroundColor: colors.primary + '20',
  },
  selectTaskSubtext: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 16,
    textAlign: 'center',
  },
  quickTaskCard: {
    marginTop: 8,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.primary + '30',
  },
  quickTaskContent: {
    paddingVertical: 8,
  },
  quickTaskTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 4,
  },
  quickTaskMeta: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 20,
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    maxWidth: 320,
    width: '100%',
  },
  modalIcon: {
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
    textAlign: 'center',
  },
  modalText: {
    fontSize: 14,
    color: colors.text,
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 20,
  },
  modalSubtext: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'left',
    marginBottom: 20,
    lineHeight: 18,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
  },
  modalButton: {
    flex: 1,
  },
});