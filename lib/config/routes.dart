import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../screens/login_screen.dart';
import '../screens/home_screen.dart';
import '../screens/task_detail_screen.dart';
import '../screens/task_execute_screen.dart';
import '../screens/notifications_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/completed_tasks_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/reports_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final isAuthenticated = authProvider.isAuthenticated;
      final isLoginRoute = state.matchedLocation == '/login';
      
      // Se não autenticado e não está na tela de login, redirecionar
      if (!isAuthenticated && !isLoginRoute) {
        return '/login';
      }
      
      // Se autenticado e está na tela de login, redirecionar para home
      if (isAuthenticated && isLoginRoute) {
        return '/';
      }
      
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/',
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/task/:id',
        name: 'task-detail',
        builder: (context, state) {
          final taskId = int.parse(state.pathParameters['id']!);
          return TaskDetailScreen(taskId: taskId);
        },
      ),
      GoRoute(
        path: '/task/:id/execute',
        name: 'task-execute',
        builder: (context, state) {
          final taskId = int.parse(state.pathParameters['id']!);
          return TaskExecuteScreen(taskId: taskId);
        },
      ),
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/completed-tasks',
        name: 'completed-tasks',
        builder: (context, state) => const CompletedTasksScreen(),
      ),
      GoRoute(
        path: '/task/:id/chat',
        name: 'chat',
        builder: (context, state) {
          final taskId = int.parse(state.pathParameters['id']!);
          final taskTitle = state.uri.queryParameters['title'] ?? 'Chat';
          return ChatScreen(taskId: taskId, taskTitle: taskTitle);
        },
      ),
      GoRoute(
        path: '/reports',
        name: 'reports',
        builder: (context, state) => const ReportsScreen(),
      ),
    ],
  );
}
