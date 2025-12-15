import React, { useMemo, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import FastImage from 'react-native-fast-image';
import { getThumbnail } from '../data/videos';

export default function MediaCarousel({ title, items, onPressItem }) {
  const data = useMemo(() => items, [items]);
  const renderItem = useCallback(({ item }) => (
    <TouchableOpacity onPress={() => onPressItem(item)} style={styles.card} activeOpacity={0.8}>
      <FastImage style={styles.poster} source={{ uri: getThumbnail(item.id), priority: FastImage.priority.normal }} resizeMode={FastImage.resizeMode.cover} />
      <Text style={styles.caption} numberOfLines={1}>{item.title}</Text>
    </TouchableOpacity>
  ), [onPressItem]);

  return (
    <View style={styles.container}>
      <Text style={styles.brand}>EOEX</Text>
      <Text style={styles.subtitle}>App Market</Text>
      <Text style={styles.title}>{title}</Text>
      <FlatList horizontal showsHorizontalScrollIndicator={false} data={data} keyExtractor={(item) => item.id} renderItem={renderItem} initialNumToRender={4} windowSize={7} removeClippedSubviews />
    </View>
  );
}
const styles = StyleSheet.create({
  container: { paddingVertical: 16, paddingHorizontal: 16 },
  brand: { color: '#E50914', fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#E50914', fontSize: 14, fontWeight: '700', letterSpacing: 1.5, marginBottom: 4 },
  title: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 12 },
  card: { marginRight: 12, width: 140 },
  poster: { width: 140, height: 210, borderRadius: 8, backgroundColor: '#221F1F' },
  caption: { color: '#B3B3B3', marginTop: 6, fontSize: 12 },
});
