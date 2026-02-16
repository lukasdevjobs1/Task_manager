import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/user.dart';

class StorageService {
  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  
  // Keys
  static const String _userKey = 'user_data';
  static const String _tokenKey = 'auth_token';
  static const String _themeKey = 'theme_mode';
  static const String _offlineModeKey = 'offline_mode';
  
  // Salvar usuário
  static Future<void> saveUser(User user) async {
    await _secureStorage.write(
      key: _userKey,
      value: jsonEncode(user.toJson()),
    );
  }
  
  // Obter usuário
  static Future<User?> getUser() async {
    try {
      final userString = await _secureStorage.read(key: _userKey);
      if (userString == null) return null;
      
      final userJson = jsonDecode(userString) as Map<String, dynamic>;
      return User.fromJson(userJson);
    } catch (e) {
      print('Erro ao obter usuário: $e');
      return null;
    }
  }
  
  // Remover usuário (logout)
  static Future<void> removeUser() async {
    await _secureStorage.delete(key: _userKey);
    await _secureStorage.delete(key: _tokenKey);
  }
  
  // Salvar token
  static Future<void> saveToken(String token) async {
    await _secureStorage.write(key: _tokenKey, value: token);
  }
  
  // Obter token
  static Future<String?> getToken() async {
    return await _secureStorage.read(key: _tokenKey);
  }
  
  // Preferências - Tema
  static Future<void> saveThemeMode(String mode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_themeKey, mode);
  }
  
  static Future<String> getThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_themeKey) ?? 'system';
  }
  
  // Preferências - Modo Offline
  static Future<void> setOfflineMode(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_offlineModeKey, enabled);
  }
  
  static Future<bool> getOfflineMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_offlineModeKey) ?? false;
  }
  
  // Limpar tudo
  static Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
