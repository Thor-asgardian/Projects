// screens/PremiumSettingsScreen.js
import React, { useEffect, useState } from 'react';
import { View, Text, Switch, Button, Alert, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import RazorpayCheckout from 'react-native-razorpay';

const PremiumSettingsScreen = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      const dark = await AsyncStorage.getItem('darkMode');
      const premium = await AsyncStorage.getItem('isPremium');
      if (dark !== null) setDarkMode(JSON.parse(dark));
      if (premium !== null) setIsPremium(JSON.parse(premium));
    };
    loadSettings();
  }, []);

  const toggleDarkMode = async () => {
    const updated = !darkMode;
    setDarkMode(updated);
    await AsyncStorage.setItem('darkMode', JSON.stringify(updated));
  };

  const handlePayment = () => {
    const options = {
      description: 'Upgrade to premium membership',
      image: 'https://yourapp.com/logo.png',
      currency: 'INR',
      key: 'YOUR_RAZORPAY_KEY_ID',
      amount: '19900', // Rs.199.00
      name: 'Virtual Closet Premium',
      prefill: {
        email: 'user@example.com',
        contact: '9876543210',
        name: 'User'
      },
      theme: { color: '#3399cc' }
    };
    RazorpayCheckout.open(options)
      .then(async (data) => {
        await AsyncStorage.setItem('isPremium', JSON.stringify(true));
        setIsPremium(true);
        Alert.alert('Success', 'You are now a Premium user!');
      })
      .catch((error) => {
        Alert.alert('Payment Failed', error.description);
      });
  };

  return (
    <View style={[styles.container, darkMode && styles.dark]}>
      <Text style={[styles.title, darkMode && styles.darkText]}>Premium Settings</Text>

      <View style={styles.row}>
        <Text style={[styles.label, darkMode && styles.darkText]}>Dark Mode</Text>
        <Switch value={darkMode} onValueChange={toggleDarkMode} />
      </View>

      <View style={styles.row}>
        <Text style={[styles.label, darkMode && styles.darkText]}>Premium Status</Text>
        <Text style={[styles.badge, isPremium ? styles.active : styles.inactive]}>
          {isPremium ? '👑 Active' : '❌ Not Premium'}
        </Text>
      </View>

      {!isPremium && <Button title="Upgrade Now" onPress={handlePayment} />}
    </View>
  );
};

export default PremiumSettingsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#fff'
  },
  dark: {
    backgroundColor: '#000'
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20
  },
  darkText: {
    color: '#fff'
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  label: {
    fontSize: 18
  },
  badge: {
    fontSize: 16,
    fontWeight: 'bold'
  },
  active: {
    color: 'gold'
  },
  inactive: {
    color: 'gray'
  }
});