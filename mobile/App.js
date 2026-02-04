import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  AppRegistry,
} from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { StatusBar } from "expo-status-bar";
import { createClient } from "@supabase/supabase-js";

// Configuração Supabase
const supabaseUrl = "https://ntatxgsykdnsfqxwnz.supabase.co";
const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M";
const supabase = createClient(supabaseUrl, supabaseKey);

// Paleta de cores dinâmica
const colors = {
  primary: "#6366f1",
  primaryDark: "#4f46e5",
  secondary: "#06b6d4",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  background: "#f8fafc",
  surface: "#ffffff",
  text: "#1e293b",
  textSecondary: "#64748b",
  border: "#e2e8f0",
};

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Tela de Login simplificada
function LoginScreen({ navigation }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username.trim()) {
      Alert.alert("Erro", "Informe o nome de usuário.");
      return;
    }
    if (!password.trim()) {
      Alert.alert("Erro", "Informe a senha.");
      return;
    }

    setLoading(true);

    try {
      // Buscar usuário no Supabase
      const { data: users, error } = await supabase
        .from("users")
        .select("*, companies(name, active)")
        .eq("username", username)
        .eq("active", true)
        .single();

      if (error || !users) {
        Alert.alert("Erro", "Usuário não encontrado ou inativo.");
        setLoading(false);
        return;
      }

      // Verificar se a empresa está ativa
      if (!users.companies?.active) {
        Alert.alert("Erro", "Empresa inativa.");
        setLoading(false);
        return;
      }

      // Verificar senha (simples para teste)
      if (password === "123456") {
        Alert.alert("Login realizado!", `Bem-vindo, ${users.full_name}!`, [
          {
            text: "OK",
            onPress: () => navigation.navigate("MainTabs", { user: users }),
          },
        ]);
      } else {
        Alert.alert("Erro", "Senha incorreta.");
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
      console.error("Erro no login:", error);
    }

    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <View style={styles.iconCircle}>
          <Ionicons name="construct" size={48} color="#ffffff" />
        </View>
        <Text style={styles.title}>Task Manager</Text>
        <Text style={styles.subtitle}>Acesse sua conta para continuar</Text>
      </View>

      <View style={styles.formContainer}>
        <View style={styles.inputContainer}>
          <Ionicons
            name="person-outline"
            size={20}
            color="#8e8e93"
            style={styles.inputIcon}
          />
          <TextInput
            style={styles.input}
            placeholder="Nome de usuário"
            placeholderTextColor="#8e8e93"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons
            name="lock-closed-outline"
            size={20}
            color="#8e8e93"
            style={styles.inputIcon}
          />
          <TextInput
            style={styles.input}
            placeholder="Senha"
            placeholderTextColor="#8e8e93"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            autoCorrect={false}
          />
          <TouchableOpacity
            style={styles.eyeButton}
            onPress={() => setShowPassword(!showPassword)}
          >
            <Ionicons
              name={showPassword ? "eye-off-outline" : "eye-outline"}
              size={20}
              color="#8e8e93"
            />
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.loginButton, loading && styles.loginButtonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.loginButtonText}>Entrar</Text>
          )}
        </TouchableOpacity>

        <Text style={styles.testCredentials}>Utilize as suas credenciais</Text>
      </View>
    </View>
  );
}

