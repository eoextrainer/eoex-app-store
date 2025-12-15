import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function Features() {
  const items = [
    { h: 'Enjoy on your TV', p: 'Watch on Smart TVs, consoles, and more.' },
    { h: 'Download to watch offline', p: 'Save favorites to watch anywhere.' },
    { h: 'Watch everywhere', p: 'Stream across devices, anytime.' },
    { h: 'Create profiles for kids', p: 'Family-friendly space with controls.' },
  ];
  return (
    <View style={styles.container}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.title}>More reasons to join</Text>
      <View style={styles.grid}>
        {items.map((it, i) => (
          <View key={i} style={styles.card}>
            <Text style={styles.h}>{it.h}</Text>
            <Text style={styles.p}>{it.p}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { padding: 16 },
  brand: { color: '#E50914', fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 14, fontWeight: '700', letterSpacing: 1.5, marginBottom: 4 },
  title: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 12 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  card: { backgroundColor: '#221F1F', padding: 16, borderRadius: 8, width: '48%', marginBottom: 12 },
  h: { color: '#fff', fontWeight: '700', marginBottom: 8 },
  p: { color: '#B3B3B3' },
});
