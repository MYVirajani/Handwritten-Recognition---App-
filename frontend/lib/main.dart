import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'features/recognition/provider/recognition_provider.dart';
import 'features/splash/splash_screen.dart';

void main() {
  runApp(const HandwritingApp());
}

class HandwritingApp extends StatelessWidget {
  const HandwritingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => RecognitionProvider(),
      child: MaterialApp(
        title: 'Handwriting Recognition',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
          useMaterial3: true,
        ),
        home: const SplashScreen(),
      ),
    );
  }
}