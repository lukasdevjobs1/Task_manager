import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';
import '../config/theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final themeProvider = Provider.of<ThemeProvider>(context);
    final user = authProvider.user;

    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: ListView(
        children: [
          // Header com info do usuário
          Container(
            padding: const EdgeInsets.all(24),
            color: AppTheme.primaryColor.withOpacity(0.1),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 50,
                  backgroundColor: AppTheme.primaryColor,
                  child: Text(
                    user?.fullName.substring(0, 2).toUpperCase() ?? 'U',
                    style: const TextStyle(fontSize: 32, color: Colors.white),
                  ),
                ),
                const SizedBox(height: 16),
                Text(user?.fullName ?? '', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 4),
                Text('@${user?.username ?? ''}', style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),

          // Informações
          ListTile(
            leading: const Icon(Icons.business),
            title: const Text('Empresa'),
            subtitle: Text(user?.companyName ?? 'N/A'),
          ),
          ListTile(
            leading: const Icon(Icons.group),
            title: const Text('Equipe'),
            subtitle: Text(user?.team.toUpperCase() ?? 'N/A'),
          ),

          const Divider(),

          // Configurações
          ListTile(
            leading: const Icon(Icons.dark_mode_outlined),
            title: const Text('Tema Escuro'),
            trailing: Switch(
              value: themeProvider.themeMode == ThemeMode.dark,
              onChanged: (value) {
                themeProvider.setThemeMode(value ? ThemeMode.dark : ThemeMode.light);
              },
            ),
          ),

          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Tarefas Concluídas'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.push('/completed-tasks'),
          ),

          ListTile(
            leading: const Icon(Icons.analytics_outlined),
            title: const Text('Relatórios'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.push('/reports'),
          ),

          const Divider(),

          // Logout
          ListTile(
            leading: const Icon(Icons.logout, color: AppTheme.errorColor),
            title: const Text('Sair', style: TextStyle(color: AppTheme.errorColor)),
            onTap: () async {
              await authProvider.logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
    );
  }
}
