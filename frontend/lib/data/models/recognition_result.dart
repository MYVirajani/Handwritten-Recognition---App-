class RecognitionResult {
  final String recognizedText;
  final double? confidenceScore;
  final double? processingTime;

  const RecognitionResult({
    required this.recognizedText,
    this.confidenceScore,
    this.processingTime,
  });

  factory RecognitionResult.fromJson(Map<String, dynamic> json) {
    return RecognitionResult(
      recognizedText: json['recognized_text'] ?? json['text'] ?? '',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      processingTime: (json['processing_time'] as num?)?.toDouble(),
    );
  }
}