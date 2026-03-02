import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../screens/login_screen.dart';
import '../screens/home_screen.dart';
import '../screens/tasks_screen.dart';
import '../screens/task_detail_screen.dart';
import '../screens/task_execute_screen.dart';
import '../screens/notifications_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/completed_tasks_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/reports_screen.dart';
import '../widgets/main_shell.dart';

class AppRouter {
  static GoRouter createRouter(AuthProvider authProvider) {
    return GoRouter(
      initialLocation: '/home',
      refreshListenable: authProvider,
      redirect: (context, state) {
        final isAuthenticated = authProvider.isAuthenticated;
        final isLoginRoute = state.matchedLocation == '/login';

        if (!isAuthenticated && !isLoginRoute) return '/login';
        if (isAuthenticated && isLoginRoute) return '/home';

        // Redirecionar raiz antiga para /home
        if (isAuthenticated && state.matchedLocation == '/') return '/home';

        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          name: 'login',
          builder: (context, state) => const LoginScreen(),
        ),

        // Shell principal com BottomNavigationBar
        StatefulShellRoute.indexedStack(
          builder: (context, state, navigationShell) =>
              MainShell(navigationShell: navigationShell),
          branches: [
            // Aba 0 — Início (Dashboard)
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/home',
                  name: 'home',
                  builder: (context, state) => const HomeScreen(),
                ),
              ],
            ),

            // Aba 1 — Tarefas
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/tasks',
                  name: 'tasks',
                  builder: (context, state) => const TasksScreen(),
                ),
              ],
            ),

            // Aba 2 — Relatórios
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/reports',
                  name: 'reports',
                  builder: (context, state) => const ReportsScreen(),
                ),
              ],
            ),

            // Aba 3 — Perfil
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/profile',
                  name: 'profile',
                  builder: (context, state) => const ProfileScreen(),
                ),
              ],
            ),
          ],
        ),

        // Telas full-screen (sem BottomNavigationBar)
        GoRoute(
          path: '/task/:id',
          name: 'task-detail',
          builder: (context, state) {
            final taskId = int.parse(state.pathParameters['id']!);
            return TaskDetailScreen(taskId: taskId);
          },
          routes: [
            GoRoute(
              path: 'execute',
              name: 'task-execute',
              builder: (context, state) {
                final taskId = int.parse(state.pathParameters['id']!);
                return TaskExecuteScreen(taskId: taskId);
              },
            ),
            GoRoute(
              path: 'chat',
              name: 'chat',
              builder: (context, state) {
                final taskId = int.parse(state.pathParameters['id']!);
                final taskTitle =
                    state.uri.queryParameters['title'] ?? 'Chat';
                return ChatScreen(taskId: taskId, taskTitle: taskTitle);
              },
            ),
          ],
        ),

        GoRoute(
          path: '/notifications',
          name: 'notifications',
          builder: (context, state) => const NotificationsScreen(),
        ),

        GoRoute(
          path: '/completed-tasks',
          name: 'completed-tasks',
          builder: (context, state) => const CompletedTasksScreen(),
        ),
      ],
    );
  }
}
