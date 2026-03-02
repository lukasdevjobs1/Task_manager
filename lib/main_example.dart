// ARQUIVO DE EXEMPLO — NÃO contém credenciais reais.
// Copie este arquivo para main.dart e preencha com os valores do seu projeto.
//
// Como obter as credenciais:
//   Supabase Dashboard → Settings → API
//     - Project URL  → SUPABASE_URL
//     - anon/public  → SUPABASE_ANON_KEY
//
// NUNCA commite o main.dart com valores reais.

import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:firebase_core/firebase_core.dart';

import 'config/theme.dart';
import 'config/routes.dart';
import 'providers/auth_provider.dart';
import 'providers/task_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/offline_provider.dart';
import 'services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Configurar orientação (apenas mobile)
  if (!kIsWeb) {
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
  }

  // Inicializar Hive para cache offline
  await Hive.initFlutter();
  await Hive.openBox('tasks_cache');
  await Hive.openBox('user_cache');

  // Inicializar Firebase (apenas mobile)
  if (!kIsWeb) {
    try {
      await Firebase.initializeApp();
    } catch (e) {
      print('Firebase initialization error: $e');
    }
  }

  // Inicializar Supabase
  // Substitua os valores abaixo pelos do seu projeto (Supabase Dashboard > Settings > API)
  await Supabase.initialize(
    url: 'https://SEU_PROJETO.supabase.co',
    anonKey: 'SUA_ANON_KEY_AQUI',
  );

  // Inicializar serviço de notificações (apenas mobile)
  if (!kIsWeb) {
    try {
      await NotificationService.initialize();
    } catch (e) {
      print('Notification service error: $e');
    }
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => TaskProvider()),
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
        ChangeNotifierProvider(create: (_) => OfflineProvider()),
      ],
      child: Consumer2<ThemeProvider, AuthProvider>(
        builder: (context, themeProvider, authProvider, child) {
          return MaterialApp.router(
            title: 'Task Manager ISP',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            routerConfig: AppRouter.createRouter(authProvider),
          );
        },
      ),
    );
  }
}
