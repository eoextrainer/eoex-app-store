import React, { createContext, useState, useEffect, useMemo } from 'react';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

const palettes = {
  dark: { bg: '#141414', panel: '#221F1F', text: '#FFFFFF', subtext: '#B3B3B3', red: '#E50914' },
  light: { bg: '#FFFFFF', panel: '#F3F3F3', text: '#000000', subtext: '#4A4A4A', red: '#E50914' },
};

export const ThemeContext = createContext();
const THEME_KEY = 'eoex.theme';

export function ThemeProvider({ children }) {
  const system = useColorScheme();
  const [mode, setMode] = useState(system || 'dark');
  const [booted, setBooted] = useState(false);

  useEffect(() => {
    (async () => {
      const stored = await AsyncStorage.getItem(THEME_KEY);
      setMode(stored || system || 'dark');
      setBooted(true);
    })();
  }, [system]);

  const persistMode = async (next) => {
    setMode(next);
    await AsyncStorage.setItem(THEME_KEY, next);
    await SecureStore.setItemAsync(THEME_KEY, next); // optional
  };

  const value = useMemo(() => ({ theme: palettes[mode], mode, setMode: persistMode }), [mode]);

  if (!booted) return null;
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
