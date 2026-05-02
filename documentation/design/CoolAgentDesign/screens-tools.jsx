// Coolpanion · Tools (calculators) + Image diagnosis + Guides + Offline + extras

const _Tt = () => window.DIRECTIONS.dark;

// ─────────────────────────────────────────────────────────────
// SHARED Header
// ─────────────────────────────────────────────────────────────
function ScrHeader({ title, sub, back, right }) {
  const t = _Tt();
  return (
    <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 14, borderBottom: `1px solid ${t.border}`, background: t.bg }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
        {back && <window.Icons.chevLeft size={18} color={t.text}/>}
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em' }}>{sub}</div>
        <div style={{ marginLeft: 'auto' }}>{right}</div>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.025em' }}>{title}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// TOOLS HUB
// ─────────────────────────────────────────────────────────────
function ToolsHub() {
  const t = _Tt();
  const tiles = [
    { i: 'camera', label: 'Diagnóstico por imagen', sub: 'Foto + análisis IA', online: true },
    { i: 'thermo', label: 'Superheat', sub: 'Sobrecalentamiento', online: false },
    { i: 'thermo', label: 'Subcooling', sub: 'Subenfriamiento', online: false },
    { i: 'cpu', label: 'PT Chart', sub: 'Presión / temperatura', online: false },
    { i: 'cpu', label: 'Conversor', sub: 'PSI · bar · °C · °F', online: false },
    { i: 'bookmark', label: 'Guías', sub: 'Procedimientos', online: false },
  ];
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="HERRAMIENTAS" title="Caja técnica"/>
      <div style={{ flex: 1, padding: '14px 12px', overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {tiles.map((tile, idx) => {
            const Icon = window.Icons[tile.i];
            return (
              <div key={idx} style={{
                background: t.surface, border: `1px solid ${t.border}`,
                borderRadius: 12, padding: '14px 14px 12px', minHeight: 116,
                display: 'flex', flexDirection: 'column', gap: 8, position: 'relative',
              }}>
                <div style={{ width: 36, height: 36, borderRadius: 9, background: t.accentSoft, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={20} color={t.accent}/>
                </div>
                <div style={{ fontSize: 13.5, fontWeight: 500, lineHeight: 1.25, letterSpacing: '-0.01em' }}>{tile.label}</div>
                <div style={{ fontFamily: t.mono, fontSize: 10, color: t.textMuted, letterSpacing: '0.04em', marginTop: 'auto' }}>{tile.sub}</div>
                {!tile.online && (
                  <div style={{ position: 'absolute', top: 12, right: 12, fontFamily: t.mono, fontSize: 9, color: t.success, letterSpacing: '0.06em' }}>OFFLINE ✓</div>
                )}
                {tile.online && (
                  <div style={{ position: 'absolute', top: 12, right: 12, fontFamily: t.mono, fontSize: 9, color: t.accent, letterSpacing: '0.06em' }}>IA</div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      <window.TabBar active="tools"/>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// SUPERHEAT CALCULATOR
// ─────────────────────────────────────────────────────────────
function CalcSuperheat() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="CALCULADORA" title="Superheat" back right={
        <span style={{ fontFamily: t.mono, fontSize: 9.5, color: t.success, letterSpacing: '0.06em' }}>OFFLINE ✓</span>
      }/>
      <div style={{ flex: 1, padding: 16, overflow: 'hidden' }}>
        <CalcRow label="Refrigerante" value="R-410A" mono pill/>
        <CalcRow label="Presión succión" unit="psi" value="118.0" input/>
        <CalcRow label="Temp. línea succión" unit="°F" value="58.4" input/>

        <div style={{
          background: t.surface, border: `1px solid ${t.borderStrong}`,
          borderRadius: 14, padding: 16, marginTop: 18,
        }}>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>RESULTADO</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 44, fontWeight: 600, fontFamily: t.mono, letterSpacing: '-0.03em', color: t.accent }}>17.6</span>
            <span style={{ fontFamily: t.mono, fontSize: 13, color: t.textMuted }}>°F SH</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', background: t.bg, border: `1px solid ${t.border}`, borderRadius: 9 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.success, flexShrink: 0 }}/>
            <span style={{ fontSize: 12.5, color: t.textMuted, lineHeight: 1.45 }}>Dentro de rango típico (8–20°F). Confirmar contra spec del fabricante.</span>
          </div>
        </div>

        <div style={{ marginTop: 14, padding: '10px 12px', background: t.warningSoft, border: `1px solid ${t.warning}40`, borderRadius: 9, fontSize: 11.5, color: t.warning, lineHeight: 1.4, fontFamily: t.mono, letterSpacing: '0.02em' }}>
          ⚠ No reemplaza criterio técnico certificado.
        </div>
      </div>
      <window.TabBar active="tools"/>
    </div>
  );
}

function CalcRow({ label, value, unit, input, pill, mono }) {
  const t = _Tt();
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 0', borderBottom: `1px solid ${t.border}` }}>
      <div style={{ fontSize: 13.5, color: t.textMuted }}>{label}</div>
      {pill ? (
        <div style={{ padding: '6px 12px', borderRadius: 999, background: t.accentSoft, color: t.accent, fontFamily: t.mono, fontSize: 12, letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 6 }}>
          {value} <window.Icons.chevRight size={12} color={t.accent}/>
        </div>
      ) : input ? (
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <span style={{ fontFamily: t.mono, fontSize: 18, color: t.text, fontWeight: 500 }}>{value}</span>
          <span style={{ fontFamily: t.mono, fontSize: 11, color: t.textDim, letterSpacing: '0.04em' }}>{unit}</span>
        </div>
      ) : (
        <span style={{ fontFamily: mono ? t.mono : t.font, fontSize: 13.5, color: t.text }}>{value}</span>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// PT CHART
// ─────────────────────────────────────────────────────────────
function CalcPT() {
  const t = _Tt();
  const rows = [
    { p: 100, t: 31.2 }, { p: 110, t: 35.5 }, { p: 118, t: 38.7, hl: true },
    { p: 130, t: 43.0 }, { p: 145, t: 48.4 }, { p: 160, t: 53.2 },
  ];
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="CALCULADORA" title="PT Chart" back right={<span style={{ fontFamily: t.mono, fontSize: 9.5, color: t.success, letterSpacing: '0.06em' }}>OFFLINE ✓</span>}/>
      <div style={{ flex: 1, padding: 16, overflow: 'hidden' }}>
        <CalcRow label="Refrigerante" value="R-410A" pill/>
        <div style={{ display: 'flex', gap: 8, marginTop: 14, marginBottom: 10 }}>
          <div style={{ flex: 1, padding: '10px 12px', background: t.accent, borderRadius: 9, color: '#001318', fontSize: 12, fontFamily: t.mono, fontWeight: 600, textAlign: 'center', letterSpacing: '0.04em' }}>PRESIÓN</div>
          <div style={{ flex: 1, padding: '10px 12px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 9, color: t.textMuted, fontSize: 12, fontFamily: t.mono, textAlign: 'center', letterSpacing: '0.04em' }}>TEMPERATURA</div>
        </div>
        <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', padding: '10px 14px', borderBottom: `1px solid ${t.border}`, background: t.bg }}>
            <span style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.08em' }}>PSI</span>
            <span style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.08em', textAlign: 'right' }}>°F</span>
          </div>
          {rows.map((r, idx) => (
            <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', padding: '12px 14px', borderBottom: idx < rows.length-1 ? `1px solid ${t.border}` : 'none', background: r.hl ? t.accentSoft : 'transparent' }}>
              <span style={{ fontFamily: t.mono, fontSize: 14, color: r.hl ? t.accent : t.text, fontWeight: r.hl ? 600 : 400 }}>{r.p.toFixed(1)}</span>
              <span style={{ fontFamily: t.mono, fontSize: 14, color: r.hl ? t.accent : t.text, fontWeight: r.hl ? 600 : 400, textAlign: 'right' }}>{r.t.toFixed(1)}</span>
            </div>
          ))}
        </div>
      </div>
      <window.TabBar active="tools"/>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// IMAGE DIAGNOSIS · CAPTURE
// ─────────────────────────────────────────────────────────────
function DiagCapture() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: '#000', color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* Camera preview */}
      <div style={{ flex: 1, position: 'relative', background: 'linear-gradient(180deg, #1a1d20 0%, #0a0d10 100%)', overflow: 'hidden' }}>
        {/* Simulated equipment in viewfinder */}
        <div style={{
          position: 'absolute', top: '30%', left: '15%', right: '15%', height: 160,
          background: 'linear-gradient(135deg, #2a2d30, #1a1d20)',
          borderRadius: 6, border: '2px solid #3a3d40',
          boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
        }}>
          <div style={{ position: 'absolute', top: 12, left: 12, width: 40, height: 14, background: '#0a0d10', borderRadius: 2 }}/>
          <div style={{ position: 'absolute', top: 12, right: 12, width: 8, height: 8, borderRadius: '50%', background: '#22C55E', boxShadow: '0 0 8px #22C55E' }}/>
        </div>

        {/* Top status bar */}
        <div style={{ position: 'absolute', top: 56, left: 16, right: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <window.Icons.x size={18} color="#fff"/>
          </div>
          <div style={{ padding: '8px 14px', borderRadius: 999, background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(10px)', fontFamily: t.mono, fontSize: 10.5, color: '#fff', letterSpacing: '0.06em' }}>
            ENCUADRAR EQUIPO
          </div>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: '#fff', fontSize: 16 }}>⚡</span>
          </div>
        </div>

        {/* Frame guide */}
        <div style={{ position: 'absolute', top: '24%', left: '8%', right: '8%', bottom: '32%', border: '1px dashed rgba(255,255,255,0.3)', borderRadius: 12 }}/>
        <Corner pos="tl"/><Corner pos="tr"/><Corner pos="bl"/><Corner pos="br"/>

        {/* Hint */}
        <div style={{ position: 'absolute', bottom: 30, left: 16, right: 16, padding: '12px 16px', background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(12px)', borderRadius: 12, color: '#fff', fontSize: 12.5, lineHeight: 1.4, textAlign: 'center' }}>
          Captura la <strong>placa de identificación</strong>, el componente con falla y el área completa.
        </div>
      </div>

      {/* Controls */}
      <div style={{ padding: '24px 16px 40px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'space-around' }}>
        <div style={{ width: 48, height: 48, borderRadius: 10, background: '#1a1d20', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <window.Icons.image size={20} color="#fff"/>
        </div>
        <div style={{ width: 76, height: 76, borderRadius: '50%', background: '#fff', border: '4px solid #000', boxShadow: '0 0 0 3px #fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}/>
        <div style={{ width: 48, height: 48, borderRadius: 10, background: '#1a1d20', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ color: '#fff', fontSize: 18 }}>↻</span>
        </div>
      </div>
    </div>
  );
}

function Corner({ pos }) {
  const t = _Tt();
  const styles = {
    tl: { top: '24%', left: '8%', borderTop: `2px solid ${t.accent}`, borderLeft: `2px solid ${t.accent}`, borderTopLeftRadius: 12 },
    tr: { top: '24%', right: '8%', borderTop: `2px solid ${t.accent}`, borderRight: `2px solid ${t.accent}`, borderTopRightRadius: 12 },
    bl: { bottom: '32%', left: '8%', borderBottom: `2px solid ${t.accent}`, borderLeft: `2px solid ${t.accent}`, borderBottomLeftRadius: 12 },
    br: { bottom: '32%', right: '8%', borderBottom: `2px solid ${t.accent}`, borderRight: `2px solid ${t.accent}`, borderBottomRightRadius: 12 },
  };
  return <div style={{ position: 'absolute', width: 22, height: 22, ...styles[pos] }}/>;
}

// ─────────────────────────────────────────────────────────────
// IMAGE DIAGNOSIS · ANALYZING
// ─────────────────────────────────────────────────────────────
function DiagAnalyzing() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="DIAGNÓSTICO IA" title="Analizando imagen…" back/>
      <div style={{ flex: 1, padding: 16, display: 'flex', flexDirection: 'column' }}>
        {/* Image preview */}
        <div style={{ aspectRatio: '4/3', borderRadius: 14, overflow: 'hidden', background: 'linear-gradient(135deg, #1a1d20, #0a0d10)', border: `1px solid ${t.border}`, position: 'relative', marginBottom: 18 }}>
          <div style={{ position: 'absolute', top: '30%', left: '15%', right: '15%', height: '50%', background: 'linear-gradient(135deg, #2a2d30, #1a1d20)', borderRadius: 6, border: '2px solid #3a3d40' }}>
            <div style={{ position: 'absolute', top: 8, left: 8, width: 28, height: 10, background: '#0a0d10', borderRadius: 2 }}/>
          </div>
          {/* Scanning overlay */}
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '100%', background: `linear-gradient(180deg, transparent 0%, ${t.accent}40 50%, transparent 100%)`, animation: 'cgScan 2s linear infinite' }}/>
          <div style={{ position: 'absolute', top: 12, left: 12, padding: '6px 10px', borderRadius: 6, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)', fontFamily: t.mono, fontSize: 10, color: t.accent, letterSpacing: '0.06em' }}>
            ESCANEANDO…
          </div>
        </div>

        {/* Steps */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <DiagStep done label="Detectando equipo y componentes"/>
          <DiagStep done label="Identificando placa de identificación"/>
          <DiagStep active label="Comparando con base técnica RAG"/>
          <DiagStep label="Generando diagnóstico"/>
        </div>

        <div style={{ marginTop: 'auto', padding: '12px 14px', background: t.warningSoft, border: `1px solid ${t.warning}40`, borderRadius: 10, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
          <span style={{ fontSize: 16 }}>⚠</span>
          <div style={{ fontSize: 12, color: t.warning, lineHeight: 1.45 }}>
            No manipules el equipo energizado mientras esperas. Usa EPP si vas a operar.
          </div>
        </div>
      </div>
    </div>
  );
}

function DiagStep({ done, active, label }) {
  const t = _Tt();
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{
        width: 22, height: 22, borderRadius: '50%',
        background: done ? t.success : active ? t.accentSoft : 'transparent',
        border: `1.5px solid ${done ? t.success : active ? t.accent : t.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {done && <window.Icons.check size={12} color="#001318" stroke={2.5}/>}
        {active && <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.accent, animation: 'cgPulse 1s infinite' }}/>}
      </div>
      <div style={{ fontSize: 13.5, color: done ? t.textMuted : active ? t.text : t.textDim, fontWeight: active ? 500 : 400 }}>{label}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// IMAGE DIAGNOSIS · RESULT
// ─────────────────────────────────────────────────────────────
function DiagResult() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="DIAGNÓSTICO" title="Resultado" back right={
        <span style={{ fontFamily: t.mono, fontSize: 10, color: t.accent, letterSpacing: '0.06em' }}>78% CONF.</span>
      }/>
      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden' }}>
        <div style={{ aspectRatio: '16/9', borderRadius: 12, overflow: 'hidden', background: 'linear-gradient(135deg, #1a1d20, #0a0d10)', border: `1px solid ${t.border}`, position: 'relative', marginBottom: 14 }}>
          <div style={{ position: 'absolute', top: '30%', left: '20%', width: '50%', height: '45%', background: '#2a2d30', borderRadius: 4, border: '2px solid #3a3d40' }}/>
          {/* Annotation pin */}
          <div style={{ position: 'absolute', top: '35%', left: '35%', width: 24, height: 24, borderRadius: '50%', background: t.accent, border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#001318', fontSize: 11, fontWeight: 700, fontFamily: t.mono }}>1</div>
          <div style={{ position: 'absolute', top: '60%', left: '55%', width: 24, height: 24, borderRadius: '50%', background: t.warning, border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0a0d10', fontSize: 11, fontWeight: 700, fontFamily: t.mono }}>2</div>
        </div>

        {/* Findings */}
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8 }}>HALLAZGOS</div>
        <Finding num={1} color={t.accent} title="Escarcha en línea de succión" body="Indica baja carga de refrigerante o bloqueo en filtro."/>
        <Finding num={2} color={t.warning} title="Conexión eléctrica con corrosión" body="Puede causar caídas de voltaje intermitentes."/>

        <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
          <button style={{ flex: 1, height: 42, borderRadius: 10, border: 'none', background: t.accent, color: '#001318', fontWeight: 600, fontSize: 13, fontFamily: t.font }}>Crear caso técnico</button>
          <button style={{ height: 42, padding: '0 14px', borderRadius: 10, background: 'transparent', border: `1px solid ${t.border}`, color: t.text, fontSize: 13 }}>Pasos →</button>
        </div>
      </div>
    </div>
  );
}

function Finding({ num, color, title, body }) {
  const t = _Tt();
  return (
    <div style={{ display: 'flex', gap: 10, padding: '10px 0', borderBottom: `1px solid ${t.border}` }}>
      <div style={{ width: 22, height: 22, borderRadius: '50%', background: color, color: '#001318', fontFamily: t.mono, fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 2 }}>{num}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13.5, fontWeight: 500, color: t.text, marginBottom: 2 }}>{title}</div>
        <div style={{ fontSize: 12.5, color: t.textMuted, lineHeight: 1.45 }}>{body}</div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// CODE DETAIL
// ─────────────────────────────────────────────────────────────
function CodeDetail() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="CARRIER · 38AKS" title="E1 · Alta presión" back right={
        <div style={{ padding: '4px 10px', borderRadius: 999, background: t.errorSoft, color: t.error, fontFamily: t.mono, fontSize: 10, letterSpacing: '0.06em' }}>CRÍTICO</div>
      }/>
      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden' }}>
        <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 12, padding: 14, marginBottom: 14 }}>
          <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>DESCRIPCIÓN</div>
          <div style={{ fontSize: 13.5, color: t.text, lineHeight: 1.5 }}>
            Detención por presión alta en el lado de descarga. El presostato HP abrió arriba de 425 psi.
          </div>
        </div>

        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.08em', marginBottom: 8 }}>CAUSAS PROBABLES</div>
        {['Condensador sucio o ventilador parado', 'Sobrecarga de refrigerante', 'No-condensables en el sistema', 'Tubería de descarga obstruida'].map((c, i) => (
          <div key={i} style={{ display: 'flex', gap: 10, padding: '10px 0', borderBottom: `1px solid ${t.border}` }}>
            <span style={{ fontFamily: t.mono, fontSize: 11, color: t.textDim, marginTop: 2 }}>{String(i+1).padStart(2,'0')}</span>
            <span style={{ flex: 1, fontSize: 13.5, color: t.text, lineHeight: 1.45 }}>{c}</span>
          </div>
        ))}

        <div style={{ marginTop: 14, padding: 12, background: t.accentSoft, borderRadius: 10, fontSize: 12, color: t.text, lineHeight: 1.45 }}>
          <strong style={{ color: t.accent, fontFamily: t.mono, fontSize: 10.5, letterSpacing: '0.06em' }}>FUENTE · </strong>
          Carrier 38AKS Service Manual, p. 47 (rev. 2022).
        </div>

        <button style={{ width: '100%', marginTop: 14, height: 46, borderRadius: 11, border: 'none', background: t.accent, color: '#001318', fontWeight: 600, fontSize: 13.5, fontFamily: t.font }}>
          Crear caso desde este código
        </button>
      </div>
      <window.TabBar active="codes"/>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// GUIDE DETAIL · CHECKLIST
// ─────────────────────────────────────────────────────────────
function GuideDetail() {
  const t = _Tt();
  const steps = [
    { done: true, title: 'Cortar energía', body: 'Bloqueo y etiquetado (LOTO).' },
    { done: true, title: 'Verificar ausencia de tensión', body: 'Multímetro en escala adecuada.' },
    { done: false, active: true, title: 'Recuperar refrigerante', body: 'Usar máquina certificada. No venteo.' },
    { done: false, title: 'Aislar componente con falla', body: 'Cierre de válvulas y purga.' },
    { done: false, title: 'Reemplazar componente', body: 'Torque según fabricante.' },
    { done: false, title: 'Vacío y prueba de fuga', body: '500 micrones · 30 min.' },
  ];
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="GUÍA · 6 PASOS" title="Reemplazo de compresor" back right={
        <span style={{ fontFamily: t.mono, fontSize: 10, color: t.success, letterSpacing: '0.06em' }}>OFFLINE ✓</span>
      }/>
      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden' }}>
        {/* Progress */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
          <div style={{ flex: 1, height: 4, background: t.surface, borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ width: '33%', height: '100%', background: t.accent }}/>
          </div>
          <span style={{ fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.04em' }}>2 / 6</span>
        </div>

        {/* EPP strip */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 14, overflowX: 'hidden' }}>
          {['Guantes', 'Lentes', 'LOTO', 'Máquina recup.'].map(p => (
            <div key={p} style={{ padding: '6px 10px', borderRadius: 999, background: t.surface, border: `1px solid ${t.border}`, fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.04em', whiteSpace: 'nowrap' }}>{p}</div>
          ))}
        </div>

        {/* Steps */}
        {steps.map((s, i) => (
          <div key={i} style={{ display: 'flex', gap: 12, padding: '12px 0', borderBottom: `1px solid ${t.border}` }}>
            <div style={{
              width: 22, height: 22, borderRadius: 5,
              background: s.done ? t.success : s.active ? t.accent : 'transparent',
              border: `1.5px solid ${s.done ? t.success : s.active ? t.accent : t.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 1,
            }}>
              {s.done && <window.Icons.check size={12} color="#001318" stroke={2.5}/>}
            </div>
            <div style={{ flex: 1, opacity: s.done ? 0.5 : 1 }}>
              <div style={{ fontSize: 14, fontWeight: s.active ? 600 : 500, color: s.active ? t.accent : t.text, marginBottom: 2, textDecoration: s.done ? 'line-through' : 'none' }}>{s.title}</div>
              <div style={{ fontSize: 12.5, color: t.textMuted, lineHeight: 1.4 }}>{s.body}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// OFFLINE STATE
// ─────────────────────────────────────────────────────────────
function OfflineGlobal() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: 56, paddingLeft: 16, paddingRight: 16, paddingBottom: 14, background: t.warningSoft, borderBottom: `1px solid ${t.warning}40` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: t.warning }}/>
          <span style={{ fontFamily: t.mono, fontSize: 11, color: t.warning, letterSpacing: '0.08em' }}>SIN CONEXIÓN · ÚLTIMA SYNC HACE 2 H</span>
        </div>
        <div style={{ fontSize: 19, fontWeight: 600, letterSpacing: '-0.02em', color: t.text }}>Modo offline activo</div>
      </div>

      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden' }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.success, letterSpacing: '0.08em', marginBottom: 8 }}>✓ DISPONIBLE OFFLINE</div>
        <OffRow ok label="Calculadoras" sub="Superheat, subcooling, PT, conversor"/>
        <OffRow ok label="Códigos sincronizados" sub="2 482 códigos · 8 fabricantes"/>
        <OffRow ok label="Guías descargadas" sub="14 procedimientos"/>
        <OffRow ok label="Casos recientes" sub="Solo lectura"/>

        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.warning, letterSpacing: '0.08em', marginTop: 18, marginBottom: 8 }}>✕ REQUIERE CONEXIÓN</div>
        <OffRow label="Chat con Coolpanion" sub="Streaming, RAG, contexto del caso"/>
        <OffRow label="Diagnóstico por imagen" sub="Análisis IA en backend"/>
        <OffRow label="Sincronizar casos nuevos" sub="3 cambios pendientes"/>

        <div style={{ marginTop: 16, padding: '12px 14px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 11, display: 'flex', alignItems: 'center', gap: 10 }}>
          <window.Icons.refresh size={16} color={t.accent}/>
          <div style={{ flex: 1, fontSize: 13, color: t.text }}>Reintentar conexión</div>
          <window.Icons.chevRight size={14} color={t.textDim}/>
        </div>
      </div>

      <window.TabBar active="home"/>
    </div>
  );
}

function OffRow({ ok, label, sub }) {
  const t = _Tt();
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: `1px solid ${t.border}` }}>
      <div style={{ width: 22, height: 22, borderRadius: 6, background: ok ? `${t.success}20` : `${t.error}20`, border: `1px solid ${ok ? t.success : t.error}40`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <span style={{ color: ok ? t.success : t.error, fontSize: 12, fontWeight: 700 }}>{ok ? '✓' : '✕'}</span>
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13.5, color: t.text, fontWeight: 500 }}>{label}</div>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.02em', marginTop: 2 }}>{sub}</div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// CASE EXTRAS · Empty case + Out-of-domain
// ─────────────────────────────────────────────────────────────
function CaseEmptyChat() {
  const t = _Tt();
  const prompts = [
    'Mi nevera no enfría, ¿qué reviso primero?',
    '¿Qué significa este código de error?',
    '¿Cómo diagnostico baja presión de succión?',
    '¿Qué reviso en un split que congela la tubería?',
  ];
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="C-0042 · ABIERTO" title="Carrier 38AKS no enfría" back/>
      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '20px 8px' }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: t.accentSoft, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
            <window.Icons.bolt size={26} color={t.accent}/>
          </div>
          <div style={{ fontSize: 17, fontWeight: 600, letterSpacing: '-0.02em', marginBottom: 6 }}>Empieza por aquí</div>
          <div style={{ fontSize: 13, color: t.textMuted, lineHeight: 1.45, maxWidth: 240 }}>Describe el síntoma o elige una pregunta sugerida.</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
          {prompts.map((p, i) => (
            <div key={i} style={{ padding: '12px 14px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 11, fontSize: 13, color: t.text, lineHeight: 1.4 }}>
              {p}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 999 }}>
          <input placeholder="Pregunta a Coolpanion…" style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: t.text, fontSize: 13, fontFamily: t.font }}/>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: t.accent, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: '#001318', fontSize: 14 }}>↑</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CaseOutOfDomain() {
  const t = _Tt();
  return (
    <div style={{ width: '100%', height: '100%', background: t.bg, color: t.text, fontFamily: t.font, display: 'flex', flexDirection: 'column' }}>
      <ScrHeader sub="C-0042 · ABIERTO" title="Carrier 38AKS no enfría" back/>
      <div style={{ flex: 1, padding: '14px 16px', overflow: 'hidden', display: 'flex', flexDirection: 'column', gap: 14 }}>
        {/* User message */}
        <div style={{ alignSelf: 'flex-end', maxWidth: '78%', padding: '10px 14px', background: t.accentSoft, color: t.text, borderRadius: '14px 14px 4px 14px', fontSize: 13, lineHeight: 1.4 }}>
          ¿Cuál es la receta de pasta carbonara?
        </div>

        {/* Block */}
        <div style={{ alignSelf: 'flex-start', maxWidth: '88%', padding: 14, background: t.warningSoft, border: `1px solid ${t.warning}40`, borderRadius: '4px 14px 14px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 14 }}>⚠</span>
            <span style={{ fontFamily: t.mono, fontSize: 10.5, color: t.warning, letterSpacing: '0.08em' }}>FUERA DE DOMINIO</span>
          </div>
          <div style={{ fontSize: 13, color: t.text, lineHeight: 1.5, marginBottom: 10 }}>
            Coolpanion solo te ayuda con <strong>refrigeración y climatización</strong>: equipos, fallas, refrigerantes, eléctrica aplicada, controles y mantenimiento.
          </div>
          <div style={{ fontSize: 12.5, color: t.textMuted, lineHeight: 1.45 }}>
            Reformula la consulta como un problema técnico — por ejemplo, una falla, código de error o medición que estés viendo.
          </div>
        </div>

        <div style={{ marginTop: 'auto' }}>
          <div style={{ fontFamily: t.mono, fontSize: 10, color: t.textDim, letterSpacing: '0.08em', marginBottom: 6 }}>SUGERIDO</div>
          <div style={{ padding: '10px 14px', background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, fontSize: 13, color: t.text }}>
            ¿Qué reviso si el equipo no enfría tras un mantenimiento?
          </div>
        </div>
      </div>
    </div>
  );
}

window.ToolsHub = ToolsHub;
window.CalcSuperheat = CalcSuperheat;
window.CalcPT = CalcPT;
window.DiagCapture = DiagCapture;
window.DiagAnalyzing = DiagAnalyzing;
window.DiagResult = DiagResult;
window.CodeDetail = CodeDetail;
window.GuideDetail = GuideDetail;
window.OfflineGlobal = OfflineGlobal;
window.CaseEmptyChat = CaseEmptyChat;
window.CaseOutOfDomain = CaseOutOfDomain;
