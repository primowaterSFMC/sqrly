import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, ScrollView, Animated } from 'react-native';
import { Text, Button, Surface, ProgressBar, IconButton, Chip } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import CircularProgress from '../components/CircularProgress';

export default function FocusScreen({ navigation, route }) {
  const [mode, setMode] = useState(route.params?.mode || 'pomodoro');
  const [isRunning, setIsRunning] = useState(false);
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [sessions, setSessions] = useState(0);
  const [currentTask, setCurrentTask] = useState(null);
  const animatedValue = useRef(new Animated.Value(0)).current;

  const focusModes = {
    pomodoro: {
      work: 25 * 60,
      break: 5 * 60,
      longBreak: 15 * 60,
      sessionsUntilLong: 4,
    },
    deepWork: {
      work: 90 * 60,
      break: 20 * 60,
    },
    microSession: {
      work: 10 * 60,
      break: 2 * 60,
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

  const handleSessionComplete = () => {
    setIsRunning(false);
    setSessions(prev => prev + 1);
    // TODO: Show notification, play sound
    // Reset timer for break
    setTimeLeft(currentMode.break);
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft(currentMode.work);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
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
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Tasks')}
              style={styles.selectButton}
            >
              Choose Task
            </Button>
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
              <Text style={styles.statValue}>{sessions}</Text>
              <Text style={styles.statLabel}>Sessions</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons 
                name="clock-check" 
                size={24} 
                color={colors.success}
              />
              <Text style={styles.statValue}>
                {Math.floor((sessions * currentMode.work) / 60)}m
              </Text>
              <Text style={styles.statLabel}>Total Focus</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons 
                name="trophy" 
                size={24} 
                color={colors.warning}
              />
              <Text style={styles.statValue}>3</Text>
              <Text style={styles.statLabel}>Day Streak</Text>
            </View>
          </View>
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
});