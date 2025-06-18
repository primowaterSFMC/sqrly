# Sqrly Mobile App

An ADHD-friendly task planner mobile app built with React Native, Expo, and React Native Paper.

## Features

- **ADHD-Centric Design**: Calming muted color scheme optimized for ADHD and executive dysfunction
- **Four-Quadrant System**: Eisenhower Matrix implementation for task prioritization
- **AI Integration**: Task breakdown and analysis with OpenAI integration
- **Energy Tracking**: Match tasks to your current energy levels
- **Focus Timer**: Pomodoro and custom focus sessions
- **Executive Function Support**: Difficulty ratings for initiation, execution, and completion

## Color Scheme

- **Background**: Soft Beige (#F9F8F4)
- **Primary**: Sage Green (#A8B9A2)  
- **Secondary**: Dusty Lavender (#C7B7D4)
- **Accent**: Muted Coral (#E1A192)
- **Focus Highlight**: Warm Blue (#A2B8D3)
- **Text**: Graphite Gray (#444444)

## Tech Stack

- **Framework**: React Native + Expo
- **UI Library**: React Native Paper (Material Design 3)
- **Navigation**: React Navigation
- **State Management**: React Context + AsyncStorage
- **Charts**: React Native Chart Kit
- **Icons**: Material Community Icons

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Run on device/simulator**:
   ```bash
   npm run ios     # iOS
   npm run android # Android
   ```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── TaskCard.tsx
│   ├── EnergyTracker.tsx
│   ├── QuadrantView.tsx
│   ├── AIAssistantModal.tsx
│   └── ...
├── screens/             # Screen components
│   ├── HomeScreen.tsx
│   ├── TasksScreen.tsx
│   ├── FocusScreen.tsx
│   ├── InsightsScreen.tsx
│   └── ProfileScreen.tsx
├── contexts/            # React Context providers
│   ├── AuthContext.tsx
│   └── TaskContext.tsx
└── theme.ts            # Design system & colors
```

## Key Screens

### Home Screen
- Today's task overview
- Energy level tracker
- Progress visualization
- Quick actions

### Tasks Screen
- List and quadrant views
- Task filtering and search
- AI-powered task breakdown
- Quick task capture

### Focus Screen
- Pomodoro timer
- Deep work sessions
- Task selection
- Focus statistics

### Insights Screen
- Productivity analytics
- Energy pattern analysis
- AI-generated recommendations
- Progress charts

### Profile Screen
- User settings
- ADHD-specific preferences
- Notification controls
- Help and support

## ADHD-Friendly Features

- **Overwhelm Prevention**: Visual indicators and gentle notifications
- **Executive Function Support**: Break down complex tasks automatically
- **Energy Matching**: Suggest tasks based on current energy levels
- **Focus Assistance**: Built-in timers and break reminders
- **Progress Visualization**: Clear progress indicators and achievement tracking

## Backend Integration

This mobile app connects to the Sqrly FastAPI backend for:
- User authentication
- Task synchronization
- AI-powered analysis
- Cross-device data sync

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for type safety
3. Maintain ADHD-friendly design principles
4. Test on both iOS and Android
5. Update documentation for new features

## License

Private - All rights reserved