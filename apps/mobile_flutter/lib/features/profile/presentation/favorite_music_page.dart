import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kPurple = Color(0xFF8B5CF6);
const _kPurpleSoft = Color(0xFFEDE9FE);

/// Một bài nhạc/giai điệu giúp thư giãn — danh sách built-in để người
/// dùng đánh dấu yêu thích. Lưu local qua SharedPreferences (offline-first).
class _Track {
  final String id;
  final String title;
  final String artist;
  final String mood;
  final String duration;
  final IconData icon;
  final Color color;

  const _Track({
    required this.id,
    required this.title,
    required this.artist,
    required this.mood,
    required this.duration,
    required this.icon,
    required this.color,
  });
}

const _tracks = <_Track>[
  _Track(
    id: 'rain_forest',
    title: 'Mưa rừng nhẹ',
    artist: 'Ambient Nature',
    mood: 'Thư giãn · Ngủ ngon',
    duration: '12:30',
    icon: Icons.cloud_outlined,
    color: Color(0xFF3B82F6),
  ),
  _Track(
    id: 'ocean_calm',
    title: 'Sóng biển dịu',
    artist: 'Ocean Sounds',
    mood: 'Tĩnh tâm',
    duration: '15:00',
    icon: Icons.waves_rounded,
    color: Color(0xFF06B6D4),
  ),
  _Track(
    id: 'piano_morning',
    title: 'Piano buổi sáng',
    artist: 'Soft Keys',
    mood: 'Tỉnh táo · Nhẹ nhàng',
    duration: '08:45',
    icon: Icons.music_note_rounded,
    color: _kPurple,
  ),
  _Track(
    id: 'lofi_focus',
    title: 'Lofi tập trung',
    artist: 'Study Beats',
    mood: 'Tập trung · Học bài',
    duration: '20:00',
    icon: Icons.headphones_rounded,
    color: Color(0xFFEC4899),
  ),
  _Track(
    id: 'meditation_breath',
    title: 'Hơi thở thiền',
    artist: 'Mindful Moments',
    mood: 'Thiền · Hít thở',
    duration: '10:00',
    icon: Icons.self_improvement_rounded,
    color: Color(0xFF16A34A),
  ),
  _Track(
    id: 'forest_birds',
    title: 'Chim hót buổi sớm',
    artist: 'Forest Choir',
    mood: 'Năng lượng',
    duration: '11:20',
    icon: Icons.eco_rounded,
    color: Color(0xFF22C55E),
  ),
  _Track(
    id: 'night_stars',
    title: 'Đêm sao yên tĩnh',
    artist: 'Sleep Sounds',
    mood: 'Ngủ sâu',
    duration: '30:00',
    icon: Icons.nightlight_round,
    color: Color(0xFF6366F1),
  ),
  _Track(
    id: 'fireplace',
    title: 'Tiếng lò sưởi',
    artist: 'Cozy Atmosphere',
    mood: 'Ấm áp · Thư giãn',
    duration: '18:00',
    icon: Icons.local_fire_department_rounded,
    color: Color(0xFFF97316),
  ),
];

const _kPrefsKey = 'profile.favorite_music';

class FavoriteMusicPage extends StatefulWidget {
  const FavoriteMusicPage({super.key});

  @override
  State<FavoriteMusicPage> createState() => _FavoriteMusicPageState();
}

class _FavoriteMusicPageState extends State<FavoriteMusicPage> {
  Set<String> _favorites = <String>{};
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList(_kPrefsKey) ?? <String>[];
    if (!mounted) return;
    setState(() {
      _favorites = list.toSet();
      _loading = false;
    });
  }

  Future<void> _toggle(String id) async {
    HapticFeedback.selectionClick();
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      if (_favorites.contains(id)) {
        _favorites.remove(id);
      } else {
        _favorites.add(id);
      }
    });
    await prefs.setStringList(_kPrefsKey, _favorites.toList());
  }

  @override
  Widget build(BuildContext context) {
    final favList = _tracks.where((t) => _favorites.contains(t.id)).toList();
    final restList =
        _tracks.where((t) => !_favorites.contains(t.id)).toList();

    return Scaffold(
      backgroundColor: _kBg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        foregroundColor: _kInk,
        title: const Text(
          'Âm nhạc yêu thích',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: _kInk,
          ),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _kPurple))
          : SafeArea(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                children: [
                  _Header(count: _favorites.length),
                  const SizedBox(height: 16),
                  if (favList.isNotEmpty) ...[
                    const _SectionTitle(
                      icon: Icons.favorite_rounded,
                      iconColor: Color(0xFFEC4899),
                      title: 'Yêu thích',
                    ),
                    const SizedBox(height: 8),
                    ...favList.map((t) => _TrackCard(
                          track: t,
                          favorite: true,
                          onToggle: () => _toggle(t.id),
                        )),
                    const SizedBox(height: 16),
                  ],
                  if (restList.isNotEmpty) ...[
                    const _SectionTitle(
                      icon: Icons.library_music_rounded,
                      iconColor: _kPurple,
                      title: 'Khám phá',
                    ),
                    const SizedBox(height: 8),
                    ...restList.map((t) => _TrackCard(
                          track: t,
                          favorite: false,
                          onToggle: () => _toggle(t.id),
                        )),
                  ],
                ],
              ),
            ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.count});
  final int count;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kPurpleSoft, Color(0xFFFCE7F3)],
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
            child: const Icon(Icons.music_note_rounded,
                color: _kPurple, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Giai điệu chữa lành',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  count == 0
                      ? 'Chưa có bài yêu thích nào — chạm ❤ để lưu lại.'
                      : 'Bạn đã lưu $count bài để nghe lại.',
                  style: const TextStyle(
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
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({
    required this.icon,
    required this.iconColor,
    required this.title,
  });

  final IconData icon;
  final Color iconColor;
  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: iconColor),
          const SizedBox(width: 6),
          Text(
            title,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: _kInk,
            ),
          ),
        ],
      ),
    );
  }
}

class _TrackCard extends StatelessWidget {
  const _TrackCard({
    required this.track,
    required this.favorite,
    required this.onToggle,
  });

  final _Track track;
  final bool favorite;
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: () {
            HapticFeedback.selectionClick();
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Đang phát: ${track.title}'),
                duration: const Duration(seconds: 2),
              ),
            );
          },
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
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: track.color.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(track.icon, color: track.color, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        track.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
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
                        '${track.artist} · ${track.mood}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
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
                Text(
                  track.duration,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 11.5,
                    color: _kInkMuted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 6),
                IconButton(
                  tooltip: favorite ? 'Bỏ yêu thích' : 'Thêm vào yêu thích',
                  onPressed: onToggle,
                  icon: Icon(
                    favorite
                        ? Icons.favorite_rounded
                        : Icons.favorite_border_rounded,
                    color:
                        favorite ? const Color(0xFFEC4899) : _kInkMuted,
                    size: 20,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
