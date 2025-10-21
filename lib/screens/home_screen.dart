import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/schedule_provider.dart';
import '../providers/announcement_provider.dart';
import '../providers/user_profile_provider.dart';
import '../models/schedule_item.dart';
import '../models/announcement.dart';
import '../widgets/schedule_card.dart';
import '../widgets/announcement_card.dart';
import '../widgets/ai_recommendation_card.dart';
import '../widgets/ai_chat_dialog.dart';
import '../widgets/urgent_schedule_card.dart';
import '../widgets/interest_tag_management_box.dart';
import '../services/web_crawling_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // 사용자 프로필 로드
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<UserProfileProvider>().loadUserProfile();
      _testCrawling();
    });
  }

  // 크롤링 테스트
  Future<void> _testCrawling() async {
    try {
      await WebCrawlingService.instance.crawlAllSites();
    } catch (e) {
      // 조용히 처리
    }
  }

  // URL 런처 함수
  Future<void> _launchURL(String url) async {
    try {
      final Uri uri = Uri.parse(url);
      
      // 먼저 외부 앱으로 열기 시도
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        // 외부 앱으로 열 수 없으면 기본 브라우저로 시도
        await launchUrl(uri, mode: LaunchMode.platformDefault);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('링크를 열 수 없습니다: $url'),
            action: SnackBarAction(
              label: '복사',
              onPressed: () {
                // 클립보드에 URL 복사
                // Clipboard.setData(ClipboardData(text: url));
              },
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '유니버',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false, // 제목을 왼쪽으로 정렬
        titleSpacing: 16, // 왼쪽 여백 설정
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              // 알림 화면으로 이동
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          context.read<ScheduleProvider>().loadSchedules();
          context.read<AnnouncementProvider>().loadAnnouncements();
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWelcomeSection(context),
              const SizedBox(height: 12),
              const InterestTagManagementBox(),
              const SizedBox(height: 12),
              _buildQuickStats(context),
              const SizedBox(height: 12),
              _buildUrgentSchedules(context),
              const SizedBox(height: 12),
              _buildAISection(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(BuildContext context) {
    final now = DateTime.now();
    final greeting = _getGreeting(now.hour);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary,
            Theme.of(context).colorScheme.primary.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            greeting,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '유니버와 함께하는 스마트한 대학생활!',
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context) {
    return Consumer2<ScheduleProvider, AnnouncementProvider>(
      builder: (context, scheduleProvider, announcementProvider, child) {
        // null 안전성 체크
        if (scheduleProvider == null || announcementProvider == null) {
          return const SizedBox.shrink();
        }
        
        final upcomingCount = (scheduleProvider.upcomingSchedules ?? []).length;
        final importantCount = (announcementProvider.importantAnnouncements ?? []).length;
        final urgentCount = (scheduleProvider.urgentSchedules ?? []).length;
        
        return Row(
          children: [
            Expanded(
              child: _buildStatCard(
                context,
                '긴급 일정',
                urgentCount.toString(),
                Icons.warning,
                urgentCount > 0 ? Colors.red : Colors.grey,
                onTap: () => _launchURL('https://portal.yonsei.ac.kr/main/index.jsp'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                context,
                '다가오는 일정',
                upcomingCount.toString(),
                Icons.calendar_today,
                Colors.blue,
                onTap: () => _launchURL('https://portal.yonsei.ac.kr/main/index.jsp'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                context,
                '중요 공지',
                importantCount.toString(),
                Icons.campaign,
                Colors.orange,
                onTap: () => _launchURL('https://www.yonsei.ac.kr/sc/notice/'),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color,
    {VoidCallback? onTap}
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            // 아이콘과 숫자를 아래에 배치
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, color: color, size: 16),
                const SizedBox(width: 4),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUrgentSchedules(BuildContext context) {
    return Consumer<ScheduleProvider>(
      builder: (context, provider, child) {
        // null 안전성 체크
        if (provider == null) {
          return const SizedBox.shrink();
        }
        
        final urgentSchedules = provider.urgentSchedules ?? [];
        
        if (urgentSchedules.isEmpty) {
          return const SizedBox.shrink();
        }
        
        return InkWell(
          onTap: () => _launchURL('https://portal.yonsei.ac.kr/main/index.jsp'),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.red.withOpacity(0.05), Colors.red.withOpacity(0.02)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.red.withOpacity(0.2), width: 1),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.warning_rounded,
                        color: Colors.red.shade700,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '긴급한 일정',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade700,
                        fontSize: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.red.shade700,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        '${urgentSchedules.length}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ...urgentSchedules.take(2).map((schedule) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: UrgentScheduleCard(schedule: schedule),
                  );
                }),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAISection(BuildContext context) {
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.psychology,
                  color: Theme.of(context).colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'AI 어시스턴트',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'AI 오버레이를 눌러서 언제든 도움을 요청하세요!',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getGreeting(int hour) {
    if (hour < 12) {
      return '좋은 아침이에요! 🌅';
    } else if (hour < 18) {
      return '좋은 오후에요! ☀️';
    } else {
      return '좋은 저녁이에요! 🌙';
    }
  }
}