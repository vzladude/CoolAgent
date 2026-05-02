import type { ComponentType, ReactNode } from 'react';

export type TabId = 'home' | 'cases' | 'tools' | 'codes' | 'settings';

export type AppRouteName =
  | 'home'
  | 'cases'
  | 'newCase'
  | 'chat'
  | 'caseDetails'
  | 'tools'
  | 'diagnosisCapture'
  | 'diagnosisContext'
  | 'diagnosisAnalyzing'
  | 'diagnosisResult'
  | 'calculator'
  | 'guides'
  | 'guideDetail'
  | 'offline'
  | 'codes'
  | 'codeDetail'
  | 'settings';

export type AppRoute = {
  name: AppRouteName;
  params?: Record<string, unknown>;
};

export type NavigationApi = {
  activeTab: TabId;
  goBack: () => void;
  open: (name: AppRouteName, params?: Record<string, unknown>) => void;
  resetToTab: (tab: TabId) => void;
};

export type IconComponent = ComponentType<{
  size?: number;
  color?: string;
  strokeWidth?: number;
}>;

export type TechnicalCaseStatus = 'open' | 'closed';

export type TechnicalCase = {
  id: string;
  title: string;
  manufacturer?: string;
  equipmentModel?: string;
  category?: string;
  status: TechnicalCaseStatus;
  createdAt?: string;
  updatedAt: string;
  lastMessageAt?: string;
  lastMessage?: string;
  summary?: string;
};

export type ChatMessage = {
  id: string;
  technicalCaseId?: string;
  role: 'user' | 'assistant';
  content: string;
  tokensUsed?: number;
  modelUsed?: string;
  createdAt?: string;
  citations?: RagCitation[];
};

export type TechnicalCaseInput = {
  title?: string;
  manufacturer?: string;
  equipmentModel?: string;
  category?: string;
  status?: TechnicalCaseStatus;
};

export type RagCitation = {
  id: string;
  title: string;
  source: string;
  detail: string;
};

export type ErrorCode = {
  id: string;
  code: string;
  manufacturer: string;
  model?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  possibleCauses: string[];
  suggestedFix?: string;
  source?: string;
};

export type ManufacturerSummary = {
  id: string;
  name: string;
  modelCount: number;
  errorCodeCount: number;
};

export type Guide = {
  id: string;
  title: string;
  category: string;
  duration: string;
  offline: boolean;
  tools: string[];
  steps: string[];
};

export type ToolAction = {
  id: string;
  title: string;
  subtitle: string;
  icon: IconComponent;
  target: AppRouteName;
  badge?: string;
  params?: Record<string, unknown>;
};

export type SettingRow = {
  label: string;
  value: string;
  icon: IconComponent;
  muted?: boolean;
};

export type ChildrenProps = {
  children: ReactNode;
};
