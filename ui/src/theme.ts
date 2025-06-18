import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const colors = {
  background: '#F9F8F4',      // Soft Beige
  primary: '#A8B9A2',         // Sage Green
  secondary: '#C7B7D4',       // Dusty Lavender
  accent: '#E1A192',          // Muted Coral
  focusHighlight: '#A2B8D3',  // Warm Blue
  text: '#444444',            // Graphite Gray
  textSecondary: '#666666',
  surface: '#FFFFFF',
  surfaceVariant: '#F5F4F0',
  error: '#D67B7B',
  success: '#95B895',
  warning: '#E6C695',
  disabled: '#C4C4C4',
};

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    secondary: colors.secondary,
    tertiary: colors.accent,
    surface: colors.surface,
    surfaceVariant: colors.surfaceVariant,
    background: colors.background,
    error: colors.error,
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onSurface: colors.text,
    onBackground: colors.text,
    elevation: {
      level0: 'transparent',
      level1: colors.surface,
      level2: colors.surface,
      level3: colors.surface,
      level4: colors.surface,
      level5: colors.surface,
    },
  },
  roundness: 12,
};