class ApiConstants {

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:5000',
  );

  static const String recognizeEndpoint = '$baseUrl/api/recognize';
  static const String downloadPdfEndpoint = '$baseUrl/api/download-pdf';
}