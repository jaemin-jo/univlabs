import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/schedule_item.dart';
import '../models/university.dart';
import '../models/academic_calendar.dart';
import '../services/academic_calendar_service.dart';
import '../services/university_schedule_service.dart';
import '../services/university_service.dart';
import '../widgets/university_schedule_card.dart';

class UniversityScheduleScreen extends StatefulWidget {
  const UniversityScheduleScreen({super.key});

  @override
  State<UniversityScheduleScreen> createState() => _UniversityScheduleScreenState();
}

class _UniversityScheduleScreenState extends State<UniversityScheduleScreen> {
  University? _selectedUniversity;
  bool _isLoading = false;
  String? _error;
  AcademicCalendar? _academicCalendar;
  String _selectedMonth = '';

  @override
  void initState() {
    super.initState();
    _loadAcademicCalendar();
  }

  Future<void> _loadAcademicCalendar() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // JSON 파일에서 학사일정 로드 (크롤링 대신)
      _academicCalendar = await AcademicCalendarService.loadAcademicCalendar();
      
      // 현재 월을 기본 선택
      final now = DateTime.now();
      _selectedMonth = '${now.month}월';
      
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('대학교 학사일정'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAcademicCalendar,
          ),
          PopupMenuButton<String>(
            onSelected: (month) {
              setState(() {
                _selectedMonth = month;
              });
            },
            itemBuilder: (context) => _academicCalendar?.schedule.map((monthSchedule) => PopupMenuItem(
              value: monthSchedule.month,
              child: Text(monthSchedule.month),
            )).toList() ?? [],
          ),
        ],
      ),
      body: Column(
        children: [
          // 월 선택 표시
          if (_selectedMonth.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: Colors.blue.shade50,
              child: Row(
                children: [
                  Icon(Icons.calendar_month, color: Colors.blue.shade700),
                  const SizedBox(width: 8),
                  Text(
                    '$_selectedMonth 학사일정',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.blue.shade700,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '${_academicCalendar?.university} ${_academicCalendar?.semester}',
                    style: TextStyle(
                      color: Colors.blue.shade600,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          
          // 학사일정 목록
          Expanded(
            child: _buildScheduleList(),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleList() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('학사일정을 불러오는 중...'),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '오류가 발생했습니다',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              style: TextStyle(color: Colors.grey.shade500),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadAcademicCalendar,
              icon: const Icon(Icons.refresh),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      );
    }

    if (_academicCalendar == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.calendar_today,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              '학사일정 데이터가 없습니다',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      );
    }

    // 선택된 월의 일정 가져오기
    final selectedMonthSchedule = _academicCalendar!.schedule
        .where((schedule) => schedule.month == _selectedMonth)
        .firstOrNull;

    if (selectedMonthSchedule == null || selectedMonthSchedule.events.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.calendar_today,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '$_selectedMonth 학사일정이 없습니다',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '다른 월을 선택해보세요',
              style: TextStyle(color: Colors.grey.shade500),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: selectedMonthSchedule.events.length,
      itemBuilder: (context, index) {
        final event = selectedMonthSchedule.events[index];
        return _buildEventCard(event);
      },
    );
  }

  Widget _buildEventCard(CalendarEvent event) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: _parseColor(event.typeColor),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Center(
            child: Text(
              event.typeIcon,
              style: const TextStyle(fontSize: 20),
            ),
          ),
        ),
        title: Text(
          event.title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              event.date,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (event.description.isNotEmpty) ...[
              const SizedBox(height: 2),
              Text(
                event.description,
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _parseColor(event.typeColor).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                event.type,
                style: TextStyle(
                  color: _parseColor(event.typeColor),
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: _parseColor(event.priorityColor).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                _getPriorityText(event.priority),
                style: TextStyle(
                  color: _parseColor(event.priorityColor),
                  fontSize: 8,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        onTap: () => _showEventDetail(event),
      ),
    );
  }

  Color _parseColor(String colorString) {
    try {
      return Color(int.parse(colorString.replaceAll('#', '0xFF')));
    } catch (e) {
      return Colors.grey;
    }
  }

  String _getPriorityText(String priority) {
    switch (priority) {
      case 'high':
        return '높음';
      case 'medium':
        return '보통';
      case 'low':
        return '낮음';
      default:
        return '보통';
    }
  }

  void _showEventDetail(CalendarEvent event) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Text(event.typeIcon, style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 8),
            Expanded(child: Text(event.title)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('날짜', event.date),
              _buildDetailRow('타입', event.type),
              _buildDetailRow('우선순위', _getPriorityText(event.priority)),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('닫기'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

}




