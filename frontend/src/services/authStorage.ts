import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'coolagent.accessToken';

function webStorage() {
  const storage = (globalThis as { localStorage?: Storage }).localStorage;
  return Platform.OS === 'web' ? storage : undefined;
}

export async function loadStoredToken() {
  const storage = webStorage();
  if (storage) return storage.getItem(TOKEN_KEY);

  const available = await SecureStore.isAvailableAsync();
  if (!available) return null;
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function saveStoredToken(token: string) {
  const storage = webStorage();
  if (storage) {
    storage.setItem(TOKEN_KEY, token);
    return;
  }

  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearStoredToken() {
  const storage = webStorage();
  if (storage) {
    storage.removeItem(TOKEN_KEY);
    return;
  }

  const available = await SecureStore.isAvailableAsync();
  if (available) {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  }
}
