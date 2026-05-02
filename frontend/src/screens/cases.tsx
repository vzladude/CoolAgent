import { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { Info, Plus, RefreshCw, Send, Wrench } from 'lucide-react-native';

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
import { mockCases } from '../mocks/data';
import { api } from '../services/api';
import { theme } from '../theme/tokens';
import type { ChatMessage, NavigationApi, TechnicalCase } from '../types';

function fallbackCase(caseId?: unknown): TechnicalCase {
  return mockCases.find((item) => item.id === caseId) ?? mockCases[0];
}

function isTechnicalCase(value: unknown): value is TechnicalCase {
  return Boolean(
    value &&
      typeof value === 'object' &&
      'id' in value &&
      'status' in value &&
      'updatedAt' in value,
  );
}

function resolveCaseId(caseId?: unknown) {
  return typeof caseId === 'string' ? caseId : mockCases[0].id;
}

function metaForCase(item: TechnicalCase) {
  return `${item.id} / ${item.status.toUpperCase()} / ${item.updatedAt}`;
}

function labelOrDash(value?: string) {
  return value && value.trim().length > 0 ? value : 'No definido';
}

export function CasesListScreen({ nav }: { nav: NavigationApi }) {
  const [filter, setFilter] = useState<'open' | 'all'>('open');
  const [cases, setCases] = useState<TechnicalCase[]>(mockCases);
  const [loading, setLoading] = useState(false);

  const loadCases = useCallback(async () => {
    setLoading(true);
    try {
      setCases(await api.listCases());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCases();
  }, [loadCases]);

  const visibleCases = useMemo(
    () => cases.filter((item) => filter === 'all' || item.status === 'open'),
    [cases, filter],
  );

  return (
    <Screen>
      <Header
        title="Casos tecnicos"
        eyebrow="Trabajos"
        right={
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <IconButton icon={RefreshCw} onPress={loadCases} />
            <IconButton icon={Plus} onPress={() => nav.open('newCase')} />
          </View>
        }
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

      {loading ? (
        <Panel>
          <View style={{ alignItems: 'center', flexDirection: 'row', gap: 10 }}>
            <ActivityIndicator color={theme.color.accent} />
            <BodyText muted>Cargando casos...</BodyText>
          </View>
        </Panel>
      ) : null}

      {visibleCases.map((item) => (
        <ListRow
          key={item.id}
          title={item.title}
          subtitle={item.lastMessage ?? 'Sin mensajes todavia.'}
          meta={metaForCase(item)}
          icon={Wrench}
          right={<Badge tone={item.status === 'open' ? 'success' : 'neutral'}>{item.status}</Badge>}
          onPress={() => nav.open('chat', { caseId: item.id, case: item })}
        />
      ))}

      {visibleCases.length === 0 ? (
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
  const [saving, setSaving] = useState(false);

  const createCase = async () => {
    setSaving(true);
    try {
      const created = await api.createCase({
        title,
        manufacturer,
        equipmentModel: model,
        category,
      });
      nav.open('chat', { caseId: created.id, case: created });
    } finally {
      setSaving(false);
    }
  };

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
        icon={saving ? RefreshCw : Send}
        label={saving ? 'Creando...' : 'Crear y empezar chat'}
        onPress={createCase}
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
  initialCase,
}: {
  nav: NavigationApi;
  caseId?: unknown;
  initialCase?: unknown;
}) {
  const resolvedCaseId = resolveCaseId(caseId);
  const [technicalCase, setTechnicalCase] = useState<TechnicalCase>(
    isTechnicalCase(initialCase) ? initialCase : fallbackCase(caseId),
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  const loadChat = useCallback(async () => {
    setLoading(true);
    try {
      const [caseData, caseMessages] = await Promise.all([
        api.getCase(resolvedCaseId),
        api.listCaseMessages(resolvedCaseId),
      ]);
      setTechnicalCase(caseData);
      setMessages(caseMessages);
    } finally {
      setLoading(false);
    }
  }, [resolvedCaseId]);

  useEffect(() => {
    void loadChat();
  }, [loadChat]);

  const sendMessage = async () => {
    const content = input.trim();
    if (!content || sending) return;

    const userMessage: ChatMessage = {
      id: `LOCAL-USER-${Date.now()}`,
      technicalCaseId: resolvedCaseId,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };

    setInput('');
    setMessages((current) => [...current, userMessage]);
    setSending(true);

    try {
      const assistantMessage = await api.sendCaseMessage(resolvedCaseId, content);
      setMessages((current) => [...current, assistantMessage]);
    } finally {
      setSending(false);
    }
  };

  return (
    <Screen scroll={false}>
      <View style={{ paddingHorizontal: 16, paddingTop: 12 }}>
        <Header
          title={technicalCase.title}
          eyebrow={technicalCase.id}
          nav={nav}
          right={<IconButton icon={Info} onPress={() => nav.open('caseDetails', { caseId: technicalCase.id, case: technicalCase })} />}
        />
        <View style={{ flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginTop: 10 }}>
          <Badge tone={technicalCase.status === 'open' ? 'success' : 'neutral'}>{technicalCase.status}</Badge>
          <Badge>{labelOrDash(technicalCase.manufacturer)}</Badge>
          <Badge>{labelOrDash(technicalCase.equipmentModel)}</Badge>
        </View>
      </View>

      <ScrollView
        contentContainerStyle={{ gap: 12, padding: 16 }}
        showsVerticalScrollIndicator={false}
        style={{ flex: 1 }}
      >
        {loading ? (
          <Panel>
            <View style={{ alignItems: 'center', flexDirection: 'row', gap: 10 }}>
              <ActivityIndicator color={theme.color.accent} />
              <BodyText muted>Cargando historial...</BodyText>
            </View>
          </Panel>
        ) : null}

        {messages.map((message) => (
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

        {messages.length === 0 && !loading ? (
          <EmptyState
            title="Caso sin mensajes"
            body="Describe la falla, mediciones o sintomas para empezar el diagnostico."
          />
        ) : null}

        {sending ? (
          <Panel>
            <Text style={{ color: theme.color.accent, fontFamily: theme.font.mono, fontSize: 11 }}>
              RESPONDIENDO
            </Text>
            <BodyText muted>Consultando reglas de dominio, contexto del caso y RAG si aplica.</BodyText>
          </Panel>
        ) : null}
      </ScrollView>

      <View style={{ padding: 16, paddingBottom: 96, borderTopWidth: 1, borderColor: theme.color.line }}>
        <Panel>
          <TextInput
            multiline
            onChangeText={setInput}
            placeholder="Pregunta o describe el sintoma..."
            placeholderTextColor={theme.color.dim}
            style={{
              color: theme.color.text,
              fontSize: 15,
              minHeight: 46,
              textAlignVertical: 'top',
            }}
            value={input}
          />
          <View style={{ alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 }}>
            <Badge tone="accent">Backend + mock fallback</Badge>
            <PrimaryButton
              icon={sending ? RefreshCw : Send}
              label={sending ? '...' : 'Enviar'}
              onPress={sendMessage}
            />
          </View>
        </Panel>
      </View>
    </Screen>
  );
}

export function CaseDetailsScreen({
  nav,
  caseId,
  initialCase,
}: {
  nav: NavigationApi;
  caseId?: unknown;
  initialCase?: unknown;
}) {
  const resolvedCaseId = resolveCaseId(caseId);
  const [technicalCase, setTechnicalCase] = useState<TechnicalCase>(
    isTechnicalCase(initialCase) ? initialCase : fallbackCase(caseId),
  );

  useEffect(() => {
    let cancelled = false;
    void api.getCase(resolvedCaseId).then((caseData) => {
      if (!cancelled) setTechnicalCase(caseData);
    });
    return () => {
      cancelled = true;
    };
  }, [resolvedCaseId]);

  return (
    <Screen>
      <Header title="Metadata del caso" eyebrow={technicalCase.id} nav={nav} />
      <Panel>
        <View style={{ gap: 12 }}>
          <ListRow title="Fabricante" subtitle={labelOrDash(technicalCase.manufacturer)} />
          <ListRow title="Modelo" subtitle={labelOrDash(technicalCase.equipmentModel)} />
          <ListRow title="Categoria" subtitle={labelOrDash(technicalCase.category)} />
          <ListRow title="Estado" subtitle={technicalCase.status} />
        </View>
      </Panel>
      <SectionTitle>Resumen tecnico</SectionTitle>
      <Panel>
        <BodyText muted>{technicalCase.summary ?? 'Aun no hay resumen tecnico compactado.'}</BodyText>
      </Panel>
      <SectionTitle>Fuentes RAG usadas</SectionTitle>
      <Panel>
        <BodyText>Las fuentes apareceran cuando el backend devuelva citas RAG para mensajes.</BodyText>
        <Text style={{ color: theme.color.muted, fontSize: 12, marginTop: 4 }}>
          El upload de manuales sigue fuera del MVP mobile.
        </Text>
      </Panel>
    </Screen>
  );
}
