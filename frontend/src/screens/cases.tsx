import { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { Archive, Info, Plus, RefreshCw, Send, Wrench } from 'lucide-react-native';

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
import { api } from '../services/api';
import { theme } from '../theme/tokens';
import type { ChatMessage, NavigationApi, TechnicalCase } from '../types';

type CaseFilter = 'open' | 'closed' | 'all';
type CaseStatusAction = 'closing' | 'reopening';

const caseFilters: { id: CaseFilter; label: string }[] = [
  { id: 'open', label: 'Abiertos' },
  { id: 'closed', label: 'Archivados' },
  { id: 'all', label: 'Todos' },
];

function normalizeCaseFilter(value?: unknown): CaseFilter {
  return value === 'closed' || value === 'all' ? value : 'open';
}

function placeholderCase(caseId?: unknown): TechnicalCase {
  return {
    id: typeof caseId === 'string' ? caseId : 'sin-caso',
    title: 'Cargando caso...',
    status: 'open',
    updatedAt: 'sin sincronizar',
  };
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
  return typeof caseId === 'string' ? caseId : '';
}

function metaForCase(item: TechnicalCase) {
  return `${item.id} / ${item.status.toUpperCase()} / ${item.updatedAt}`;
}

function labelOrDash(value?: string) {
  return value && value.trim().length > 0 ? value : 'No definido';
}

function BlockingStatusOverlay({ action }: { action: CaseStatusAction | null }) {
  const copy =
    action === 'closing'
      ? {
          title: 'Archivando caso...',
          body: 'Guardando el estado y volviendo a la lista de casos.',
        }
      : {
          title: 'Reabriendo caso...',
          body: 'Restaurando el caso para continuar el diagnostico.',
        };

  return (
    <Modal animationType="fade" transparent visible={action !== null}>
      <View
        style={{
          alignItems: 'center',
          backgroundColor: 'rgba(0,0,0,0.72)',
          flex: 1,
          justifyContent: 'center',
          padding: 24,
        }}
      >
        <View
          style={{
            alignItems: 'center',
            backgroundColor: theme.color.surface,
            borderColor: theme.color.lineStrong,
            borderRadius: theme.radius.md,
            borderWidth: 1,
            gap: 12,
            padding: 18,
            width: '100%',
          }}
        >
          <ActivityIndicator color={theme.color.accent} />
          <Text style={{ color: theme.color.text, fontSize: 17, fontWeight: '800' }}>
            {copy.title}
          </Text>
          <Text style={{ color: theme.color.muted, fontSize: 13, lineHeight: 18, textAlign: 'center' }}>
            {copy.body}
          </Text>
        </View>
      </View>
    </Modal>
  );
}

export function CasesListScreen({
  nav,
  initialFilter,
}: {
  nav: NavigationApi;
  initialFilter?: unknown;
}) {
  const [filter, setFilter] = useState<CaseFilter>(normalizeCaseFilter(initialFilter));
  const [cases, setCases] = useState<TechnicalCase[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setCases(await api.listCases());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los casos.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCases();
  }, [loadCases]);

  const visibleCases = useMemo(
    () => cases.filter((item) => filter === 'all' || item.status === filter),
    [cases, filter],
  );

  const emptyCopy =
    filter === 'closed'
      ? {
          title: 'No hay casos archivados',
          body: 'Cuando cierres un caso, aparecera aqui para consulta historica.',
        }
      : {
          title: 'No hay casos abiertos',
          body: 'Crea un nuevo caso tecnico para empezar el diagnostico.',
        };

  return (
    <Screen>
      <Header
        title="Casos tecnicos"
        eyebrow="Trabajos"
        right={
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <Badge tone={api.isLocalMode() ? 'warning' : 'success'}>
              {api.isLocalMode() ? 'LOCAL' : 'AUTH'}
            </Badge>
            <IconButton icon={RefreshCw} onPress={loadCases} />
            <IconButton icon={Plus} onPress={() => nav.open('newCase')} />
          </View>
        }
      />

      <View style={{ flexDirection: 'row', gap: 8 }}>
        {caseFilters.map((item) => (
          <Pressable
            key={item.id}
            onPress={() => setFilter(item.id)}
            style={{
              backgroundColor: filter === item.id ? theme.color.accent : theme.color.surface,
              borderRadius: theme.radius.pill,
              paddingHorizontal: 12,
              paddingVertical: 8,
            }}
          >
            <Text style={{ color: filter === item.id ? theme.color.black : theme.color.text, fontWeight: '700' }}>
              {item.label}
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

      {error ? (
        <Panel>
          <Text style={{ color: theme.color.danger, fontSize: 13, lineHeight: 18 }}>
            {error}
          </Text>
          <View style={{ marginTop: 10 }}>
            <PrimaryButton icon={RefreshCw} label="Reintentar" onPress={loadCases} variant="ghost" />
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

      {visibleCases.length === 0 && !loading && !error ? (
        <EmptyState
          title={filter === 'all' ? 'Todavia no hay casos' : emptyCopy.title}
          body={filter === 'all' ? 'Crea tu primer caso tecnico para empezar.' : emptyCopy.body}
          action={
            filter !== 'closed' ? (
              <PrimaryButton icon={Plus} label="Crear caso" onPress={() => nav.open('newCase')} />
            ) : undefined
          }
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
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const createCase = async () => {
    setSaving(true);
    setError(null);
    try {
      const created = await api.createCase({
        title,
        manufacturer,
        equipmentModel: model,
        category,
      });
      nav.open('chat', { caseId: created.id, case: created });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el caso.');
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
      {error ? (
        <Panel>
          <Text style={{ color: theme.color.danger, fontSize: 13, lineHeight: 18 }}>
            {error}
          </Text>
        </Panel>
      ) : null}
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
    isTechnicalCase(initialCase) ? initialCase : placeholderCase(caseId),
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  const loadChat = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [caseData, caseMessages] = await Promise.all([
        api.getCase(resolvedCaseId),
        api.listCaseMessages(resolvedCaseId),
      ]);
      setTechnicalCase(caseData);
      setMessages(caseMessages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar el chat.');
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
    if (technicalCase.status === 'closed') {
      setError('Este caso esta cerrado. Reabre el caso para enviar mensajes.');
      return;
    }

    const userMessage: ChatMessage = {
      id: `LOCAL-USER-${Date.now()}`,
      technicalCaseId: resolvedCaseId,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };

    setInput('');
    setMessages((current) => [...current, userMessage]);
    setError(null);
    setSending(true);

    try {
      const assistantMessage = await api.sendCaseMessage(resolvedCaseId, content);
      setMessages((current) => [...current, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo enviar el mensaje.');
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

        {error ? (
          <Panel>
            <Text style={{ color: theme.color.danger, fontSize: 13, lineHeight: 18 }}>
              {error}
            </Text>
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
            editable={technicalCase.status === 'open'}
            multiline
            onChangeText={setInput}
            placeholder={
              technicalCase.status === 'open'
                ? 'Pregunta o describe el sintoma...'
                : 'Caso cerrado'
            }
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
            <Badge tone={api.isLocalMode() ? 'warning' : 'success'}>
              {api.isLocalMode() ? 'Modo local' : 'Backend seguro'}
            </Badge>
            <PrimaryButton
              disabled={sending || technicalCase.status === 'closed'}
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
    isTechnicalCase(initialCase) ? initialCase : placeholderCase(caseId),
  );
  const [error, setError] = useState<string | null>(null);
  const [statusAction, setStatusAction] = useState<CaseStatusAction | null>(null);

  useEffect(() => {
    let cancelled = false;
    void api
      .getCase(resolvedCaseId)
      .then((caseData) => {
        if (!cancelled) setTechnicalCase(caseData);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'No se pudo cargar el caso.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [resolvedCaseId]);

  const toggleCaseStatus = async () => {
    const nextStatus = technicalCase.status === 'open' ? 'closed' : 'open';
    const action = nextStatus === 'closed' ? 'closing' : 'reopening';
    setStatusAction(action);
    setError(null);
    try {
      const updatedCase = await api.updateCase(resolvedCaseId, { status: nextStatus });
      nav.resetToRoute('cases', {
        filter: updatedCase.status === 'closed' ? 'closed' : 'open',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar el caso.');
      setStatusAction(null);
    } finally {
      if (nextStatus !== 'closed') {
        setStatusAction(null);
      }
    }
  };

  return (
    <Screen>
      <BlockingStatusOverlay action={statusAction} />
      <Header title="Metadata del caso" eyebrow={technicalCase.id} nav={nav} />
      <Panel>
        <View style={{ gap: 12 }}>
          <ListRow title="Fabricante" subtitle={labelOrDash(technicalCase.manufacturer)} />
          <ListRow title="Modelo" subtitle={labelOrDash(technicalCase.equipmentModel)} />
          <ListRow title="Categoria" subtitle={labelOrDash(technicalCase.category)} />
          <ListRow
            title="Estado"
            subtitle={technicalCase.status === 'open' ? 'Abierto' : 'Cerrado'}
            right={
              <Badge tone={technicalCase.status === 'open' ? 'success' : 'neutral'}>
                {technicalCase.status}
              </Badge>
            }
          />
        </View>
      </Panel>
      <PrimaryButton
        disabled={statusAction !== null}
        icon={technicalCase.status === 'open' ? Archive : RefreshCw}
        label={
          statusAction
            ? 'Actualizando...'
            : technicalCase.status === 'open'
              ? 'Cerrar caso'
              : 'Reabrir caso'
        }
        onPress={toggleCaseStatus}
        variant={technicalCase.status === 'open' ? 'primary' : 'ghost'}
      />
      {error ? (
        <Panel>
          <Text style={{ color: theme.color.danger, fontSize: 13, lineHeight: 18 }}>
            {error}
          </Text>
        </Panel>
      ) : null}
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
