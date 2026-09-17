import 'package:dio/dio.dart';
import 'constants.dart';

class ApiClient {
  final Dio dio;

  ApiClient()
      : dio = Dio(
    BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      // TrOCR inference on CPU can take a while - allow a generous window.
      receiveTimeout: const Duration(seconds: 120),
    ),
  );
}