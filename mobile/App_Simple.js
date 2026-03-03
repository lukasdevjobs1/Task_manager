import React, { useState } from 'react';
import { View, Text, StyleSheet, AppRegistry, TouchableOpacity, Alert } from 'react-native';

function App() {
  const [count, setCount] = useState(0);

  const showAlert = () => {
    Alert.alert('Sucesso!', 'App Task Manager funcionando perfeitamente!');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Task Manager ISP v2.0</Text>
      <Text style={styles.subtitle}>Sistema funcionando!</Text>
      
      <TouchableOpacity style={styles.button} onPress={showAlert}>
        <Text style={styles.buttonText}>Testar Alert</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.button} onPress={() => setCount(count + 1)}>
        <Text style={styles.buttonText}>Contador: {count}</Text>
      </TouchableOpacity>
      
      <Text style={styles.info}>✅ React Native funcionando</Text>
      <Text style={styles.info}>✅ Expo Go conectado</Text>
      <Text style={styles.info}>✅ Pronto para desenvolvimento</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#6366f1',
    padding: 20,
  },
  text: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: 'white',
    marginBottom: 30,
    textAlign: 'center',
  },
  button: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    marginVertical: 8,
    minWidth: 200,
  },
  buttonText: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  info: {
    color: 'white',
    fontSize: 14,
    marginTop: 5,
    textAlign: 'center',
  },
});

AppRegistry.registerComponent('main', () => App);
export default App;