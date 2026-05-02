import { Text, View } from 'react-native';
import {
  Bell,
  CircleHelp,
  Cloud,
  Info,
  Moon,
  Ruler,
  ShieldAlert,
  User,
} from 'lucide-react-native';

import { Badge, BodyText, Header, ListRow, Panel, Screen, SectionTitle } from '../components/ui';
import { theme } from '../theme/tokens';
import type { NavigationApi } from '../types';

export function SettingsScreen({ nav }: { nav: NavigationApi }) {
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
              Tecnico de campo
            </Text>
            <BodyText muted>Perfil local MVP</BodyText>
          </View>
          <Badge tone="success">ACTIVO</Badge>
        </View>
      </Panel>

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
          subtitle="Mock local con adapter listo para API real"
          icon={Cloud}
          right={<Badge tone="accent">MOCK</Badge>}
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
    </Screen>
  );
}
