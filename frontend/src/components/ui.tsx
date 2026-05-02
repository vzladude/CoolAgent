import type { ReactNode } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  AlertTriangle,
  ChevronLeft,
  ClipboardList,
  Home,
  Settings,
  Wrench,
} from 'lucide-react-native';

import { shadow, theme } from '../theme/tokens';
import type { AppRouteName, IconComponent, NavigationApi, TabId } from '../types';

type ScreenProps = {
  children: ReactNode;
  scroll?: boolean;
  footer?: ReactNode;
};

export function Screen({ children, scroll = true, footer }: ScreenProps) {
  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      {scroll ? (
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {children}
        </ScrollView>
      ) : (
        <View style={styles.flex}>{children}</View>
      )}
      {footer}
    </SafeAreaView>
  );
}

export function Header({
  title,
  eyebrow,
  nav,
  right,
}: {
  title: string;
  eyebrow?: string;
  nav?: NavigationApi;
  right?: ReactNode;
}) {
  return (
    <View style={styles.header}>
      <View style={styles.headerTop}>
        {nav ? (
          <IconButton icon={ChevronLeft} onPress={nav.goBack} />
        ) : (
          <View style={styles.logoBox}>
            <Text style={styles.logoText}>C</Text>
          </View>
        )}
        {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
        <View style={styles.headerRight}>{right}</View>
      </View>
      <Text style={styles.title}>{title}</Text>
    </View>
  );
}

export function BottomTabs({ nav }: { nav: NavigationApi }) {
  const tabs: { id: TabId; label: string; icon: IconComponent }[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'cases', label: 'Casos', icon: ClipboardList },
    { id: 'tools', label: 'Herr.', icon: Wrench },
    { id: 'codes', label: 'Codigos', icon: AlertTriangle },
    { id: 'settings', label: 'Ajustes', icon: Settings },
  ];

  return (
    <View style={styles.tabBar}>
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const active = nav.activeTab === tab.id;
        return (
          <Pressable
            key={tab.id}
            onPress={() => nav.resetToTab(tab.id)}
            style={[styles.tabItem, active && styles.tabItemActive]}
          >
            <Icon
              size={18}
              color={active ? theme.color.black : theme.color.muted}
              strokeWidth={2}
            />
            <Text style={[styles.tabLabel, active && styles.tabLabelActive]}>
              {tab.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export function Panel({
  children,
  accent,
}: {
  children: ReactNode;
  accent?: boolean;
}) {
  return <View style={[styles.panel, accent && styles.panelAccent]}>{children}</View>;
}

export function SectionTitle({ children }: { children: ReactNode }) {
  return <Text style={styles.sectionTitle}>{children}</Text>;
}

export function BodyText({ children, muted }: { children: ReactNode; muted?: boolean }) {
  return <Text style={[styles.body, muted && styles.bodyMuted]}>{children}</Text>;
}

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode;
  tone?: 'neutral' | 'accent' | 'success' | 'warning' | 'danger';
}) {
  return <Text style={[styles.badge, styles[`badge_${tone}`]]}>{children}</Text>;
}

export function PrimaryButton({
  label,
  icon: Icon,
  onPress,
  variant = 'primary',
}: {
  label: string;
  icon?: IconComponent;
  onPress: () => void;
  variant?: 'primary' | 'ghost';
}) {
  const ghost = variant === 'ghost';
  return (
    <Pressable
      onPress={onPress}
      style={[styles.button, ghost && styles.buttonGhost]}
    >
      {Icon ? (
        <Icon
          size={16}
          color={ghost ? theme.color.text : theme.color.black}
          strokeWidth={2.2}
        />
      ) : null}
      <Text style={[styles.buttonText, ghost && styles.buttonTextGhost]}>
        {label}
      </Text>
    </Pressable>
  );
}

export function IconButton({
  icon: Icon,
  onPress,
}: {
  icon: IconComponent;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={styles.iconButton}>
      <Icon size={18} color={theme.color.text} strokeWidth={2} />
    </Pressable>
  );
}

export function ToolTile({
  title,
  subtitle,
  icon: Icon,
  badge,
  onPress,
}: {
  title: string;
  subtitle: string;
  icon: IconComponent;
  badge?: string;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={styles.toolTile}>
      <View style={styles.toolIcon}>
        <Icon size={20} color={theme.color.accent} strokeWidth={2} />
      </View>
      {badge ? <Badge tone={badge === 'OFFLINE' ? 'success' : 'accent'}>{badge}</Badge> : null}
      <Text style={styles.toolTitle}>{title}</Text>
      <Text style={styles.toolSubtitle}>{subtitle}</Text>
    </Pressable>
  );
}

export function ListRow({
  title,
  subtitle,
  meta,
  icon: Icon,
  onPress,
  right,
}: {
  title: string;
  subtitle?: string;
  meta?: string;
  icon?: IconComponent;
  onPress?: () => void;
  right?: ReactNode;
}) {
  const content = (
    <View style={styles.row}>
      {Icon ? (
        <View style={styles.rowIcon}>
          <Icon size={18} color={theme.color.text} strokeWidth={1.8} />
        </View>
      ) : null}
      <View style={styles.rowBody}>
        {meta ? <Text style={styles.rowMeta}>{meta}</Text> : null}
        <Text style={styles.rowTitle}>{title}</Text>
        {subtitle ? <Text style={styles.rowSubtitle}>{subtitle}</Text> : null}
      </View>
      {right}
    </View>
  );

  return onPress ? <Pressable onPress={onPress}>{content}</Pressable> : content;
}

export function Field({
  label,
  value,
  onChangeText,
  placeholder,
}: {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.color.dim}
        style={styles.input}
      />
    </View>
  );
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <Panel>
      <Text style={styles.emptyTitle}>{title}</Text>
      <Text style={styles.emptyBody}>{body}</Text>
      {action ? <View style={styles.emptyAction}>{action}</View> : null}
    </Panel>
  );
}

