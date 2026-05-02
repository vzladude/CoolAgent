// Coolpanion · Home (Tool Hub) + extras
// Reflects MVP brief: app is a technical toolbox, not chat-centric.

const _T = () => window.DIRECTIONS.dark;

// ─────────────────────────────────────────────────────────────
// 1. HOME · Tool Hub
// ─────────────────────────────────────────────────────────────
function Home() {
  const t = _T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 26, height: 26, borderRadius: 6, background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`, color: '#001318', fontWeight: 700, fontSize: 13, fontFamily: t.mono, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>C</div>
            <div style={{ fontSize: 14, fontWeight: 600, letterSpacing: '-0.02em' }}>Coolpanion</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: t.mono, fontSize: 10.5, color: t.success, letterSpacing: '0.06em' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.success, boxShadow: `0 0 6px ${t.success}` }}/>
            ONLINE
          </div>
        </div>

        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4 }}>VIE 1 MAY · 14:32</div>
        <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.03em', marginBottom: 4 }}>Buenas, Ricardo.</div>
        <div style={{ fontSize: 14, color: t.textMuted, lineHeight: 1.45 }}>2 casos abiertos · sincronizado hace 4 min.</div>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', padding: '8px 12px 0' }}>
        {/* Primary action: nuevo caso */}
        <div style={{
          background: t.surface, border: `1px solid ${t.borderStrong}`,
          borderRadius: 16, padding: 14, marginBottom: 14,
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: -30, right: -30, width: 140, height: 140,
            borderRadius: '50%', background: `radial-gradient(circle, ${t.accentSoft}, transparent 65%)`,
            pointerEvents: 'none',
          }}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, position: 'relative' }}>
            <window.Icons.plus size={16} color={t.accent} stroke={2.2}/>
            <span style={{ fontFamily: t.mono, fontSize: 10.5, color: t.accent, letterSpacing: '0.08em' }}>NUEVO CASO TÉCNICO</span>
          </div>
          <div style={{ fontSize: 17, fontWeight: 500, letterSpacing: '-0.02em', lineHeight: 1.3, position: 'relative', marginBottom: 12 }}>
            ¿Qué equipo o falla<br/>vamos a revisar hoy?
          </div>
          <div style={{ display: 'flex', gap: 8, position: 'relative' }}>
            <button style={{
              flex: 1, height: 42, borderRadius: 11, border: 'none',
              background: t.accent, color: '#001318',
              fontFamily: t.font, fontSize: 13, fontWeight: 600,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            }}>Empezar</button>
            <button style={{
              height: 42, padding: '0 14px', borderRadius: 11,
              background: 'transparent', border: `1px solid ${t.border}`, color: t.text,
              fontSize: 13, fontFamily: t.font, fontWeight: 500,
              display: 'flex', alignItems: 'center', gap: 6,
            }}><window.Icons.camera size={14} color={t.text}/> Foto</button>
          </div>
        </div>

        {/* Continue working: latest case */}
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8, padding: '0 4px' }}>CONTINUAR</div>
        <div style={{
          background: t.surface, border: `1px solid ${t.border}`,
          borderRadius: 12, padding: '12px 14px', marginBottom: 16,
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: 9,
            background: t.bg, border: `1px solid ${t.border}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <window.Icons.thermo size={18} color={t.textMuted} stroke={1.6}/>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: t.mono, fontSize: 10, color: t.success, letterSpacing: '0.06em', marginBottom: 2 }}>C-0042 · ABIERTO · HACE 12 MIN</div>
            <div style={{ fontSize: 14, fontWeight: 500, color: t.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Carrier 38AKS no enfría</div>
          </div>
          <window.Icons.chevRight size={16} color={t.textDim}/>
        </div>

        {/* Tool grid */}
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8, padding: '0 4px' }}>HERRAMIENTAS</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <ToolTile icon={<window.Icons.camera size={20} color={t.accent}/>} label="Diagnóstico por imagen" sub="Foto + análisis IA"/>
          <ToolTile icon={<window.Icons.alert size={20} color={t.accent}/>} label="Códigos de error" sub="8 fabricantes · offline"/>
          <ToolTile icon={<window.Icons.cpu size={20} color={t.accent}/>} label="Calculadoras" sub="Superheat · Subcool · PT"/>
          <ToolTile icon={<window.Icons.bookmark size={20} color={t.accent}/>} label="Guías" sub="Procedimientos paso a paso"/>
        </div>
      </div>

      <window.TabBar active="home"/>
    </div>
  );
}

