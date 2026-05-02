export const theme = {
  color: {
    bg: '#0E0F11',
    surface: '#16181B',
    surfaceAlt: '#1E2125',
    line: 'rgba(255,255,255,0.08)',
    lineStrong: 'rgba(255,255,255,0.16)',
    text: '#F2F3F5',
    muted: '#9BA0A8',
    dim: '#6A6F77',
    accent: '#5AE0FF',
    accentSoft: 'rgba(90,224,255,0.12)',
    success: '#52D195',
    successSoft: 'rgba(82,209,149,0.12)',
    warning: '#F0A052',
    warningSoft: 'rgba(240,160,82,0.12)',
    danger: '#F26A6A',
    dangerSoft: 'rgba(242,106,106,0.12)',
    black: '#050608',
  },
  radius: {
    sm: 6,
    md: 8,
    pill: 999,
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
  },
  font: {
    mono: 'Courier',
  },
} as const;

export const shadow = {
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 8 },
  shadowOpacity: 0.22,
  shadowRadius: 18,
  elevation: 6,
} as const;
