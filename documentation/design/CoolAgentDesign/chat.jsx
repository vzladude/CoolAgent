// Chat screens — 3 directions. Streaming active state with RAG citations.

// --- Shared sample data ---
const SAMPLE_CASE = {
  title: 'Carrier 38AKS no enfría',
  manufacturer: 'Carrier',
  model: '38AKS-024',
  category: 'Aire acondicionado · Split',
  status: 'open',
};

const SAMPLE_MESSAGES = [
  { role: 'user', content: 'El equipo prende, ventila normal pero no baja la temperatura. Hace 30 min que está corriendo.' },
  {
    role: 'assistant',
    content: 'Síntoma compatible con falla de circuito de refrigerante. Antes de abrir, verifica en este orden:',
    list: [
      'Presión de baja: debería estar entre 60–75 psi con R-410A.',
      'Amperaje del compresor vs. placa (RLA).',
      'Diferencial de temperatura aire entrada/salida del evaporador (∆T esperado: 8–11 °C).',
    ],
    citations: [
      { id: 1, doc: 'Carrier 38AKS Service Manual', page: 'p. 42', section: '§ 4.3 Troubleshooting' },
    ],
  },
  { role: 'user', content: '∆T me da 3°C. Baja presión 35 psi.' },
];

// Streaming-in-progress message (used as the last bubble)
const STREAMING_TEXT = 'Esos valores indican carga insuficiente de refrigerante o restricción en la línea de líquido. Antes de cargar, descarta:';