function ToolTile({ icon, label, sub }) {
  const t = _T();
  return (
    <div style={{
      background: t.surface, border: `1px solid ${t.border}`,
      borderRadius: 12, padding: '14px 14px 12px',
      display: 'flex', flexDirection: 'column', gap: 8, minHeight: 110,
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 9, background: t.accentSoft,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>{icon}</div>
      <div style={{ fontSize: 13.5, fontWeight: 500, color: t.text, letterSpacing: '-0.01em', lineHeight: 1.25 }}>{label}</div>
      <div style={{ fontFamily: t.mono, fontSize: 10, color: t.textMuted, letterSpacing: '0.04em', marginTop: 'auto' }}>{sub}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 2. EMPTY HOME (sin casos)
// ─────────────────────────────────────────────────────────────
function HomeEmpty() {
  const t = _T();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <div style={{ width: 26, height: 26, borderRadius: 6, background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`, color: '#001318', fontWeight: 700, fontSize: 13, fontFamily: t.mono, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>C</div>
          <div style={{ fontSize: 14, fontWeight: 600, letterSpacing: '-0.02em' }}>Coolpanion</div>
        </div>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>PRIMER ARRANQUE</div>
        <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.03em', lineHeight: 1.1 }}>Tu caja de herramientas técnica.</div>
      </div>

      <div style={{ flex: 1, padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{
          background: t.surface, border: `1px solid ${t.borderStrong}`,
          borderRadius: 14, padding: 16,
        }}>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.accent, letterSpacing: '0.08em', marginBottom: 6 }}>EMPIEZA AQUÍ</div>
          <div style={{ fontSize: 15.5, color: t.text, lineHeight: 1.45, marginBottom: 12 }}>
            Crea tu primer caso técnico. Cada caso guarda el chat, la metadata del equipo y las fuentes consultadas.
          </div>
          <button style={{
            width: '100%', height: 46, borderRadius: 11, border: 'none',
            background: t.accent, color: '#001318',
            fontFamily: t.font, fontSize: 14, fontWeight: 600,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
          }}>
            <window.Icons.plus size={15} color="#001318" stroke={2.2}/> Crear primer caso
          </button>
        </div>

        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginTop: 4, marginBottom: 4, padding: '0 4px' }}>O EXPLORA</div>
        <AltRow icon={<window.Icons.camera size={18} color={t.text}/>} label="Diagnóstico por imagen" sub="Toma una foto del equipo o falla"/>
        <AltRow icon={<window.Icons.alert size={18} color={t.text}/>} label="Códigos de error" sub="Busca por fabricante o código"/>
        <AltRow icon={<window.Icons.cpu size={18} color={t.text}/>} label="Calculadoras" sub="Superheat, subcooling, PT chart"/>
      </div>

      <window.TabBar active="home"/>
    </div>
  );
}

function AltRow({ icon, label, sub }) {
  const t = _T();
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
      background: t.surface, border: `1px solid ${t.border}`, borderRadius: 12,
    }}>
      <div style={{ width: 34, height: 34, borderRadius: 9, background: t.bg, border: `1px solid ${t.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{icon}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13.5, fontWeight: 500, color: t.text }}>{label}</div>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.02em', marginTop: 2 }}>{sub}</div>
      </div>
      <window.Icons.chevRight size={14} color={t.textDim}/>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// 3. SPLASH (refactor): minimal · funcional
// ─────────────────────────────────────────────────────────────
function SplashUtil() {
  const t = _T();
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'space-between',
      padding: '120px 28px 60px', boxSizing: 'border-box',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%, -50%)',
        width: 360, height: 360, borderRadius: '50%',
        background: `radial-gradient(circle, ${t.accentSoft}, transparent 65%)`,
        filter: 'blur(20px)', pointerEvents: 'none',
      }}/>

      <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, marginTop: 80 }}>
        <div style={{
          width: 64, height: 64, borderRadius: 18,
          background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#001318', fontWeight: 700, fontSize: 30, fontFamily: t.mono,
          boxShadow: `0 0 40px ${t.accentSoft}`,
        }}>C</div>
        <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.025em' }}>Coolpanion</div>
        <div style={{ fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.08em', textAlign: 'center' }}>
          REFRIGERACIÓN · CLIMATIZACIÓN · CADENA DE FRÍO
        </div>
      </div>

      <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.06em' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.accent, animation: 'cgPulse 1s infinite' }}/>
          CARGANDO BASE OFFLINE…
        </div>
        <div style={{ width: 200, height: 2, background: t.surface, borderRadius: 1, overflow: 'hidden' }}>
          <div style={{ width: '64%', height: '100%', background: t.accent, boxShadow: `0 0 8px ${t.accent}` }}/>
        </div>
        <div style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.06em' }}>v0.1 · 142</div>
      </div>
    </div>
  );
}

window.Home = Home;
window.HomeEmpty = HomeEmpty;
window.SplashUtil = SplashUtil;
