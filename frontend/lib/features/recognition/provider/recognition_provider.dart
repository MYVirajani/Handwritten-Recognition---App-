import 'dart:io';
import 'package:flutter/material.dart';
import '../../../data/models/recognition_result.dart';
import '../../../data/repositories/recognition_repository.dart';

enum RecognitionStatus { initial, loading, success, failure }

class RecognitionProvider extends ChangeNotifier {
  final RecognitionRepository _repository;
  RecognitionProvider(this._repository);

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

    try {
      final RecognitionResult result = await _repository.recognizePdf(file!);
      recognizedText = result.recognizedText;
      confidenceScore = result.confidenceScore;
      processingTime = result.processingTime;
      status = RecognitionStatus.success;
    } catch (e) {
      errorMessage = e.toString().replaceFirst('Exception: ', '');
      status = RecognitionStatus.failure;
    }
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