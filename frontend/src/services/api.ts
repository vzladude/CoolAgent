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
} from '../types';

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

const delay = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

export const api = {
  baseUrl: API_BASE_URL,

  async listCases(): Promise<TechnicalCase[]> {
    await delay();
    return mockCases;
  },

  async listCaseMessages(_caseId: string): Promise<ChatMessage[]> {
    await delay();
    return mockMessages;
  },

  async searchErrorCodes(query: {
    code?: string;
    manufacturer?: string;
    model?: string;
  }): Promise<ErrorCode[]> {
    await delay();
    const code = query.code?.trim().toLowerCase();
    const manufacturer = query.manufacturer?.trim().toLowerCase();
    const model = query.model?.trim().toLowerCase();

    return mockErrorCodes.filter((item) => {
      const matchesCode = !code || item.code.toLowerCase().includes(code);
      const matchesManufacturer =
        !manufacturer || item.manufacturer.toLowerCase().includes(manufacturer);
      const matchesModel = !model || item.model?.toLowerCase().includes(model);
      return matchesCode && matchesManufacturer && matchesModel;
    });
  },

  async listManufacturers(): Promise<ManufacturerSummary[]> {
    await delay();
    return mockManufacturers;
  },
};
