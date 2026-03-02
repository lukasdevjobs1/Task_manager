import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/supabase_service.dart';
import '../services/storage_service.dart';
import '../services/notification_service.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  String? _errorMessage;
  
  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _user != null;
  
  // Inicializar - verificar se há usuário salvo
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      _user = await StorageService.getUser();
    } catch (e) {
      print('Erro ao inicializar auth: $e');
    }
    
    _isLoading = false;
    notifyListeners();
  }
  
  // Login
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      print('Tentando login: $username');
      final user = await SupabaseService.authenticateUser(username, password);
      print('Resposta do Supabase: ${user != null ? user.username : "null"}');
      
      if (user != null) {
        _user = user;
        await StorageService.saveUser(user);

        // Atualizar push token para receber notificações
        await NotificationService.updateTokenOnServer(user.id);

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Usuário ou senha inválidos';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      print('Erro no login: $e');
      _errorMessage = 'Erro ao fazer login: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  // Logout
  Future<void> logout() async {
    _user = null;
    await StorageService.removeUser();
    notifyListeners();
  }
  
  // Limpar erro
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
