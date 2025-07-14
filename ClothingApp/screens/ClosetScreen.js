// screens/ClosetScreen.js
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, Image, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ClosetScreen = () => {
  const [clothes, setClothes] = useState([]);
  const [premium, setPremium] = useState(false);

  useEffect(() => {
    fetchClothes();
    checkPremium();
  }, []);

  const fetchClothes = async () => {
    const token = await AsyncStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:5000/api/closet', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setClothes(data.items || []);
    } catch (err) {
      console.error('Failed to fetch closet items:', err);
    }
  };

  const checkPremium = async () => {
    const status = await AsyncStorage.getItem('isPremium');
    setPremium(status === 'true');
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      {item.image && <Image source={{ uri: item.image }} style={styles.image} />}
      <Text style={styles.text}>{item.name}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Closet</Text>
      {premium && (
        <Text style={styles.premiumBadge}>👑 Premium User</Text>
      )}
      <FlatList
        data={clothes}
        keyExtractor={(item, index) => index.toString()}
        renderItem={renderItem}
      />
    </View>
  );
};

export default ClosetScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff'
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 10
  },
  premiumBadge: {
    fontSize: 16,
    color: 'gold',
    fontWeight: 'bold',
    marginBottom: 10
  },
  card: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8
  },
  image: {
    width: '100%',
    height: 150,
    marginBottom: 8,
    borderRadius: 6
  },
  text: {
    fontSize: 16
  }
});
