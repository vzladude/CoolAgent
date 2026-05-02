import { Platform } from 'react-native';

import {
  mockCases,
  mockErrorCodes,
  mockManufacturers,
  mockMessages,
} from '../mocks/data';
import type {
  ChatMessage,
  ErrorCode,
  ManufacturerSummary,
  TechnicalCase,
  TechnicalCaseInput,
} from '../types';

type BackendTechnicalCase = {
  id: string;
  title: string | null;
  manufacturer: string | null;
  equipment_model: string | null;
  category: string | null;
  status: 'open' | 'closed';
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
};

type BackendChatMessage = {
  id: string;
  technical_case_id: string;
  conversation_id?: string | null;
  role: 'user' | 'assistant';
  content: string;
  tokens_used: number | null;
  model_used: string | null;
  created_at: string;
};

type BackendMessageList = {
  messages: BackendChatMessage[];
  count: number;
  limit: number;
  offset: number;
};

type BackendErrorCode = {
  id: string;
  code: string;
  description: string;
  manufacturer: string;
  model: string | null;
  severity: string | null;
  possible_causes: string[];
  suggested_fix: string | null;
  source: string | null;
  created_at: string;
  updated_at: string;
};

type BackendManufacturer = {
  id: string;
  name: string;
  country: string | null;
  website: string | null;
  model_count: number;
  error_code_count: number;
};

const DEFAULT_API_BASE_URL =
  Platform.OS === 'android'
    ? 'http://10.0.2.2:8000/api/v1'
    : 'http://localhost:8000/api/v1';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? DEFAULT_API_BASE_URL;

const delay = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));
const localCases = new Map<string, TechnicalCase>();
const localMessages = new Map<string, ChatMessage[]>();

function compactDate(value?: string | null) {
  if (!value) return 'sin mensajes';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
  });
}

function cleanInput(value?: string) {
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : undefined;
}

function toBackendCaseInput(input: TechnicalCaseInput) {
  return {
    title: cleanInput(input.title),
    manufacturer: cleanInput(input.manufacturer),
    equipment_model: cleanInput(input.equipmentModel),
    category: cleanInput(input.category),
    status: input.status ?? 'open',
  };
}

function toTechnicalCase(item: BackendTechnicalCase): TechnicalCase {
  return {
    id: item.id,
    title: item.title ?? 'Caso tecnico sin titulo',
    manufacturer: item.manufacturer ?? undefined,
    equipmentModel: item.equipment_model ?? undefined,
    category: item.category ?? undefined,
    status: item.status,
    createdAt: item.created_at,
    updatedAt: compactDate(item.updated_at),
    lastMessageAt: item.last_message_at ?? undefined,
    lastMessage: item.last_message_at
      ? 'Ultimo mensaje sincronizado con backend.'
      : 'Sin mensajes todavia.',
  };
}

function toChatMessage(item: BackendChatMessage): ChatMessage {
  return {
    id: item.id,
    technicalCaseId: item.technical_case_id,
    role: item.role,
    content: item.content,
    tokensUsed: item.tokens_used ?? undefined,
    modelUsed: item.model_used ?? undefined,
    createdAt: item.created_at,
  };
}

function toSeverity(value: string | null): ErrorCode['severity'] {
  if (value === 'low' || value === 'medium' || value === 'high' || value === 'critical') {
    return value;
  }
  return undefined;
}

function toErrorCode(item: BackendErrorCode): ErrorCode {
  return {
    id: item.id,
    code: item.code,
    manufacturer: item.manufacturer,
    model: item.model ?? undefined,
    severity: toSeverity(item.severity),
    description: item.description,
    possibleCauses: item.possible_causes ?? [],
    suggestedFix: item.suggested_fix ?? undefined,
    source: item.source ?? undefined,
  };
}

function toManufacturerSummary(item: BackendManufacturer): ManufacturerSummary {
  return {
    id: item.id,
    name: item.name,
    modelCount: item.model_count,
    errorCodeCount: item.error_code_count,
  };
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const details = await response.text();
    throw new Error(`API ${response.status}: ${details}`);
  }

  return (await response.json()) as T;
}

function createLocalCase(input: TechnicalCaseInput): TechnicalCase {
  const now = new Date().toISOString();
  const localCase = {
    id: `LOCAL-${Date.now()}`,
    title: cleanInput(input.title) ?? 'Nuevo caso tecnico',
    manufacturer: cleanInput(input.manufacturer),
    equipmentModel: cleanInput(input.equipmentModel),
    category: cleanInput(input.category),
    status: input.status ?? 'open',
    createdAt: now,
    updatedAt: 'ahora',
    lastMessage: 'Modo mock local. Backend no disponible.',
  };
  localCases.set(localCase.id, localCase);
  localMessages.set(localCase.id, []);
  return localCase;
}

