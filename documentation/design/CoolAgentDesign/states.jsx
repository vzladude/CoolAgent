// Empty / Loading / Error states — one per direction

function EmptyClean() {
  const t = window.DIRECTIONS.clean;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      paddingTop: 56,
    }}>
      <div style={{ padding: '12px 16px 16px', borderBottom: `1px solid ${t.border}` }}>
        <div style={{ fontSize: 11, fontFamily: t.mono, color: t.textDim, letterSpacing: '0.06em', marginBottom: 4 }}>NUEVO CASO</div>
        <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.025em' }}>¿Qué equipo necesita revisión?</div>
      </div>

      <div style={{ flex: 1, padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ fontSize: 11, fontFamily: t.mono, color: t.textDim, letterSpacing: '0.08em', marginBottom: 4, textTransform: 'uppercase' }}>Sugerido</div>
        {[
          { t: 'Diagnosticar fuga de refrigerante', s: 'R-410A · Split residencial' },
          { t: 'Interpretar código de error', s: 'Carrier · Trane · Daikin' },
          { t: 'Verificar carga del sistema', s: 'Procedimiento subcooling' },
        ].map((s, i) => (
          <button key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '14px 14px', background: t.surface, border: `1px solid ${t.border}`,
            borderRadius: 12, textAlign: 'left', cursor: 'pointer',
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8, background: t.surfaceAlt,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <window.Icons.spark size={16} color={t.text} stroke={1.5}/>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14.5, fontWeight: 500, color: t.text, marginBottom: 2 }}>{s.t}</div>
              <div style={{ fontSize: 12, color: t.textMuted, fontFamily: t.mono }}>{s.s}</div>
            </div>
            <window.Icons.chevRight size={16} color={t.textDim}/>
          </button>
        ))}
      </div>

      <div style={{ padding: '10px 12px 36px' }}>
        <div style={{
          background: t.surface, borderRadius: 18, border: `1px solid ${t.border}`,
          padding: '14px 14px', display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <div style={{ flex: 1, fontSize: 15, color: t.textDim }}>O describe el problema…</div>
          <button style={{
            width: 36, height: 36, borderRadius: 12,
            background: t.surfaceAlt, border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}><window.Icons.arrowUp size={18} color={t.textDim}/></button>
        </div>
      </div>
    </div>
  );
}

function LoadingDark() {
  const t = window.DIRECTIONS.dark;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      paddingTop: 56,
    }}>
      <div style={{ padding: '12px 16px 14px', borderBottom: `1px solid ${t.border}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <button style={{ width: 36, height: 36, borderRadius: 10, background: 'transparent', border: `1px solid ${t.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <window.Icons.chevLeft size={18} color={t.text}/>
          </button>
          <div style={{ fontSize: 11, fontFamily: t.mono, color: t.accent, letterSpacing: '0.08em', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: 1, background: t.accent, animation: 'cgPulse 1s infinite' }}/>
            CONECTANDO
          </div>
          <div style={{ width: 36 }}/>
        </div>
        <div style={{ fontSize: 19, fontWeight: 600, letterSpacing: '-0.02em' }}>Carrier 38AKS no enfría</div>
      </div>

      <div style={{ flex: 1, padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textDim, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Pipeline</div>
        {[
          { l: 'Domain guard', s: 'ok' },
          { l: 'Recuperando contexto del caso', s: 'ok' },
          { l: 'Búsqueda RAG · 3/3 docs', s: 'ok' },
          { l: 'Cache lookup', s: 'miss' },
          { l: 'Claude Haiku 4.5', s: 'streaming' },
        ].map((s, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '12px 14px', background: t.surface,
            border: `1px solid ${t.border}`, borderRadius: 10,
          }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%',
              background: s.s === 'streaming' ? t.accent : s.s === 'miss' ? t.warn : t.success,
              boxShadow: s.s === 'streaming' ? `0 0 8px ${t.accent}` : 'none',
              animation: s.s === 'streaming' ? 'cgPulse 1s infinite' : 'none',
            }}/>
            <div style={{ flex: 1, fontSize: 14, color: t.text }}>{s.l}</div>
            <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.08em', textTransform: 'uppercase' }}>{s.s}</div>
          </div>
        ))}
        <div style={{
          marginTop: 8, fontFamily: t.mono, fontSize: 11, color: t.textDim,
          letterSpacing: '0.04em', textAlign: 'center',
        }}>~2.4s · 1,240 tokens contexto</div>
      </div>
    </div>
  );
}

function ErrorMono() {
  const t = window.DIRECTIONS.mono;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      paddingTop: 56,
    }}>
      <div style={{ padding: '12px 18px 14px', borderBottom: `1.5px solid ${t.text}` }}>
        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.08em' }}>ERR · CONEXIÓN INTERRUMPIDA</div>
        <div style={{ fontSize: 22, fontWeight: 500, letterSpacing: '-0.02em', fontStyle: 'italic', marginTop: 4 }}>
          Sin servicio.
        </div>
      </div>

      <div style={{ flex: 1, padding: '24px 18px', display: 'flex', flexDirection: 'column' }}>
        <div style={{
          borderLeft: `3px solid ${t.danger}`, paddingLeft: 12, marginBottom: 24,
        }}>
          <div style={{ fontFamily: t.mono, fontSize: 11, color: t.danger, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>Aviso técnico</div>
          <div style={{ fontSize: 15, lineHeight: 1.55, color: t.text }}>
            No fue posible alcanzar el servidor de inferencia. El último intento fue a las <span style={{ fontFamily: t.mono }}>14:33:02</span>.
          </div>
        </div>

        <div style={{ fontFamily: t.mono, fontSize: 10.5, color: t.textMuted, letterSpacing: '0.1em', marginBottom: 8, textTransform: 'uppercase' }}>Disponible offline</div>
        <div style={{
          background: t.surface, border: `1px solid ${t.borderStrong}`,
          padding: 14, marginBottom: 16,
        }}>
          {[
            'Códigos de error (8 fabricantes, sincronizado hace 2 días)',
            'Último caso técnico: Carrier 38AKS no enfría',
            'Resumen del caso (compactado por Claude)',
          ].map((s, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, fontSize: 13.5, lineHeight: 1.6, color: t.text }}>
              <span style={{ color: t.textMuted, fontFamily: t.mono }}>—</span>
              <span style={{ flex: 1 }}>{s}</span>
            </div>
          ))}
        </div>

        <button style={{
          width: '100%', height: 50, border: `1.5px solid ${t.text}`,
          background: t.text, color: t.bg, fontFamily: t.font, fontSize: 14.5,
          fontWeight: 500, fontStyle: 'italic', letterSpacing: '-0.01em',
          marginBottom: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>
          <window.Icons.refresh size={15} color={t.bg}/>
          Reintentar conexión
        </button>
        <button style={{
          width: '100%', height: 50, border: `1.5px solid ${t.text}`,
          background: 'transparent', color: t.text, fontFamily: t.font, fontSize: 14.5,
          fontWeight: 500, fontStyle: 'italic', letterSpacing: '-0.01em',
        }}>
          Trabajar offline
        </button>
      </div>
    </div>
  );
}

window.EmptyClean = EmptyClean;
window.LoadingDark = LoadingDark;
window.ErrorMono = ErrorMono;
