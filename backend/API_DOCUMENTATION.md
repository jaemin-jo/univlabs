# LearnUs 자동화 서버 API 문서

## 🚀 **서버 실행 방법**

### 1. 로컬 실행
```bash
cd backend
pip install -r requirements.txt
python server_architecture.py
```

### 2. Docker 실행
```bash
cd backend
docker-compose up -d
```

## 📱 **모바일 앱과의 통합**

### **Base URL**: `http://localhost:8000`

---

## 🔐 **사용자 관리 API**

### **1. 사용자 등록**
```http
POST /users/register
Content-Type: application/json

{
  "username": "학번",
  "password": "비밀번호",
  "learnus_id": "LearnUs ID"
}
```

**응답:**
```json
{
  "message": "사용자가 성공적으로 등록되었습니다",
  "user_id": 123
}
```

### **2. 사용자 로그인**
```http
POST /users/login
Content-Type: application/json

{
  "username": "학번",
  "password": "비밀번호"
}
```

---

## 📋 **과제 관리 API**

### **1. 사용자의 모든 과제 조회**
```http
GET /users/{user_id}/assignments
```

**응답:**
```json
{
  "user_id": 123,
  "assignments": [
    {
      "id": 1,
      "course_name": "AI응용수학",
      "activity_name": "5주차 과제",
      "activity_type": "과제",
      "activity_url": "https://ys.learnus.org/mod/assign/view.php?id=123",
      "status": "❌ 해야 할 과제",
      "due_date": "2025-10-10T23:59:59",
      "updated_at": "2025-10-03T00:37:16"
    }
  ]
}
```

### **2. 미완료 과제만 조회**
```http
GET /users/{user_id}/assignments/incomplete
```

**응답:**
```json
{
  "user_id": 123,
  "incomplete_assignments": [
    {
      "id": 1,
      "course_name": "AI응용수학",
      "activity_name": "5주차 과제",
      "activity_type": "과제",
      "activity_url": "https://ys.learnus.org/mod/assign/view.php?id=123",
      "status": "❌ 해야 할 과제",
      "due_date": "2025-10-10T23:59:59",
      "updated_at": "2025-10-03T00:37:16"
    }
  ]
}
```

### **3. 특정 상태의 과제 조회**
```http
GET /users/{user_id}/assignments?status=❌ 해야 할 과제
```

---

## 🤖 **자동화 관리 API**

### **1. 즉시 자동화 실행**
```http
POST /users/{user_id}/automation/run
```

**응답:**
```json
{
  "message": "자동화 작업이 시작되었습니다"
}
```

### **2. 자동화 로그 조회**
```http
GET /users/{user_id}/logs?limit=10
```

**응답:**
```json
{
  "user_id": 123,
  "logs": [
    {
      "id": 1,
      "status": "성공",
      "message": "자동화 작업 완료: 15개 활동 처리",
      "execution_time": "2025-10-03T00:37:16"
    }
  ]
}
```

---

## 📱 **Flutter 앱 통합 예시**

### **1. HTTP 클라이언트 설정**
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class LearnUsApiService {
  static const String baseUrl = 'http://localhost:8000';
  
  // 미완료 과제 조회
  static Future<List<Assignment>> getIncompleteAssignments(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$userId/assignments/incomplete'),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['incomplete_assignments'] as List)
          .map((json) => Assignment.fromJson(json))
          .toList();
    }
    throw Exception('과제 조회 실패');
  }
  
  // 즉시 자동화 실행
  static Future<void> runAutomation(int userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/$userId/automation/run'),
    );
    
    if (response.statusCode != 200) {
      throw Exception('자동화 실행 실패');
    }
  }
}
```

### **2. Assignment 모델**
```dart
class Assignment {
  final int id;
  final String courseName;
  final String activityName;
  final String activityType;
  final String activityUrl;
  final String status;
  final DateTime? dueDate;
  final DateTime updatedAt;
  
  Assignment({
    required this.id,
    required this.courseName,
    required this.activityName,
    required this.activityType,
    required this.activityUrl,
    required this.status,
    this.dueDate,
    required this.updatedAt,
  });
  
  factory Assignment.fromJson(Map<String, dynamic> json) {
    return Assignment(
      id: json['id'],
      courseName: json['course_name'],
      activityName: json['activity_name'],
      activityType: json['activity_type'],
      activityUrl: json['activity_url'],
      status: json['status'],
      dueDate: json['due_date'] != null 
          ? DateTime.parse(json['due_date']) 
          : null,
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
```

### **3. UI 위젯 예시**
```dart
class AssignmentListWidget extends StatefulWidget {
  final int userId;
  
  const AssignmentListWidget({Key? key, required this.userId}) : super(key: key);
  
  @override
  _AssignmentListWidgetState createState() => _AssignmentListWidgetState();
}

class _AssignmentListWidgetState extends State<AssignmentListWidget> {
  List<Assignment> assignments = [];
  bool isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadAssignments();
  }
  
  Future<void> _loadAssignments() async {
    try {
      final incompleteAssignments = await LearnUsApiService
          .getIncompleteAssignments(widget.userId);
      setState(() {
        assignments = incompleteAssignments;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('과제 조회 실패: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    
    return ListView.builder(
      itemCount: assignments.length,
      itemBuilder: (context, index) {
        final assignment = assignments[index];
        return Card(
          child: ListTile(
            title: Text(assignment.activityName),
            subtitle: Text(assignment.courseName),
            trailing: Text(
              assignment.status,
              style: TextStyle(
                color: assignment.status.contains('❌') 
                    ? Colors.red 
                    : Colors.green,
                fontWeight: FontWeight.bold,
              ),
            ),
            onTap: () {
              // 과제 상세 페이지로 이동
              _openAssignmentDetail(assignment);
            },
          ),
        );
      },
    );
  }
  
  void _openAssignmentDetail(Assignment assignment) {
    // 과제 상세 페이지 구현
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AssignmentDetailPage(assignment: assignment),
      ),
    );
  }
}
```

---

## 🔄 **자동화 스케줄링**

### **기본 설정:**
- **실행 주기**: 6시간마다
- **실행 시간**: 24시간 내내
- **재시도**: 실패 시 1시간 후 재시도

### **스케줄 변경:**
```python
# 특정 사용자의 스케줄 변경
scheduler.schedule_user_automation(user_id, interval_hours=3)  # 3시간마다
```

---

## 📊 **모니터링 및 로깅**

### **로그 레벨:**
- `INFO`: 일반적인 작업 로그
- `WARNING`: 주의가 필요한 상황
- `ERROR`: 오류 발생

### **헬스체크:**
```http
GET /health
```

---

## 🚀 **배포 가이드**

### **1. 로컬 개발**
```bash
cd backend
python server_architecture.py
```

### **2. Docker 배포**
```bash
cd backend
docker-compose up -d
```

### **3. 프로덕션 배포**
```bash
# 환경 변수 설정
export DATABASE_URL="postgresql://user:password@localhost/learnus_db"
export LOG_LEVEL="WARNING"

# 서버 실행
gunicorn server_architecture:app -w 4 -k uvicorn.workers.UvicornWorker
```




















