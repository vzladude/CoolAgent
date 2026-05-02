import { useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  ChevronRight,
  CloudOff,
  Gauge,
  Image,
  Save,
  Search,
  Snowflake,
  ThermometerSun,
  Upload,
} from 'lucide-react-native';

import {
  Badge,
  BodyText,
  EmptyState,
  Field,
  Header,
  ListRow,
  Panel,
  PrimaryButton,
  Screen,
  SectionTitle,
  ToolTile,
} from '../components/ui';
import { mockErrorCodes, mockGuides, toolHub } from '../mocks/data';
import { theme } from '../theme/tokens';
import type { Guide, NavigationApi } from '../types';

type CalculatorMode = 'superheat' | 'subcooling' | 'pt' | 'converter';

function getGuide(guideId?: unknown): Guide {
  return mockGuides.find((guide) => guide.id === guideId) ?? mockGuides[0];
}

function resolveCalculatorMode(mode?: unknown): CalculatorMode {
  return mode === 'subcooling' || mode === 'pt' || mode === 'converter' ? mode : 'superheat';
}

function toNumber(value: string) {
  const parsed = Number(value.replace(',', '.'));
  return Number.isFinite(parsed) ? parsed : 0;
}

export function ToolsHubScreen({ nav }: { nav: NavigationApi }) {
  return (
    <Screen>
      <Header title="Herramientas" eyebrow="Tecnico" />
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
        {toolHub.map((tool) => (
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

      <SectionTitle>Estado local</SectionTitle>
      <Panel>
        <View style={{ gap: 10 }}>
          <ListRow
            title="Calculadoras y guias"
            subtitle="Contenido listo para uso sin conexion."
            icon={CloudOff}
            right={<Badge tone="success">OFFLINE</Badge>}
          />
          <ListRow
            title="Diagnostico visual"
            subtitle="Requiere conexion para analizar imagenes."
            icon={Camera}
            right={<Badge tone="warning">ONLINE</Badge>}
          />
        </View>
      </Panel>
    </Screen>
  );
}

export function DiagnosisCaptureScreen({ nav }: { nav: NavigationApi }) {
  return (
    <Screen>
      <Header title="Diagnostico visual" eyebrow="Imagen" nav={nav} />

      <Panel accent>
        <View
          style={{
            alignItems: 'center',
            aspectRatio: 3 / 4,
            backgroundColor: theme.color.black,
            borderColor: theme.color.lineStrong,
            borderRadius: theme.radius.md,
            borderWidth: 1,
            justifyContent: 'center',
          }}
        >
          <Image size={44} color={theme.color.accent} strokeWidth={1.6} />
          <Text style={{ color: theme.color.muted, marginTop: 10 }}>Preview de imagen</Text>
        </View>
      </Panel>

      <View style={{ flexDirection: 'row', gap: 10 }}>
        <View style={{ flex: 1 }}>
          <PrimaryButton icon={Camera} label="Camara" onPress={() => {}} />
        </View>
        <View style={{ flex: 1 }}>
          <PrimaryButton icon={Upload} label="Galeria" variant="ghost" onPress={() => {}} />
        </View>
      </View>

      <PrimaryButton
        icon={ChevronRight}
        label="Agregar contexto"
        onPress={() => nav.open('diagnosisContext')}
      />
    </Screen>
  );
}

export function DiagnosisContextScreen({ nav }: { nav: NavigationApi }) {
  const [equipmentType, setEquipmentType] = useState('Aire acondicionado split');
  const [symptom, setSymptom] = useState('Tuberia de succion congelada');
  const [model, setModel] = useState('Carrier 38AKS');

  return (
    <Screen>
      <Header title="Contexto" eyebrow="Diagnostico" nav={nav} />
      <Panel>
        <View style={{ gap: 12 }}>
          <Field label="Tipo de equipo" value={equipmentType} onChangeText={setEquipmentType} />
          <Field label="Sintoma" value={symptom} onChangeText={setSymptom} />
          <Field label="Fabricante / modelo" value={model} onChangeText={setModel} />
        </View>
      </Panel>
      <PrimaryButton
        icon={Search}
        label="Analizar imagen"
        onPress={() => nav.open('diagnosisAnalyzing')}
      />
    </Screen>
  );
}

export function DiagnosisAnalyzingScreen({ nav }: { nav: NavigationApi }) {
  return (
    <Screen>
      <Header title="Analizando" eyebrow="Vision AI" nav={nav} />
      <Panel accent>
        <View style={{ alignItems: 'center', gap: 16, paddingVertical: 18 }}>
          <ActivityIndicator color={theme.color.accent} size="large" />
          <Text style={{ color: theme.color.text, fontSize: 18, fontWeight: '700' }}>
            Revisando imagen y contexto
          </Text>
          <BodyText muted>
            Se esta evaluando condicion visual, posibles causas y proximos pasos tecnicos.
          </BodyText>
        </View>
      </Panel>

      <View style={{ gap: 10 }}>
        {['Imagen recibida', 'Contexto aplicado', 'Buscando codigos relacionados'].map((item) => (
          <ListRow key={item} title={item} icon={CheckCircle2} right={<Badge tone="success">OK</Badge>} />
        ))}
      </View>

      <PrimaryButton
        icon={ChevronRight}
        label="Ver resultado"
        onPress={() => nav.open('diagnosisResult')}
      />
    </Screen>
  );
}

export function DiagnosisResultScreen({ nav }: { nav: NavigationApi }) {
  const relatedCode = mockErrorCodes[0];

  return (
    <Screen>
      <Header title="Resultado visual" eyebrow="Diagnostico" nav={nav} />
      <Panel accent>
        <Badge tone="warning">Revisar antes de operar</Badge>
        <Text style={{ color: theme.color.text, fontSize: 20, fontWeight: '700', marginTop: 12 }}>
          Posible bajo flujo de aire o restriccion
        </Text>
        <BodyText muted>
          La imagen sugiere congelamiento en linea de succion. Confirmar filtro, serpentines,
          ventilador, presiones y superheat antes de cargar refrigerante.
        </BodyText>
      </Panel>

      <SectionTitle>Pasos sugeridos</SectionTitle>
      <View style={{ gap: 10 }}>
        {[
          'Apagar equipo si hay hielo severo.',
          'Revisar filtro, evaporador y velocidad del ventilador.',
          'Medir presion de baja y temperatura de linea.',
          'Comparar superheat con condicion de operacion.',
        ].map((step, index) => (
          <ListRow key={step} title={`${index + 1}. ${step}`} icon={CheckCircle2} />
        ))}
      </View>

      <SectionTitle>Codigos relacionados</SectionTitle>
      <ListRow
        title={`${relatedCode.manufacturer} ${relatedCode.code}`}
        subtitle={relatedCode.description}
        icon={AlertTriangle}
        right={<Badge tone="warning">{relatedCode.severity}</Badge>}
        onPress={() => nav.open('codeDetail', { codeId: relatedCode.id })}
      />
    </Screen>
  );
}

export function CalculatorScreen({
  nav,
  mode,
}: {
  nav: NavigationApi;
  mode?: unknown;
}) {
  const [activeMode, setActiveMode] = useState<CalculatorMode>(resolveCalculatorMode(mode));
  const [satTemp, setSatTemp] = useState('4');
  const [lineTemp, setLineTemp] = useState('12');
  const [condTemp, setCondTemp] = useState('43');
  const [liquidTemp, setLiquidTemp] = useState('35');
  const superheat = toNumber(lineTemp) - toNumber(satTemp);
  const subcooling = toNumber(condTemp) - toNumber(liquidTemp);

  const modes: { id: CalculatorMode; label: string }[] = [
    { id: 'superheat', label: 'Superheat' },
    { id: 'subcooling', label: 'Subcool' },
    { id: 'pt', label: 'PT' },
    { id: 'converter', label: 'Unidades' },
  ];

  return (
    <Screen>
      <Header title="Calculadoras" eyebrow="Offline" nav={nav} />
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {modes.map((item) => (
          <Pressable
            key={item.id}
            onPress={() => setActiveMode(item.id)}
            style={{
              backgroundColor: activeMode === item.id ? theme.color.accent : theme.color.surface,
              borderRadius: theme.radius.pill,
              paddingHorizontal: 12,
              paddingVertical: 8,
            }}
          >
            <Text
              style={{
                color: activeMode === item.id ? theme.color.black : theme.color.text,
                fontWeight: '700',
              }}
            >
              {item.label}
            </Text>
          </Pressable>
        ))}
      </View>

      {activeMode === 'superheat' ? (
        <>
          <Panel>
            <View style={{ gap: 12 }}>
              <Field label="Temp. saturacion C" value={satTemp} onChangeText={setSatTemp} />
              <Field label="Temp. linea succion C" value={lineTemp} onChangeText={setLineTemp} />
            </View>
          </Panel>
          <ResultPanel
            icon={ThermometerSun}
            title={`${superheat.toFixed(1)} C`}
            body="Sobrecalentamiento calculado. Interpretar contra manual, carga termica y condiciones reales."
            tone={superheat > 5 && superheat < 14 ? 'success' : 'warning'}
          />
        </>
      ) : null}

      {activeMode === 'subcooling' ? (
        <>
          <Panel>
            <View style={{ gap: 12 }}>
              <Field label="Temp. condensacion C" value={condTemp} onChangeText={setCondTemp} />
              <Field label="Temp. linea liquido C" value={liquidTemp} onChangeText={setLiquidTemp} />
            </View>
          </Panel>
          <ResultPanel
            icon={Snowflake}
            title={`${subcooling.toFixed(1)} C`}
            body="Subenfriamiento calculado. Valores bajos pueden apuntar a baja carga o flash gas."
            tone={subcooling > 4 && subcooling < 12 ? 'success' : 'warning'}
          />
        </>
      ) : null}

      {activeMode === 'pt' ? (
        <Panel>
          <Badge tone="accent">R-410A</Badge>
          <Text style={{ color: theme.color.text, fontSize: 28, fontWeight: '800', marginTop: 12 }}>
            118 psi / 4.4 C
          </Text>
          <BodyText muted>
            Lookup mock para validar layout. La tabla real se conectara a datos tecnicos versionados.
          </BodyText>
        </Panel>
      ) : null}

      {activeMode === 'converter' ? (
        <Panel>
          <View style={{ gap: 12 }}>
            <ListRow title="35 F" subtitle="1.7 C" icon={Gauge} />
            <ListRow title="120 psi" subtitle="827 kPa" icon={Gauge} />
            <ListRow title="1 tonelada" subtitle="12,000 BTU/h" icon={Gauge} />
          </View>
        </Panel>
      ) : null}
    </Screen>
  );
}

function ResultPanel({
  icon: Icon,
  title,
  body,
  tone,
}: {
  icon: typeof ThermometerSun;
  title: string;
  body: string;
  tone: 'success' | 'warning';
}) {
  return (
    <Panel accent>
      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Icon size={28} color={theme.color.accent} strokeWidth={1.8} />
        <View style={{ flex: 1, gap: 8 }}>
          <Badge tone={tone}>{tone === 'success' ? 'Rango comun' : 'Revisar'}</Badge>
          <Text style={{ color: theme.color.text, fontSize: 30, fontWeight: '800' }}>{title}</Text>
          <BodyText muted>{body}</BodyText>
        </View>
      </View>
    </Panel>
  );
}

export function GuidesScreen({ nav }: { nav: NavigationApi }) {
  const categories = useMemo(() => ['Todas', ...new Set(mockGuides.map((guide) => guide.category))], []);
  const [category, setCategory] = useState('Todas');
  const guides = mockGuides.filter((guide) => category === 'Todas' || guide.category === category);

  return (
    <Screen>
      <Header title="Guias" eyebrow="Procedimientos" nav={nav} />
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {categories.map((item) => (
          <Pressable
            key={item}
            onPress={() => setCategory(item)}
            style={{
              backgroundColor: category === item ? theme.color.accent : theme.color.surface,
              borderRadius: theme.radius.pill,
              paddingHorizontal: 12,
              paddingVertical: 8,
            }}
          >
            <Text style={{ color: category === item ? theme.color.black : theme.color.text, fontWeight: '700' }}>
              {item}
            </Text>
          </Pressable>
        ))}
      </View>

      {guides.map((guide) => (
        <ListRow
          key={guide.id}
          title={guide.title}
          subtitle={`${guide.category} / ${guide.duration}`}
          icon={Save}
          right={guide.offline ? <Badge tone="success">OFFLINE</Badge> : undefined}
          onPress={() => nav.open('guideDetail', { guideId: guide.id })}
        />
      ))}

      {guides.length === 0 ? (
        <EmptyState title="Contenido pendiente" body="Aun no hay guias en esta categoria." />
      ) : null}
    </Screen>
  );
}

export function GuideDetailScreen({
  nav,
  guideId,
}: {
  nav: NavigationApi;
  guideId?: unknown;
}) {
  const guide = getGuide(guideId);

  return (
    <Screen>
      <Header title={guide.title} eyebrow={guide.category} nav={nav} />
      <Panel accent>
        <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
          <Badge tone="accent">{guide.duration}</Badge>
          {guide.offline ? <Badge tone="success">OFFLINE</Badge> : null}
        </View>
        <SectionTitle>Herramientas / EPP</SectionTitle>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
          {guide.tools.map((tool) => (
            <Badge key={tool}>{tool}</Badge>
          ))}
        </View>
      </Panel>

      <SectionTitle>Checklist</SectionTitle>
      <View style={{ gap: 10 }}>
        {guide.steps.map((step, index) => (
          <ListRow key={step} title={`${index + 1}. ${step}`} icon={CheckCircle2} />
        ))}
      </View>
    </Screen>
  );
}

export function OfflineScreen({ nav }: { nav: NavigationApi }) {
  return (
    <Screen>
      <Header title="Offline / Sync" eyebrow="Estado" nav={nav} />
      <Panel accent>
        <Badge tone="warning">Conexion pobre</Badge>
        <Text style={{ color: theme.color.text, fontSize: 22, fontWeight: '800', marginTop: 12 }}>
          Modo campo activo
        </Text>
        <BodyText muted>
          Datos locales disponibles para calculadoras, guias y casos recientes. Las acciones pendientes
          se sincronizaran cuando vuelva la conexion.
        </BodyText>
      </Panel>

      <SectionTitle>Disponible offline</SectionTitle>
      <View style={{ gap: 10 }}>
        <ListRow title="Calculadoras tecnicas" subtitle="Superheat, subcooling, PT y unidades" icon={Gauge} />
        <ListRow title="Guias guardadas" subtitle="2 procedimientos" icon={Save} />
        <ListRow title="Casos recientes" subtitle="3 casos con mensajes cacheados" icon={CheckCircle2} />
      </View>

      <SectionTitle>Cola pendiente</SectionTitle>
      <Panel>
        <View style={{ gap: 10 }}>
          <ListRow
            title="1 mensaje pendiente"
            subtitle="Caso C-0042"
            icon={CloudOff}
            right={<Badge tone="warning">SYNC</Badge>}
          />
          <ListRow
            title="Ultima sincronizacion"
            subtitle="hace 18 min"
            icon={CheckCircle2}
            right={<Badge tone="success">OK</Badge>}
          />
        </View>
      </Panel>
    </Screen>
  );
}
