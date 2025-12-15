import React, { useState } from 'react';
import { View, Text, TouchableOpacity, LayoutAnimation, StyleSheet } from 'react-native';

export default function FAQ() {
  const [open, setOpen] = useState(null);
  const items = [
    { q: 'What is EOEX App Market?', a: 'Discover, download, and enjoy the best hybrid apps for every device.' },
    { q: 'How much does it cost?', a: 'Plans start at €7.99 per month.' },
  ];
  const toggle = (i) => { LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut); setOpen(open === i ? null : i); };
  return (
    <View style={styles.container}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.title}>Frequently Asked Questions</Text>
      {items.map((it, i) => (
        <View key={i} style={styles.item}>
          <TouchableOpacity onPress={() => toggle(i)}><Text style={styles.q}>{it.q}</Text></TouchableOpacity>
          {open === i && <Text style={styles.a}>{it.a}</Text>}
        </View>
      ))}
    </View>
  );
}
const styles = StyleSheet.create({
  container: { padding: 16 },
  brand: { color: '#E50914', fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 14, fontWeight: '700', letterSpacing: 1.5, marginBottom: 4 },
  title: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 12 },
  item: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: 'rgba(255,255,255,0.1)', paddingVertical: 12 },
  q: { color: '#fff', fontSize: 16, fontWeight: '600' },
  a: { color: '#B3B3B3', marginTop: 6 },
});
