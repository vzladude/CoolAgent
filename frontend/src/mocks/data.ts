import {
  AlertTriangle,
  BookOpenCheck,
  Calculator,
  Camera,
  CloudOff,
  Gauge,
  Settings,
  Snowflake,
  ThermometerSun,
  Wrench,
} from 'lucide-react-native';

import type {
  ChatMessage,
  ErrorCode,
  Guide,
  ManufacturerSummary,
  TechnicalCase,
  ToolAction,
} from '../types';

export const mockCases: TechnicalCase[] = [
  {
    id: 'C-0042',
    title: 'Carrier 38AKS no enfria',
    manufacturer: 'Carrier',
    equipmentModel: '38AKS-024',
    category: 'Aire acondicionado split',
    status: 'open',
    updatedAt: 'hace 12 min',
    lastMessage: 'Delta T bajo y presion de succion en 35 psi.',
    summary: 'Equipo prende y ventila, pero no baja temperatura. Delta T de 3 C.',
  },
  {
    id: 'C-0041',
    title: 'Nevera Whirlpool congela evaporador',
    manufacturer: 'Whirlpool',
    equipmentModel: 'WRX',
    category: 'Nevera domestica',
    status: 'open',
    updatedAt: 'hace 2 h',
    lastMessage: 'Revisar sensor de evaporador y ciclo de defrost.',
  },
  {
    id: 'C-0039',
    title: 'Camara frigorifica sube a 8 C',
    manufacturer: 'Copeland',
    equipmentModel: 'Scroll ZB',
    category: 'Refrigeracion comercial',
    status: 'closed',
    updatedAt: 'ayer',
    lastMessage: 'Caso cerrado: filtro secador restringido.',
  },
];

export const mockMessages: ChatMessage[] = [
  {
    id: 'm1',
    role: 'user',
    content:
      'El equipo prende, ventila normal pero no baja la temperatura. Hace 30 min que esta corriendo.',
  },
  {
    id: 'm2',
    role: 'assistant',
    content:
      'Sintoma compatible con falla del circuito de refrigerante. Verifica presion de baja, amperaje del compresor y diferencial de temperatura del evaporador antes de cargar refrigerante.',
    citations: [
      {
        id: '1',
        title: 'Carrier 38AKS Service Manual',
        source: 'RAG',
        detail: 'Troubleshooting, seccion 4.3',
      },
    ],
  },
  {
    id: 'm3',
    role: 'user',
    content: 'Delta T me da 3 C. Baja presion 35 psi.',
  },
  {
    id: 'm4',
    role: 'assistant',
    content:
      'Esos valores apuntan a baja carga, restriccion o bajo flujo de aire. Antes de agregar refrigerante, revisa filtro, serpentines, fuga visible y subcooling.',
  },
];

export const mockErrorCodes: ErrorCode[] = [
  {
    id: 'ec1',
    code: 'E7',
    manufacturer: 'Carrier',
    model: '38AKS',
    severity: 'medium',
    description: 'Sensor de evaporador fuera de rango.',
    possibleCauses: ['Sensor abierto', 'Cableado suelto', 'Conector sulfatado'],
    suggestedFix: 'Medir resistencia del sensor y revisar continuidad del cableado.',
    source: 'Manual de servicio Carrier 38AKS',
  },
  {
    id: 'ec2',
    code: 'U4',
    manufacturer: 'Daikin',
    model: 'VRV',
    severity: 'medium',
    description: 'Error de comunicacion entre unidades.',
    possibleCauses: ['Cableado de comunicacion', 'Direccionamiento incorrecto'],
    suggestedFix: 'Verificar polaridad, continuidad y direccionamiento de unidades.',
    source: 'Manual de servicio Daikin VRV',
  },
  {
    id: 'ec3',
    code: 'CH05',
    manufacturer: 'LG',
    model: 'Multi V',
    severity: 'high',
    description: 'Falla de comunicacion entre evaporador y condensador.',
    possibleCauses: ['Conexion incorrecta', 'Tarjeta de control defectuosa'],
    suggestedFix: 'Revisar cableado de comunicacion y voltajes de control.',
    source: 'Catalogo tecnico LG Multi V',
  },
];

