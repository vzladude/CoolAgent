// Additional Coolpanion screens — Editorial Dark direction
// Screens: CasesList, NewCase, CaseDetail (metadata editable), ErrorCodes, Knowledge, Profile

const T = () => window.DIRECTIONS.dark;

// ---- shared shell helpers ----
function Header({ title, sub, onBack = true, right }) {
  const t = T();
  return (
    <div style={{
      paddingTop: 56, paddingBottom: 14, paddingLeft: 16, paddingRight: 16,
      background: t.bg, borderBottom: `1px solid ${t.border}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: sub || title ? 10 : 0 }}>
        {onBack ? (
          <button style={iconBtnD()}><window.Icons.chevLeft size={18} color={t.text}/></button>
        ) : <div style={{ width: 36 }}/>}
        {sub && (
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em' }}>{sub}</div>
        )}
        {right || <button style={iconBtnD()}><window.Icons.more size={18} color={t.text}/></button>}
      </div>
      {title && (
        <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.03em' }}>{title}</div>
      )}
    </div>
  );
}

function iconBtnD(ghost) {
  const t = T();
  return {
    width: 36, height: 36, borderRadius: 10,
    background: 'transparent',
    border: ghost ? 'none' : `1px solid ${t.border}`,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', padding: 0,
  };
}

function TabBar({ active = 'home' }) {
  const t = T();
  const items = [
    { id: 'home',  label: 'Inicio',    icon: <window.Icons.bolt    size={20} color={active==='home'?t.accent:t.textDim} stroke={1.6}/> },
    { id: 'cases', label: 'Casos',     icon: <window.Icons.inbox   size={20} color={active==='cases'?t.accent:t.textDim} stroke={1.6}/> },
    { id: 'tools', label: 'Herram.',   icon: <window.Icons.wrench  size={20} color={active==='tools'?t.accent:t.textDim} stroke={1.6}/> },
    { id: 'codes', label: 'Códigos',   icon: <window.Icons.alert   size={20} color={active==='codes'?t.accent:t.textDim} stroke={1.6}/> },
    { id: 'me',    label: 'Ajustes',   icon: <window.Icons.cpu     size={20} color={active==='me'?t.accent:t.textDim} stroke={1.6}/> },
  ];
  return (
    <div style={{
      borderTop: `1px solid ${t.border}`, background: t.bg,
      display: 'grid', gridTemplateColumns: 'repeat(5,1fr)',
      paddingTop: 8, paddingBottom: 28,
    }}>
      {items.map(it => (
        <div key={it.id} style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
        }}>
          {it.icon}
          <span style={{
            fontSize: 9.5, fontFamily: t.mono, letterSpacing: '0.06em',
            color: active === it.id ? t.accent : t.textDim,
          }}>{it.label.toUpperCase()}</span>
        </div>
      ))}
    </div>
  );
}

// =============================================================
// 1. Cases list (Home)
// =============================================================
const CASES = [
  { id: 'C-0042', title: 'Carrier 38AKS no enfría', mfr: 'Carrier', model: '38AKS-024', cat: 'Split', status: 'open',  last: 'hace 12 min', preview: 'CoolAgent · Esos valores indican carga insuficiente o restricción en línea de líquido…', unread: 2 },
  { id: 'C-0041', title: 'Cámara fría 2 — pérdida de SP', mfr: 'Bitzer', model: '4FES-5Y', cat: 'Compresor', status: 'open', last: 'hace 1 h', preview: 'Operador · Aceite por debajo del visor a temperatura de servicio.', unread: 0 },
  { id: 'C-0040', title: 'Trane chiller alarma E7-3', mfr: 'Trane', model: 'CGAM-070', cat: 'Chiller', status: 'open', last: 'hoy 09:14', preview: 'CoolAgent · E7-3 corresponde a falla de sensor de presión de evaporador…', unread: 0 },
  { id: 'C-0039', title: 'VRV Daikin desbalance fases',  mfr: 'Daikin', model: 'RXYQ-10', cat: 'VRV', status: 'closed', last: 'ayer', preview: 'Cerrado · Reapriete de bornera resolvió desbalance.', unread: 0 },
  { id: 'C-0038', title: 'Copeland ZR scroll ruido',     mfr: 'Copeland', model: 'ZR94KCE', cat: 'Compresor', status: 'closed', last: '28 abr', preview: 'Cerrado · Reemplazo del scroll bajo garantía.', unread: 0 },
];

function CasesList() {
  const t = T();
  const open = CASES.filter(c => c.status === 'open');
  const closed = CASES.filter(c => c.status === 'closed');
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      {/* Custom header with greeting */}
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 26, height: 26, borderRadius: 6, background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`, color: '#001318', fontWeight: 700, fontSize: 13, fontFamily: t.mono, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>C</div>
            <div style={{ fontSize: 14, fontWeight: 600, letterSpacing: '-0.02em' }}>Coolpanion</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button style={iconBtnD()}><window.Icons.search size={17} color={t.text}/></button>
            <button style={iconBtnD()}><window.Icons.bolt size={17} color={t.text}/></button>
          </div>
        </div>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4 }}>1 MAY · VIERNES · 14:32</div>
        <div style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.03em', marginBottom: 12 }}>Casos técnicos</div>
        <div style={{ display: 'flex', gap: 6 }}>
          <FilterPill active>Abiertos · {open.length}</FilterPill>
          <FilterPill>Cerrados · {closed.length}</FilterPill>
          <FilterPill>Todos</FilterPill>
        </div>
      </div>

      {/* List */}
      <div style={{ flex: 1, overflow: 'hidden', padding: '6px 12px 0' }}>
        {open.map((c) => <CaseRow key={c.id} c={c}/>)}
        <div style={{
          fontFamily: t.mono, fontSize: 10.5, color: t.textDim,
          letterSpacing: '0.08em', padding: '14px 6px 6px',
        }}>CERRADOS</div>
        {closed.map((c) => <CaseRow key={c.id} c={c} dim/>)}
      </div>

      {/* FAB */}
      <div style={{ position: 'relative' }}>
        <div style={{
          position: 'absolute', right: 16, bottom: 12,
          width: 56, height: 56, borderRadius: 18,
          background: t.accent, color: '#001318',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: `0 0 24px ${t.accentSoft}, 0 8px 24px rgba(0,0,0,0.4)`,
        }}>
          <window.Icons.plus size={24} color="#001318" stroke={2.4}/>
        </div>
      </div>

      <TabBar active="cases"/>
    </div>
  );
}

