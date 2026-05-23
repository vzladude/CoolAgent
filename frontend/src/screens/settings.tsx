import { Text, View } from 'react-native';
import {
  Bell,
  CircleHelp,
  Cloud,
  Info,
  LogOut,
  Moon,
  Ruler,
  ShieldAlert,
  User,
} from 'lucide-react-native';

import { Badge, BodyText, Header, ListRow, Panel, PrimaryButton, Screen, SectionTitle } from '../components/ui';
import { api } from '../services/api';
import { theme } from '../theme/tokens';
import type { AuthSession, NavigationApi } from '../types';

function profileName(session: AuthSession) {
  return session.user.fullName ?? session.user.email;
}

function profileStatus(session: AuthSession) {
  if (session.isLocal) return 'Sesion local';
  return session.user.isVerified ? 'Email verificado' : 'Email pendiente';
}

export function SettingsScreen({
  nav,
  session,
  onLogout,
}: {
  nav: NavigationApi;
  session: AuthSession;
  onLogout: () => Promise<void>;
}) {
  return (
    <Screen>
      <Header title="Ajustes" eyebrow="CoolAgent" />

      <Panel accent>
        <View style={{ flexDirection: 'row', gap: 12, alignItems: 'center' }}>
          <View
            style={{
              alignItems: 'center',
              backgroundColor: theme.color.accent,
              borderRadius: theme.radius.md,
              height: 48,
              justifyContent: 'center',
              width: 48,
            }}
          >
            <User size={22} color={theme.color.black} strokeWidth={2} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: theme.color.text, fontSize: 18, fontWeight: '800' }}>
              {profileName(session)}
            </Text>
            <BodyText muted>{profileStatus(session)}</BodyText>
          </View>
          <Badge tone={session.isLocal ? 'warning' : 'success'}>{session.user.role.toUpperCase()}</Badge>
        </View>
      </Panel>

      <SectionTitle>Cuenta</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow
          title="Email"
          subtitle={session.user.email}
          icon={User}
          right={<Badge tone={session.user.isActive ? 'success' : 'danger'}>{session.user.isActive ? 'activo' : 'inactivo'}</Badge>}
        />
        <ListRow
          title="Token"
          subtitle={session.isLocal ? 'Casos y chat usan datos mock' : 'Guardado en SecureStore para chat y usage'}
          icon={ShieldAlert}
          right={<Badge tone={session.isLocal ? 'warning' : 'success'}>{session.isLocal ? 'local' : 'seguro'}</Badge>}
        />
      </View>

      <SectionTitle>Preferencias</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow title="Idioma" subtitle="Espanol" icon={Info} />
        <ListRow title="Unidades" subtitle="Celsius / PSI" icon={Ruler} />
        <ListRow title="Tema" subtitle="Oscuro" icon={Moon} />
        <ListRow title="Notificaciones" subtitle="Pendiente para version futura" icon={Bell} />
      </View>

      <SectionTitle>Conexion</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow
          title="API backend"
          subtitle={api.baseUrl}
          icon={Cloud}
          right={<Badge tone={session.isLocal ? 'warning' : 'accent'}>{session.isLocal ? 'LOCAL' : 'AUTH'}</Badge>}
        />
        <ListRow
          title="Offline / Sync"
          subtitle="Ver datos locales y acciones pendientes"
          icon={Cloud}
          onPress={() => nav.open('offline')}
        />
      </View>

      <SectionTitle>Seguridad tecnica</SectionTitle>
      <Panel>
        <View style={{ flexDirection: 'row', gap: 12 }}>
          <ShieldAlert size={22} color={theme.color.warning} strokeWidth={1.8} />
          <View style={{ flex: 1 }}>
            <BodyText>
              Verifica mediciones, EPP y normativa aplicable antes de intervenir equipos.
            </BodyText>
            <Text style={{ color: theme.color.muted, fontSize: 12, marginTop: 8 }}>
              CoolAgent apoya diagnostico tecnico, no reemplaza criterio profesional.
            </Text>
          </View>
        </View>
      </Panel>

      <SectionTitle>Ayuda</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow title="Soporte" subtitle="Canal pendiente" icon={CircleHelp} />
        <ListRow title="Version" subtitle="0.1.0 MVP mobile" icon={Info} />
      </View>

      <PrimaryButton icon={LogOut} label="Cerrar sesion" onPress={onLogout} variant="ghost" />
    </Screen>
  );
}
