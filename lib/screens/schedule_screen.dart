import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:intl/date_symbol_data_local.dart';
import '../providers/schedule_provider.dart';
import '../models/schedule_item.dart';
import '../widgets/schedule_card.dart';

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  CalendarFormat _calendarFormat = CalendarFormat.month;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  ScheduleType? _selectedType;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _selectedDay = DateTime.now();
    // 한국어 로케일 초기화
    initializeDateFormatting('ko_KR', null);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // 한글 월 표시를 위한 헬퍼 메서드
  String _getKoreanMonthYear(DateTime date) {
    final months = [
      '1월', '2월', '3월', '4월', '5월', '6월',
      '7월', '8월', '9월', '10월', '11월', '12월'
    ];
    
    return '${date.year}년 ${months[date.month - 1]}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('일정 관리'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '캘린더'),
            Tab(text: '목록'),
            Tab(text: '분류별'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              _showAddScheduleDialog();
            },
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildCalendarView(),
          _buildListView(),
          _buildCategoryView(),
        ],
      ),
    );
  }

  Widget _buildCalendarView() {
    return Column(
      children: [
        TableCalendar<ScheduleItem>(
          firstDay: DateTime.utc(2020, 1, 1),
          lastDay: DateTime.utc(2030, 12, 31),
          focusedDay: _focusedDay,
          calendarFormat: _calendarFormat,
          locale: 'ko_KR', // 한국어 로케일 설정
          eventLoader: (day) {
            return context.read<ScheduleProvider>().schedules
                .where((schedule) => 
                    schedule.date.year == day.year &&
                    schedule.date.month == day.month &&
                    schedule.date.day == day.day)
                .toList();
          },
          startingDayOfWeek: StartingDayOfWeek.monday,
          calendarStyle: CalendarStyle(
            outsideDaysVisible: false,
            markersMaxCount: 3,
            markerDecoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              shape: BoxShape.circle,
            ),
          ),
          headerStyle: HeaderStyle(
            formatButtonVisible: true,
            titleCentered: true,
            titleTextStyle: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
            leftChevronIcon: const Icon(Icons.chevron_left),
            rightChevronIcon: const Icon(Icons.chevron_right),
            formatButtonShowsNext: false,
            formatButtonDecoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              borderRadius: BorderRadius.circular(12),
            ),
            formatButtonTextStyle: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          onDaySelected: (selectedDay, focusedDay) {
            setState(() {
              _selectedDay = selectedDay;
              _focusedDay = focusedDay;
            });
          },
          onFormatChanged: (format) {
            setState(() {
              _calendarFormat = format;
            });
          },
          onPageChanged: (focusedDay) {
            _focusedDay = focusedDay;
          },
          selectedDayPredicate: (day) {
            return isSameDay(_selectedDay, day);
          },
        ),
        const Divider(),
        Expanded(
          child: _buildSelectedDayEvents(),
        ),
      ],
    );
  }

  Widget _buildSelectedDayEvents() {
    if (_selectedDay == null) return const SizedBox();

    return Consumer<ScheduleProvider>(
      builder: (context, provider, child) {
        final dayEvents = provider.schedules
            .where((schedule) => 
                schedule.date.year == _selectedDay!.year &&
                schedule.date.month == _selectedDay!.month &&
                schedule.date.day == _selectedDay!.day)
            .toList();

        if (dayEvents.isEmpty) {
          return const Center(
            child: Text('선택한 날짜에 일정이 없습니다.'),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: dayEvents.length,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: ScheduleCard(schedule: dayEvents[index]),
            );
          },
        );
      },
    );
  }

  Widget _buildListView() {
    return Consumer<ScheduleProvider>(
      builder: (context, provider, child) {
        final schedules = provider.schedules;
        
        if (schedules.isEmpty) {
          return const Center(
            child: Text('등록된 일정이 없습니다.'),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: schedules.length,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: ScheduleCard(schedule: schedules[index]),
            );
          },
        );
      },
    );
  }

  Widget _buildCategoryView() {
    return Column(
      children: [
        Container(
          height: 50,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: ScheduleType.values.length,
            itemBuilder: (context, index) {
              final type = ScheduleType.values[index];
              final isSelected = _selectedType == type;
              
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: FilterChip(
                  label: Text(type.displayName),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      _selectedType = selected ? type : null;
                    });
                  },
                  avatar: Text(type.icon),
                ),
              );
            },
          ),
        ),
        const Divider(),
        Expanded(
          child: Consumer<ScheduleProvider>(
            builder: (context, provider, child) {
              List<ScheduleItem> filteredSchedules = provider.schedules;
              
              if (_selectedType != null) {
                filteredSchedules = provider.schedules
                    .where((schedule) => schedule.type == _selectedType)
                    .toList();
              }

              if (filteredSchedules.isEmpty) {
                return Center(
                  child: Text(
                    _selectedType == null 
                        ? '등록된 일정이 없습니다.'
                        : '${_selectedType!.displayName} 일정이 없습니다.',
                  ),
                );
              }

              return ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: filteredSchedules.length,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: ScheduleCard(schedule: filteredSchedules[index]),
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }

  void _showAddScheduleDialog() {
    showDialog(
      context: context,
      builder: (context) => const AddScheduleDialog(),
    );
  }
}

class AddScheduleDialog extends StatefulWidget {
  const AddScheduleDialog({super.key});

  @override
  State<AddScheduleDialog> createState() => _AddScheduleDialogState();
}

class _AddScheduleDialogState extends State<AddScheduleDialog> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  DateTime _date = DateTime.now();
  DateTime? _endDate;
  ScheduleType _selectedType = ScheduleType.general;
  SchedulePriority _priority = SchedulePriority.medium;
  bool _isImportant = false;

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  // 학기 판단
  String _getSemester(DateTime date) {
    final month = date.month;
    if (month >= 2 && month <= 7) {
      return '2025-1학기';
    } else {
      return '2025-2학기';
    }
  }

  // 태그 생성
  List<String> _generateTags(ScheduleType type, String title) {
    final tags = <String>[];
    
    // 타입 기반 태그
    switch (type) {
      case ScheduleType.enrollment:
        tags.addAll(['수강신청', '등록']);
        break;
      case ScheduleType.exam:
        tags.addAll(['시험', '성적']);
        break;
      case ScheduleType.leave:
        tags.addAll(['휴학', '복학']);
        break;
      case ScheduleType.graduation:
        tags.addAll(['졸업', '학위']);
        break;
      default:
        tags.add('학사일정');
    }
    
    // 제목 기반 태그
    if (title.contains('수강신청')) tags.add('수강신청');
    if (title.contains('등록')) tags.add('등록');
    if (title.contains('시험')) tags.add('시험');
    if (title.contains('휴학')) tags.add('휴학');
    if (title.contains('복학')) tags.add('복학');
    if (title.contains('졸업')) tags.add('졸업');
    
    return tags.toSet().toList(); // 중복 제거
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('새 일정 추가'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: '제목',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '제목을 입력해주세요';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: '설명',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<ScheduleType>(
                value: _selectedType,
                decoration: const InputDecoration(
                  labelText: '분류',
                  border: OutlineInputBorder(),
                ),
                items: ScheduleType.values.map((type) {
                  return DropdownMenuItem(
                    value: type,
                    child: Row(
                      children: [
                        Text(type.icon),
                        const SizedBox(width: 8),
                        Text(type.displayName),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedType = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              ListTile(
                title: const Text('날짜'),
                subtitle: Text('${_date.year}년 ${_date.month}월 ${_date.day}일'),
                onTap: () async {
                  final date = await showDatePicker(
                    context: context,
                    initialDate: _date,
                    firstDate: DateTime.now(),
                    lastDate: DateTime.now().add(const Duration(days: 365)),
                  );
                  if (date != null) {
                    setState(() {
                      _date = date;
                    });
                  }
                },
              ),
              const SizedBox(height: 8),
              CheckboxListTile(
                title: const Text('기간 일정 (종료일 있음)'),
                value: _endDate != null,
                onChanged: (value) {
                  setState(() {
                    _endDate = value! ? _date.add(const Duration(days: 1)) : null;
                  });
                },
              ),
              if (_endDate != null) ...[
                const SizedBox(height: 8),
                ListTile(
                  title: const Text('종료일'),
                  subtitle: Text('${_endDate!.year}년 ${_endDate!.month}월 ${_endDate!.day}일'),
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: _endDate!,
                      firstDate: _date,
                      lastDate: DateTime.now().add(const Duration(days: 365)),
                    );
                    if (date != null) {
                      setState(() {
                        _endDate = date;
                      });
                    }
                  },
                ),
              ],
              const SizedBox(height: 16),
              DropdownButtonFormField<SchedulePriority>(
                value: _priority,
                decoration: const InputDecoration(
                  labelText: '우선순위',
                  border: OutlineInputBorder(),
                ),
                items: SchedulePriority.values.map((priority) {
                  String displayName;
                  switch (priority) {
                    case SchedulePriority.high:
                      displayName = '높음';
                      break;
                    case SchedulePriority.medium:
                      displayName = '보통';
                      break;
                    case SchedulePriority.low:
                      displayName = '낮음';
                      break;
                  }
                  return DropdownMenuItem(
                    value: priority,
                    child: Text(displayName),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _priority = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              CheckboxListTile(
                title: const Text('중요 일정'),
                value: _isImportant,
                onChanged: (value) {
                  setState(() {
                    _isImportant = value!;
                  });
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('취소'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_formKey.currentState!.validate()) {
              final schedule = ScheduleItem(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
                title: _titleController.text,
                description: _descriptionController.text,
                date: _date,
                endDate: _endDate,
                type: _selectedType,
                status: ScheduleStatus.upcoming,
                priority: _priority,
                isImportant: _isImportant,
                university: '연세대학교',
                semester: _getSemester(_date),
                tags: _generateTags(_selectedType, _titleController.text),
              );
              
              context.read<ScheduleProvider>().addSchedule(schedule);
              Navigator.of(context).pop();
              
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('일정이 추가되었습니다')),
              );
            }
          },
          child: const Text('추가'),
        ),
      ],
    );
  }
}
