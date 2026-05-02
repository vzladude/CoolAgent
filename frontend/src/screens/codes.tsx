import { useMemo, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { AlertTriangle, Factory, Search, SlidersHorizontal } from 'lucide-react-native';

import {
  Badge,
  BodyText,
  EmptyState,
  Field,
  Header,
  ListRow,
  Panel,
  Screen,
  SectionTitle,
} from '../components/ui';
import { mockErrorCodes, mockManufacturers } from '../mocks/data';
import { theme } from '../theme/tokens';
import type { ErrorCode, NavigationApi } from '../types';

function getErrorCode(codeId?: unknown): ErrorCode {
  return mockErrorCodes.find((code) => code.id === codeId) ?? mockErrorCodes[0];
}

function severityTone(severity: ErrorCode['severity']) {
  if (severity === 'critical' || severity === 'high') return 'danger';
  if (severity === 'medium') return 'warning';
  return 'success';
}

export function ErrorCodesScreen({ nav }: { nav: NavigationApi }) {
  const [query, setQuery] = useState('E7');
  const [manufacturer, setManufacturer] = useState('Todos');
  const manufacturers = useMemo(
    () => ['Todos', ...mockManufacturers.map((item) => item.name)],
    [],
  );
  const results = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return mockErrorCodes.filter((code) => {
      const matchesQuery =
        normalizedQuery.length === 0 ||
        code.code.toLowerCase().includes(normalizedQuery) ||
        code.description.toLowerCase().includes(normalizedQuery) ||
        code.model?.toLowerCase().includes(normalizedQuery);
      const matchesManufacturer =
        manufacturer === 'Todos' || code.manufacturer === manufacturer;
      return matchesQuery && matchesManufacturer;
    });
  }, [manufacturer, query]);

  return (
    <Screen>
      <Header title="Codigos de error" eyebrow="Catalogo" />
      <Panel>
        <View style={{ gap: 12 }}>
          <Field label="Buscar codigo, modelo o sintoma" value={query} onChangeText={setQuery} />
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {manufacturers.map((item) => (
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
      {results.map((code) => (
        <ListRow
          key={code.id}
          title={`${code.manufacturer} ${code.code}`}
          subtitle={`${code.model ?? 'Modelo general'} / ${code.description}`}
          meta={code.source}
          icon={AlertTriangle}
          right={<Badge tone={severityTone(code.severity)}>{code.severity}</Badge>}
          onPress={() => nav.open('codeDetail', { codeId: code.id })}
        />
      ))}

      {results.length === 0 ? (
        <EmptyState
          title="Sin resultados"
          body="Prueba con otro codigo, fabricante o modelo. El catalogo aun esta creciendo."
        />
      ) : null}

      <SectionTitle>Fabricantes</SectionTitle>
      <View style={{ gap: 10 }}>
        {mockManufacturers.map((item) => (
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
}: {
  nav: NavigationApi;
  codeId?: unknown;
}) {
  const code = getErrorCode(codeId);

  return (
    <Screen>
      <Header title={`${code.manufacturer} ${code.code}`} eyebrow="Codigo de error" nav={nav} />
      <Panel accent>
        <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
          <Badge tone={severityTone(code.severity)}>{code.severity}</Badge>
          {code.model ? <Badge tone="accent">{code.model}</Badge> : null}
        </View>
        <Text style={{ color: theme.color.text, fontSize: 21, fontWeight: '800', marginTop: 12 }}>
          {code.description}
        </Text>
        <BodyText muted>{code.source}</BodyText>
      </Panel>

      <SectionTitle>Causas probables</SectionTitle>
      <View style={{ gap: 10 }}>
        {code.possibleCauses.map((cause) => (
          <ListRow key={cause} title={cause} icon={SlidersHorizontal} />
        ))}
      </View>

      <SectionTitle>Solucion sugerida</SectionTitle>
      <Panel>
        <BodyText>{code.suggestedFix}</BodyText>
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