export function openTabRoute(tab: TabId): AppRouteName {
  return tab === 'home'
    ? 'home'
    : tab === 'cases'
      ? 'cases'
      : tab === 'tools'
        ? 'tools'
        : tab === 'codes'
          ? 'codes'
          : 'settings';
}

export const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: theme.color.bg,
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 120,
    gap: 14,
  },
  header: {
    gap: 8,
    marginBottom: 2,
  },
  headerTop: {
    alignItems: 'center',
    flexDirection: 'row',
    minHeight: 36,
  },
  headerRight: {
    alignItems: 'flex-end',
    flex: 1,
  },
  logoBox: {
    alignItems: 'center',
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    height: 32,
    justifyContent: 'center',
    width: 32,
  },
  logoText: {
    color: theme.color.black,
    fontFamily: theme.font.mono,
    fontSize: 16,
    fontWeight: '700',
  },
  eyebrow: {
    color: theme.color.dim,
    fontFamily: theme.font.mono,
    fontSize: 11,
    letterSpacing: 0,
    marginLeft: 10,
    textTransform: 'uppercase',
  },
  title: {
    color: theme.color.text,
    fontSize: 25,
    fontWeight: '700',
    letterSpacing: 0,
    lineHeight: 31,
  },
  panel: {
    backgroundColor: theme.color.surface,
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    padding: 14,
  },
  panelAccent: {
    borderColor: theme.color.lineStrong,
    ...shadow,
  },
  sectionTitle: {
    color: theme.color.dim,
    fontFamily: theme.font.mono,
    fontSize: 11,
    letterSpacing: 0,
    marginTop: 6,
    textTransform: 'uppercase',
  },
  body: {
    color: theme.color.text,
    fontSize: 14,
    lineHeight: 20,
  },
  bodyMuted: {
    color: theme.color.muted,
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: theme.radius.pill,
    fontFamily: theme.font.mono,
    fontSize: 10,
    overflow: 'hidden',
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  badge_neutral: {
    backgroundColor: theme.color.surfaceAlt,
    color: theme.color.muted,
  },
  badge_accent: {
    backgroundColor: theme.color.accentSoft,
    color: theme.color.accent,
  },
  badge_success: {
    backgroundColor: theme.color.successSoft,
    color: theme.color.success,
  },
  badge_warning: {
    backgroundColor: theme.color.warningSoft,
    color: theme.color.warning,
  },
  badge_danger: {
    backgroundColor: theme.color.dangerSoft,
    color: theme.color.danger,
  },
  button: {
    alignItems: 'center',
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    flexDirection: 'row',
    gap: 8,
    justifyContent: 'center',
    minHeight: 44,
    paddingHorizontal: 14,
  },
  buttonGhost: {
    backgroundColor: 'transparent',
    borderColor: theme.color.lineStrong,
    borderWidth: 1,
  },
  buttonText: {
    color: theme.color.black,
    fontSize: 14,
    fontWeight: '700',
  },
  buttonTextGhost: {
    color: theme.color.text,
  },
  iconButton: {
    alignItems: 'center',
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    height: 36,
    justifyContent: 'center',
    width: 36,
  },
  tabBar: {
    alignItems: 'center',
    backgroundColor: theme.color.black,
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    bottom: 20,
    flexDirection: 'row',
    gap: 6,
    left: 16,
    padding: 6,
    position: 'absolute',
    right: 16,
  },
  tabItem: {
    alignItems: 'center',
    borderRadius: theme.radius.sm,
    flex: 1,
    gap: 2,
    minHeight: 48,
    justifyContent: 'center',
  },
  tabItemActive: {
    backgroundColor: theme.color.accent,
  },
  tabLabel: {
    color: theme.color.muted,
    fontSize: 10,
    fontWeight: '600',
  },
  tabLabelActive: {
    color: theme.color.black,
  },
  toolTile: {
    backgroundColor: theme.color.surface,
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    flex: 1,
    gap: 8,
    minHeight: 132,
    padding: 14,
  },
  toolIcon: {
    alignItems: 'center',
    backgroundColor: theme.color.accentSoft,
    borderRadius: theme.radius.md,
    height: 38,
    justifyContent: 'center',
    width: 38,
  },
  toolTitle: {
    color: theme.color.text,
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 18,
  },
  toolSubtitle: {
    color: theme.color.muted,
    fontSize: 12,
    lineHeight: 16,
  },
  row: {
    alignItems: 'center',
    backgroundColor: theme.color.surface,
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 12,
    padding: 12,
  },
  rowIcon: {
    alignItems: 'center',
    backgroundColor: theme.color.surfaceAlt,
    borderRadius: theme.radius.md,
    height: 36,
    justifyContent: 'center',
    width: 36,
  },
  rowBody: {
    flex: 1,
    gap: 3,
  },
  rowMeta: {
    color: theme.color.accent,
    fontFamily: theme.font.mono,
    fontSize: 10,
  },
  rowTitle: {
    color: theme.color.text,
    fontSize: 14,
    fontWeight: '700',
  },
  rowSubtitle: {
    color: theme.color.muted,
    fontSize: 12,
    lineHeight: 16,
  },
  field: {
    gap: 6,
  },
  fieldLabel: {
    color: theme.color.dim,
    fontFamily: theme.font.mono,
    fontSize: 11,
    textTransform: 'uppercase',
  },
  input: {
    backgroundColor: theme.color.surfaceAlt,
    borderColor: theme.color.line,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    color: theme.color.text,
    fontSize: 15,
    minHeight: 44,
    paddingHorizontal: 12,
  },
  emptyTitle: {
    color: theme.color.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  emptyBody: {
    color: theme.color.muted,
    fontSize: 14,
    lineHeight: 20,
  },
  emptyAction: {
    marginTop: 14,
  },
});
