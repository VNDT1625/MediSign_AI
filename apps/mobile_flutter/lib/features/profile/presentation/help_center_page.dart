import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kBrand = Color(0xFF0284C7);
const _kBrandSoft = Color(0xFFE0F2FE);

class _Faq {
  final String q;
  final String a;
  const _Faq(this.q, this.a);
}

const _faqs = <_Faq>[
  _Faq(
    'Làm sao để hỏi AI về thuốc?',
    'Mở tab "Chat" rồi nhập tên thuốc hoặc chụp đơn thuốc. AI sẽ tóm tắt liều dùng, tương tác và lưu ý.',
  ),
  _Faq(
    'Tôi có thể đổi mật khẩu ở đâu?',
    'Vào tab "Hồ sơ" → "Đổi mật khẩu", nhập mật khẩu hiện tại và mật khẩu mới (tối thiểu 8 ký tự).',
  ),
  _Faq(
    'Dữ liệu nhật ký cảm xúc có được đồng bộ không?',
    'Khi đăng nhập, nhật ký được đồng bộ qua Soul Garden Service. Khi offline, dữ liệu lưu cục bộ và sẽ tự đồng bộ khi có mạng.',
  ),
  _Faq(
    'Tôi có thể xoá tài khoản không?',
    'Có. Vào "Quyền riêng tư" → "Yêu cầu xoá dữ liệu". Toàn bộ dữ liệu sẽ được xoá trong 14 ngày làm việc.',
  ),
  _Faq(
    'Tủ thuốc lưu thông tin gì?',
    'Tủ thuốc lưu danh sách thuốc đang dùng, lịch nhắc liều và lịch sử dùng thuốc. Bạn có thể xuất file qua Quyền riêng tư → Tải dữ liệu.',
  ),
  _Faq(
    'Ứng dụng có hỗ trợ ngôn ngữ ký hiệu không?',
    'Có. Trong Cài đặt → Cách giao tiếp, bạn có thể bật chế độ ngôn ngữ ký hiệu. Hệ thống sẽ hiển thị video VSL khi cần.',
  ),
];

class HelpCenterPage extends StatelessWidget {
  const HelpCenterPage({super.key});

  void _showComingSoon(BuildContext context, String label) {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$label đang phát triển — sẽ mở sớm.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        foregroundColor: _kInk,
        title: const Text(
          'Trung tâm hỗ trợ',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: _kInk,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          children: [
            Container(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [_kBrandSoft, Color(0xFFF0F9FF)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white, width: 1.5),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: const BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.support_agent_rounded,
                        color: _kBrand, size: 22),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Chúng tôi luôn ở đây',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: _kInk,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'Tìm câu trả lời nhanh hoặc liên hệ đội hỗ trợ.',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 12,
                            color: _kInkSoft,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: _ContactCard(
                    icon: Icons.email_outlined,
                    iconColor: _kBrand,
                    title: 'Email',
                    sub: 'support@medisign.ai',
                    onTap: () => _showComingSoon(context, 'Liên hệ qua email'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _ContactCard(
                    icon: Icons.chat_bubble_outline_rounded,
                    iconColor: const Color(0xFF8B5CF6),
                    title: 'Chat trực tuyến',
                    sub: 'Phản hồi trong ngày',
                    onTap: () => _showComingSoon(context, 'Chat trực tuyến'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 4),
              child: Row(
                children: [
                  Icon(Icons.help_outline_rounded,
                      size: 16, color: _kBrand),
                  SizedBox(width: 6),
                  Text(
                    'Câu hỏi thường gặp',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: _kInk,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _kBorder),
              ),
              child: Column(
                children: List.generate(_faqs.length, (i) {
                  final faq = _faqs[i];
                  final isLast = i == _faqs.length - 1;
                  return _FaqTile(faq: faq, isLast: isLast);
                }),
              ),
            ),
            const SizedBox(height: 18),
            Center(
              child: Text(
                'MediSign AI · Phiên bản 1.0.0',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11,
                  color: _kInkMuted,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContactCard extends StatelessWidget {
  const _ContactCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.sub,
    required this.onTap,
  });

  final IconData icon;
  final Color iconColor;
  final String title;
  final String sub;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: _kBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 18, color: iconColor),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                sub,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11.5,
                  color: _kInkSoft,
                  height: 1.2,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FaqTile extends StatelessWidget {
  const _FaqTile({required this.faq, required this.isLast});
  final _Faq faq;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: !isLast
            ? const Border(
                bottom: BorderSide(color: _kBorder, width: 0.6),
              )
            : null,
      ),
      child: Theme(
        // Bỏ default divider của ExpansionTile.
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 14),
          childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 12),
          iconColor: _kInkSoft,
          collapsedIconColor: _kInkSoft,
          title: Text(
            faq.q,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 13.5,
              fontWeight: FontWeight.w700,
              color: _kInk,
            ),
          ),
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                faq.a,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12.5,
                  color: _kInkSoft,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