export const mockManufacturers: ManufacturerSummary[] = [
  { id: 'm1', name: 'Carrier', modelCount: 1, errorCodeCount: 1 },
  { id: 'm2', name: 'Daikin', modelCount: 1, errorCodeCount: 1 },
  { id: 'm3', name: 'LG', modelCount: 1, errorCodeCount: 1 },
  { id: 'm4', name: 'Trane', modelCount: 0, errorCodeCount: 0 },
  { id: 'm5', name: 'Bitzer', modelCount: 0, errorCodeCount: 0 },
];

export const mockGuides: Guide[] = [
  {
    id: 'g1',
    title: 'Diagnostico de baja presion de succion',
    category: 'Diagnostico',
    duration: '12 min',
    offline: true,
    tools: ['Manifold', 'Termometro de pinza', 'Pinza amperimetrica', 'EPP'],
    steps: [
      'Confirmar refrigerante y condiciones de operacion.',
      'Medir presion de baja y temperatura de linea.',
      'Revisar flujo de aire y serpentines.',
      'Descartar fuga antes de cargar refrigerante.',
    ],
  },
  {
    id: 'g2',
    title: 'Checklist de seguridad con R-410A',
    category: 'Seguridad',
    duration: '7 min',
    offline: true,
    tools: ['Guantes', 'Gafas', 'Recuperadora', 'Bascula'],
    steps: [
      'Verificar ventilacion del area.',
      'Usar proteccion ocular y guantes.',
      'No liberar refrigerante a la atmosfera.',
      'Recuperar y pesar refrigerante cuando aplique.',
    ],
  },
];

export const primaryTools: ToolAction[] = [
  {
    id: 'new-case',
    title: 'Nuevo caso tecnico',
    subtitle: 'Chat, fuentes y metadata',
    icon: Wrench,
    target: 'newCase',
  },
  {
    id: 'diagnosis',
    title: 'Diagnostico por imagen',
    subtitle: 'Foto + analisis AI',
    icon: Camera,
    target: 'diagnosisCapture',
    badge: 'IA',
  },
  {
    id: 'codes',
    title: 'Codigos de error',
    subtitle: 'Fabricante y modelo',
    icon: AlertTriangle,
    target: 'codes',
  },
  {
    id: 'calculators',
    title: 'Calculadoras',
    subtitle: 'Superheat, subcool, PT',
    icon: Calculator,
    target: 'calculator',
    badge: 'OFFLINE',
  },
];

export const toolHub: ToolAction[] = [
  {
    id: 'diagnosis',
    title: 'Diagnostico por imagen',
    subtitle: 'Captura, contexto y resultado',
    icon: Camera,
    target: 'diagnosisCapture',
    badge: 'IA',
  },
  {
    id: 'superheat',
    title: 'Superheat',
    subtitle: 'Sobrecalentamiento',
    icon: ThermometerSun,
    target: 'calculator',
    params: { mode: 'superheat' },
    badge: 'OFFLINE',
  },
  {
    id: 'subcooling',
    title: 'Subcooling',
    subtitle: 'Subenfriamiento',
    icon: Snowflake,
    target: 'calculator',
    params: { mode: 'subcooling' },
    badge: 'OFFLINE',
  },
  {
    id: 'pt',
    title: 'PT Chart',
    subtitle: 'Presion / temperatura',
    icon: Gauge,
    target: 'calculator',
    params: { mode: 'pt' },
    badge: 'OFFLINE',
  },
  {
    id: 'guides',
    title: 'Guias',
    subtitle: 'Procedimientos paso a paso',
    icon: BookOpenCheck,
    target: 'guides',
    badge: 'OFFLINE',
  },
  {
    id: 'offline',
    title: 'Offline / Sync',
    subtitle: 'Datos locales y cola',
    icon: CloudOff,
    target: 'offline',
  },
  {
    id: 'settings',
    title: 'Ajustes',
    subtitle: 'Unidades, ayuda y version',
    icon: Settings,
    target: 'settings',
  },
];
