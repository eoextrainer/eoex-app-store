import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Dimensions, Easing } from 'react-native';
const { height } = Dimensions.get('window');

export default function SplashScreen({ onFinish }) {
  const translateY = useRef(new Animated.Value(100)).current;
  const opacity = useRef(new Animated.Value(1)).current;
  const scale = useRef(new Animated.Value(0.9)).current;
  const letterSpacing = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(translateY, { toValue: -50, duration: 1500, easing: Easing.out(Easing.quad), useNativeDriver: true }),
      Animated.timing(scale, { toValue: 1, duration: 1500, easing: Easing.out(Easing.quad), useNativeDriver: true }),
      Animated.timing(letterSpacing, { toValue: 2, duration: 1500, easing: Easing.out(Easing.quad), useNativeDriver: false }),
    ]).start(() => {
      Animated.timing(opacity, { toValue: 0, duration: 1000, delay: 700, useNativeDriver: true }).start(() => onFinish?.());
    });
  }, [translateY, opacity, scale, letterSpacing, onFinish]);

  return (
    <Animated.View style={[styles.overlay, { opacity }]}> 
      <View style={styles.baseline} />
      <Animated.Text style={[styles.brand, { transform: [{ translateY }, { scale }], letterSpacing }]}>EOEX</Animated.Text>
      <Text style={styles.subtitle}>App Market</Text>
    </Animated.View>
  );
}
const styles = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: '#000', justifyContent: 'flex-end', alignItems: 'center', paddingBottom: height / 2, zIndex: 999 },
  baseline: { width: '100%', height: 2, backgroundColor: '#fff' },
  brand: { position: 'absolute', bottom: 0, fontSize: 48, fontWeight: '900', color: '#E50914', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 22, fontWeight: '700', marginTop: 12, letterSpacing: 1.5 },
});