function FilterPill({ active, children }) {
  const t = T();
  return (
    <span style={{
      padding: '6px 12px', borderRadius: 999,
      fontFamily: t.mono, fontSize: 11, letterSpacing: '0.04em',
      background: active ? t.accentSoft : 'transparent',
      color: active ? t.accent : t.textMuted,
      border: `1px solid ${active ? t.borderStrong : t.border}`,
    }}>{children}</span>
  );
}

function CaseRow({ c, dim }) {
  const t = T();
  return (
    <div style={{
      display: 'flex', gap: 12, padding: '12px 10px',
      borderBottom: `1px solid ${t.border}`,
      opacity: dim ? 0.55 : 1,
    }}>
      <div style={{
        width: 38, height: 38, borderRadius: 10,
        background: t.surface, border: `1px solid ${t.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <window.Icons.thermo size={18} color={t.textMuted} stroke={1.6}/>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 2 }}>
          <span style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.06em' }}>{c.id}</span>
          <span style={{
            fontFamily: t.mono, fontSize: 10, letterSpacing: '0.04em',
            color: c.status === 'open' ? t.success : t.textDim,
          }}>· {c.status === 'open' ? 'ABIERTO' : 'CERRADO'}</span>
          <span style={{ marginLeft: 'auto', fontFamily: t.mono, fontSize: 10, color: t.textDim }}>{c.last}</span>
        </div>
        <div style={{ fontSize: 14.5, fontWeight: 500, color: t.text, letterSpacing: '-0.01em', marginBottom: 3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.title}</div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginBottom: 4 }}>
          <span style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted }}>{c.mfr} / {c.model}</span>
          <span style={{ fontSize: 11, color: t.textDim }}>· {c.cat}</span>
        </div>
        <div style={{ fontSize: 12.5, color: t.textMuted, lineHeight: 1.4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {c.preview}
        </div>
      </div>
      {c.unread > 0 && (
        <div style={{
          alignSelf: 'flex-start', marginTop: 4,
          width: 18, height: 18, borderRadius: 9,
          background: t.accent, color: '#001318',
          fontFamily: t.mono, fontSize: 10, fontWeight: 700,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>{c.unread}</div>
      )}
    </div>
  );
}

// =============================================================
// 2. New case
// =============================================================
function NewCase() {
  const t = T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <Header title="Nuevo caso" sub="C-0043 · BORRADOR" right={<button style={{ ...iconBtnD(true), color: t.accent, fontFamily: t.mono, fontSize: 12, letterSpacing: '0.06em', width: 'auto', padding: '0 4px' }}>CANCELAR</button>}/>

      <div style={{ flex: 1, overflow: 'hidden', padding: '18px 16px 0', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Field label="Título del caso" value="Carrier 38AKS no enfría" placeholder="Describe el síntoma principal"/>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <Field label="Fabricante" value="Carrier" mono/>
          <Field label="Modelo" value="38AKS-024" mono/>
        </div>

        <FieldSelect label="Categoría" value="Aire acondicionado · Split"/>

        <div>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8 }}>SUGERIDOS</div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {['Chiller', 'VRV', 'Cámara fría', 'Compresor scroll', 'Compresor semi-hermético', 'Cadena de frío'].map(c => (
              <FilterPill key={c}>{c}</FilterPill>
            ))}
          </div>
        </div>

        <div>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8 }}>CONTEXTO INICIAL · OPCIONAL</div>
          <div style={{
            background: t.surface, border: `1px solid ${t.border}`, borderRadius: 12,
            padding: '12px 14px', minHeight: 80,
            fontSize: 14, color: t.textDim, lineHeight: 1.5,
          }}>
            Equipo en azotea, opera 18h/día. Reportado por mantenimiento que no baja la temperatura desde anoche…
          </div>
        </div>
      </div>

      <div style={{ padding: '12px 16px 28px', borderTop: `1px solid ${t.border}` }}>
        <button style={{
          width: '100%', height: 52, borderRadius: 14, border: 'none',
          background: t.accent, color: '#001318', fontFamily: t.font,
          fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>Abrir caso y empezar a chatear <window.Icons.arrowUp size={16} color="#001318" stroke={2.2}/></button>
      </div>
    </div>
  );
}

function Field({ label, value, placeholder, mono }) {
  const t = T();
  return (
    <div>
      <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>{label.toUpperCase()}</div>
      <div style={{
        background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10,
        padding: '12px 14px', fontSize: 15, color: value ? t.text : t.textDim,
        fontFamily: mono ? t.mono : t.font, letterSpacing: mono ? '0.01em' : '-0.005em',
      }}>{value || placeholder}</div>
    </div>
  );
}

function FieldSelect({ label, value }) {
  const t = T();
  return (
    <div>
      <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>{label.toUpperCase()}</div>
      <div style={{
        background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10,
        padding: '12px 14px', fontSize: 15, color: t.text,
        display: 'flex', alignItems: 'center',
      }}>
        <span style={{ flex: 1 }}>{value}</span>
        <window.Icons.chevRight size={16} color={t.textDim}/>
      </div>
    </div>
  );
}

// =============================================================
// 3. Case detail (editable metadata)
// =============================================================
function CaseDetail() {
  const t = T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <Header sub="C-0042 · DETALLES"/>

      <div style={{ flex: 1, overflow: 'hidden', padding: '0 16px' }}>
        {/* Hero block */}
        <div style={{ paddingBottom: 16, borderBottom: `1px solid ${t.border}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.success }}/>
            <span style={{ fontFamily: t.mono, fontSize: 10.5, color: t.success, letterSpacing: '0.08em' }}>ABIERTO · 12 mensajes</span>
            <span style={{ marginLeft: 'auto', fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.04em' }}>Creado 28 abr · 09:14</span>
          </div>
          <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.025em', marginBottom: 12 }}>Carrier 38AKS no enfría</div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button style={{
              flex: 1, height: 42, borderRadius: 12, border: 'none',
              background: t.accent, color: '#001318', fontFamily: t.font,
              fontSize: 13.5, fontWeight: 600, letterSpacing: '-0.01em',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            }}><window.Icons.arrowUp size={14} color="#001318" stroke={2.2} /> Abrir chat</button>
            <button style={{
              height: 42, padding: '0 14px', borderRadius: 12,
              background: t.surface, border: `1px solid ${t.border}`, color: t.text,
              fontSize: 13, fontFamily: t.font, fontWeight: 500,
              display: 'flex', alignItems: 'center', gap: 6,
            }}><window.Icons.check size={14} color={t.text}/> Cerrar</button>
          </div>
        </div>

        {/* Editable metadata */}
        <div style={{ paddingTop: 14 }}>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.1em', marginBottom: 8 }}>METADATA · TOCA PARA EDITAR</div>
          <DataRow label="Fabricante" value="Carrier" mono/>
          <DataRow label="Modelo" value="38AKS-024" mono/>
          <DataRow label="Categoría" value="Aire acondicionado · Split"/>
          <DataRow label="Refrigerante" value="R-410A" mono/>
          <DataRow label="Ubicación" value="Edificio B · Azotea sur"/>
        </div>

        {/* Auto summary */}
        <div style={{ marginTop: 16, padding: '12px 14px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 12 }}>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.accent, letterSpacing: '0.08em', marginBottom: 6 }}>RESUMEN AUTO · CLAUDE</div>
          <div style={{ fontSize: 13, lineHeight: 1.5, color: t.textMuted }}>
            Equipo opera con ventilación normal pero ∆T evaporador 3°C y baja presión 35 psi (R-410A). Pendiente: descartar restricción en línea de líquido antes de carga.
          </div>
          <div style={{ marginTop: 8, fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.04em' }}>compactado hace 4 min · 1,240 → 380 tokens</div>
        </div>
      </div>

      <TabBar active="cases"/>
    </div>
  );
}

function DataRow({ label, value, mono }) {
  const t = T();
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '12px 0', borderBottom: `1px solid ${t.border}`,
    }}>
      <div style={{ fontSize: 13, color: t.textMuted }}>{label}</div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        fontSize: 14, fontFamily: mono ? t.mono : t.font, color: t.text,
      }}>
        {value}
        <window.Icons.chevRight size={14} color={t.textDim}/>
      </div>
    </div>
  );
}

