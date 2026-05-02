// Tiny stroke icons (24x24 viewBox)
const Icon = ({ d, size = 20, color = 'currentColor', stroke = 1.6, fill = 'none' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">
    {typeof d === 'string' ? <path d={d} /> : d}
  </svg>
);

const Icons = {
  arrowUp: (p) => <Icon {...p} d="M12 19V5 M5 12l7-7 7 7" />,
  send: (p) => <Icon {...p} d="M22 2L11 13 M22 2l-7 20-4-9-9-4 20-7z" />,
  chevLeft: (p) => <Icon {...p} d="M15 18l-6-6 6-6" />,
  chevRight: (p) => <Icon {...p} d="M9 6l6 6-6 6" />,
  more: (p) => <Icon {...p} d={<g><circle cx="5" cy="12" r="1.4" fill={p.color || 'currentColor'} stroke="none"/><circle cx="12" cy="12" r="1.4" fill={p.color || 'currentColor'} stroke="none"/><circle cx="19" cy="12" r="1.4" fill={p.color || 'currentColor'} stroke="none"/></g>} />,
  close: (p) => <Icon {...p} d="M18 6L6 18 M6 6l12 12" />,
  search: (p) => <Icon {...p} d={<g><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></g>} />,
  doc: (p) => <Icon {...p} d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M9 13h6 M9 17h4" />,
  spark: (p) => <Icon {...p} d="M12 2l2.4 6.6L21 11l-6.6 2.4L12 20l-2.4-6.6L3 11l6.6-2.4z" />,
  bolt: (p) => <Icon {...p} d="M13 2L4 14h7l-1 8 9-12h-7z" />,
  thermo: (p) => <Icon {...p} d={<g><path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z"/></g>} />,
  cpu: (p) => <Icon {...p} d={<g><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3 M15 1v3 M9 20v3 M15 20v3 M20 9h3 M20 14h3 M1 9h3 M1 14h3"/></g>} />,
  attach: (p) => <Icon {...p} d="M21 11.5l-8.5 8.5a5 5 0 01-7-7l8.5-8.5a3.5 3.5 0 015 5L10.5 18a2 2 0 01-3-3l7-7" />,
  camera: (p) => <Icon {...p} d={<g><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></g>} />,
  copy: (p) => <Icon {...p} d={<g><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></g>} />,
  check: (p) => <Icon {...p} d="M20 6L9 17l-5-5" />,
  plus: (p) => <Icon {...p} d="M12 5v14 M5 12h14" />,
  refresh: (p) => <Icon {...p} d={<g><path d="M3 12a9 9 0 0115-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 01-15 6.7L3 16"/><path d="M3 21v-5h5"/></g>} />,
  bookmark: (p) => <Icon {...p} d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />,
  alert: (p) => <Icon {...p} d={<g><path d="M10.3 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4 M12 17h.01"/></g>} />,
  inbox: (p) => <Icon {...p} d="M22 12h-6l-2 3h-4l-2-3H2 M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z" />,
  wifi: (p) => <Icon {...p} d={<g><path d="M5 12.55a11 11 0 0114 0"/><path d="M1.42 9a16 16 0 0121.16 0"/><path d="M8.53 16.11a6 6 0 016.95 0"/><circle cx="12" cy="20" r="0.5" fill={p.color || 'currentColor'}/></g>} />,
  wrench: (p) => <Icon {...p} d="M14.7 6.3a4 4 0 005.4 5.4L21 12l-9 9-4-4 9-9 .7-.7z" />,
  spinner: (p) => <Icon {...p} d={<g><path d="M21 12a9 9 0 11-9-9" /></g>} />,
  image: (p) => <Icon {...p} d={<g><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/></g>} />,
  x: (p) => <Icon {...p} d="M18 6L6 18 M6 6l12 12" />,
};

window.Icon = Icon;
window.Icons = Icons;
