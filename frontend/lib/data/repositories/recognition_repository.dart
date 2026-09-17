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
      throw Exception('Unexpected response: ${response.statusCode}');
    } on DioException catch (e) {
      final data = e.response?.data;
      final message = (data is Map && data['error'] != null)
          ? data['error'].toString()
          : (e.message ?? 'Failed to reach the recognition server');
      throw Exception(message);
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
      throw Exception('Unexpected response: ${response.statusCode}');
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Failed to download PDF');
    }
  }
}