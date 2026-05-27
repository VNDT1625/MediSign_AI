import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kBrand = Color(0xFF16A34A);
const _kSuccess = Color(0xFF10B981);

const _kPrefsPrefix = 'profile.privacy.';

class _PrivacyOption {
  final String key;
  final String title;
  final String desc;
  final IconData icon;
  final Color iconColor;
  final Color iconBg;
  final bool defaultOn;

  const _PrivacyOption({
    required this.key,
    required this.title,
    required this.desc,
    required this.icon,
    required this.iconColor,
    required this.iconBg,
    required this.defaultOn,
  });
}

const _options = <_PrivacyOption>[
  _PrivacyOption(
    key: 'analytics',
    title: 'Cho phép phân tích ẩn danh',
    desc: 'Giúp cải thiện ứng dụng — không kèm dữ liệu cá nhân.',
    icon: Icons.insights_rounded,
    iconColor: _kBrand,
    iconBg: Color(0xFFDCFCE7),
    defaultOn: true,
  ),
  _PrivacyOption(
    key: 'crash_reports',
    title: 'Gửi báo cáo lỗi',
    desc: 'Tự động gửi log khi ứng dụng gặp sự cố.',
    icon: Icons.bug_report_outlined,
    iconColor: Color(0xFFF97316),
    iconBg: Color(0xFFFFEDD5),
    defaultOn: true,
  ),
  _PrivacyOption(
    key: 'personalized_tips',
    title: 'Gợi ý cá nhân hoá',
    desc: 'Dùng nhật ký cảm xúc để gợi ý nội dung phù hợp.',
    icon: Icons.auto_awesome_rounded,
    iconColor: Color(0xFF8B5CF6),
    iconBg: Color(0xFFEDE9FE),
    defaultOn: true,
  ),
  _PrivacyOption(
    key: 'share_doctor',
    title: 'Chia sẻ tóm tắt với bác sĩ',
    desc: 'Cho phép xuất tóm tắt tình trạng khi bạn yêu cầu.',
    icon: Icons.medical_services_outlined,
    iconColor: Color(0xFF0284C7),
    iconBg: Color(0xFFE0F2FE),
    defaultOn: false,
  ),
  _PrivacyOption(
    key: 'biometric_lock',
    title: 'Khoá ứng dụng bằng sinh trắc',
    desc: 'Yêu cầu vân tay/Face ID khi mở ứng dụng.',
    icon: Icons.fingerprint_rounded,
    iconColor: _kInk,
    iconBg: Color(0xFFF1F5F9),
    defaultOn: false,
  ),
];

class PrivacyPage extends StatefulWidget {
  const PrivacyPage({super.key});

  @override
  State<PrivacyPage> createState() => _PrivacyPageState();
}

class _PrivacyPageState extends State<PrivacyPage> {
  final Map<String, bool> _values = {};
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final next = <String, bool>{};
    for (final opt in _options) {
      next[opt.key] =
          prefs.getBool(_kPrefsPrefix + opt.key) ?? opt.defaultOn;
    }
    if (!mounted) return;
    setState(() {
      _values.addAll(next);
      _loading = false;
    });
  }

  Future<void> _toggle(_PrivacyOption opt, bool value) async {
    HapticFeedback.selectionClick();
    setState(() => _values[opt.key] = value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_kPrefsPrefix + opt.key, value);
  }

  void _exportData() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Yêu cầu xuất dữ liệu đã được ghi nhận. Bạn sẽ nhận file qua email.'),
        backgroundColor: _kSuccess,
      ),
    );
  }

  void _requestDelete() {
    HapticFeedback.mediumImpact();
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text(
          'Yêu cầu xoá dữ liệu',
          style: TextStyle(
              fontFamily: 'Outfit', fontWeight: FontWeight.w700),
        ),
        content: const Text(
          'Hành động này sẽ gửi yêu cầu xoá toàn bộ dữ liệu tài khoản trong vòng 14 ngày làm việc. Bạn có muốn tiếp tục?',
          style: TextStyle(fontFamily: 'Outfit'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Huỷ',
                style: TextStyle(fontFamily: 'Outfit')),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Đã ghi nhận yêu cầu xoá dữ liệu.'),
                ),
              );
            },
            child: const Text(
              'Gửi yêu cầu',
              style: TextStyle(
                fontFamily: 'Outfit',
                color: Color(0xFFDC2626),
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
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
          'Quyền riêng tư',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: _kInk,
          ),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _kBrand))
          : SafeArea(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: const Color(0xFFBBF7D0)),
                    ),
                    child: const Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.lock_outline_rounded,
                            color: _kBrand, size: 20),
                        SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Dữ liệu của bạn được mã hoá và chỉ bạn mới truy cập được. Tuỳ chỉnh các lựa chọn bên dưới để kiểm soát việc chia sẻ.',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 12.5,
                              color: _kInkSoft,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _kBorder),
                    ),
                    child: Column(
                      children: List.generate(_options.length, (i) {
                        final opt = _options[i];
                        final isLast = i == _options.length - 1;
                        return _PrivacyToggleRow(
                          opt: opt,
                          value: _values[opt.key] ?? opt.defaultOn,
                          onChanged: (v) => _toggle(opt, v),
                          isLast: isLast,
                        );
                      }),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _ActionRow(
                    icon: Icons.download_rounded,
                    title: 'Tải dữ liệu cá nhân',
                    desc: 'Xuất bản sao dữ liệu của bạn (JSON).',
                    onTap: _exportData,
                  ),
                  const SizedBox(height: 10),
                  _ActionRow(
                    icon: Icons.delete_outline_rounded,
                    title: 'Yêu cầu xoá dữ liệu',
                    desc: 'Xoá toàn bộ dữ liệu tài khoản trong 14 ngày.',
                    danger: true,
                    onTap: _requestDelete,
                  ),
                ],
              ),
            ),
    );
  }
}

class _PrivacyToggleRow extends StatelessWidget {
  const _PrivacyToggleRow({
    required this.opt,
    required this.value,
    required this.onChanged,
    required this.isLast,
  });

  final _PrivacyOption opt;
  final bool value;
  final ValueChanged<bool> onChanged;
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
      padding: const EdgeInsets.fromLTRB(14, 12, 8, 12),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: opt.iconBg,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(opt.icon, size: 18, color: opt.iconColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  opt.title,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: _kInk,
                    height: 1.2,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  opt.desc,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 11.5,
                    color: _kInkSoft,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
          Switch.adaptive(
            value: value,
            onChanged: onChanged,
            activeThumbColor: _kBrand,
          ),
        ],
      ),
    );
  }
}

class _ActionRow extends StatelessWidget {
  const _ActionRow({
    required this.icon,
    required this.title,
    required this.desc,
    required this.onTap,
    this.danger = false,
  });

  final IconData icon;
  final String title;
  final String desc;
  final VoidCallback onTap;
  final bool danger;

  @override
  Widget build(BuildContext context) {
    final color = danger ? const Color(0xFFDC2626) : _kInk;
    final bg = danger ? const Color(0xFFFEF2F2) : const Color(0xFFF1F5F9);
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
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: bg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 18, color: color),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: color,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      desc,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11.5,
                        color: _kInkSoft,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_right_rounded,
                  size: 20, color: color.withOpacity(0.6)),
            ],
          ),
        ),
      ),
    );
  }
}
