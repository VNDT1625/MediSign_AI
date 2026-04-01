import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisign_mobile/core/models/consult_mode.dart';
import 'package:medisign_mobile/features/onboarding/presentation/onboarding_page.dart';

void main() {
  /// Helper to pump the onboarding page inside a MaterialApp.
  Widget buildSubject({
    ConsultMode initialMode = ConsultMode.hybrid,
    OnOnboardingComplete? onComplete,
  }) {
    return MaterialApp(
      home: OnboardingPage(
        initialMode: initialMode,
        onComplete: onComplete ?? (_) {},
      ),
    );
  }

  group('OnboardingPage', () {
    testWidgets('renders app title "MediSign AI"', (tester) async {
      await tester.pumpWidget(buildSubject());

      expect(find.text('MediSign AI'), findsOneWidget);
    });

    testWidgets('renders all 3 mode buttons', (tester) async {
      await tester.pumpWidget(buildSubject());

      // Each mode should show its user-friendly title.
      expect(find.text('Tốt nhất cho tôi'), findsOneWidget);
      expect(find.text('Riêng tư tuyệt đối'), findsOneWidget);
      expect(find.text('Nhẹ nhất'), findsOneWidget);
    });

    testWidgets('renders helper text', (tester) async {
      await tester.pumpWidget(buildSubject());

      expect(
        find.textContaining('Không biết chọn gì'),
        findsOneWidget,
      );
      expect(
        find.text('Đổi lại bất cứ lúc nào trong Cài đặt'),
        findsOneWidget,
      );
    });

    testWidgets('tapping mode button shows confirmation and calls onComplete',
        (tester) async {
      ConsultMode? result;

      await tester.pumpWidget(buildSubject(
        onComplete: (mode) => result = mode,
      ));

      // Tap the "Riêng tư tuyệt đối" button (Local mode).
      await tester.tap(find.text('Riêng tư tuyệt đối'));
      await tester.pumpAndSettle();

      // Confirmation dialog should appear.
      expect(find.text('Bạn chọn: Riêng tư tuyệt đối'), findsOneWidget);

      // Tap "Tiếp tục" to confirm.
      await tester.tap(find.text('Tiếp tục'));
      // Pump past the dialog dismiss animation + Future.delayed(300ms).
      // Cannot use pumpAndSettle because CircularProgressIndicator animates forever.
      await tester.pump(const Duration(milliseconds: 100)); // dismiss dialog
      await tester.pump(const Duration(milliseconds: 400)); // past Future.delayed

      expect(result, equals(ConsultMode.local));
    });

    testWidgets('no overflow at textScaleFactor 2.0', (tester) async {
      tester.view.devicePixelRatio = 1.0;
      tester.view.physicalSize = const Size(412, 915);

      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(
            textScaler: TextScaler.linear(2.0),
            size: Size(412, 915),
          ),
          child: buildSubject(),
        ),
      );

      // Should not throw overflow errors.
      expect(tester.takeException(), isNull);
    });

    testWidgets('no overflow at 320px width (small screen)', (tester) async {
      tester.view.devicePixelRatio = 1.0;
      tester.view.physicalSize = const Size(320, 568);

      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(
            size: Size(320, 568),
          ),
          child: buildSubject(),
        ),
      );

      // Should not throw overflow errors.
      expect(tester.takeException(), isNull);
    });
  });
}
