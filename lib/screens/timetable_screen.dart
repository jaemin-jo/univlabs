import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/course_provider.dart';
import '../models/course.dart';
import '../widgets/timetable_widget.dart';
import '../widgets/course_card.dart';

class TimetableScreen extends StatefulWidget {
  const TimetableScreen({super.key});

  @override
  State<TimetableScreen> createState() => _TimetableScreenState();
}

class _TimetableScreenState extends State<TimetableScreen> with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('시간표'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '내 시간표'),
            Tab(text: '과목 검색'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.check_circle_outline),
            onPressed: () {
              _showScheduleCheckDialog();
            },
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildMyTimetable(),
          _buildCourseSearch(),
        ],
      ),
    );
  }

  Widget _buildMyTimetable() {
    return Consumer<CourseProvider>(
      builder: (context, provider, child) {
        final selectedCourses = provider.selectedCourses;
        
        if (selectedCourses.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.schedule,
                  size: 64,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  '등록된 과목이 없습니다',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '과목 검색 탭에서 과목을 추가해보세요',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[500],
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    _tabController.animateTo(1);
                  },
                  icon: const Icon(Icons.search),
                  label: const Text('과목 검색하기'),
                ),
              ],
            ),
          );
        }

        return Column(
          children: [
            Expanded(
              flex: 3,
              child: TimetableWidget(courses: selectedCourses),
            ),
            const Divider(),
            Expanded(
              flex: 2,
              child: _buildSelectedCoursesList(selectedCourses),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSelectedCoursesList(List<Course> courses) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Text(
                '등록된 과목 (${courses.length}개)',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Text(
                '총 ${courses.fold(0, (sum, course) => sum + course.credits)}학점',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: courses.length,
            itemBuilder: (context, index) {
              final course = courses[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    child: Text(
                      course.credits.toString(),
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  title: Text(course.name),
                  subtitle: Text('${course.professor} • ${course.code}'),
                  trailing: IconButton(
                    icon: const Icon(Icons.remove_circle_outline, color: Colors.red),
                    onPressed: () {
                      _showRemoveCourseDialog(course);
                    },
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCourseSearch() {
    return Consumer<CourseProvider>(
      builder: (context, provider, child) {
        final availableCourses = provider.availableCourses;
        
        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                decoration: InputDecoration(
                  hintText: '과목명, 교수명, 학과명으로 검색',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onChanged: (value) {
                  // 검색 기능 구현
                },
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: availableCourses.length,
                itemBuilder: (context, index) {
                  final course = availableCourses[index];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: CourseCard(
                      course: course,
                      onAdd: () {
                        provider.addCourseToTimeTable(course);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('${course.name}이(가) 추가되었습니다')),
                        );
                      },
                      onRemove: () {
                        provider.removeCourseFromTimeTable(course);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('${course.name}이(가) 제거되었습니다')),
                        );
                      },
                      isSelected: provider.selectedCourses.contains(course),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  void _showRemoveCourseDialog(Course course) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('과목 제거'),
        content: Text('${course.name}을(를) 시간표에서 제거하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<CourseProvider>().removeCourseFromTimeTable(course);
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('${course.name}이(가) 제거되었습니다')),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('제거'),
          ),
        ],
      ),
    );
  }

  void _showScheduleCheckDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('시간표 점검'),
        content: Consumer<CourseProvider>(
          builder: (context, provider, child) {
            final courses = provider.selectedCourses;
            final totalCredits = courses.fold(0, (sum, course) => sum + course.credits);
            final hasConflicts = _checkForConflicts(courses);
            
            return Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCheckItem(
                  '총 학점',
                  '$totalCredits학점',
                  totalCredits >= 12 && totalCredits <= 21 ? Colors.green : Colors.orange,
                ),
                const SizedBox(height: 8),
                _buildCheckItem(
                  '시간 충돌',
                  hasConflicts ? '충돌 있음' : '충돌 없음',
                  hasConflicts ? Colors.red : Colors.green,
                ),
                const SizedBox(height: 8),
                _buildCheckItem(
                  '등록 과목',
                  '${courses.length}개',
                  Colors.blue,
                ),
                if (hasConflicts) ...[
                  const SizedBox(height: 16),
                  const Text(
                    '⚠️ 시간 충돌이 발견되었습니다. 시간표를 다시 확인해주세요.',
                    style: TextStyle(color: Colors.red),
                  ),
                ],
              ],
            );
          },
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }

  Widget _buildCheckItem(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  bool _checkForConflicts(List<Course> courses) {
    for (int i = 0; i < courses.length; i++) {
      for (int j = i + 1; j < courses.length; j++) {
        if (_coursesHaveConflict(courses[i], courses[j])) {
          return true;
        }
      }
    }
    return false;
  }

  bool _coursesHaveConflict(Course course1, Course course2) {
    for (final time1 in course1.times) {
      for (final time2 in course2.times) {
        if (time1.dayOfWeek == time2.dayOfWeek) {
          final start1 = time1.startHour * 60 + time1.startMinute;
          final end1 = time1.endHour * 60 + time1.endMinute;
          final start2 = time2.startHour * 60 + time2.startMinute;
          final end2 = time2.endHour * 60 + time2.endMinute;
          
          if ((start1 < end2 && end1 > start2)) {
            return true;
          }
        }
      }
    }
    return false;
  }
}