// =============================================================
// 4. Error codes search
// =============================================================
const CODES = [
  { code: 'E1-0', mfr: 'Carrier', mdl: '38AKS', desc: 'Falla sensor temperatura aire de retorno', sev: 'med' },
  { code: 'E7-3', mfr: 'Trane',  mdl: 'CGAM',   desc: 'Sensor presión evaporador fuera de rango', sev: 'high' },
  { code: 'U0',   mfr: 'Daikin', mdl: 'RXYQ',   desc: 'Bajo nivel de refrigerante detectado', sev: 'high' },
  { code: 'F0',   mfr: 'LG',     mdl: 'Multi V', desc: 'Comunicación interior–exterior interrumpida', sev: 'med' },
  { code: 'CH07', mfr: 'Samsung',mdl: 'DVM S',  desc: 'Modo emergencia · ventilador int. detenido', sev: 'high' },
  { code: 'A1',   mfr: 'Daikin', mdl: 'RXYQ',   desc: 'Falla EEPROM placa principal', sev: 'med' },
];

function ErrorCodes() {
  const t = T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 14 }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4 }}>BASE OFFLINE · 8 FABRICANTES · SINCRONIZADO HACE 2D</div>
        <div style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.03em', marginBottom: 14 }}>Códigos de error</div>

        {/* Search bar */}
        <div style={{
          background: t.surface, border: `1px solid ${t.borderStrong}`, borderRadius: 12,
          padding: '11px 12px', display: 'flex', alignItems: 'center', gap: 10,
          marginBottom: 12,
        }}>
          <window.Icons.search size={17} color={t.textMuted}/>
          <span style={{ flex: 1, fontFamily: t.mono, fontSize: 14, color: t.text }}>E7-3</span>
          <span style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.06em' }}>6 RESULTADOS</span>
        </div>

        <div style={{ display: 'flex', gap: 6, overflow: 'hidden' }}>
          <FilterPill active>Todos</FilterPill>
          <FilterPill>Carrier</FilterPill>
          <FilterPill>Trane</FilterPill>
          <FilterPill>Daikin</FilterPill>
          <FilterPill>+5</FilterPill>
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', padding: '4px 12px 0' }}>
        {CODES.map((c, i) => (
          <div key={i} style={{
            display: 'flex', gap: 12, padding: '12px 8px',
            borderBottom: `1px solid ${t.border}`,
          }}>
            <div style={{
              width: 64, fontFamily: t.mono, fontSize: 16, fontWeight: 600,
              color: c.sev === 'high' ? t.danger : t.warn, letterSpacing: '0.02em',
              display: 'flex', alignItems: 'flex-start',
            }}>{c.code}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, color: t.text, lineHeight: 1.4, marginBottom: 4 }}>{c.desc}</div>
              <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.04em' }}>
                {c.mfr.toUpperCase()} · {c.mdl}
              </div>
            </div>
            <window.Icons.chevRight size={14} color={t.textDim}/>
          </div>
        ))}
      </div>

      <TabBar active="codes"/>
    </div>
  );
}

