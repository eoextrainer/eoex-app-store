import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

const SESSION_KEY = 'eoex.session';
const TOKEN_KEY = 'eoex.token';

export const saveSession = (profile) => AsyncStorage.setItem(SESSION_KEY, JSON.stringify(profile));
export const loadSession = async () => {
  const raw = await AsyncStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
};
export const clearSession = async () => {
  await AsyncStorage.removeItem(SESSION_KEY);
  await SecureStore.deleteItemAsync(TOKEN_KEY);
};
export const saveToken = (token) => SecureStore.setItemAsync(TOKEN_KEY, token);
export const getToken = () => SecureStore.getItemAsync(TOKEN_KEY);
