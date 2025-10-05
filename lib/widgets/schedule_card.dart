import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/schedule_item.dart';

class ScheduleCard extends StatelessWidget {
  final ScheduleItem schedule;

  const ScheduleCard({
    super.key,
    required this.schedule,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: () {
          // 일정 상세 화면으로 이동
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: _getTypeColor(schedule.type).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      schedule.type.icon,
                      style: const TextStyle(fontSize: 20),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          schedule.title,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          schedule.type.displayName,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: _getTypeColor(schedule.type),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (schedule.isImportant)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        '중요',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                schedule.description,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: Colors.grey[600],
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${DateFormat('MM/dd').format(schedule.date)} - ${DateFormat('MM/dd').format(schedule.endDate!)}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                  const Spacer(),
                  _buildStatusChip(context),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(BuildContext context) {
    Color statusColor;
    String statusText;
    
    switch (schedule.status) {
      case ScheduleStatus.upcoming:
        statusColor = Colors.blue;
        statusText = '예정';
        break;
      case ScheduleStatus.inProgress:
        statusColor = Colors.orange;
        statusText = '진행중';
        break;
      case ScheduleStatus.completed:
        statusColor = Colors.green;
        statusText = '완료';
        break;
      case ScheduleStatus.cancelled:
        statusColor = Colors.grey;
        statusText = '취소';
        break;
      case ScheduleStatus.overdue:
        statusColor = Colors.red;
        statusText = '지연';
        break;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Text(
        statusText,
        style: TextStyle(
          color: statusColor,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Color _getTypeColor(ScheduleType type) {
    switch (type) {
      case ScheduleType.enrollment:
        return Colors.blue;
      case ScheduleType.registration:
        return Colors.purple;
      case ScheduleType.dormitoryApplication:
        return Colors.green;
      case ScheduleType.courseChange:
        return Colors.orange;
      case ScheduleType.scheduleCheck:
        return Colors.purple;
      case ScheduleType.doubleMajor:
        return Colors.indigo;
      case ScheduleType.contest:
        return Colors.red;
      case ScheduleType.exam:
        return Colors.brown;
      case ScheduleType.assignment:
        return Colors.teal;
      case ScheduleType.event:
        return Colors.pink;
      case ScheduleType.leave:
        return Colors.orange;
      case ScheduleType.return_:
        return Colors.green;
      case ScheduleType.graduation:
        return Colors.indigo;
      case ScheduleType.holiday:
        return Colors.amber;
      case ScheduleType.transfer:
        return Colors.cyan;
      case ScheduleType.grade:
        return Colors.deepPurple;
      case ScheduleType.semesterStart:
        return Colors.blue.shade300;
      case ScheduleType.vacation:
        return Colors.green.shade300;
      case ScheduleType.summerWinter:
        return Colors.orange.shade300;
      case ScheduleType.general:
        return Colors.grey;
      case ScheduleType.other:
        return Colors.grey;
    }
  }
}
