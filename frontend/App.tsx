import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { BodyText, BottomTabs, Header, openTabRoute, Panel, Screen } from './src/components/ui';
import { AuthScreen } from './src/screens/auth';
import {
  CaseDetailsScreen,
  CasesListScreen,
  ChatScreen,
  NewCaseScreen,
} from './src/screens/cases';
import { ErrorCodeDetailScreen, ErrorCodesScreen } from './src/screens/codes';
import { HomeScreen } from './src/screens/home';
import { SettingsScreen } from './src/screens/settings';
import { api } from './src/services/api';
import { clearStoredToken, loadStoredToken, saveStoredToken } from './src/services/authStorage';
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
import type {
  AppRoute,
  AppRouteName,
  AuthActions,
  AuthCredentials,
  AuthRegisterInput,
  AuthSession,
  NavigationApi,
  TabId,
} from './src/types';

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

function localSession(): AuthSession {
  const now = new Date().toISOString();
  return {
    isLocal: true,
    user: {
      id: 'LOCAL-USER',
      email: 'local@coolagent.dev',
      fullName: 'Tecnico local',
      role: 'technician',
      isActive: true,
      isVerified: false,
      createdAt: now,
      updatedAt: now,
    },
  };
}

function LoadingSessionScreen() {
  return (
    <Screen>
      <Header title="CoolAgent" eyebrow="Sesion" />
      <Panel>
        <View style={{ alignItems: 'center', flexDirection: 'row', gap: 10 }}>
          <ActivityIndicator color={theme.color.accent} />
          <BodyText muted>Restaurando sesion...</BodyText>
        </View>
      </Panel>
    </Screen>
  );
}

function renderRoute(route: AppRoute, nav: NavigationApi, session: AuthSession, auth: AuthActions) {
  switch (route.name) {
    case 'auth':
      return <AuthScreen auth={auth} />;
    case 'home':
      return <HomeScreen nav={nav} session={session} />;
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
      return <SettingsScreen nav={nav} session={session} onLogout={auth.logout} />;
    default:
      return <HomeScreen nav={nav} session={session} />;
  }
}

export default function App() {
  const [stack, setStack] = useState<AppRoute[]>([{ name: 'home' }]);
  const [session, setSession] = useState<AuthSession | null>(null);
  const [authNotice, setAuthNotice] = useState<string | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const currentRoute = stack[stack.length - 1];

  useEffect(() => {
    let cancelled = false;
    api.setUnauthorizedHandler(async () => {
      api.setAuthToken(null);
      api.setLocalMode(false);
      await clearStoredToken();
      if (!cancelled) {
        setAuthNotice('Tu sesion expiro. Entra de nuevo para sincronizar casos.');
        setSession(null);
        setStack([{ name: 'home' }]);
      }
    });

    const restoreSession = async () => {
      const token = await loadStoredToken();
      if (!token) {
        if (!cancelled) setSessionLoading(false);
        return;
      }

      api.setAuthToken(token);
      api.setLocalMode(false);
      try {
        const user = await api.getCurrentUser();
        if (!cancelled) {
          setAuthNotice(null);
          setSession({
            accessToken: token,
            tokenType: 'bearer',
            user,
          });
        }
      } catch {
        api.setAuthToken(null);
        api.setLocalMode(false);
        await clearStoredToken();
      } finally {
        if (!cancelled) setSessionLoading(false);
      }
    };

    void restoreSession();
    return () => {
      cancelled = true;
      api.setUnauthorizedHandler(undefined);
    };
  }, []);

  const nav = useMemo<NavigationApi>(
    () => ({
      activeTab: tabForRoute(currentRoute.name),
      goBack: () => setStack((current) => (current.length > 1 ? current.slice(0, -1) : current)),
      open: (name, params) => setStack((current) => [...current, { name, params }]),
      resetToTab: (tab) => setStack([{ name: openTabRoute(tab) }]),
    }),
    [currentRoute.name],
  );

  const auth = useMemo<AuthActions>(
    () => ({
      login: async (credentials: AuthCredentials) => {
        const nextSession = await api.login(credentials);
        api.setAuthToken(nextSession.accessToken);
        api.setLocalMode(false);
        if (nextSession.accessToken) {
          await saveStoredToken(nextSession.accessToken);
        }
        setAuthNotice(null);
        setSession(nextSession);
        setStack([{ name: 'home' }]);
      },
      register: async (input: AuthRegisterInput) => {
        await api.register(input);
        const nextSession = await api.login({
          email: input.email,
          password: input.password,
        });
        api.setAuthToken(nextSession.accessToken);
        api.setLocalMode(false);
        if (nextSession.accessToken) {
          await saveStoredToken(nextSession.accessToken);
        }
        setAuthNotice(null);
        setSession(nextSession);
        setStack([{ name: 'home' }]);
      },
      continueLocal: () => {
        api.setAuthToken(null);
        api.setLocalMode(true);
        setAuthNotice(null);
        setSession(localSession());
        setStack([{ name: 'home' }]);
      },
      logout: async () => {
        api.setAuthToken(null);
        api.setLocalMode(false);
        await clearStoredToken();
        setAuthNotice(null);
        setSession(null);
        setStack([{ name: 'home' }]);
      },
    }),
    [],
  );

  return (
    <SafeAreaProvider>
      <View style={{ backgroundColor: theme.color.bg, flex: 1 }}>
        <StatusBar backgroundColor={theme.color.bg} style="light" translucent={false} />
        {sessionLoading ? (
          <LoadingSessionScreen />
        ) : session ? (
          <>
            {renderRoute(currentRoute, nav, session, auth)}
            <BottomTabs nav={nav} />
          </>
        ) : (
          <AuthScreen auth={auth} notice={authNotice} />
        )}
      </View>
    </SafeAreaProvider>
  );
}
