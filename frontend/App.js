import React, { useMemo, useState, useEffect, useRef } from 'react';
import { Animated, StyleSheet, ActivityIndicator, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ThemeProvider } from './src/theme/ThemeContext';
import { saveSession, loadSession, clearSession, saveToken } from './src/services/session';
import SplashScreen from './src/screens/SplashScreen';
import SignIn from './src/screens/SignIn';
import Home from './src/screens/Home';
import Player from './src/screens/Player';

const Stack = createNativeStackNavigator();

export default function App() {
  const [user, setUser] = useState(null);
  const [booted, setBooted] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const homeOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    (async () => {
      const existing = await loadSession();
      if (existing) setUser(existing);
      setBooted(true);
      Animated.timing(homeOpacity, { toValue: 1, duration: 1000, useNativeDriver: true }).start();
    })();
  }, [homeOpacity]);

  const auth = useMemo(() => ({
    signInLocal: async (email, password) => {
      if (!email?.includes('@') || password?.length < 6) throw new Error('Invalid credentials');
      const profile = { email, provider: 'local' };
      await saveSession(profile);
      setUser(profile);
    },
    signInGoogle: async (profile, token) => {
      await saveSession(profile);
      if (token) await saveToken(token);
      setUser(profile);
    },
    signOut: async () => { await clearSession(); setUser(null); },
    user,
  }), [user]);

  if (!booted) {
    return (
      <View style={{ flex: 1, backgroundColor: '#141414', justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator color="#E50914" />
      </View>
    );
  }

  return (
    <ThemeProvider>
      <NavigationContainer>
        <Animated.View style={[styles.homeWrapper, { opacity: homeOpacity }]}> 
          <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: '#141414' }, headerTintColor: '#fff', contentStyle: { backgroundColor: '#141414' } }}>
            {user ? (
              <>
                <Stack.Screen name="Home" options={{ title: 'EOEX Market' }}>{(props) => <Home {...props} auth={auth} />}</Stack.Screen>
                <Stack.Screen name="Player" options={{ title: 'Now Playing' }}>{(props) => <Player {...props} />}</Stack.Screen>
              </>
            ) : (
              <Stack.Screen name="SignIn" options={{ title: 'Sign In' }}>{(props) => <SignIn {...props} auth={auth} />}</Stack.Screen>
            )}
          </Stack.Navigator>
        </Animated.View>
        {showSplash && <SplashScreen onFinish={() => setShowSplash(false)} />}
      </NavigationContainer>
    </ThemeProvider>
  );
}
const styles = StyleSheet.create({ homeWrapper: { flex: 1 } });
