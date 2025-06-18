import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { Text, Surface, Chip, SegmentedButtons } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import { LineChart, BarChart } from 'react-native-chart-kit';

const { width } = Dimensions.get('window');

export default function InsightsScreen() {
  const [timeframe, setTimeframe] = useState('week');
  const [selectedMetric, setSelectedMetric] = useState('completion');

  const chartConfig = {
    backgroundColor: colors.surface,
    backgroundGradientFrom: colors.surface,
    backgroundGradientTo: colors.surface,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(168, 185, 162, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(68, 68, 68, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: colors.primary,
    },
  };

  const completionData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [8, 12, 6, 15, 10, 5, 9],
        color: (opacity = 1) => `rgba(168, 185, 162, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const energyData = {
    labels: ['9AM', '12PM', '3PM', '6PM', '9PM'],
    datasets: [
      {
        data: [4.2, 3.8, 2.5, 3.2, 2.1],
      },
    ],
  };

  const insights = [
    {
      icon: 'trending-up',
      title: 'Productivity Peak',
      description: 'Your focus is strongest between 9-11 AM',
      color: colors.success,
      trend: '+15%',
    },
    {
      icon: 'lightbulb-outline',
      title: 'Task Completion',
      description: 'You complete 23% more tasks when they\'re broken down',
      color: colors.focusHighlight,
      trend: '+23%',
    },
    {
      icon: 'battery-70',
      title: 'Energy Patterns',
      description: 'Your energy dips after lunch - schedule lighter tasks',
      color: colors.warning,
      trend: '-30%',
    },
    {
      icon: 'timer',
      title: 'Focus Sessions',
      description: '25-minute sessions work best for your attention span',
      color: colors.accent,
      trend: '89%',
    },
  ];

  const weeklyStats = [
    { label: 'Tasks Completed', value: '47', change: '+12%', positive: true },
    { label: 'Focus Time', value: '8.5h', change: '+2.1h', positive: true },
    { label: 'Energy Level', value: '3.2/5', change: '-0.3', positive: false },
    { label: 'Completion Rate', value: '78%', change: '+5%', positive: true },
  ];

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Your Insights</Text>
          <Text style={styles.subtitle}>Understand your productivity patterns</Text>
          
          <SegmentedButtons
            value={timeframe}
            onValueChange={setTimeframe}
            buttons={[
              { value: 'week', label: 'Week' },
              { value: 'month', label: 'Month' },
              { value: 'quarter', label: '3 Months' },
            ]}
            style={styles.timeframeSelector}
          />
        </View>

        <Surface style={styles.statsGrid} elevation={1}>
          <Text style={styles.sectionTitle}>Weekly Overview</Text>
          <View style={styles.statsRow}>
            {weeklyStats.map((stat, index) => (
              <View key={index} style={styles.statCard}>
                <Text style={styles.statValue}>{stat.value}</Text>
                <Text style={styles.statLabel}>{stat.label}</Text>
                <View style={styles.changeRow}>
                  <MaterialCommunityIcons
                    name={stat.positive ? 'trending-up' : 'trending-down'}
                    size={14}
                    color={stat.positive ? colors.success : colors.error}
                  />
                  <Text
                    style={[
                      styles.changeText,
                      { color: stat.positive ? colors.success : colors.error },
                    ]}
                  >
                    {stat.change}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </Surface>

        <Surface style={styles.chartCard} elevation={1}>
          <View style={styles.chartHeader}>
            <Text style={styles.sectionTitle}>Task Completion</Text>
            <View style={styles.metricSelector}>
              {['completion', 'energy', 'focus'].map((metric) => (
                <Chip
                  key={metric}
                  mode="flat"
                  selected={selectedMetric === metric}
                  onPress={() => setSelectedMetric(metric)}
                  style={[
                    styles.metricChip,
                    selectedMetric === metric && styles.selectedMetricChip,
                  ]}
                  textStyle={[
                    styles.metricChipText,
                    selectedMetric === metric && styles.selectedMetricChipText,
                  ]}
                >
                  {metric.charAt(0).toUpperCase() + metric.slice(1)}
                </Chip>
              ))}
            </View>
          </View>
          
          {selectedMetric === 'completion' ? (
            <LineChart
              data={completionData}
              width={width - 60}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          ) : (
            <BarChart
              data={energyData}
              width={width - 60}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
            />
          )}
        </Surface>

        <View style={styles.insightsSection}>
          <Text style={styles.sectionTitle}>AI Insights</Text>
          {insights.map((insight, index) => (
            <Surface key={index} style={styles.insightCard} elevation={1}>
              <View style={styles.insightHeader}>
                <View style={[styles.insightIcon, { backgroundColor: insight.color + '15' }]}>
                  <MaterialCommunityIcons
                    name={insight.icon as any}
                    size={24}
                    color={insight.color}
                  />
                </View>
                <View style={styles.insightContent}>
                  <Text style={styles.insightTitle}>{insight.title}</Text>
                  <Text style={styles.insightDescription}>{insight.description}</Text>
                </View>
                <View style={styles.trendBadge}>
                  <Text style={[styles.trendText, { color: insight.color }]}>
                    {insight.trend}
                  </Text>
                </View>
              </View>
            </Surface>
          ))}
        </View>

        <Surface style={styles.recommendationsCard} elevation={1}>
          <Text style={styles.sectionTitle}>Recommendations</Text>
          <View style={styles.recommendation}>
            <MaterialCommunityIcons
              name="clock-outline"
              size={20}
              color={colors.focusHighlight}
            />
            <Text style={styles.recommendationText}>
              Schedule important tasks between 9-11 AM when your focus is strongest
            </Text>
          </View>
          <View style={styles.recommendation}>
            <MaterialCommunityIcons
              name="pause"
              size={20}
              color={colors.secondary}
            />
            <Text style={styles.recommendationText}>
              Take a 15-minute break after lunch to restore your energy levels
            </Text>
          </View>
          <View style={styles.recommendation}>
            <MaterialCommunityIcons
              name="robot"
              size={20}
              color={colors.primary}
            />
            <Text style={styles.recommendationText}>
              Use AI task breakdown for complex projects - it increases completion by 23%
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
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    marginBottom: 20,
  },
  timeframeSelector: {
    marginTop: 16,
  },
  statsGrid: {
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    padding: 12,
    borderRadius: 8,
    backgroundColor: colors.surfaceVariant,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: 6,
  },
  changeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  changeText: {
    fontSize: 12,
    fontWeight: '500',
  },
  chartCard: {
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  metricSelector: {
    flexDirection: 'row',
    gap: 6,
  },
  metricChip: {
    backgroundColor: colors.surfaceVariant,
    height: 28,
  },
  selectedMetricChip: {
    backgroundColor: colors.primary + '20',
  },
  metricChipText: {
    fontSize: 11,
    color: colors.textSecondary,
  },
  selectedMetricChipText: {
    color: colors.primary,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  insightsSection: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  insightCard: {
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  insightIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  insightContent: {
    flex: 1,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 4,
  },
  insightDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  trendBadge: {
    backgroundColor: colors.surfaceVariant,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  trendText: {
    fontSize: 12,
    fontWeight: '600',
  },
  recommendationsCard: {
    marginHorizontal: 20,
    marginBottom: 40,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.primary + '10',
  },
  recommendation: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 16,
  },
  recommendationText: {
    flex: 1,
    fontSize: 14,
    color: colors.text,
    lineHeight: 20,
  },
});