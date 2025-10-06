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
      debugPrint('크롤링 테스트 시작...');
      await WebCrawlingService.instance.crawlAllSites();
      debugPrint('크롤링 테스트 완료');
    } catch (e) {
      debugPrint('크롤링 테스트 오류: $e');
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
              const SizedBox(height: 12),
              _buildUpcomingSchedules(context),
              const SizedBox(height: 12),
              _buildPersonalizedAnnouncements(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(BuildContext context) {
    final now = DateTime.now();
    final greeting = _getGreeting(now.hour);

    return Consumer<UserProfileProvider>(
      builder: (context, userProvider, child) {
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
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  greeting,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  DateFormat('yyyy년 MM월 dd일 EEEE', 'ko').format(now),
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                // 선택된 대학교 정보 표시
                if (userProvider.selectedUniversity != null) ...[
                  Row(
                    children: [
                      Icon(
                        Icons.school,
                        color: Colors.white.withOpacity(0.9),
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        userProvider.currentUniversityName,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (userProvider.currentCampus.isNotEmpty) ...[
                        const SizedBox(width: 4),
                        Text(
                          '(${userProvider.currentCampus})',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.7),
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 12),
          // 사용자 정보 요약 카드 (더 컴팩트하게)
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 4),
                if (userProvider.hasProfile) ...[
                  // 이름 (가장 크게)
                  Text(
                    userProvider.userProfile!.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  // 대학교 정보
                  if (userProvider.selectedUniversity != null) ...[
                    Row(
                      children: [
                        Icon(
                          Icons.school,
                          color: Colors.white.withOpacity(0.9),
                          size: 12,
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            userProvider.currentUniversityName,
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.9),
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                  ],
                  // 학년 정보
                  Text(
                    '${userProvider.userProfile!.grade}학년',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ] else ...[
                  Text(
                    '프로필 설정 필요',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 10,
                    ),
                  ),
                  const SizedBox(height: 2),
                  GestureDetector(
                    onTap: () {
                      // 설정 화면으로 이동
                      Navigator.pushNamed(context, '/settings');
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        '설정하기',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 8,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
      },
    );
  }

  Widget _buildQuickStats(BuildContext context) {
    return Consumer2<ScheduleProvider, AnnouncementProvider>(
      builder: (context, scheduleProvider, announcementProvider, child) {
        final upcomingCount = scheduleProvider.upcomingSchedules.length;
        final importantCount = announcementProvider.importantAnnouncements.length;
        final urgentCount = scheduleProvider.urgentSchedules.length;

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
                '중요 공지사항',
                importantCount.toString(),
                Icons.notifications,
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
    Color color, {
    VoidCallback? onTap,
  }) {
    return Card(
      elevation: 1,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 제목을 중간에 배치
              Text(
                title,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontSize: 10,
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
      ),
    );
  }

  Widget _buildUrgentSchedules(BuildContext context) {
    return Consumer<ScheduleProvider>(
      builder: (context, provider, child) {
        final urgentSchedules = provider.urgentSchedules;

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
                        fontSize: 14,
                      fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
                ),
              const SizedBox(height: 16),
              ...urgentSchedules.map((schedule) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: UrgentScheduleCard(schedule: schedule),
              )),
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
      child: InkWell(
        onTap: () => _launchURL('https://www.yonsei.ac.kr/sc/notice/'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
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
                    'AI 추천',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const AIRecommendationCard(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUpcomingSchedules(BuildContext context) {
    return Card(
      elevation: 1,
      child: InkWell(
        onTap: () => _launchURL('https://portal.yonsei.ac.kr/main/index.jsp'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.schedule,
                        color: Theme.of(context).colorScheme.primary,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '다가오는 일정',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  TextButton(
                    onPressed: () => _launchURL('https://portal.yonsei.ac.kr/main/index.jsp'),
                    child: const Text('더보기', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            const SizedBox(height: 8),
        Consumer<ScheduleProvider>(
          builder: (context, provider, child) {
            try {
              final upcomingSchedules = provider.upcomingSchedules?.take(3).toList() ?? [];

              if (upcomingSchedules.isEmpty) {
                return Container(
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Column(
                    children: [
                      Icon(
                        Icons.calendar_today_outlined,
                        size: 48,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '다가오는 일정이 없습니다',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '새로운 일정을 추가하거나 학사일정을 확인해보세요',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                );
              }

              return Column(
                children: upcomingSchedules
                    .map((schedule) => Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                          child: ScheduleCard(schedule: schedule),
                        ))
                    .toList(),
              );
            } catch (e) {
              debugPrint('일정 로드 오류: $e');
              return Container(
                padding: const EdgeInsets.all(20),
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.schedule_outlined,
                      size: 48,
                      color: Colors.blue.shade400,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '일정을 불러오는 중입니다',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                        color: Colors.blue.shade700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '잠시만 기다려주세요',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue.shade600,
                      ),
                    ),
                  ],
                ),
              );
            }
          },
        ),
      ],
          ),
        ),
      ),
    );
  }

  Widget _buildPersonalizedAnnouncements(BuildContext context) {
    return Consumer2<AnnouncementProvider, UserProfileProvider>(
      builder: (context, announcementProvider, userProvider, child) {
        // 사용자 정보에 맞는 공지사항 필터링
        final personalizedAnnouncements = _getPersonalizedAnnouncements(
          announcementProvider.importantAnnouncements,
          userProvider,
        );

        return Card(
          elevation: 1,
          child: InkWell(
            onTap: () => _launchURL('https://www.yonsei.ac.kr/sc/notice/'),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.person_pin,
                            color: Theme.of(context).colorScheme.primary,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            userProvider.hasProfile
                              ? '${userProvider.userProfile!.name}님을 위한 공지사항'
                              : '맞춤형 공지사항',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      TextButton(
                        onPressed: () => _launchURL('https://www.yonsei.ac.kr/sc/notice/'),
                        child: const Text('더보기', style: TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                if (userProvider.hasProfile) ...[
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${userProvider.userSummary} 관련 정보',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.primary,
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 8),
                if (personalizedAnnouncements.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(
                            Icons.info_outline,
                            color: Colors.grey[400],
                            size: 32,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            userProvider.hasProfile
                              ? '${userProvider.userProfile!.name}님과 관련된 공지사항이 없습니다.'
                              : '프로필을 설정하면 맞춤형 공지사항을 받아보실 수 있습니다.',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          if (!userProvider.hasProfile) ...[
                            const SizedBox(height: 8),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.pushNamed(context, '/settings');
                              },
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                textStyle: const TextStyle(fontSize: 12),
                              ),
                              child: const Text('프로필 설정하기'),
                            ),
                          ],
                        ],
                      ),
                    ),
                  )
                else
                  Column(
                    children: personalizedAnnouncements
                        .take(3)
                  .map((announcement) => Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                        child: AnnouncementCard(announcement: announcement),
                      ))
                  .toList(),
                  ),
              ],
            ),
            ),
          ),
        );
      },
    );
  }

  // 사용자 정보에 맞는 공지사항 필터링
  List<Announcement> _getPersonalizedAnnouncements(
    List<Announcement> announcements,
    UserProfileProvider userProvider,
  ) {
    if (!userProvider.hasProfile) {
      return announcements.take(3).toList();
    }

    final userProfile = userProvider.userProfile!;
    final relevantKeywords = userProvider.allRelevantKeywords;

    // 키워드 기반 필터링
    final filteredAnnouncements = announcements.where((announcement) {
      final title = announcement.title.toLowerCase();
      final content = announcement.content.toLowerCase();
      final department = announcement.department?.toLowerCase() ?? '';

      // 학과명이 정확히 일치하는 경우 우선순위 높음
      if (userProfile.department != null &&
          department.contains(userProfile.department!.toLowerCase())) {
        return true;
      }

      // 관련 키워드가 포함된 경우
      for (final keyword in relevantKeywords) {
        if (title.contains(keyword.toLowerCase()) ||
            content.contains(keyword.toLowerCase())) {
          return true;
        }
      }

      // 학년별 관련 키워드
      for (final gradeKeyword in userProvider.gradeKeywords) {
        if (title.contains(gradeKeyword.toLowerCase()) ||
            content.contains(gradeKeyword.toLowerCase())) {
          return true;
        }
      }

      return false;
    }).toList();

    // 우선순위 정렬 (학과명 일치 > 키워드 일치)
    filteredAnnouncements.sort((a, b) {
      final aDepartment = a.department?.toLowerCase() ?? '';
      final bDepartment = b.department?.toLowerCase() ?? '';

      final aHasDepartmentMatch = userProfile.department != null &&
          aDepartment.contains(userProfile.department!.toLowerCase());
      final bHasDepartmentMatch = userProfile.department != null &&
          bDepartment.contains(userProfile.department!.toLowerCase());

      if (aHasDepartmentMatch && !bHasDepartmentMatch) return -1;
      if (!aHasDepartmentMatch && bHasDepartmentMatch) return 1;

      // 중요도 순으로 정렬 (isImportant 기준)
      if (a.isImportant && !b.isImportant) return -1;
      if (!a.isImportant && b.isImportant) return 1;

      // 발행일 순으로 정렬 (최신순)
      return b.publishDate.compareTo(a.publishDate);
    });

    return filteredAnnouncements;
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