// =============================================================
// 5. Knowledge base (RAG glossary)
// =============================================================
const DOCS = [
  { name: 'Carrier 38AKS Service Manual', kind: 'PDF', size: '4.2 MB', chunks: 142, status: 'active', date: '12 abr' },
  { name: 'Trane CGAM Troubleshooting Guide', kind: 'PDF', size: '2.8 MB', chunks: 96, status: 'active', date: '08 abr' },
  { name: 'Daikin VRV Service Bulletin 2024-Q4', kind: 'PDF', size: '1.1 MB', chunks: 38, status: 'active', date: '02 abr' },
  { name: 'Glosario · Refrigerantes y compatibilidades', kind: 'TXT', size: '180 KB', chunks: 12, status: 'active', date: '28 mar' },
  { name: 'Copeland ZR scroll · Boletín técnico', kind: 'PDF', size: '780 KB', chunks: 24, status: 'indexing', date: 'hoy' },
];

function Knowledge() {
  const t = T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
          <div>
            <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4 }}>BASE DE CONOCIMIENTO · RAG</div>
            <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.03em' }}>Manuales</div>
          </div>
          <button style={{
            height: 38, padding: '0 14px', borderRadius: 10,
            background: t.accent, color: '#001318',
            fontFamily: t.font, fontSize: 13, fontWeight: 600, border: 'none',
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <window.Icons.plus size={14} color="#001318" stroke={2.2}/>
            Subir
          </button>
        </div>

        <div style={{ display: 'flex', gap: 10, marginBottom: 4 }}>
          <Stat label="Documentos" value="5"/>
          <Stat label="Chunks" value="312"/>
          <Stat label="Tokens" value="48k"/>
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', padding: '0 12px' }}>
        {DOCS.map((d, i) => (
          <div key={i} style={{
            display: 'flex', gap: 12, padding: '12px 8px',
            borderBottom: `1px solid ${t.border}`,
          }}>
            <div style={{
              width: 38, height: 38, borderRadius: 8,
              background: t.surface, border: `1px solid ${t.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <window.Icons.doc size={17} color={t.textMuted} stroke={1.6}/>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, fontWeight: 500, color: t.text, lineHeight: 1.35, marginBottom: 3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.name}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.04em' }}>
                <span>{d.kind}</span>
                <span>·</span>
                <span>{d.size}</span>
                <span>·</span>
                <span>{d.chunks} chunks</span>
                <span style={{ marginLeft: 'auto', color: t.textDim }}>{d.date}</span>
              </div>
            </div>
            <div style={{ alignSelf: 'center' }}>
              {d.status === 'indexing' ? (
                <span style={{ fontFamily: t.mono, fontSize: 10, color: t.warn, letterSpacing: '0.06em' }}>INDEX…</span>
              ) : (
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: t.success, display: 'inline-block' }}/>
              )}
            </div>
          </div>
        ))}
      </div>

      <TabBar active="kb"/>
    </div>
  );
}

function Stat({ label, value }) {
  const t = T();
  return (
    <div style={{
      flex: 1, padding: '10px 12px',
      background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10,
    }}>
      <div style={{ fontSize: 18, fontWeight: 600, letterSpacing: '-0.02em', color: t.text }}>{value}</div>
      <div style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</div>
    </div>
  );
}

// =============================================================
// 6. Profile / settings
// =============================================================
function Profile() {
  const t = T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 18 }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4 }}>PERFIL · TÉCNICO</div>
        <div style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.03em' }}>Yo</div>
      </div>

      {/* Profile card */}
      <div style={{ padding: '0 16px 14px' }}>
        <div style={{
          background: t.surface, border: `1px solid ${t.border}`, borderRadius: 14,
          padding: 16, display: 'flex', alignItems: 'center', gap: 14,
        }}>
          <div style={{
            width: 52, height: 52, borderRadius: 14,
            background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#001318', fontWeight: 700, fontSize: 20, fontFamily: t.mono,
          }}>RG</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 16, fontWeight: 600, letterSpacing: '-0.02em' }}>Ricardo G.</div>
            <div style={{ fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.04em', marginTop: 2 }}>TÉCNICO HVAC/R · NIVEL 3</div>
          </div>
          <window.Icons.chevRight size={16} color={t.textDim}/>
        </div>
      </div>

      {/* Usage strip */}
      <div style={{ padding: '0 16px 14px' }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8 }}>USO · MAYO</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <Stat label="Casos" value="12"/>
          <Stat label="Mensajes" value="148"/>
          <Stat label="Cache hit" value="34%"/>
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', padding: '4px 12px 0' }}>
        <SettingsRow icon={<window.Icons.bolt size={17} color={t.text}/>} label="Modelo IA" value="Claude Haiku 4.5"/>
        <SettingsRow icon={<window.Icons.wifi size={17} color={t.text}/>} label="Modo offline" value="Códigos · Último caso"/>
        <SettingsRow icon={<window.Icons.doc size={17} color={t.text}/>} label="Manuales sincronizados" value="5 · 312 chunks"/>
        <SettingsRow icon={<window.Icons.bookmark size={17} color={t.text}/>} label="Idioma" value="Español"/>
        <SettingsRow icon={<window.Icons.wrench size={17} color={t.text}/>} label="Diagnósticos avanzados" value="Off"/>
        <SettingsRow icon={<window.Icons.cpu size={17} color={t.text}/>} label="Versión" value="0.1.0 · build 142" mute/>
      </div>

      <TabBar active="me"/>
    </div>
  );
}

function SettingsRow({ icon, label, value, mute }) {
  const t = T();
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14, padding: '14px 8px',
      borderBottom: `1px solid ${t.border}`,
      opacity: mute ? 0.6 : 1,
    }}>
      <div style={{
        width: 32, height: 32, borderRadius: 8,
        background: t.surface, border: `1px solid ${t.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>{icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, color: t.text }}>{label}</div>
        <div style={{ fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.02em', marginTop: 2 }}>{value}</div>
      </div>
      <window.Icons.chevRight size={14} color={t.textDim}/>
    </div>
  );
}

window.CasesList = CasesList;
window.NewCase = NewCase;
window.CaseDetail = CaseDetail;
window.ErrorCodes = ErrorCodes;
window.Knowledge = Knowledge;
window.Profile = Profile;
window.TabBar = TabBar;
