import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Text, Surface } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';

interface EnergyTrackerProps {
  currentEnergy: number;
  onEnergyChange: (energy: number) => void;
}

const energyLevels = [
  { level: 1, label: 'Very Low', icon: 'battery-10' as const, color: colors.error },
  { level: 2, label: 'Low', icon: 'battery-30' as const, color: colors.warning },
  { level: 3, label: 'Medium', icon: 'battery-50' as const, color: colors.secondary },
  { level: 4, label: 'Good', icon: 'battery-70' as const, color: colors.primary },
  { level: 5, label: 'High', icon: 'battery' as const, color: colors.success },
];

export default function EnergyTracker({ currentEnergy, onEnergyChange }: EnergyTrackerProps) {
  const currentEnergyData = energyLevels.find(e => e.level === currentEnergy) || energyLevels[2];

  return (
    <Surface style={styles.container} elevation={1}>
      <View style={styles.header}>
        <Text style={styles.title}>Current Energy</Text>
        <View style={styles.currentLevel}>
          <MaterialCommunityIcons
            name={currentEnergyData.icon}
            size={24}
            color={currentEnergyData.color}
          />
          <Text style={[styles.levelText, { color: currentEnergyData.color }]}>
            {currentEnergyData.label}
          </Text>
        </View>
      </View>

      <View style={styles.levels}>
        {energyLevels.map((energy) => (
          <TouchableOpacity
            key={energy.level}
            onPress={() => onEnergyChange(energy.level)}
            style={[
              styles.levelButton,
              currentEnergy === energy.level && styles.selectedLevel,
              currentEnergy === energy.level && { backgroundColor: energy.color + '20' }
            ]}
          >
            <MaterialCommunityIcons
              name={energy.icon}
              size={28}
              color={currentEnergy === energy.level ? energy.color : colors.disabled}
            />
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.hint}>
        Tap to update your energy level - we'll match tasks accordingly
      </Text>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    margin: 20,
    padding: 20,
    borderRadius: 16,
    backgroundColor: colors.surface,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  currentLevel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  levelText: {
    fontSize: 14,
    fontWeight: '500',
  },
  levels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  levelButton: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: colors.surfaceVariant,
  },
  selectedLevel: {
    transform: [{ scale: 1.1 }],
  },
  hint: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});