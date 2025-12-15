import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function Hero() {
  const [email, setEmail] = React.useState('');
  return (
    <LinearGradient colors={['rgba(229,9,20,0.15)', 'rgba(0,0,0,0.9)']} style={styles.hero}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.headline}>Unlimited apps, one store</Text>
      <Text style={styles.subhead}>Discover, download, and enjoy the best hybrid apps for every device. Anytime, anywhere.</Text>
      <View style={styles.form}>
        <TextInput style={styles.input} placeholder="Email address" placeholderTextColor="#B3B3B3" value={email} onChangeText={setEmail} />
        <TouchableOpacity style={styles.cta}><Text style={styles.ctaText}>Get Started</Text></TouchableOpacity>
      </View>
    </LinearGradient>
  );
}
const styles = StyleSheet.create({
  hero: { padding: 24, alignItems: 'center' },
  brand: { color: '#E50914', fontSize: 32, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 18, fontWeight: '700', letterSpacing: 1.5, marginBottom: 8 },
  headline: { color: '#fff', fontSize: 28, fontWeight: '700', textAlign: 'center', marginBottom: 12 },
  subhead: { color: '#B3B3B3', fontSize: 18, textAlign: 'center', marginBottom: 16 },
  form: { width: '100%', flexDirection: 'row', alignItems: 'center' },
  input: { flex: 1, backgroundColor: '#221F1F', color: '#fff', padding: 12, borderRadius: 8, marginRight: 8 },
  cta: { backgroundColor: '#E50914', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 8 },
  ctaText: { color: '#fff', fontWeight: '600' },
});
