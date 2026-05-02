import { useEffect, useState } from 'react';
import { Plus, Wifi } from 'lucide-react-native';
import { Text, View } from 'react-native';

import {
  Badge,
  Header,
  ListRow,
  Panel,
  PrimaryButton,
  Screen,
  SectionTitle,
  ToolTile,
} from '../components/ui';
import { mockCases, primaryTools } from '../mocks/data';
import { api } from '../services/api';
import { theme } from '../theme/tokens';
import type { NavigationApi, TechnicalCase } from '../types';

export function HomeScreen({ nav }: { nav: NavigationApi }) {
  const [latestCase, setLatestCase] = useState<TechnicalCase>(mockCases[0]);

  useEffect(() => {
    let cancelled = false;
    void api.listCases().then((cases) => {
      if (!cancelled && cases.length > 0) {
        setLatestCase(cases[0]);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <Screen>
      <Header
        title="Buenas, Ricardo."
        eyebrow="CoolAgent"
        right={<Badge tone="success">ONLINE</Badge>}
      />

      <Panel accent>
        <View style={{ gap: 12 }}>
          <Text style={{ color: theme.color.accent, fontFamily: theme.font.mono, fontSize: 11 }}>
            NUEVO CASO TECNICO
          </Text>
          <Text style={{ color: theme.color.text, fontSize: 18, fontWeight: '700', lineHeight: 24 }}>
            Que equipo o falla vamos a revisar hoy?
          </Text>
          <View style={{ flexDirection: 'row', gap: 10 }}>
            <View style={{ flex: 1 }}>
              <PrimaryButton
                icon={Plus}
                label="Empezar"
                onPress={() => nav.open('newCase')}
              />
            </View>
            <View style={{ flex: 1 }}>
              <PrimaryButton
                label="Foto"
                variant="ghost"
                onPress={() => nav.open('diagnosisCapture')}
              />
            </View>
          </View>
        </View>
      </Panel>

      <SectionTitle>Continuar</SectionTitle>
      <ListRow
        title={latestCase.title}
        subtitle={latestCase.lastMessage ?? 'Sin mensajes todavia.'}
        meta={`${latestCase.id} / ${latestCase.status.toUpperCase()} / ${latestCase.updatedAt}`}
        onPress={() => nav.open('chat', { caseId: latestCase.id, case: latestCase })}
      />

      <SectionTitle>Herramientas</SectionTitle>
      <View style={{ flexDirection: 'row', gap: 10 }}>
        {primaryTools.slice(0, 2).map((tool) => (
          <ToolTile
            key={tool.id}
            title={tool.title}
            subtitle={tool.subtitle}
            icon={tool.icon}
            badge={tool.badge}
            onPress={() => nav.open(tool.target, tool.params)}
          />
        ))}
      </View>
      <View style={{ flexDirection: 'row', gap: 10 }}>
        {primaryTools.slice(2).map((tool) => (
          <ToolTile
            key={tool.id}
            title={tool.title}
            subtitle={tool.subtitle}
            icon={tool.icon}
            badge={tool.badge}
            onPress={() => nav.open(tool.target, tool.params)}
          />
        ))}
      </View>

      <Panel>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
          <Wifi size={18} color={theme.color.success} />
          <View style={{ flex: 1 }}>
            <Text style={{ color: theme.color.text, fontWeight: '700' }}>
              Sincronizado hace 4 min
            </Text>
            <Text style={{ color: theme.color.muted, marginTop: 3 }}>
              Calculadoras, guias guardadas y codigos pueden funcionar offline.
            </Text>
          </View>
        </View>
      </Panel>
    </Screen>
  );
}
