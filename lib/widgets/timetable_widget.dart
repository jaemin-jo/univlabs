import 'package:flutter/material.dart';
import '../models/course.dart';

class TimetableWidget extends StatelessWidget {
  final List<Course> courses;

  const TimetableWidget({
    super.key,
    required this.courses,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          _buildHeader(),
          Expanded(
            child: _buildTimetableGrid(),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    const days = ['월', '화', '수', '목', '금'];
    const timeSlots = [
      '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'
    ];

    return Column(
      children: [
        // 시간 슬롯 헤더
        Container(
          height: 40,
          decoration: BoxDecoration(
            color: Colors.grey[100],
            border: Border(
              bottom: BorderSide(color: Colors.grey[300]!),
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 60,
                decoration: BoxDecoration(
                  border: Border(right: BorderSide(color: Colors.grey[300]!)),
                ),
                child: const Center(
                  child: Text(
                    '시간',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              ...days.map((day) => Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    border: Border(right: BorderSide(color: Colors.grey[300]!)),
                  ),
                  child: Center(
                    child: Text(
                      day,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              )),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTimetableGrid() {
    const timeSlots = [
      '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'
    ];

    return SingleChildScrollView(
      child: Column(
        children: timeSlots.asMap().entries.map((entry) {
          final index = entry.key;
          final time = entry.value;
          
          return Container(
            height: 60,
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Colors.grey[300]!),
              ),
            ),
            child: Row(
              children: [
                // 시간 표시
                Container(
                  width: 60,
                  decoration: BoxDecoration(
                    border: Border(right: BorderSide(color: Colors.grey[300]!)),
                  ),
                  child: Center(
                    child: Text(
                      time,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                ),
                // 각 요일별 셀
                ...List.generate(5, (dayIndex) {
                  return Expanded(
                    child: _buildTimeSlot(dayIndex + 1, index),
                  );
                }),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildTimeSlot(int dayOfWeek, int timeSlotIndex) {
    final coursesInSlot = courses.where((course) {
      return course.times.any((time) {
        final courseStartSlot = _getTimeSlotIndex(time.startHour, time.startMinute);
        final courseEndSlot = _getTimeSlotIndex(time.endHour, time.endMinute);
        return time.dayOfWeek == dayOfWeek && 
               timeSlotIndex >= courseStartSlot && 
               timeSlotIndex < courseEndSlot;
      });
    }).toList();

    if (coursesInSlot.isEmpty) {
      return Container(
        decoration: BoxDecoration(
          border: Border(right: BorderSide(color: Colors.grey[300]!)),
        ),
      );
    }

    final course = coursesInSlot.first;
    final courseTime = course.times.firstWhere((time) => time.dayOfWeek == dayOfWeek);
    final isStartOfCourse = _getTimeSlotIndex(courseTime.startHour, courseTime.startMinute) == timeSlotIndex;

    return Container(
      decoration: BoxDecoration(
        border: Border(right: BorderSide(color: Colors.grey[300]!)),
        color: _getCourseColor(course).withOpacity(0.3),
      ),
      child: isStartOfCourse
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    course.name,
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    course.classroom ?? '',
                    style: const TextStyle(fontSize: 8),
                  ),
                ],
              ),
            )
          : null,
    );
  }

  int _getTimeSlotIndex(int hour, int minute) {
    final totalMinutes = hour * 60 + minute;
    return (totalMinutes - 540) ~/ 60; // 9:00 = 540분부터 시작
  }

  Color _getCourseColor(Course course) {
    final colors = [
      Colors.blue,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.red,
      Colors.teal,
      Colors.indigo,
      Colors.pink,
    ];
    
    final index = course.hashCode % colors.length;
    return colors[index];
  }
}
