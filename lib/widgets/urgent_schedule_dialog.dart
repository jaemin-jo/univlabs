import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/schedule_item.dart';

class UrgentScheduleDialog extends StatefulWidget {
  final ScheduleItem schedule;

  const UrgentScheduleDialog({
    super.key,
    required this.schedule,
  });

  @override
  State<UrgentScheduleDialog> createState() => _UrgentScheduleDialogState();
}

class _UrgentScheduleDialogState extends State<UrgentScheduleDialog>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  bool _isLoadingAI = false;
  String _aiSummary = '';

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));

    _fadeController.forward();
    _slideController.forward();
    
    // AI 요약 생성
    _generateAISummary();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  Future<void> _generateAISummary() async {
    setState(() {
      _isLoadingAI = true;
    });

    // 실제 AI 서비스와 연동하는 부분
    // 여기서는 시뮬레이션된 AI 요약을 생성
    await Future.delayed(const Duration(seconds: 2));
    
    setState(() {
      _isLoadingAI = false;
      _aiSummary = _generateMockAISummary();
    });
  }

  String _generateMockAISummary() {
    final schedule = widget.schedule;
    final now = DateTime.now();
    final daysUntilStart = schedule.date.difference(now).inDays;
    
    if (daysUntilStart == 0) {
      return "🚨 오늘 마감되는 중요한 일정입니다! 즉시 처리하시기 바랍니다. 마감 시간을 놓치지 않도록 주의하세요.";
    } else if (daysUntilStart == 1) {
      return "⚠️ 내일 마감되는 긴급한 일정입니다. 사전 준비가 필요하며, 관련 서류나 자료를 미리 준비해두세요.";
    } else if (daysUntilStart <= 3) {
      return "📅 3일 이내 마감되는 중요한 일정입니다. 시간을 충분히 확보하여 체계적으로 준비하시기 바랍니다.";
    } else {
      return "📋 마감이 다가오는 일정입니다. 미리 계획을 세우고 준비하시기 바랍니다.";
    }
  }

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

  String _getRelatedURL() {
    // 일정 타입에 따른 관련 URL 반환
    switch (widget.schedule.type) {
      case ScheduleType.enrollment:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.registration:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.dormitoryApplication:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.courseChange:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.scheduleCheck:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.doubleMajor:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.contest:
        return 'https://www.yonsei.ac.kr/sc/notice/';
      case ScheduleType.exam:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.assignment:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.event:
        return 'https://www.yonsei.ac.kr/sc/notice/';
      case ScheduleType.exam:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.leave:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.return_:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.graduation:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.holiday:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.transfer:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.grade:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.semesterStart:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.vacation:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.summerWinter:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.general:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
      case ScheduleType.other:
        return 'https://portal.yonsei.ac.kr/main/index.jsp';
    }
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final daysUntilStart = widget.schedule.date.difference(now).inDays;
    final hoursUntilStart = widget.schedule.date.difference(now).inHours;
    final minutesUntilStart = widget.schedule.date.difference(now).inMinutes;
    final isToday = daysUntilStart == 0;
    final isTomorrow = daysUntilStart == 1;
    
    String getTimeRemaining() {
      if (isToday) {
        if (hoursUntilStart > 0) {
          return '오늘 마감! ${hoursUntilStart}시간 남음';
        } else if (minutesUntilStart > 0) {
          return '오늘 마감! ${minutesUntilStart}분 남음';
        } else {
          return '오늘 마감! 지금!';
        }
      } else if (isTomorrow) {
        return '내일 마감!';
      } else {
        return '${daysUntilStart}일 후 마감';
      }
    }

    return AnimatedBuilder(
      animation: Listenable.merge([_fadeAnimation, _slideAnimation]),
      builder: (context, child) {
        return FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: Dialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              child: Container(
                constraints: const BoxConstraints(maxHeight: 600),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // 헤더
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.red.shade600,
                            Colors.red.shade700,
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(20),
                          topRight: Radius.circular(20),
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              widget.schedule.type.icon,
                              style: const TextStyle(fontSize: 24),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  widget.schedule.title,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  widget.schedule.type.displayName,
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.9),
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              getTimeRemaining(),
                              style: TextStyle(
                                color: Colors.red.shade700,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    // 내용
                    Flexible(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // 일정 상세 정보
                            _buildDetailSection(),
                            const SizedBox(height: 20),
                            
                            // AI 요약 섹션
                            _buildAISection(),
                            const SizedBox(height: 20),
                            
                            // 시간 정보
                            _buildTimeInfo(),
                          ],
                        ),
                      ),
                    ),
                    
                    // 버튼들
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: const BorderRadius.only(
                          bottomLeft: Radius.circular(20),
                          bottomRight: Radius.circular(20),
                        ),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => Navigator.of(context).pop(),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                side: BorderSide(color: Colors.grey.shade300),
                              ),
                              child: const Text('닫기'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            flex: 2,
                            child: ElevatedButton(
                              onPressed: () => _launchURL(_getRelatedURL()),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.red.shade600,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.open_in_new, size: 16),
                                  SizedBox(width: 4),
                                  Text('링크접속'),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildDetailSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.info_outline,
              color: Colors.blue.shade600,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              '상세 정보',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.shade200),
          ),
          child: Text(
            widget.schedule.description,
            style: const TextStyle(
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAISection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.psychology,
              color: Colors.purple.shade600,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              'AI 요약',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.purple.shade600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.purple.shade50,
                Colors.purple.shade100.withOpacity(0.3),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.shade200),
          ),
          child: _isLoadingAI
              ? Row(
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.purple.shade600),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'AI가 요약을 생성하고 있습니다...',
                      style: TextStyle(
                        color: Colors.purple.shade600,
                        fontSize: 14,
                      ),
                    ),
                  ],
                )
              : Text(
                  _aiSummary,
                  style: const TextStyle(
                    fontSize: 14,
                    height: 1.5,
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildTimeInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.schedule,
              color: Colors.green.shade600,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              '시간 정보',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.green.shade600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.green.shade200),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(
                    Icons.play_arrow,
                    color: Colors.green.shade600,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '시작: ${widget.schedule.date.year}년 ${widget.schedule.date.month}월 ${widget.schedule.date.day}일 ${widget.schedule.date.hour.toString().padLeft(2, '0')}:${widget.schedule.date.minute.toString().padLeft(2, '0')}',
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(
                    Icons.stop,
                    color: Colors.red.shade600,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '종료: ${widget.schedule.endDate!.year}년 ${widget.schedule.endDate!.month}월 ${widget.schedule.endDate!.day}일 ${widget.schedule.endDate!.hour.toString().padLeft(2, '0')}:${widget.schedule.endDate!.minute.toString().padLeft(2, '0')}',
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}
