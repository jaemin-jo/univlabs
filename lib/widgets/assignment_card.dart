import 'package:flutter/material.dart';
import '../models/assignment.dart';

/// 과제 정보 카드 위젯
class AssignmentCard extends StatelessWidget {
  final Assignment assignment;
  
  const AssignmentCard({
    super.key,
    required this.assignment,
  });
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 제목과 상태
            Row(
              children: [
                Expanded(
                  child: Text(
                    assignment.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                _buildStatusChip(),
              ],
            ),
            const SizedBox(height: 8),
            
            // 과목 정보
            Row(
              children: [
                Icon(
                  Icons.school,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 4),
                Text(
                  assignment.courseName,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '(${assignment.courseCode})',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // 마감일 정보
            Row(
              children: [
                Icon(
                  Icons.schedule,
                  size: 16,
                  color: _getDueDateColor(),
                ),
                const SizedBox(width: 4),
                Text(
                  '마감일: ${_formatDueDate()}',
                  style: TextStyle(
                    fontSize: 14,
                    color: _getDueDateColor(),
                    fontWeight: assignment.isDueSoon ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
              ],
            ),
            
            // 설명 (있는 경우)
            if (assignment.description.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                assignment.description,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[700],
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
            
            // 태그 (있는 경우)
            if (assignment.tags.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: assignment.tags.take(3).map((tag) => 
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: Text(
                      tag,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                      ),
                    ),
                  ),
                ).toList(),
              ),
            ],
            
            // 우선순위 표시
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  _getPriorityIcon(),
                  size: 16,
                  color: _getPriorityColor(),
                ),
                const SizedBox(width: 4),
                Text(
                  '우선순위: ${_getPriorityText()}',
                  style: TextStyle(
                    fontSize: 12,
                    color: _getPriorityColor(),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (assignment.isNew)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.green,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'NEW',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                if (assignment.isUpcoming)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.orange,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'URGENT',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusChip() {
    Color color;
    String text;
    
    switch (assignment.status) {
      case AssignmentStatus.pending:
        color = Colors.grey;
        text = '대기중';
        break;
      case AssignmentStatus.inProgress:
        color = Colors.blue;
        text = '진행중';
        break;
      case AssignmentStatus.submitted:
        color = Colors.green;
        text = '제출완료';
        break;
      case AssignmentStatus.graded:
        color = Colors.purple;
        text = '채점완료';
        break;
      case AssignmentStatus.overdue:
        color = Colors.red;
        text = '마감지남';
        break;
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
  
  Color _getDueDateColor() {
    if (assignment.isOverdue) {
      return Colors.red;
    } else if (assignment.isDueSoon) {
      return Colors.orange;
    } else {
      return Colors.grey[600]!;
    }
  }
  
  String _formatDueDate() {
    final now = DateTime.now();
    final dueDate = assignment.dueDate;
    final difference = dueDate.difference(now).inDays;
    
    if (difference < 0) {
      return '${-difference}일 지남';
    } else if (difference == 0) {
      return '오늘';
    } else if (difference == 1) {
      return '내일';
    } else {
      return '${difference}일 후';
    }
  }
  
  IconData _getPriorityIcon() {
    switch (assignment.priority) {
      case AssignmentPriority.high:
        return Icons.priority_high;
      case AssignmentPriority.medium:
        return Icons.remove;
      case AssignmentPriority.low:
        return Icons.keyboard_arrow_down;
    }
  }
  
  Color _getPriorityColor() {
    switch (assignment.priority) {
      case AssignmentPriority.high:
        return Colors.red;
      case AssignmentPriority.medium:
        return Colors.orange;
      case AssignmentPriority.low:
        return Colors.green;
    }
  }
  
  String _getPriorityText() {
    switch (assignment.priority) {
      case AssignmentPriority.high:
        return '높음';
      case AssignmentPriority.medium:
        return '보통';
      case AssignmentPriority.low:
        return '낮음';
    }
  }
}
