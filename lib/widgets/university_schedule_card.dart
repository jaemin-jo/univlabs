import 'package:flutter/material.dart';
import '../models/schedule_item.dart';

class UniversityScheduleCard extends StatelessWidget {
  final ScheduleItem schedule;
  final VoidCallback? onTap;

  const UniversityScheduleCard({
    super.key,
    required this.schedule,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      elevation: schedule.isImportant ? 4 : 2,
      color: schedule.isImportant 
          ? Colors.red.shade50 
          : schedule.isUrgent c
              ? Colors.orange.shade50 cccdcdcccccccccdccdcdccdccdccdccdccccdccdcdcccd
              : null,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 제목과 중요도 표시
              Row(
                children: [
                  if (schedule.isImportant)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.red.shade100,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        '중요',
                        style: TextStyle(
                          color: Colors.red.shade700,
                          fontSize: 10,
                   c dcdcdccdcdcccdc c  ccdc d bc bc    fontWeight: FontWeight.bold,
                        ),
                      ),
               cccdccccccd      ),
                  if (schedule.isImportant) const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      schedule.title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: schedule.isImportant ? Colors.red.shade700 : null,
                      ),
                    ),
                  ),
                  if (schedule.university != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade100,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        schedule.university!,
                        style: TextStyle(
                          color: Colors.blue.shade700,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              
              if (schedule.description.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  schedule.description,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              
              const SizedBox(height: 12),
              
              // 날짜와 시간 정보
              Row(
                children: [
                  Icon(
                    Icons.calendar_today,
                    size: 16,
                    color: Colors.grey.shade600,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _formatDate(schedule.startDate),
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (schedule.startDate != schedule.endDate) ...[
                    const SizedBox(width: 8),
                    Text(
                      '~ ${_formatDate(schedule.endDate)}',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ],
              ),
              
              if (schedule.location != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      size: 16,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      schedule.location!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                      ),
                    ),
                  ],
                ),
              ],
              
              if (schedule.campus != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.school,
                      size: 16,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      schedule.campus!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                      ),
                    ),
                  ],
                ),
              ],
              
              const SizedBox(height: 8),
              
              // 카테고리와 우선순위
              Row(
                children: [
                  if (schedule.category != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        schedule.category!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ),
                  const Spacer(),
                  _buildPriorityIndicator(schedule.priority),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriorityIndicator(int priority) {
    Color color;
    String text;
    
    switch (priority) {
      case 1:
        color = Colors.green;
        text = '낮음';
        break;
      case 2:
        color = Colors.blue;
        text = '보통';
        break;
      case 3:
        color = Colors.orange;
        text = '높음';
        break;
      case 4:
        color = Colors.red;
        text = '매우 높음';
        break;
      case 5:
        color = Colors.purple;
        text = '긴급';
        break;
      default:
        color = Colors.grey;
        text = '보통';
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = date.difference(now).inDays;
    
    if (difference == 0) {
      return '오늘';
    } else if (difference == 1) {
      return '내일';
    } else if (difference == -1) {
      return '어제';
    } else if (difference > 0 && difference <= 7) {
      return '${difference}일 후';
    } else if (difference < 0 && difference >= -7) {
      return '${-difference}일 전';
    } else {
      return '${date.month}월 ${date.day}일';
    }
  }
}




