import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import { Text, Surface, Switch, Button, Avatar, Divider, List, Chip, Card, Modal, Portal, TextInput } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';
import { useAuth } from '../contexts/AuthContext';
import { useTask } from '../contexts/TaskContext';
import { ProfileScreenProps } from '../types/navigation';
import apiService from '../services/api';

export default function ProfileScreen({ navigation }: ProfileScreenProps) {
  const { user, signOut } = useAuth();
  const { tasks } = useTask();
  const [notifications, setNotifications] = useState(true);
  const [focusReminders, setFocusReminders] = useState(true);
  const [weeklyReport, setWeeklyReport] = useState(false);
  const [adhdProfile, setAdhdProfile] = useState(user?.adhd_preferences || {});
  const [userStats, setUserStats] = useState({
    streak: 0,
    totalTasks: 0,
    focusTime: '0h 0m',
    completedToday: 0
  });
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingField, setEditingField] = useState('');
  const [editValue, setEditValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadUserStats();
    loadUserPreferences();
  }, [tasks]);

  const loadUserStats = async () => {
    try {
      // Calculate stats from tasks
      const completedTasks = tasks.filter(task => task.completed);
      const todayCompleted = tasks.filter(task =>
        task.completed &&
        new Date(task.updated_at || task.created_at).toDateString() === new Date().toDateString()
      );

      // Get focus stats from API
      const focusStats = await apiService.getFocusStats('all');

      setUserStats({
        streak: focusStats.streak || 5,
        totalTasks: completedTasks.length,
        focusTime: formatFocusTime(focusStats.totalFocusTime || 0),
        completedToday: todayCompleted.length
      });
    } catch (error) {
      console.error('Failed to load user stats:', error);
    }
  };

  const loadUserPreferences = async () => {
    try {
      const preferences = await apiService.get('/users/me/preferences');
      setNotifications(preferences.pushNotifications ?? true);
      setFocusReminders(preferences.gentleReminders ?? true);
      setWeeklyReport(preferences.emailNotifications ?? false);
    } catch (error) {
      console.error('Failed to load preferences:', error);
    }
  };

  const formatFocusTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const updatePreference = async (key: string, value: boolean) => {
    try {
      await apiService.put('/users/me/preferences', { [key]: value });
    } catch (error) {
      console.error('Failed to update preference:', error);
      Alert.alert('Error', 'Failed to update preference');
    }
  };

  const handleSignOut = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Sign Out', style: 'destructive', onPress: signOut },
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. All your data will be permanently deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => {} },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <Surface style={styles.profileCard} elevation={1}>
          <View style={styles.profileHeader}>
            <Avatar.Text
              size={80}
              label={user?.first_name?.[0] || 'U'}
              style={styles.avatar}
              color="#FFFFFF"
            />
            <View style={styles.userInfo}>
              <Text style={styles.userName}>
                {user?.first_name} {user?.last_name}
              </Text>
              <Text style={styles.userEmail}>{user?.email}</Text>
              <Text style={styles.memberSince}>
                Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'Recently'}
              </Text>
              {user?.subscription_tier && (
                <View style={styles.profileMeta}>
                  <Chip mode="flat" style={styles.tierChip}>
                    {user.subscription_tier.charAt(0).toUpperCase() + user.subscription_tier.slice(1)}
                  </Chip>
                  {userStats.completedToday > 0 && (
                    <Chip mode="flat" style={styles.todayChip}>
                      {userStats.completedToday} done today
                    </Chip>
                  )}
                </View>
              )}
            </View>
          </View>

          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <MaterialCommunityIcons name="fire" size={24} color={colors.accent} />
              <Text style={styles.statValue}>{userStats.streak}</Text>
              <Text style={styles.statLabel}>Day Streak</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons name="check-circle" size={24} color={colors.success} />
              <Text style={styles.statValue}>{userStats.totalTasks}</Text>
              <Text style={styles.statLabel}>Tasks Done</Text>
            </View>
            <View style={styles.stat}>
              <MaterialCommunityIcons name="clock" size={24} color={colors.focusHighlight} />
              <Text style={styles.statValue}>{userStats.focusTime}</Text>
              <Text style={styles.statLabel}>Focus Time</Text>
            </View>
          </View>
        </Surface>

        <Surface style={styles.settingsCard} elevation={1}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Push Notifications</Text>
              <Text style={styles.settingDescription}>
                Get notified about tasks and reminders
              </Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={(value) => {
                setNotifications(value);
                updatePreference('pushNotifications', value);
              }}
              color={colors.primary}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Focus Reminders</Text>
              <Text style={styles.settingDescription}>
                Gentle reminders to take breaks
              </Text>
            </View>
            <Switch
              value={focusReminders}
              onValueChange={(value) => {
                setFocusReminders(value);
                updatePreference('gentleReminders', value);
              }}
              color={colors.primary}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Weekly Report</Text>
              <Text style={styles.settingDescription}>
                Get a summary of your productivity
              </Text>
            </View>
            <Switch
              value={weeklyReport}
              onValueChange={(value) => {
                setWeeklyReport(value);
                updatePreference('emailNotifications', value);
              }}
              color={colors.primary}
            />
          </View>
        </Surface>

        <Surface style={styles.settingsCard} elevation={1}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          
          <List.Item
            title="ADHD Support Settings"
            description="Customize your executive function support"
            left={(props) => (
              <MaterialCommunityIcons
                name="brain"
                size={24}
                color={colors.primary}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.textSecondary} />
            )}
            onPress={() => navigation.navigate('ADHDSettings')}
            style={styles.listItem}
          />

          <List.Item
            title="Task Preferences"
            description="Default settings for new tasks"
            left={(props) => (
              <MaterialCommunityIcons
                name="cog"
                size={24}
                color={colors.secondary}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.textSecondary} />
            )}
            onPress={() => navigation.navigate('TaskSettings')}
            style={styles.listItem}
          />

          <List.Item
            title="Data & Privacy"
            description="Manage your data and privacy settings"
            left={(props) => (
              <MaterialCommunityIcons
                name="shield-check"
                size={24}
                color={colors.focusHighlight}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.textSecondary} />
            )}
            onPress={() => navigation.navigate('Privacy')}
            style={styles.listItem}
          />
        </Surface>

        <Surface style={styles.supportCard} elevation={1}>
          <Text style={styles.sectionTitle}>Support</Text>
          
          <List.Item
            title="Help & Tutorial"
            description="Learn how to use Sqrly effectively"
            left={(props) => (
              <MaterialCommunityIcons
                name="help-circle"
                size={24}
                color={colors.accent}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.textSecondary} />
            )}
            onPress={() => navigation.navigate('Help')}
            style={styles.listItem}
          />

          <List.Item
            title="Send Feedback"
            description="Help us improve the app"
            left={(props) => (
              <MaterialCommunityIcons
                name="message-text"
                size={24}
                color={colors.secondary}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.textSecondary} />
            )}
            onPress={() => navigation.navigate('Feedback')}
            style={styles.listItem}
          />

          <List.Item
            title="Rate Sqrly"
            description="Share your experience on the App Store"
            left={(props) => (
              <MaterialCommunityIcons
                name="star"
                size={24}
                color={colors.warning}
                style={{ marginLeft: 12 }}
              />
            )}
            right={(props) => (
              <MaterialCommunityIcons name="external-link" size={24} color={colors.textSecondary} />
            )}
            onPress={() => {}}
            style={styles.listItem}
          />
        </Surface>

        <View style={styles.accountActions}>
          <Button
            mode="outlined"
            onPress={handleSignOut}
            style={styles.signOutButton}
            textColor={colors.text}
          >
            Sign Out
          </Button>
          
          <Button
            mode="text"
            onPress={handleDeleteAccount}
            style={styles.deleteButton}
            textColor={colors.error}
          >
            Delete Account
          </Button>
        </View>

        <View style={styles.footer}>
          <Text style={styles.version}>Version 1.0.0</Text>
          <Text style={styles.copyright}>© 2024 Sqrly. Made with ❤️ for ADHD minds.</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  profileCard: {
    margin: 20,
    padding: 24,
    borderRadius: 16,
    backgroundColor: colors.surface,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  avatar: {
    backgroundColor: colors.primary,
    marginRight: 16,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  memberSince: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  profileMeta: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 4,
  },
  tierChip: {
    backgroundColor: colors.primary + '20',
  },
  todayChip: {
    backgroundColor: colors.success + '20',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceVariant,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  settingsCard: {
    marginHorizontal: 20,
    marginBottom: 16,
    padding: 20,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  supportCard: {
    marginHorizontal: 20,
    marginBottom: 16,
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
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceVariant,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    color: colors.text,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  listItem: {
    paddingHorizontal: 0,
    paddingVertical: 8,
  },
  accountActions: {
    paddingHorizontal: 20,
    marginBottom: 32,
  },
  signOutButton: {
    marginBottom: 12,
    borderColor: colors.textSecondary,
  },
  deleteButton: {
    alignSelf: 'center',
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 40,
  },
  version: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  copyright: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});