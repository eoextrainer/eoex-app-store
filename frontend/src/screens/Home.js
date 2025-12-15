import React, { useEffect, useRef, useContext } from 'react';
import { Animated, StyleSheet, ScrollView, Easing, View, Text } from 'react-native';
import Hero from '../components/Hero';
import MediaCarousel from '../components/MediaCarousel';
import Features from '../components/Features';
import FAQ from '../components/FAQ';
import Footer from '../components/Footer';
import { videos } from '../data/videos';
import { ThemeContext } from '../theme/ThemeContext';

export default function Home({ navigation, auth }) {
  const { theme } = useContext(ThemeContext);

  const sections = [
    { key: 'hero', delay: 250, startY: 24 },
    { key: 'carousel', delay: 300, startY: 28 },
    { key: 'features', delay: 350, startY: 32 },
    { key: 'faq', delay: 380, startY: 24 },
    { key: 'footer', delay: 420, startY: 20 },
  ];

  const animated = sections.map(() => ({
    opacity: useRef(new Animated.Value(0)).current,
    translateY: useRef(new Animated.Value(30)).current,
    scale: useRef(new Animated.Value(0.95)).current,
  }));

  useEffect(() => {
    const timeline = sections.map((sec, i) =>
      Animated.sequence([
        Animated.delay(sec.delay),
        Animated.parallel([
          Animated.timing(animated[i].opacity, { toValue: 1, duration: 800, easing: Easing.out(Easing.quad), useNativeDriver: true }),
          Animated.timing(animated[i].translateY, { toValue: 0, duration: 800, easing: Easing.out(Easing.quad), useNativeDriver: true }),
          Animated.timing(animated[i].scale, { toValue: 1, duration: 800, easing: Easing.out(Easing.quad), useNativeDriver: true }),
        ]),
      ])
    );
    Animated.parallel(timeline).start();
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.headerBranding}>
        <Text style={styles.brand}>EOEX</Text>
        <Text style={styles.subtitle}>App Market</Text>
      </View>
      <Animated.View style={{ opacity: animated[0].opacity, transform: [{ translateY: animated[0].translateY }, { scale: animated[0].scale }] }}>
        <Hero />
      </Animated.View>
      <Animated.View style={{ opacity: animated[1].opacity, transform: [{ translateY: animated[1].translateY }, { scale: animated[1].scale }] }}>
        <MediaCarousel title="Trending Now" items={videos.slice(0, 5)} onPressItem={(video) => navigation.navigate('Player', { video })} />
      </Animated.View>
      <Animated.View style={{ opacity: animated[2].opacity, transform: [{ translateY: animated[2].translateY }, { scale: animated[2].scale }] }}>
        <Features />
      </Animated.View>
      <Animated.View style={{ opacity: animated[3].opacity, transform: [{ translateY: animated[3].translateY }, { scale: animated[3].scale }] }}>
        <FAQ />
      </Animated.View>
      <Animated.View style={{ opacity: animated[4].opacity, transform: [{ translateY: animated[4].translateY }, { scale: animated[4].scale }] }}>
        <Footer onSignOut={auth?.signOut} />
      </Animated.View>
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: { paddingBottom: 24 },
  headerBranding: { alignItems: 'center', marginTop: 24, marginBottom: 8 },
  brand: { color: '#E50914', fontSize: 32, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 18, fontWeight: '700', letterSpacing: 1.5 },
});
