import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/schedule_provider.dart';

class AIRecommendationCard extends StatefulWidget {
  const AIRecommendationCard({super.key});

  @override
  State<AIRecommendationCard> createState() => _AIRecommendationCardState();
}

class _AIRecommendationCardState extends State<AIRecommendationCard> {
  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ScheduleProvider>(
      builder: (context, provider, child) {
        final urgentSchedules = provider.urgentSchedules;
        final hasUrgentSchedules = urgentSchedules.isNotEmpty;
        
        return Card(
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              gradient: LinearGradient(
                colors: hasUrgentSchedules 
                    ? [
                        Colors.red.withOpacity(0.1),
                        Colors.orange.withOpacity(0.1),
                      ]
                    : [
                        Colors.purple.withOpacity(0.1),
                        Colors.blue.withOpacity(0.1),
                      ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: hasUrgentSchedules 
                              ? [Colors.red.shade400, Colors.red.shade600]
                              : [Colors.purple.shade400, Colors.blue.shade600],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: (hasUrgentSchedules ? Colors.red : Colors.purple).withOpacity(0.3),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: hasUrgentSchedules 
                                ? [Colors.red.shade400, Colors.red.shade600]
                                : [Colors.purple.shade400, Colors.blue.shade600],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: (hasUrgentSchedules ? Colors.red : Colors.purple).withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Center(
                          child: Icon(
                            hasUrgentSchedules ? Icons.warning_rounded : Icons.psychology_rounded,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            hasUrgentSchedules ? '긴급 알림' : 'AI 추천',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: hasUrgentSchedules ? Colors.red : Colors.purple,
                            ),
                          ),
                          Text(
                            hasUrgentSchedules 
                                ? '마감이 임박한 일정이 있습니다'
                                : '개인화된 일정 관리',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                if (hasUrgentSchedules) ...[
                  ...urgentSchedules.take(2).map((schedule) {
                    final daysUntilStart = schedule.date.difference(DateTime.now()).inDays;
                    final isToday = daysUntilStart == 0;
                    final isTomorrow = daysUntilStart == 1;
                    
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _buildRecommendationItem(
                        context,
                        '⚠️ ${schedule.title}',
                        isToday 
                            ? '오늘 시작됩니다! 서둘러 준비하세요'
                            : isTomorrow 
                                ? '내일 시작됩니다! 마지막 점검을 해보세요'
                                : '${daysUntilStart}일 후 시작됩니다. 미리 준비하세요',
                        Colors.red,
                      ),
                    );
                  }),
                ] else ...[
                  _buildRecommendationItem(
                    context,
                    '📚 수강신청이 3일 후에 시작됩니다',
                    '시간표를 미리 확인하고 희망 과목을 정리해보세요',
                    Colors.blue,
                  ),
                  const SizedBox(height: 12),
                  _buildRecommendationItem(
                    context,
                    '🏠 기숙사 신청 기간이 다가옵니다',
                    '기숙사 신청 서류를 미리 준비하시는 것을 추천드립니다',
                    Colors.green,
                  ),
                  const SizedBox(height: 12),
                  _buildRecommendationItem(
                    context,
                    '🏆 창업 공모전 참가를 고려해보세요',
                    '관심 분야의 공모전이 진행 중입니다',
                    Colors.orange,
                  ),
                ],
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // AI 추천 상세 화면으로 이동
                    },
                    icon: Icon(hasUrgentSchedules ? Icons.warning : Icons.auto_awesome),
                    label: Text(hasUrgentSchedules ? '긴급 일정 확인하기' : '더 많은 추천 보기'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: hasUrgentSchedules ? Colors.red : Colors.purple,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRecommendationItem(
    BuildContext context,
    String title,
    String description,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}