// =============================================================
// CLEAN LIGHT
// =============================================================
function ChatClean() {
  const t = window.DIRECTIONS.clean;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{
        paddingTop: 56, paddingBottom: 12, paddingLeft: 16, paddingRight: 16,
        background: t.bg,
        borderBottom: `1px solid ${t.border}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <button style={iconBtn(t)}><window.Icons.chevLeft size={18} color={t.text} /></button>
          <div style={{
            fontSize: 11, fontFamily: t.mono, color: t.textDim, letterSpacing: '0.06em', textTransform: 'uppercase',
          }}>Caso #C-0042</div>
          <button style={iconBtn(t)}><window.Icons.more size={18} color={t.text} /></button>
        </div>
        <div style={{ fontSize: 17, fontWeight: 600, letterSpacing: '-0.02em', marginBottom: 6 }}>
          {SAMPLE_CASE.title}
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
          <Chip t={t} mono>{SAMPLE_CASE.manufacturer}</Chip>
          <Chip t={t} mono>{SAMPLE_CASE.model}</Chip>
          <Chip t={t}>Split</Chip>
          <span style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11, fontFamily: t.mono, color: t.success, letterSpacing: '0.04em' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.success }}/>ABIERTO
          </span>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'hidden', padding: '16px 16px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <UserBubbleClean t={t}>{SAMPLE_MESSAGES[0].content}</UserBubbleClean>
        <AssistantBubbleClean t={t} m={SAMPLE_MESSAGES[1]} />
        <UserBubbleClean t={t}>{SAMPLE_MESSAGES[2].content}</UserBubbleClean>
        <StreamingBubbleClean t={t} />
      </div>

      {/* Composer */}
      <div style={{
        padding: '10px 12px 14px', background: t.bg,
        borderTop: `1px solid ${t.border}`,
      }}>
        <div style={{
          background: t.surface, borderRadius: 18, border: `1px solid ${t.border}`,
          padding: '10px 10px 8px 14px', display: 'flex', flexDirection: 'column', gap: 8,
          boxShadow: '0 1px 0 rgba(20,22,28,0.02)',
        }}>
          <div style={{ fontSize: 15, color: t.textDim }}>Pregunta o describe el síntoma…</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <button style={iconBtn(t, true)}><window.Icons.attach size={16} color={t.textMuted}/></button>
            <button style={iconBtn(t, true)}><window.Icons.camera size={16} color={t.textMuted}/></button>
            <div style={{
              marginLeft: 6, fontSize: 11, fontFamily: t.mono,
              color: t.textDim, letterSpacing: '0.04em',
            }}>RAG · 3 docs activos</div>
            <button style={{
              marginLeft: 'auto', width: 36, height: 36, borderRadius: 12,
              background: t.text, color: t.bg, border: 'none',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}><window.Icons.arrowUp size={18} color={t.bg} stroke={2.2}/></button>
          </div>
        </div>
        <div style={{ height: 22 }}/>
      </div>
    </div>
  );
}

function Chip({ t, mono, children }) {
  return (
    <span style={{
      padding: '3px 8px', borderRadius: 6, background: t.chipBg,
      fontFamily: mono ? t.mono : t.font, fontSize: mono ? 11 : 12,
      color: t.textMuted, letterSpacing: mono ? '0.02em' : 0,
    }}>{children}</span>
  );
}

function iconBtn(t, ghost) {
  return {
    width: 36, height: 36, borderRadius: 10,
    background: ghost ? 'transparent' : 'transparent',
    border: ghost ? 'none' : `1px solid ${t.border}`,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', padding: 0,
  };
}

function UserBubbleClean({ t, children }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
      <div style={{
        maxWidth: '78%', background: t.text, color: t.bg,
        padding: '10px 14px', borderRadius: '18px 18px 4px 18px',
        fontSize: 14.5, lineHeight: 1.4, letterSpacing: '-0.005em',
      }}>{children}</div>
    </div>
  );
}

function AssistantBubbleClean({ t, m }) {
  return (
    <div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6,
        fontSize: 11, fontFamily: t.mono, color: t.textDim, letterSpacing: '0.04em',
      }}>
        <span style={{ width: 16, height: 16, borderRadius: 4, background: t.text, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: t.bg, fontSize: 10, fontWeight: 700 }}>C</span>
        COOLAGENT
      </div>
      <div style={{ fontSize: 14.5, lineHeight: 1.5, color: t.text, marginBottom: 8, letterSpacing: '-0.005em' }}>
        {m.content}
      </div>
      {m.list && (
        <ol style={{ margin: '0 0 10px', paddingLeft: 0, listStyle: 'none', counterReset: 'step' }}>
          {m.list.map((it, i) => (
            <li key={i} style={{
              display: 'flex', gap: 10, fontSize: 14, lineHeight: 1.5,
              color: t.textMuted, marginBottom: 6,
            }}>
              <span style={{
                fontFamily: t.mono, fontSize: 11, color: t.textDim,
                width: 18, flexShrink: 0, paddingTop: 2,
              }}>0{i + 1}</span>
              <span>{it}</span>
            </li>
          ))}
        </ol>
      )}
      {m.citations && (
        <div style={{
          background: t.ragBg, borderLeft: `2px solid ${t.rag}`,
          padding: '8px 10px', borderRadius: '0 8px 8px 0',
          fontSize: 12, color: t.rag, fontFamily: t.mono, letterSpacing: '0.01em',
        }}>
          {m.citations.map((c) => (
            <div key={c.id} style={{ display: 'flex', gap: 8 }}>
              <span style={{ opacity: 0.7 }}>[{c.id}]</span>
              <span style={{ flex: 1 }}>
                <span style={{ fontWeight: 600 }}>{c.doc}</span>
                <span style={{ opacity: 0.7 }}> · {c.section} · {c.page}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StreamingBubbleClean({ t }) {
  return (
    <div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6,
        fontSize: 11, fontFamily: t.mono, color: t.textDim, letterSpacing: '0.04em',
      }}>
        <span style={{ width: 16, height: 16, borderRadius: 4, background: t.text, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: t.bg, fontSize: 10, fontWeight: 700 }}>C</span>
        COOLAGENT
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: t.accent, marginLeft: 4 }}>
          <span style={{ width: 5, height: 5, borderRadius: '50%', background: t.accent, animation: 'cgPulse 1s infinite' }}/>
          ESCRIBIENDO
        </span>
      </div>
      <div style={{ fontSize: 14.5, lineHeight: 1.5, color: t.text }}>
        {STREAMING_TEXT}<span style={{
          display: 'inline-block', width: 8, height: 16, background: t.accent,
          marginLeft: 2, verticalAlign: '-2px', animation: 'cgBlink 0.9s infinite',
        }}/>
      </div>
    </div>
  );
}

// =============================================================
// EDITORIAL DARK
// =============================================================
function ChatDark() {
  const t = window.DIRECTIONS.dark;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{
        paddingTop: 56, paddingBottom: 14, paddingLeft: 16, paddingRight: 16,
        background: t.bg, borderBottom: `1px solid ${t.border}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <button style={iconBtn(t)}><window.Icons.chevLeft size={18} color={t.text} /></button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.success, boxShadow: `0 0 6px ${t.success}` }}/>
            <span style={{ fontSize: 11, fontFamily: t.mono, color: t.textMuted, letterSpacing: '0.06em' }}>EN VIVO</span>
          </div>
          <button style={iconBtn(t)}><window.Icons.more size={18} color={t.text} /></button>
        </div>
        <div style={{
          fontFamily: t.mono, fontSize: 10.5, color: t.textDim,
          letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4,
        }}>CASO C-0042 · {SAMPLE_CASE.manufacturer} {SAMPLE_CASE.model}</div>
        <div style={{ fontSize: 19, fontWeight: 600, letterSpacing: '-0.025em' }}>
          {SAMPLE_CASE.title}
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'hidden', padding: '14px 16px 0', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <UserBubbleDark t={t}>{SAMPLE_MESSAGES[0].content}</UserBubbleDark>
        <AssistantBubbleDark t={t} m={SAMPLE_MESSAGES[1]} />
        <UserBubbleDark t={t}>{SAMPLE_MESSAGES[2].content}</UserBubbleDark>
        <StreamingBubbleDark t={t} />
      </div>

      {/* Composer */}
      <div style={{ padding: '10px 12px 14px', background: t.bg }}>
        <div style={{
          background: t.surface, borderRadius: 22, border: `1px solid ${t.border}`,
          padding: '12px 12px 10px 16px', display: 'flex', flexDirection: 'column', gap: 10,
        }}>
          <div style={{ fontSize: 15, color: t.textDim }}>Describe lo que ves en el equipo…</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <button style={iconBtn(t, true)}><window.Icons.attach size={16} color={t.textMuted}/></button>
            <button style={iconBtn(t, true)}><window.Icons.camera size={16} color={t.textMuted}/></button>
            <div style={{
              marginLeft: 8, fontSize: 11, fontFamily: t.mono,
              color: t.accent, letterSpacing: '0.04em',
              display: 'inline-flex', alignItems: 'center', gap: 6,
            }}>
              <span style={{ width: 6, height: 6, borderRadius: 1, background: t.accent }}/>
              RAG ACTIVO
            </div>
            <button style={{
              marginLeft: 'auto', width: 40, height: 40, borderRadius: 14,
              background: t.accent, color: '#001318', border: 'none',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: `0 0 16px ${t.accentSoft}`,
            }}><window.Icons.arrowUp size={20} color="#001318" stroke={2.4}/></button>
          </div>
        </div>
        <div style={{ height: 22 }}/>
      </div>
    </div>
  );
}

