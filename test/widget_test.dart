import 'package:flutter_test/flutter_test.dart';
import 'package:cropora_ai/main.dart';

void main() {
  testWidgets('CroporaApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const CroporaApp());
    expect(find.text('CROPORA'), findsOneWidget);
  });
}
