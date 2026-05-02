// Splash screens — 3 directions
// Each one is a static screen meant to live inside an IOSDevice frame.

function SplashClean() {
  const t = window.DIRECTIONS.clean;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      padding: '120px 32px 48px', boxSizing: 'border-box',
    }}>
      {/* Logo lockup */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 64 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8, background: t.text,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: t.bg, fontWeight: 700, fontSize: 16, fontFamily: t.mono,
          letterSpacing: '-0.02em',
        }}>C</div>
        <div style={{ fontSize: 17, fontWeight: 600, letterSpacing: '-0.02em' }}>CoolAgent</div>
        <div style={{
          marginLeft: 'auto', fontFamily: t.mono, fontSize: 11,
          color: t.textDim, letterSpacing: '0.04em',
        }}>v0.1 · BETA</div>
      </div>

      {/* Hero */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{
          fontSize: 11, fontFamily: t.mono, color: t.textMuted,
          letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 16,
        }}>Asistente técnico · HVAC/R</div>
        <div style={{
          fontSize: 38, lineHeight: 1.05, fontWeight: 500,
          letterSpacing: '-0.03em', color: t.text, marginBottom: 18,
        }}>
          Diagnóstico de campo,<br/>
          <span style={{ color: t.textMuted }}>respaldado por manuales reales.</span>
        </div>
        <div style={{ fontSize: 15, lineHeight: 1.45, color: t.textMuted, maxWidth: 320 }}>
          Casos técnicos, códigos de error y consulta directa a Claude Haiku con contexto RAG sobre tu equipo.
        </div>
      </div>

      {/* Spec strip */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 0,
        borderTop: `1px solid ${t.border}`, paddingTop: 16, marginBottom: 28,
        fontFamily: t.mono, fontSize: 10, letterSpacing: '0.06em',
        textTransform: 'uppercase', color: t.textDim,
      }}>
        <div><div style={{ color: t.text, fontSize: 13, fontFamily: t.font, fontWeight: 600, marginBottom: 2, textTransform: 'none', letterSpacing: '-0.01em' }}>RAG</div>contexto</div>
        <div><div style={{ color: t.text, fontSize: 13, fontFamily: t.font, fontWeight: 600, marginBottom: 2, textTransform: 'none', letterSpacing: '-0.01em' }}>Stream</div>en vivo</div>
        <div><div style={{ color: t.text, fontSize: 13, fontFamily: t.font, fontWeight: 600, marginBottom: 2, textTransform: 'none', letterSpacing: '-0.01em' }}>Casos</div>persistentes</div>
      </div>

      {/* CTAs */}
      <button style={{
        width: '100%', height: 52, borderRadius: 12, border: 'none',
        background: t.text, color: t.bg, fontFamily: t.font, fontSize: 15,
        fontWeight: 600, letterSpacing: '-0.01em', marginBottom: 10,
      }}>Comenzar</button>
      <button style={{
        width: '100%', height: 52, borderRadius: 12,
        background: 'transparent', color: t.text, border: `1px solid ${t.border}`,
        fontFamily: t.font, fontSize: 15, fontWeight: 500, letterSpacing: '-0.01em',
      }}>Continuar como invitado</button>

      <div style={{
        textAlign: 'center', fontSize: 11, color: t.textDim, marginTop: 18,
        fontFamily: t.mono, letterSpacing: '0.04em',
      }}>Refrigeración · Aire · Cadena de frío</div>
    </div>
  );
}

