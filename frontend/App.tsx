import { useMemo, useState } from 'react';
import { View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { BottomTabs, openTabRoute } from './src/components/ui';
import {
  CaseDetailsScreen,
  CasesListScreen,
  ChatScreen,
  NewCaseScreen,
} from './src/screens/cases';
import { ErrorCodeDetailScreen, ErrorCodesScreen } from './src/screens/codes';
import { HomeScreen } from './src/screens/home';
import { SettingsScreen } from './src/screens/settings';
import {
  CalculatorScreen,
  DiagnosisAnalyzingScreen,
  DiagnosisCaptureScreen,
  DiagnosisContextScreen,
  DiagnosisResultScreen,
  GuideDetailScreen,
  GuidesScreen,
  OfflineScreen,
  ToolsHubScreen,
} from './src/screens/tools';
import { theme } from './src/theme/tokens';
import type { AppRoute, AppRouteName, NavigationApi, TabId } from './src/types';

function tabForRoute(routeName: AppRouteName): TabId {
  if (routeName === 'cases' || routeName === 'newCase' || routeName === 'chat' || routeName === 'caseDetails') {
    return 'cases';
  }
  if (
    routeName === 'tools' ||
    routeName === 'diagnosisCapture' ||
    routeName === 'diagnosisContext' ||
    routeName === 'diagnosisAnalyzing' ||
    routeName === 'diagnosisResult' ||
    routeName === 'calculator' ||
    routeName === 'guides' ||
    routeName === 'guideDetail' ||
    routeName === 'offline'
  ) {
    return 'tools';
  }
  if (routeName === 'codes' || routeName === 'codeDetail') {
    return 'codes';
  }
  if (routeName === 'settings') {
    return 'settings';
  }
  return 'home';
}

function renderRoute(route: AppRoute, nav: NavigationApi) {
  switch (route.name) {
    case 'home':
      return <HomeScreen nav={nav} />;
    case 'cases':
      return <CasesListScreen nav={nav} />;
    case 'newCase':
      return <NewCaseScreen nav={nav} />;
    case 'chat':
      return <ChatScreen nav={nav} caseId={route.params?.caseId} initialCase={route.params?.case} />;
    case 'caseDetails':
      return <CaseDetailsScreen nav={nav} caseId={route.params?.caseId} initialCase={route.params?.case} />;
    case 'tools':
      return <ToolsHubScreen nav={nav} />;
    case 'diagnosisCapture':
      return <DiagnosisCaptureScreen nav={nav} />;
    case 'diagnosisContext':
      return <DiagnosisContextScreen nav={nav} />;
    case 'diagnosisAnalyzing':
      return <DiagnosisAnalyzingScreen nav={nav} />;
    case 'diagnosisResult':
      return <DiagnosisResultScreen nav={nav} />;
    case 'calculator':
      return <CalculatorScreen nav={nav} mode={route.params?.mode} />;
    case 'guides':
      return <GuidesScreen nav={nav} />;
    case 'guideDetail':
      return <GuideDetailScreen nav={nav} guideId={route.params?.guideId} />;
    case 'offline':
      return <OfflineScreen nav={nav} />;
    case 'codes':
      return <ErrorCodesScreen nav={nav} />;
    case 'codeDetail':
      return <ErrorCodeDetailScreen nav={nav} codeId={route.params?.codeId} initialCode={route.params?.code} />;
    case 'settings':
      return <SettingsScreen nav={nav} />;
    default:
      return <HomeScreen nav={nav} />;
  }
}

export default function App() {
  const [stack, setStack] = useState<AppRoute[]>([{ name: 'home' }]);
  const currentRoute = stack[stack.length - 1];

  const nav = useMemo<NavigationApi>(
    () => ({
      activeTab: tabForRoute(currentRoute.name),
      goBack: () => setStack((current) => (current.length > 1 ? current.slice(0, -1) : current)),
      open: (name, params) => setStack((current) => [...current, { name, params }]),
      resetToTab: (tab) => setStack([{ name: openTabRoute(tab) }]),
    }),
    [currentRoute.name],
  );

  return (
    <SafeAreaProvider>
      <View style={{ backgroundColor: theme.color.bg, flex: 1 }}>
        <StatusBar backgroundColor={theme.color.bg} style="light" translucent={false} />
        {renderRoute(currentRoute, nav)}
        <BottomTabs nav={nav} />
      </View>
    </SafeAreaProvider>
  );
}
