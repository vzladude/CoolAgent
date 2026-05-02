import { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { AlertTriangle, Factory, RefreshCw, Search, SlidersHorizontal } from 'lucide-react-native';

import {
  Badge,
  BodyText,
  EmptyState,
  Field,
  Header,
  IconButton,
  ListRow,
  Panel,
  Screen,
  SectionTitle,
} from '../components/ui';
import { mockErrorCodes, mockManufacturers } from '../mocks/data';
import { api } from '../services/api';
import { theme } from '../theme/tokens';
import type { ErrorCode, ManufacturerSummary, NavigationApi } from '../types';

function isErrorCode(value: unknown): value is ErrorCode {
  return Boolean(
    value &&
      typeof value === 'object' &&
      'id' in value &&
      'code' in value &&
      'manufacturer' in value,
  );
}

function getErrorCode(codeId?: unknown, initialCode?: unknown): ErrorCode {
  if (isErrorCode(initialCode)) return initialCode;
  return mockErrorCodes.find((code) => code.id === codeId) ?? mockErrorCodes[0];
}

function severityTone(severity: ErrorCode['severity']) {
  if (severity === 'critical' || severity === 'high') return 'danger';
  if (severity === 'medium') return 'warning';
  if (severity === 'low') return 'success';
  return 'neutral';
}

export function ErrorCodesScreen({ nav }: { nav: NavigationApi }) {
  const [query, setQuery] = useState('E7');
  const [manufacturer, setManufacturer] = useState('Todos');
  const [manufacturers, setManufacturers] = useState<ManufacturerSummary[]>(mockManufacturers);
  const [results, setResults] = useState<ErrorCode[]>(mockErrorCodes);
  const [loading, setLoading] = useState(false);

  const manufacturerNames = useMemo(
    () => ['Todos', ...manufacturers.map((item) => item.name)],
    [manufacturers],
  );

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    try {
      const [nextManufacturers, nextResults] = await Promise.all([
        api.listManufacturers(),
        api.searchErrorCodes({
          query,
          manufacturer: manufacturer === 'Todos' ? undefined : manufacturer,
        }),
      ]);
      setManufacturers(nextManufacturers);
      setResults(nextResults);
    } finally {
      setLoading(false);
    }
  }, [manufacturer, query]);

  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);

  return (
    <Screen>
      <Header
        title="Codigos de error"
        eyebrow="Catalogo"
        right={<IconButton icon={RefreshCw} onPress={loadCatalog} />}
      />
      <Panel>
        <View style={{ gap: 12 }}>
          <Field label="Buscar codigo, modelo o sintoma" value={query} onChangeText={setQuery} />
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {manufacturerNames.map((item) => (
              <Pressable
                key={item}
                onPress={() => setManufacturer(item)}
                style={{
                  backgroundColor: manufacturer === item ? theme.color.accent : theme.color.surfaceAlt,
                  borderRadius: theme.radius.pill,
                  paddingHorizontal: 12,
                  paddingVertical: 8,
                }}
              >
                <Text
                  style={{
                    color: manufacturer === item ? theme.color.black : theme.color.text,
                    fontWeight: '700',
                  }}
                >
                  {item}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>
      </Panel>

      <SectionTitle>Resultados</SectionTitle>
      {loading ? (
        <Panel>
          <View style={{ alignItems: 'center', flexDirection: 'row', gap: 10 }}>
            <ActivityIndicator color={theme.color.accent} />
            <BodyText muted>Buscando codigos...</BodyText>
          </View>
        </Panel>
      ) : null}

      {results.map((code) => (
        <ListRow
          key={code.id}
          title={`${code.manufacturer} ${code.code}`}
          subtitle={`${code.model ?? 'Modelo general'} / ${code.description}`}
          meta={code.source}
          icon={AlertTriangle}
          right={<Badge tone={severityTone(code.severity)}>{code.severity ?? 'info'}</Badge>}
          onPress={() => nav.open('codeDetail', { codeId: code.id, code })}
        />
      ))}

      {results.length === 0 && !loading ? (
        <EmptyState
          title="Sin resultados"
          body="Prueba con otro codigo, fabricante, modelo o sintoma. El catalogo aun esta creciendo."
        />
      ) : null}

      <SectionTitle>Fabricantes</SectionTitle>
      <View style={{ gap: 10 }}>
        {manufacturers.map((item) => (
          <ListRow
            key={item.id}
            title={item.name}
            subtitle={`${item.modelCount} modelos / ${item.errorCodeCount} codigos`}
            icon={Factory}
            right={
              item.errorCodeCount > 0 ? (
                <Badge tone="accent">{item.errorCodeCount}</Badge>
              ) : (
                <Badge>pendiente</Badge>
              )
            }
            onPress={() => setManufacturer(item.name)}
          />
        ))}
      </View>
    </Screen>
  );
}

export function ErrorCodeDetailScreen({
  nav,
  codeId,
  initialCode,
}: {
  nav: NavigationApi;
  codeId?: unknown;
  initialCode?: unknown;
}) {
  const code = getErrorCode(codeId, initialCode);

  return (
    <Screen>
      <Header title={`${code.manufacturer} ${code.code}`} eyebrow="Codigo de error" nav={nav} />
      <Panel accent>
        <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
          <Badge tone={severityTone(code.severity)}>{code.severity ?? 'info'}</Badge>
          {code.model ? <Badge tone="accent">{code.model}</Badge> : null}
        </View>
        <Text style={{ color: theme.color.text, fontSize: 21, fontWeight: '800', marginTop: 12 }}>
          {code.description}
        </Text>
        <BodyText muted>{code.source ?? 'Fuente no especificada.'}</BodyText>
      </Panel>

      <SectionTitle>Causas probables</SectionTitle>
      <View style={{ gap: 10 }}>
        {code.possibleCauses.length > 0 ? (
          code.possibleCauses.map((cause) => (
            <ListRow key={cause} title={cause} icon={SlidersHorizontal} />
          ))
        ) : (
          <Panel>
            <BodyText muted>No hay causas probables cargadas para este codigo.</BodyText>
          </Panel>
        )}
      </View>

      <SectionTitle>Solucion sugerida</SectionTitle>
      <Panel>
        <BodyText>{code.suggestedFix ?? 'No hay solucion sugerida cargada.'}</BodyText>
      </Panel>

      <SectionTitle>Acciones rapidas</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow
          title="Buscar en casos tecnicos"
          subtitle="Usar este codigo dentro de un caso activo."
          icon={Search}
          onPress={() => nav.open('cases')}
        />
        <ListRow
          title="Diagnosticar con imagen"
          subtitle="Agregar foto del equipo o tarjeta."
          icon={AlertTriangle}
          onPress={() => nav.open('diagnosisCapture')}
        />
      </View>
    </Screen>
  );
}