function SplashDark() {
  const t = window.DIRECTIONS.dark;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, position: 'relative', overflow: 'hidden',
      display: 'flex', flexDirection: 'column',
      padding: '110px 28px 44px', boxSizing: 'border-box',
    }}>
      {/* subtle radial */}
      <div style={{
        position: 'absolute', top: -120, left: -60, width: 320, height: 320,
        borderRadius: '50%', background: `radial-gradient(circle at center, ${t.accentSoft}, transparent 70%)`,
        filter: 'blur(20px)', pointerEvents: 'none',
      }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 56, position: 'relative' }}>
        <div style={{
          width: 30, height: 30, borderRadius: 7,
          background: `linear-gradient(135deg, ${t.accent}, #2BA4C0)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#001318', fontWeight: 700, fontSize: 14, fontFamily: t.mono,
        }}>C</div>
        <div style={{ fontSize: 16, fontWeight: 600, letterSpacing: '-0.02em' }}>Coolpanion</div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative' }}>
        {/* status pill */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 12px', borderRadius: 999,
          background: t.accentSoft, border: `1px solid ${t.borderStrong}`,
          fontSize: 11, fontFamily: t.mono, color: t.accent,
          letterSpacing: '0.04em', alignSelf: 'flex-start', marginBottom: 22,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.accent, boxShadow: `0 0 8px ${t.accent}` }} />
          MOTOR · CLAUDE HAIKU 4.5
        </div>

        <div style={{
          fontSize: 40, lineHeight: 1.02, fontWeight: 500,
          letterSpacing: '-0.035em', marginBottom: 18,
        }}>
          Tu copiloto<br/>en el taller.
        </div>
        <div style={{ fontSize: 15, lineHeight: 1.5, color: t.textMuted, maxWidth: 310 }}>
          Pregunta, adjunta foto, recibe diagnóstico con citas a manuales del fabricante. Sin esperar al supervisor.
        </div>
      </div>

      {/* equipment strip */}
      <div style={{
        display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap',
      }}>
        {['Carrier', 'Trane', 'Daikin', 'Copeland', 'Bitzer', '+3'].map((b, i) => (
          <span key={i} style={{
            padding: '5px 10px', borderRadius: 6,
            background: t.surface, border: `1px solid ${t.border}`,
            fontFamily: t.mono, fontSize: 10.5, color: t.textMuted,
            letterSpacing: '0.02em',
          }}>{b}</span>
        ))}
      </div>

      <button style={{
        width: '100%', height: 54, borderRadius: 14, border: 'none',
        background: t.accent, color: '#001318', fontFamily: t.font,
        fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em', marginBottom: 10,
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
      }}>
        Iniciar sesión
        <window.Icons.arrowUp size={16} color="#001318" stroke={2} />
      </button>
      <div style={{
        textAlign: 'center', fontSize: 12, color: t.textDim, fontFamily: t.mono,
        letterSpacing: '0.04em',
      }}>NUEVO AQUÍ? · <span style={{ color: t.accent }}>CREAR CUENTA</span></div>
    </div>
  );
}

function SplashMono() {
  const t = window.DIRECTIONS.mono;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      padding: '110px 30px 44px', boxSizing: 'border-box',
      position: 'relative',
    }}>
      {/* paper noise via subtle pattern */}
      <div style={{
        position: 'absolute', inset: 0, opacity: 0.4, pointerEvents: 'none',
        background: 'radial-gradient(circle at 20% 30%, rgba(0,0,0,0.02), transparent 50%), radial-gradient(circle at 80% 70%, rgba(0,0,0,0.025), transparent 50%)',
      }} />

      {/* Header rule */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        borderBottom: `1px solid ${t.borderStrong}`, paddingBottom: 10, marginBottom: 40,
        fontFamily: t.mono, fontSize: 10.5, letterSpacing: '0.08em',
        textTransform: 'uppercase', color: t.textMuted,
      }}>
        <span>CoolAgent · Manual del Operador</span>
        <span>Ed. 01 / 2026</span>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative' }}>
        <div style={{
          fontFamily: t.mono, fontSize: 11, letterSpacing: '0.16em',
          textTransform: 'uppercase', color: t.textMuted, marginBottom: 20,
        }}>§ 0.1 · Bienvenida</div>

        <div style={{
          fontSize: 44, lineHeight: 1.02, fontWeight: 500,
          letterSpacing: '-0.025em', marginBottom: 22, fontStyle: 'italic',
        }}>
          Refrigeración<br/>
          razonada.
        </div>

        <div style={{
          fontSize: 15.5, lineHeight: 1.55, color: t.textMuted,
          maxWidth: 320, marginBottom: 32,
        }}>
          Un asistente que <em style={{ color: t.text }}>cita la fuente</em>. Cada respuesta lleva referencia al manual, hoja de fallas o boletín técnico de donde se obtuvo.
        </div>

        {/* Footnote-style features */}
        <div style={{
          fontFamily: t.mono, fontSize: 11, color: t.textMuted, lineHeight: 1.8,
          borderLeft: `2px solid ${t.text}`, paddingLeft: 12,
        }}>
          <div><sup>1</sup> Diagnóstico por chat con streaming</div>
          <div><sup>2</sup> Citas verificables a documentos fuente</div>
          <div><sup>3</sup> Casos técnicos persistentes por equipo</div>
        </div>
      </div>

      <button style={{
        width: '100%', height: 56, borderRadius: 0, border: `1.5px solid ${t.text}`,
        background: t.text, color: t.bg, fontFamily: t.font, fontSize: 16,
        fontWeight: 500, letterSpacing: '-0.01em', marginBottom: 12,
        fontStyle: 'italic',
      }}>Abrir manual →</button>

      <div style={{
        display: 'flex', justifyContent: 'space-between',
        fontFamily: t.mono, fontSize: 10, color: t.textDim,
        letterSpacing: '0.06em', textTransform: 'uppercase',
      }}>
        <span>p. 1 / 248</span>
        <span>HVAC/R · ES</span>
      </div>
    </div>
  );
}

window.SplashClean = SplashClean;
window.SplashDark = SplashDark;
window.SplashMono = SplashMono;