function createLocalAssistantMessage(caseId: string, content: string): ChatMessage {
  const message: ChatMessage = {
    id: `LOCAL-AI-${Date.now()}`,
    technicalCaseId: caseId,
    role: 'assistant',
    content:
      `Modo mock: recibi "${content}". Cuando el backend este disponible, ` +
      'esta respuesta vendra de Claude con RAG y guardara el historial real.',
    createdAt: new Date().toISOString(),
    modelUsed: 'local-mock',
  };
  localMessages.set(caseId, [...(localMessages.get(caseId) ?? []), message]);
  return message;
}

export const api = {
  baseUrl: API_BASE_URL,

  async listCases(): Promise<TechnicalCase[]> {
    try {
      const data = await requestJson<BackendTechnicalCase[]>('/chat/cases?limit=50');
      return data.map(toTechnicalCase);
    } catch {
      await delay();
      return [...localCases.values(), ...mockCases];
    }
  },

  async getCase(caseId: string): Promise<TechnicalCase> {
    try {
      const data = await requestJson<BackendTechnicalCase>(`/chat/cases/${caseId}`);
      return toTechnicalCase(data);
    } catch {
      await delay();
      const localCase = localCases.get(caseId);
      if (localCase) return localCase;
      return mockCases.find((item) => item.id === caseId) ?? mockCases[0];
    }
  },

  async createCase(input: TechnicalCaseInput): Promise<TechnicalCase> {
    try {
      const data = await requestJson<BackendTechnicalCase>('/chat/cases', {
        method: 'POST',
        body: JSON.stringify(toBackendCaseInput(input)),
      });
      return toTechnicalCase(data);
    } catch {
      await delay();
      return createLocalCase(input);
    }
  },

  async updateCase(caseId: string, input: TechnicalCaseInput): Promise<TechnicalCase> {
    try {
      const data = await requestJson<BackendTechnicalCase>(`/chat/cases/${caseId}`, {
        method: 'PATCH',
        body: JSON.stringify(toBackendCaseInput(input)),
      });
      return toTechnicalCase(data);
    } catch {
      await delay();
      const localCase = localCases.get(caseId);
      if (localCase) {
        const updated = { ...localCase, ...input, updatedAt: 'ahora' };
        localCases.set(caseId, updated);
        return updated;
      }
      const current = mockCases.find((item) => item.id === caseId) ?? mockCases[0];
      return { ...current, ...input, updatedAt: 'ahora' };
    }
  },

  async listCaseMessages(caseId: string): Promise<ChatMessage[]> {
    try {
      const data = await requestJson<BackendMessageList>(
        `/chat/cases/${caseId}/messages?limit=100&offset=0`,
      );
      return data.messages.map(toChatMessage);
    } catch {
      await delay();
      if (localMessages.has(caseId)) return localMessages.get(caseId) ?? [];
      return mockMessages;
    }
  },

  async sendCaseMessage(caseId: string, content: string): Promise<ChatMessage> {
    try {
      const data = await requestJson<BackendChatMessage>(`/chat/cases/${caseId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      });
      return toChatMessage(data);
    } catch {
      await delay(350);
      return createLocalAssistantMessage(caseId, content);
    }
  },

  async searchErrorCodes(query: {
    query?: string;
    code?: string;
    manufacturer?: string;
    model?: string;
  }): Promise<ErrorCode[]> {
    try {
      const params = new URLSearchParams({ limit: '50', offset: '0' });
      const queryText = cleanInput(query.query);
      const code = cleanInput(query.code);
      const manufacturer = cleanInput(query.manufacturer);
      const model = cleanInput(query.model);
      if (queryText) params.set('query', queryText);
      if (code) params.set('code', code);
      if (manufacturer) params.set('manufacturer', manufacturer);
      if (model) params.set('model', model);

      const data = await requestJson<BackendErrorCode[]>(`/error-codes/?${params.toString()}`);
      return data.map(toErrorCode);
    } catch {
      await delay();
      const queryText = query.query?.trim().toLowerCase();
      const code = query.code?.trim().toLowerCase();
      const manufacturer = query.manufacturer?.trim().toLowerCase();
      const model = query.model?.trim().toLowerCase();

      return mockErrorCodes.filter((item) => {
        const matchesQuery =
          !queryText ||
          item.code.toLowerCase().includes(queryText) ||
          item.description.toLowerCase().includes(queryText) ||
          item.manufacturer.toLowerCase().includes(queryText) ||
          item.model?.toLowerCase().includes(queryText);
        const matchesCode = !code || item.code.toLowerCase().includes(code);
        const matchesManufacturer =
          !manufacturer || item.manufacturer.toLowerCase().includes(manufacturer);
        const matchesModel = !model || item.model?.toLowerCase().includes(model);
        return matchesQuery && matchesCode && matchesManufacturer && matchesModel;
      });
    }
  },

  async listManufacturers(): Promise<ManufacturerSummary[]> {
    try {
      const data = await requestJson<BackendManufacturer[]>('/error-codes/manufacturers');
      return data.map(toManufacturerSummary);
    } catch {
      await delay();
      return mockManufacturers;
    }
  },
};
