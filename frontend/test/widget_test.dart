import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('App renders splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const HandwritingApp());

    // Splash screen should show the app title.
    expect(find.text('Handwriting Recognition'), findsWidgets);
  });
}