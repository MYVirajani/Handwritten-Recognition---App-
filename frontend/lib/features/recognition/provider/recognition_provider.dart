import 'dart:io';
import 'package:flutter/material.dart';

enum RecognitionStatus { initial, loading, success, failure }

class RecognitionProvider extends ChangeNotifier {
  File? file;
  RecognitionStatus status = RecognitionStatus.initial;
  String? recognizedText;
  double? confidenceScore;
  double? processingTime;
  String? errorMessage;

  void setFile(File newFile) {
    file = newFile;
    status = RecognitionStatus.initial;
    recognizedText = null;
    errorMessage = null;
    notifyListeners();
  }

  void setFileError(String message) {
    file = null;
    errorMessage = message;
    status = RecognitionStatus.initial;
    recognizedText = null;
    notifyListeners();
  }

  void removeFile() {
    file = null;
    status = RecognitionStatus.initial;
    recognizedText = null;
    errorMessage = null;
    notifyListeners();
  }

  Future<void> recognize() async {
    if (file == null) return;
    status = RecognitionStatus.loading;
    errorMessage = null;
    notifyListeners();


    await Future.delayed(const Duration(seconds: 2));

    recognizedText =
    'This is a mocked recognition result.';
    confidenceScore = 0.94;
    processingTime = 1.8;
    status = RecognitionStatus.success;
    notifyListeners();
  }

  void reset() {
    file = null;
    status = RecognitionStatus.initial;
    recognizedText = null;
    errorMessage = null;
    notifyListeners();
  }
}