import 'dart:io';
import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../../core/constants.dart';
import '../models/recognition_result.dart';

class RecognitionRepository {
  final ApiClient _apiClient;

  RecognitionRepository(this._apiClient);

  Future<RecognitionResult> recognizePdf(File pdfFile) async {
    final fileName = pdfFile.path.split('/').last;

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(pdfFile.path, filename: fileName),
    });

    try {
      final response = await _apiClient.dio.post(
        ApiConstants.recognizeEndpoint,
        data: formData,
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data is Map<String, dynamic>
            ? response.data as Map<String, dynamic>
            : Map<String, dynamic>.from(response.data as Map);
        return RecognitionResult.fromJson(data);
      }
      throw Exception('Failed to recognize text');
    } on DioException catch (e) {
      throw Exception(_messageFor(e));
    }
  }

  Future<List<int>> downloadPdf(String text) async {
    try {
      final response = await _apiClient.dio.post(
        ApiConstants.downloadPdfEndpoint,
        data: {'text': text},
        options: Options(responseType: ResponseType.bytes),
      );

      if (response.statusCode == 200 && response.data != null) {
        return response.data as List<int>;
      }
      throw Exception('Failed to download PDF');
    } on DioException catch (e) {
      throw Exception(_messageFor(e));
    }
  }

  String _messageFor(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.unknown) {
      return 'Failed to connect to server. Please ensure the Flask server '
          'is running on port 5000.';
    }
    if (e.type == DioExceptionType.receiveTimeout) {
      return 'The server took too long to respond. Large or complex PDFs '
          'may need more processing time.';
    }

    final data = e.response?.data;
    if (data is Map && data['error'] != null) {
      return data['error'].toString();
    }
    return e.message ?? 'Something went wrong. Please try again.';
  }
}