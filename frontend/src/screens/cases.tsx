import { useMemo, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { Info, Plus, Send, Wrench } from 'lucide-react-native';

import {
  Badge,
  BodyText,
  EmptyState,
  Field,
  Header,
  IconButton,
  ListRow,
  Panel,
  PrimaryButton,
  Screen,
  SectionTitle,
} from '../components/ui';
import { mockCases, mockMessages } from '../mocks/data';
import { theme } from '../theme/tokens';
import type { NavigationApi, TechnicalCase } from '../types';

function getCase(caseId?: unknown): TechnicalCase {
  return mockCases.find((item) => item.id === caseId) ?? mockCases[0];
}

export function CasesListScreen({ nav }: { nav: NavigationApi }) {
  const [filter, setFilter] = useState<'open' | 'all'>('open');
  const cases = useMemo(
    () => mockCases.filter((item) => filter === 'all' || item.status === 'open'),
    [filter],
  );

  return (
    <Screen>
      <Header
        title="Casos tecnicos"
        eyebrow="Trabajos"
        right={<IconButton icon={Plus} onPress={() => nav.open('newCase')} />}
      />

      <View style={{ flexDirection: 'row', gap: 8 }}>
        {(['open', 'all'] as const).map((item) => (
          <Pressable
            key={item}
            onPress={() => setFilter(item)}
            style={{
              backgroundColor: filter === item ? theme.color.accent : theme.color.surface,
              borderRadius: theme.radius.pill,
              paddingHorizontal: 12,
              paddingVertical: 8,
            }}
          >
            <Text style={{ color: filter === item ? theme.color.black : theme.color.text, fontWeight: '700' }}>
              {item === 'open' ? 'Abiertos' : 'Todos'}
            </Text>
          </Pressable>
        ))}
      </View>

      {cases.map((item) => (
        <ListRow
          key={item.id}
          title={item.title}
          subtitle={item.lastMessage}
          meta={`${item.id} / ${item.status.toUpperCase()} / ${item.updatedAt}`}
          icon={Wrench}
          right={<Badge tone={item.status === 'open' ? 'success' : 'neutral'}>{item.status}</Badge>}
          onPress={() => nav.open('chat', { caseId: item.id })}
        />
      ))}

      {cases.length === 0 ? (
        <EmptyState
          title="No hay casos con este filtro"
          body="Crea un nuevo caso o revisa los casos cerrados."
          action={<PrimaryButton icon={Plus} label="Crear caso" onPress={() => nav.open('newCase')} />}
        />
      ) : null}
    </Screen>
  );
}

export function NewCaseScreen({ nav }: { nav: NavigationApi }) {
  const [title, setTitle] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [model, setModel] = useState('');
  const [category, setCategory] = useState('');

  return (
    <Screen>
      <Header title="Nuevo caso" eyebrow="Caso tecnico" nav={nav} />
      <Panel>
        <View style={{ gap: 12 }}>
          <Field label="Titulo opcional" value={title} onChangeText={setTitle} placeholder="Split no enfria" />
          <Field label="Fabricante" value={manufacturer} onChangeText={setManufacturer} placeholder="Carrier" />
          <Field label="Modelo" value={model} onChangeText={setModel} placeholder="38AKS" />
          <Field label="Categoria" value={category} onChangeText={setCategory} placeholder="Aire acondicionado" />
        </View>
      </Panel>
      <PrimaryButton
        icon={Send}
        label="Crear y empezar chat"
        onPress={() => nav.open('chat', { caseId: mockCases[0].id })}
      />
      <BodyText muted>
        Puedes dejar campos vacios. CoolAgent puede generar un titulo simple desde el primer mensaje.
      </BodyText>
    </Screen>
  );
}

export function ChatScreen({
  nav,
  caseId,
}: {
  nav: NavigationApi;
  caseId?: unknown;
}) {
  const technicalCase = getCase(caseId);

  return (
    <Screen scroll={false}>
      <View style={{ paddingHorizontal: 16, paddingTop: 12 }}>
        <Header
          title={technicalCase.title}
          eyebrow={technicalCase.id}
          nav={nav}
          right={<IconButton icon={Info} onPress={() => nav.open('caseDetails', { caseId: technicalCase.id })} />}
        />
        <View style={{ flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginTop: 10 }}>
          <Badge tone="success">{technicalCase.status}</Badge>
          <Badge>{technicalCase.manufacturer}</Badge>
          <Badge>{technicalCase.equipmentModel}</Badge>
        </View>
      </View>

      <View style={{ flex: 1, padding: 16, gap: 12 }}>
        {mockMessages.map((message) => (
          <View
            key={message.id}
            style={{
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: message.role === 'user' ? theme.color.accent : theme.color.surface,
              borderRadius: theme.radius.md,
              maxWidth: '86%',
              padding: 12,
            }}
          >
            <Text style={{ color: message.role === 'user' ? theme.color.black : theme.color.text, lineHeight: 20 }}>
              {message.content}
            </Text>
            {message.citations?.map((citation) => (
              <View key={citation.id} style={{ marginTop: 10 }}>
                <Badge tone="accent">{citation.title}</Badge>
                <Text style={{ color: theme.color.muted, fontSize: 12, marginTop: 4 }}>
                  {citation.source} / {citation.detail}
                </Text>
              </View>
            ))}
          </View>
        ))}
        <Panel>
          <Text style={{ color: theme.color.accent, fontFamily: theme.font.mono, fontSize: 11 }}>
            ESCRIBIENDO
          </Text>
          <BodyText>
            Revisaria flujo de aire, subcooling y posibles restricciones antes de cargar refrigerante.
          </BodyText>
        </Panel>
      </View>

      <View style={{ padding: 16, paddingBottom: 96, borderTopWidth: 1, borderColor: theme.color.line }}>
        <Panel>
          <Text style={{ color: theme.color.dim, marginBottom: 10 }}>
            Pregunta o describe el sintoma...
          </Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <Badge tone="accent">RAG / 1 fuente</Badge>
            <PrimaryButton icon={Send} label="Enviar" onPress={() => {}} />
          </View>
        </Panel>
      </View>
    </Screen>
  );
}

export function CaseDetailsScreen({
  nav,
  caseId,
}: {
  nav: NavigationApi;
  caseId?: unknown;
}) {
  const technicalCase = getCase(caseId);

  return (
    <Screen>
      <Header title="Metadata del caso" eyebrow={technicalCase.id} nav={nav} />
      <Panel>
        <View style={{ gap: 12 }}>
          <ListRow title="Fabricante" subtitle={technicalCase.manufacturer} />
          <ListRow title="Modelo" subtitle={technicalCase.equipmentModel} />
          <ListRow title="Categoria" subtitle={technicalCase.category} />
          <ListRow title="Estado" subtitle={technicalCase.status} />
        </View>
      </Panel>
      <SectionTitle>Resumen tecnico</SectionTitle>
      <Panel>
        <BodyText muted>{technicalCase.summary ?? 'Aun no hay resumen tecnico compactado.'}</BodyText>
      </Panel>
      <SectionTitle>Fuentes RAG usadas</SectionTitle>
      <Panel>
        <BodyText>Carrier 38AKS Service Manual</BodyText>
        <Text style={{ color: theme.color.muted, fontSize: 12, marginTop: 4 }}>
          Fuente usada para sustentar la respuesta tecnica del caso.
        </Text>
      </Panel>
    </Screen>
  );
}
