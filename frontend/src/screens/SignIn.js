import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import * as AuthSession from 'expo-auth-session';

export default function SignIn({ auth }) {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  const onLocal = async () => {
    try { await auth.signInLocal(email, password); } catch (e) { Alert.alert('Sign-in failed', e.message); }
  };

  const googleClientId = '<YOUR_GOOGLE_OAUTH_CLIENT_ID>';
  const redirectUri = AuthSession.makeRedirectUri({ useProxy: true });
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=${encodeURIComponent('profile email')}`;

  const onGoogle = async () => {
    const res = await AuthSession.startAsync({ authUrl });
    if (res.type === 'success' && res.params?.access_token) {
      const info = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: { Authorization: `Bearer ${res.params.access_token}` },
      }).then(r => r.json());
      await auth.signInGoogle({ email: info.email, name: info.name, provider: 'google' }, res.params.access_token);
    } else {
      Alert.alert('Google sign-in cancelled');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.welcome}>Welcome back</Text>
      <TextInput style={styles.input} placeholder="Email" placeholderTextColor="#B3B3B3" value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#B3B3B3" secureTextEntry value={password} onChangeText={setPassword} />
      <TouchableOpacity style={styles.cta} onPress={onLocal}><Text style={styles.ctaText}>Sign In</Text></TouchableOpacity>
      <TouchableOpacity style={styles.google} onPress={onGoogle}><Text style={styles.googleText}>Continue with Google</Text></TouchableOpacity>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { padding: 24 },
  title: { color: '#E50914', fontSize: 32, fontWeight: '900', letterSpacing: 2, textAlign: 'center', marginBottom: 0 },
  subtitle: { color: '#E50914', fontSize: 18, fontWeight: '700', letterSpacing: 1.5, textAlign: 'center', marginBottom: 16 },
  welcome: { color: '#fff', fontSize: 24, fontWeight: '700', marginBottom: 16, textAlign: 'center' },
  input: { backgroundColor: '#221F1F', color: '#fff', padding: 12, borderRadius: 8, marginBottom: 12 },
  cta: { backgroundColor: '#E50914', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  ctaText: { color: '#fff', fontWeight: '600' },
  google: { backgroundColor: '#fff', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 12 },
  googleText: { color: '#000', fontWeight: '600' },
});
