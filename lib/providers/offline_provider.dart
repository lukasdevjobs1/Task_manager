import 'package:flutter/material.dart';
import '../services/offline_service.dart';

class OfflineProvider with ChangeNotifier {
  bool _isOnline = true;
  int _pendingUpdates = 0;
  DateTime? _lastSync;
  
  bool get isOnline => _isOnline;
  int get pendingUpdates => _pendingUpdates;
  DateTime? get lastSync => _lastSync;
  bool get hasPendingUpdates => _pendingUpdates > 0;
  
  OfflineProvider() {
    _initialize();
  }
  
  Future<void> _initialize() async {
    await checkConnectivity();
    _pendingUpdates = OfflineService.getPendingUpdatesCount();
    _lastSync = OfflineService.getLastSync();
    notifyListeners();
  }
  
  Future<void> checkConnectivity() async {
    _isOnline = await OfflineService.isOnline();
    notifyListeners();
  }
  
  Future<int> syncPendingUpdates() async {
    final syncCount = await OfflineService.syncPendingUpdates();
    _pendingUpdates = OfflineService.getPendingUpdatesCount();
    _lastSync = DateTime.now();
    notifyListeners();
    return syncCount;
  }
  
  void updatePendingCount() {
    _pendingUpdates = OfflineService.getPendingUpdatesCount();
    notifyListeners();
  }
}
