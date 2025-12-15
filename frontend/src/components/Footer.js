import React, { useContext } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ThemeContext } from '../theme/ThemeContext';

export default function Footer({ onSignOut }) {
  const { mode, setMode } = useContext(ThemeContext);
  return (
    <View style={styles.container}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.help}>Questions? Contact support</Text>
      <View style={styles.links}>
        <Text style={styles.link}>FAQ</Text><Text style={styles.link}>Help Center</Text><Text style={styles.link}>Account</Text><Text style={styles.link}>Media Center</Text>
      </View>
      <TouchableOpacity style={styles.signOut} onPress={onSignOut}><Text style={styles.signOutText}>Sign Out</Text></TouchableOpacity>
      <TouchableOpacity style={styles.toggle} onPress={() => setMode(mode === 'dark' ? 'light' : 'dark')}>
        <Text style={styles.toggleText}>Switch to {mode === 'dark' ? 'Light' : 'Dark'} Mode</Text>
      </TouchableOpacity>
      <Text style={styles.legal}>© 2025 EOEX App Market. All rights reserved.</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { padding: 16, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: 'rgba(255,255,255,0.1)' },
  brand: { color: '#E50914', fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 14, fontWeight: '700', letterSpacing: 1.5, marginBottom: 4 },
  help: { color: '#B3B3B3', marginBottom: 12 },
  links: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 12 },
  link: { color: '#B3B3B3', textDecorationLine: 'underline' },
  signOut: { backgroundColor: '#E50914', padding: 10, borderRadius: 8, alignItems: 'center', marginBottom: 8 },
  signOutText: { color: '#fff', fontWeight: '600' },
  toggle: { backgroundColor: '#221F1F', padding: 10, borderRadius: 8, alignItems: 'center', marginBottom: 8 },
  toggleText: { color: '#fff', fontWeight: '600' },
  legal: { color: '#B3B3B3' },
});
