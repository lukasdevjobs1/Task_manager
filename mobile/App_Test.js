import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, StyleSheet } from 'react-native';
import { createClient } from '@supabase/supabase-js';
import { registerRootComponent } from 'expo';

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M';

const supabase = createClient(supabaseUrl, supabaseKey);

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState('');

  const testConnection = async () => {
    console.log('=== BOTÃO CLICADO ===');
    setResult('Testando conexão...');
    
    try {
      console.log('URL:', supabaseUrl);
      console.log('Fazendo requisição...');
      
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .limit(1);
      
      console.log('Resposta:', { data, error });
      
      if (error) {
        console.log('Erro encontrado:', error);
        setResult(`Erro: ${error.message}`);
      } else {
        console.log('Sucesso! Dados:', data);
        setResult(`Sucesso! Encontrados ${data?.length || 0} usuários`);
      }
    } catch (err) {
      console.log('Erro de conexão:', err);
      setResult(`Erro de conexão: ${err.message}`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Teste Supabase</Text>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={testConnection}
        activeOpacity={0.7}
      >
        <Text style={styles.buttonText}>Testar Conexão</Text>
      </TouchableOpacity>
      
      <Text style={styles.result}>{result}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
  },
  result: {
    fontSize: 14,
    textAlign: 'center',
  },
});

registerRootComponent(App);