// Tela Home com dados simulados
function HomeScreen({ navigation }) {
  const [tasks] = useState([
    {
      id: 1,
      empresaNome: "TechNet Soluções",
      gerente: "Carlos Silva",
      cliente: "Residencial São Paulo",
      bairro: "Vila Madalena",
      endereco: "Rua Harmonia, 456 - Apto 78",
      status: "pendente",
      prioridade: "alta",
      tipo: "Instalação Residencial",
      prazo: "2024-01-16 18:00",
    },
    {
      id: 2,
      empresaNome: "FibraMax Telecom",
      gerente: "Ana Santos",
      cliente: "Comercial Center",
      bairro: "Pinheiros",
      status: "em_andamento",
      prioridade: "media",
      tipo: "Manutenção Empresarial",
      prazo: "2024-01-15 17:00",
    },
  ]);

  const showNewTaskNotification = async () => {
    Alert.alert(
      "🚨 Nova Tarefa Atribuída",
      "EMPRESA: TechNet Soluções\n\nGERENTE: Carlos Silva\n\nCLIENTE: Edifício Copacabana\n\nLOCALIZAÇÃO: Itaim Bibi\nRua Pedroso Alvarenga, 1245\n\nTIPO: Instalação Urgente\nPRIORIDADE: ALTA\n\n⏰ PRAZO: Hoje até 19:00",
      [
        { text: "Ver Depois", style: "cancel" },
        { text: "Aceitar Tarefa", onPress: () => {} },
      ]
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "pendente":
        return colors.warning;
      case "em_andamento":
        return colors.secondary;
      case "concluida":
        return colors.success;
      default:
        return colors.textSecondary;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "pendente":
        return "Pendente";
      case "em_andamento":
        return "Em Andamento";
      case "concluida":
        return "Concluída";
      default:
        return status;
    }
  };

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case "alta":
        return colors.error;
      case "media":
        return colors.warning;
      case "baixa":
        return colors.success;
      default:
        return colors.textSecondary;
    }
  };

  const pendentes = tasks.filter((t) => t.status === "pendente").length;
  const emAndamento = tasks.filter((t) => t.status === "em_andamento").length;
  const concluidas = tasks.filter((t) => t.status === "concluida").length;

  return (
    <ScrollView
      style={[styles.homeContainer, { backgroundColor: colors.background }]}
    >
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.welcomeTitle, { color: colors.primary }]}>
          Minhas Tarefas
        </Text>
        <Text style={[styles.welcomeSubtitle, { color: colors.textSecondary }]}>
          João Técnico - Infraestrutura
        </Text>
      </View>

      <View style={styles.statsContainer}>
        <View
          style={[
            styles.statCard,
            { borderLeftColor: colors.warning, borderLeftWidth: 4 },
          ]}
        >
          <Ionicons name="time" size={28} color={colors.warning} />
          <Text style={[styles.statNumber, { color: colors.text }]}>
            {pendentes}
          </Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>
            Pendentes
          </Text>
        </View>
        <View
          style={[
            styles.statCard,
            { borderLeftColor: colors.secondary, borderLeftWidth: 4 },
          ]}
        >
          <Ionicons name="play-circle" size={28} color={colors.secondary} />
          <Text style={[styles.statNumber, { color: colors.text }]}>
            {emAndamento}
          </Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>
            Em Andamento
          </Text>
        </View>
        <View
          style={[
            styles.statCard,
            { borderLeftColor: colors.success, borderLeftWidth: 4 },
          ]}
        >
          <Ionicons name="checkmark-circle" size={28} color={colors.success} />
          <Text style={[styles.statNumber, { color: colors.text }]}>
            {concluidas}
          </Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>
            Concluídas
          </Text>
        </View>
      </View>

      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Tarefas Recentes
        </Text>
      </View>

      {tasks.map((task) => (
        <TouchableOpacity
          key={task.id}
          style={[styles.taskCard, { backgroundColor: colors.surface }]}
        >
          <View style={styles.taskHeader}>
            <View style={styles.taskInfo}>
              <Text style={[styles.taskEmpresa, { color: colors.text }]}>
                {task.empresaNome}
              </Text>
              <Text style={[styles.taskTipo, { color: colors.primary }]}>
                {task.tipo}
              </Text>
              <Text
                style={[styles.taskCliente, { color: colors.textSecondary }]}
              >
                {task.cliente} - {task.bairro}
              </Text>
            </View>
            <View style={styles.taskMeta}>
              <View
                style={[
                  styles.priorityDot,
                  { backgroundColor: getPriorityColor(task.prioridade) },
                ]}
              />
            </View>
          </View>
          <View style={styles.taskFooter}>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(task.status) },
              ]}
            >
              <Text style={styles.statusText}>
                {getStatusText(task.status)}
              </Text>
            </View>
            <Text style={[styles.taskPrazo, { color: colors.textSecondary }]}>
              ⏰ {task.prazo}
            </Text>
          </View>
        </TouchableOpacity>
      ))}

      <TouchableOpacity
        style={[
          styles.testNotificationButton,
          { backgroundColor: colors.primary },
        ]}
        onPress={showNewTaskNotification}
      >
        <Ionicons name="notifications" size={20} color="white" />
        <Text style={styles.testNotificationText}>Simular Nova Tarefa</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// Tela de Perfil
