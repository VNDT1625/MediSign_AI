import 'package:flutter_test/flutter_test.dart';
import 'package:medisign_mobile/app.dart';

void main() {
  testWidgets('renders onboarding with MediSign AI title',
      (WidgetTester tester) async {
    await tester.pumpWidget(const MediSignApp());

    expect(find.text('MediSign AI'), findsOneWidget);
  });
}