function UserBubbleDark({ t, children }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
      <div style={{
        maxWidth: '78%', background: t.surfaceAlt, color: t.text,
        padding: '11px 14px', borderRadius: 14,
        fontSize: 14.5, lineHeight: 1.45, border: `1px solid ${t.border}`,
      }}>{children}</div>
    </div>
  );
}

function AssistantBubbleDark({ t, m }) {
  return (
    <div>
      <div style={{ fontSize: 14.5, lineHeight: 1.55, color: t.text, marginBottom: 10 }}>
        {m.content}
      </div>
      {m.list && (
        <div style={{ marginBottom: 10 }}>
          {m.list.map((it, i) => (
            <div key={i} style={{
              display: 'flex', gap: 12, padding: '8px 12px',
              background: t.surface, borderRadius: 8, marginBottom: 4,
              fontSize: 13.5, lineHeight: 1.5, color: t.text,
              borderLeft: `2px solid ${t.accent}`,
            }}>
              <span style={{
                fontFamily: t.mono, fontSize: 11, color: t.accent,
                flexShrink: 0, paddingTop: 2,
              }}>{String(i+1).padStart(2,'0')}</span>
              <span>{it}</span>
            </div>
          ))}
        </div>
      )}
      {m.citations && (
        <div style={{
          padding: '10px 12px', borderRadius: 10,
          background: t.ragBg, border: `1px solid ${t.borderStrong}`,
        }}>
          <div style={{
            fontSize: 10, fontFamily: t.mono, color: t.accent,
            letterSpacing: '0.1em', marginBottom: 6,
          }}>FUENTE · RAG</div>
          {m.citations.map((c) => (
            <div key={c.id} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: 12 }}>
              <window.Icons.doc size={14} color={t.accent} stroke={1.6}/>
              <div style={{ flex: 1 }}>
                <div style={{ color: t.text, fontWeight: 500 }}>{c.doc}</div>
                <div style={{ color: t.textMuted, fontFamily: t.mono, fontSize: 11, marginTop: 2 }}>{c.section} · {c.page}</div>
              </div>
              <window.Icons.chevRight size={14} color={t.textMuted}/>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StreamingBubbleDark({ t }) {
  return (
    <div>
      <div style={{ fontSize: 14.5, lineHeight: 1.55, color: t.text }}>
        {STREAMING_TEXT}
        <span style={{
          display: 'inline-block', width: 8, height: 16, background: t.accent,
          marginLeft: 3, verticalAlign: '-2px',
          boxShadow: `0 0 8px ${t.accent}`,
          animation: 'cgBlink 0.9s infinite',
        }}/>
      </div>
    </div>
  );
}

// =============================================================
// MONO PRINT
// =============================================================
function ChatMono() {
  const t = window.DIRECTIONS.mono;
  return (
    <div style={{
      width: '100%', height: '100%', background: t.bg, color: t.text,
      fontFamily: t.font, display: 'flex', flexDirection: 'column',
      position: 'relative',
    }}>
      {/* Header */}
      <div style={{
        paddingTop: 56, paddingBottom: 14, paddingLeft: 16, paddingRight: 16,
        background: t.bg, borderBottom: `1.5px solid ${t.text}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <button style={iconBtn(t)}><window.Icons.chevLeft size={18} color={t.text} /></button>
          <div style={{ fontSize: 11, fontFamily: t.mono, color: t.textMuted, letterSpacing: '0.08em' }}>CASO 0042 · ABIERTO</div>
          <button style={iconBtn(t)}><window.Icons.more size={18} color={t.text} /></button>
        </div>
        <div style={{ fontSize: 22, fontWeight: 500, letterSpacing: '-0.02em', fontStyle: 'italic', marginBottom: 4 }}>
          {SAMPLE_CASE.title}
        </div>
        <div style={{ fontFamily: t.mono, fontSize: 11, color: t.textMuted, letterSpacing: '0.04em' }}>
          {SAMPLE_CASE.manufacturer} / {SAMPLE_CASE.model} / Split
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'hidden', padding: '18px 18px 0', display: 'flex', flexDirection: 'column', gap: 18 }}>
        <UserBubbleMono t={t}>{SAMPLE_MESSAGES[0].content}</UserBubbleMono>
        <AssistantBubbleMono t={t} m={SAMPLE_MESSAGES[1]} />
        <UserBubbleMono t={t}>{SAMPLE_MESSAGES[2].content}</UserBubbleMono>
        <StreamingBubbleMono t={t} />
      </div>

      {/* Composer */}
      <div style={{ padding: '10px 14px 14px', background: t.bg, borderTop: `1px solid ${t.borderStrong}` }}>
        <div style={{
          background: t.surface, border: `1.5px solid ${t.text}`,
          padding: '12px 12px 10px 14px', display: 'flex', flexDirection: 'column', gap: 8,
        }}>
          <div style={{ fontSize: 15, color: t.textDim, fontStyle: 'italic' }}>Anote la observación de campo…</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <button style={iconBtn(t, true)}><window.Icons.attach size={16} color={t.textMuted}/></button>
            <button style={iconBtn(t, true)}><window.Icons.camera size={16} color={t.textMuted}/></button>
            <div style={{
              marginLeft: 6, fontSize: 10.5, fontFamily: t.mono,
              color: t.textMuted, letterSpacing: '0.06em', textTransform: 'uppercase',
            }}>3 fuentes activas</div>
            <button style={{
              marginLeft: 'auto', height: 38, padding: '0 14px',
              background: t.text, color: t.bg, border: 'none',
              fontFamily: t.font, fontSize: 13, fontWeight: 500,
              fontStyle: 'italic', letterSpacing: '-0.01em',
            }}>Enviar →</button>
          </div>
        </div>
        <div style={{ height: 22 }}/>
      </div>
    </div>
  );
}

function UserBubbleMono({ t, children }) {
  return (
    <div style={{ borderLeft: `3px solid ${t.text}`, paddingLeft: 12 }}>
      <div style={{
        fontFamily: t.mono, fontSize: 10, color: t.textMuted,
        letterSpacing: '0.1em', marginBottom: 4, textTransform: 'uppercase',
      }}>Operador · 14:32</div>
      <div style={{ fontSize: 15, lineHeight: 1.5, color: t.text }}>{children}</div>
    </div>
  );
}

function AssistantBubbleMono({ t, m }) {
  return (
    <div>
      <div style={{
        fontFamily: t.mono, fontSize: 10, color: t.textMuted,
        letterSpacing: '0.1em', marginBottom: 6, textTransform: 'uppercase',
      }}>CoolAgent · respuesta</div>
      <div style={{ fontSize: 15.5, lineHeight: 1.55, color: t.text, marginBottom: 10 }}>
        {m.content}
      </div>
      {m.list && (
        <ol style={{ margin: '0 0 12px 0', paddingLeft: 22, fontSize: 14.5, lineHeight: 1.6, color: t.text }}>
          {m.list.map((it, i) => (
            <li key={i} style={{ marginBottom: 4 }}>{it}</li>
          ))}
        </ol>
      )}
      {m.citations && (
        <div style={{
          borderTop: `1px solid ${t.borderStrong}`, paddingTop: 8,
          fontFamily: t.mono, fontSize: 11, color: t.textMuted,
          lineHeight: 1.6,
        }}>
          {m.citations.map((c) => (
            <div key={c.id}>
              <sup style={{ color: t.text, fontWeight: 600 }}>{c.id}</sup>{' '}
              <em style={{ color: t.text, fontFamily: t.font, fontSize: 12.5 }}>{c.doc}</em>
              {' · '}{c.section}{' · '}{c.page}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StreamingBubbleMono({ t }) {
  return (
    <div>
      <div style={{
        fontFamily: t.mono, fontSize: 10, color: t.textMuted,
        letterSpacing: '0.1em', marginBottom: 6, textTransform: 'uppercase',
      }}>CoolAgent · escribiendo…</div>
      <div style={{ fontSize: 15.5, lineHeight: 1.55, color: t.text }}>
        {STREAMING_TEXT}<span style={{
          display: 'inline-block', width: 10, height: 18, background: t.text,
          marginLeft: 2, verticalAlign: '-3px', animation: 'cgBlink 0.9s infinite',
        }}/>
      </div>
    </div>
  );
}

window.ChatClean = ChatClean;
window.ChatDark = ChatDark;
window.ChatMono = ChatMono;