function ProfileScreen({ navigation }) {
  const handleLogout = () => {
    Alert.alert("Sair", "Deseja realmente sair da aplicação?", [
      { text: "Cancelar", style: "cancel" },
      { text: "Sair", onPress: () => navigation.navigate("Login") },
    ]);
  };

  return (
    <View
      style={[styles.profileContainer, { backgroundColor: colors.background }]}
    >
      <View style={[styles.profileHeader, { backgroundColor: colors.surface }]}>
        <View
          style={[styles.avatarContainer, { backgroundColor: colors.primary }]}
        >
          <Ionicons name="person" size={48} color="#ffffff" />
        </View>
        <Text style={[styles.profileName, { color: colors.text }]}>
          João Técnico
        </Text>
        <Text style={[styles.profileRole, { color: colors.textSecondary }]}>
          Infraestrutura
        </Text>
      </View>

      <TouchableOpacity
        style={[
          styles.logoutButton,
          { backgroundColor: colors.surface, borderColor: colors.error },
        ]}
        onPress={handleLogout}
      >
        <Ionicons name="log-out-outline" size={20} color={colors.error} />
        <Text style={[styles.logoutButtonText, { color: colors.error }]}>
          Sair
        </Text>
      </TouchableOpacity>
    </View>
  );
}

// Navegação por Abas
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === "Home") {
            iconName = focused ? "home" : "home-outline";
          } else if (route.name === "Profile") {
            iconName = focused ? "person" : "person-outline";
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: "gray",
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: "Início" }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: "Perfil" }}
      />
    </Tab.Navigator>
  );
}

function App() {
  return (
    <>
      <StatusBar style="auto" />
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="MainTabs"
            component={MainTabs}
            options={{ headerShown: false }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 40,
  },
  iconCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: "800",
    color: colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  formContainer: {
    width: "100%",
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: colors.border,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  inputIcon: {
    marginLeft: 16,
  },
  input: {
    flex: 1,
    paddingVertical: 16,
    paddingHorizontal: 12,
    fontSize: 16,
    color: colors.text,
  },
  eyeButton: {
    padding: 16,
  },
  loginButton: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: "center",
    marginTop: 8,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "700",
  },
  testCredentials: {
    textAlign: "center",
    marginTop: 16,
    fontSize: 14,
    color: colors.textSecondary,
    fontStyle: "italic",
  },
  homeContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: 24,
    alignItems: "center",
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.primary,
    marginBottom: 8,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: colors.surface,
    padding: 20,
    borderRadius: 20,
    alignItems: "center",
    flex: 1,
    marginHorizontal: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: "800",
    color: colors.text,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
    textAlign: "center",
    fontWeight: "600",
  },
  sectionHeader: {
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
  },
  taskCard: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 16,
    padding: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  taskHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  taskInfo: {
    flex: 1,
  },
  taskEmpresa: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 2,
  },
  taskTipo: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: "600",
    marginBottom: 4,
  },
  taskCliente: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  taskMeta: {
    alignItems: "flex-end",
  },
  priorityDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  taskFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
  },
  taskPrazo: {
    fontSize: 12,
    color: colors.textSecondary,
    fontWeight: "500",
  },
  testNotificationButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primary,
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 30,
    paddingVertical: 16,
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  testNotificationText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
    marginLeft: 8,
  },
  profileContainer: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 20,
  },
  profileHeader: {
    alignItems: "center",
    marginBottom: 40,
    backgroundColor: colors.surface,
    padding: 30,
    borderRadius: 20,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  profileName: {
    fontSize: 24,
    fontWeight: "800",
    color: colors.text,
    marginBottom: 4,
  },
  profileRole: {
    fontSize: 16,
    color: colors.textSecondary,
    fontWeight: "600",
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderRadius: 16,
    paddingVertical: 16,
    borderWidth: 2,
    borderColor: colors.error,
  },
  logoutButtonText: {
    color: colors.error,
    fontSize: 16,
    fontWeight: "700",
    marginLeft: 8,
  },
});

AppRegistry.registerComponent("main", () => App);
export default App;
