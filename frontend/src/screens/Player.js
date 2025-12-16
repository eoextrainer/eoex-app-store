import React, { useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

export default function Player({ route }) {
  const { video } = route.params;
  const embedUrl = useMemo(() => `https://www.youtube.com/embed/${video.id}?autoplay=1&playsinline=1`, [video.id]);
  return (
    <View style={styles.container}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.title}>{video.title}</Text>
      <View style={styles.player}>
        <WebView
          source={{ uri: embedUrl }}
          allowsInlineMediaPlayback
          mediaPlaybackRequiresUserAction={false}
          javaScriptEnabled
          domStorageEnabled
          startInLoadingState
          style={{ flex: 1 }}
        />
      </View>
      <Text style={styles.note}>Playback opens inline; use back to exit.</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  brand: { color: '#E50914', fontSize: 32, fontWeight: '900', letterSpacing: 2, textAlign: 'center' },
  subtitle: { color: '#E50914', fontSize: 18, fontWeight: '700', letterSpacing: 1.5, textAlign: 'center', marginBottom: 8 },
  title: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 12, textAlign: 'center' },
  player: { height: 220, borderRadius: 8, overflow: 'hidden', backgroundColor: '#000' },
  note: { color: '#B3B3B3', marginTop: 8, textAlign: 'center' },
});
