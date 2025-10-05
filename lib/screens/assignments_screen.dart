import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/assignment.dart';
import '../services/firebase_service.dart';
import '../models/learnus_credentials.dart';

class AssignmentsScreen extends StatefulWidget {
  const AssignmentsScreen({super.key});

  @override
  State<AssignmentsScreen> createState() => _AssignmentsScreenState();
}

class _AssignmentsScreenState extends State<AssignmentsScreen>
    with TickerProviderStateMixin {
  bool _isLoggedIn = false;
  bool _isLoading = false;
  String? _error;
  List<Assignment> _assignments = [];
  DateTime? _lastUpdated;
  late AnimationController _loadingController;
  late AnimationController _fadeController;

  @override
  void initState() {
    super.initState();
    _loadingController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    // LearnUs 정보 자동 확인
    _checkLearnUsCredentials();
  }

  @override
  void dispose() {
    _loadingController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      body: PageView(
        physics: const NeverScrollableScrollPhysics(), // 좌우 스와이프 비활성화
        children: [
          _isLoggedIn ? _buildAssignmentsView() : _buildOnboardingView(),
        ],
      ),
    );
  }

  Widget _buildOnboardingView() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF667EEA),
            Color(0xFF764BA2),
          ],
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 메인 아이콘
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(60),
                  border: Border.all(color: Colors.white.withOpacity(0.3), width: 2),
                ),
                child: const Icon(
                  Icons.school,
                  size: 60,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 32),
              
              // 메인 타이틀
              const Text(
                '학교사이트 아이디와 비밀번호만\n알려주세요!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 16),
              
              // 서브 타이틀
              const Text(
                'AI가 알아서 안한 과제 알려드릴게요!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.white70,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 48),

              // 로그인 버튼
              Container(
                width: double.infinity,
                height: 56,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(28),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(28),
                    onTap: _showLoginDialog,
                    child: const Center(
                      child: Text(
                        '로그인하기',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF667EEA),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // 보안 안내
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.security,
                    size: 16,
                    color: Colors.white.withOpacity(0.7),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '개인정보는 안전하게 보호됩니다',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showLoginDialog() {
    final TextEditingController idController = TextEditingController();
    final TextEditingController pwController = TextEditingController();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 아이콘
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: const Icon(
                  Icons.login,
                  size: 30,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 20),
              
              // 타이틀
              const Text(
                '학교 계정 정보',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'LearnUs 로그인 정보를 입력해주세요',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white.withOpacity(0.8),
                ),
              ),
              const SizedBox(height: 24),
              
              // 아이디 입력
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: idController,
                  decoration: const InputDecoration(
                    hintText: '아이디',
                    prefixIcon: Icon(Icons.person, color: Color(0xFF667EEA)),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // 비밀번호 입력
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: pwController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    hintText: '비밀번호',
                    prefixIcon: Icon(Icons.lock, color: Color(0xFF667EEA)),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // 로그인 버튼
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    _login(idController.text, pwController.text);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFF667EEA),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    elevation: 0,
                  ),
                  child: const Text(
                    '확인완료!',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _login(String id, String password) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    // 로딩 애니메이션 시작
    _loadingController.repeat();

    try {
      // 백엔드 연결 테스트 (여러 주소 시도)
      bool serverConnected = false;
      String? serverUrl;
      
      // 시도할 서버 주소들
      final serverUrls = [
        'https://learnus-backend-986202706020.asia-northeast3.run.app', // Cloud Run 서비스
        'http://10.0.2.2:8000',  // 에뮬레이터용
        'http://localhost:8000', // 로컬호스트
        'http://127.0.0.1:8000', // 루프백
      ];
      
      for (String url in serverUrls) {
        try {
          print('🔍 서버 연결 시도: $url');
          final testResponse = await http.get(
            Uri.parse('$url/health'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(const Duration(seconds: 5));
          
          if (testResponse.statusCode == 200) {
            print('✅ 서버 연결 성공: $url');
            serverConnected = true;
            serverUrl = url;
            break;
          }
        } catch (e) {
          print('❌ 서버 연결 실패: $url - $e');
          continue;
        }
      }

      if (serverConnected && serverUrl != null) {
        // 서버가 실행 중이면 자동화 실행
        await _runAutomation(serverUrl);
      } else {
        // 서버가 없으면 시뮬레이션 모드로 실행
        print('⚠️ 모든 서버 연결 실패, 시뮬레이션 모드로 실행');
        await _runSimulation();
      }
    } catch (e) {
      // 서버 연결 실패 시 시뮬레이션 모드로 실행
      print('서버 연결 실패, 시뮬레이션 모드로 실행: $e');
      await _runSimulation();
    } finally {
      _loadingController.stop();
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _runAutomation(String serverUrl) async {
    setState(() {
      _isLoggedIn = true;
    });

    // 페이드 인 애니메이션
    _fadeController.forward();

    try {
      // 백엔드에서 assignment.txt 파일 정보 조회
      final response = await http.get(
        Uri.parse('$serverUrl/assignments'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final assignmentsData = data['assignments'] as List;
        final totalCount = data['total_count'] ?? 0;
        final incompleteCount = data['incomplete_count'] ?? 0;
        final lastUpdate = data['last_update'];
        
        print('📊 assignment.txt 파일에서 데이터 로드 완료:');
        print('   총 과제: $totalCount개');
        print('   미완료: $incompleteCount개');
        print('   마지막 업데이트: $lastUpdate');
        
        setState(() {
          _assignments = assignmentsData.map((item) => Assignment(
            course: item['course'] ?? '',
            activity: item['activity'] ?? '',
            type: item['type'] ?? '과제',
            status: item['status'] ?? '❓ 상태 불명',
            url: item['url'] ?? '',
          )).toList();
          _lastUpdated = DateTime.now(); // 업데이트 시간 기록
        });
        
        print('✅ 실제 LearnUs 데이터 표시 완료!');
      } else {
        print('❌ assignment.txt 데이터 로드 실패, 시뮬레이션 모드로 전환');
        await _runSimulation(); // 실패 시 시뮬레이션
      }
    } catch (e) {
      print('assignment.txt 파일 읽기 실패: $e');
      await _runSimulation(); // 실패 시 시뮬레이션
    }
  }

  Future<void> _runSimulation() async {
    setState(() {
      _isLoggedIn = true;
    });

    // 페이드 인 애니메이션
    _fadeController.forward();

    // 시뮬레이션 로딩 (3초)
    await Future.delayed(const Duration(seconds: 3));
    
    setState(() {
      _assignments = [
        Assignment(
          course: 'AI응용수학',
          activity: '5주차 과제',
          type: '과제',
          status: '❌ 해야 할 과제',
          url: 'https://ys.learnus.org/mod/assign/view.php?id=123',
        ),
        Assignment(
          course: 'AI응용수학',
          activity: '4주차 퀴즈',
          type: '퀴즈',
          status: '✅ 완료',
          url: 'https://ys.learnus.org/mod/quiz/view.php?id=124',
        ),
        Assignment(
          course: '딥러닝입문',
          activity: '5주차 동영상',
          type: '동영상',
          status: '❌ 해야 할 과제',
          url: 'https://ys.learnus.org/mod/video/view.php?id=125',
        ),
        Assignment(
          course: '기초AI알고리즘',
          activity: '5주차 실습',
          type: '실습',
          status: '❌ 해야 할 과제',
          url: 'https://ys.learnus.org/mod/assign/view.php?id=126',
        ),
        Assignment(
          course: 'AI시스템프로그래밍',
          activity: '4주차 프로젝트',
          type: '프로젝트',
          status: '✅ 완료',
          url: 'https://ys.learnus.org/mod/assign/view.php?id=127',
        ),
      ];
    });
  }

  Widget _buildAssignmentsView() {
    return FadeTransition(
      opacity: _fadeController,
      child: Column(
        children: [
          // 헤더
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF667EEA).withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: SafeArea(
              child: Column(
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.assignment,
                        color: Colors.white,
                        size: 28,
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        '이번주 과제',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${_assignments.length}개',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  // 업데이트 시간 표시
                  if (_lastUpdated != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.update,
                            color: Colors.white70,
                            size: 16,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '마지막 업데이트: ${_formatDateTime(_lastUpdated!)}',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  if (_isLoading) ...[
                    const Text(
                      'assignment.txt 파일에서 과제정보를 불러오고 있어요..',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      '⚡ 빠른 로딩 (파일 기반)',
                      style: TextStyle(
                        color: Colors.white60,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: 50,
                      height: 50,
                      child: CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        strokeWidth: 4,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      '잠시만 기다려주세요...',
                      style: TextStyle(
                        color: Colors.white60,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          
          // 과제 목록
          Expanded(
            child: _assignments.isEmpty
                ? _buildEmptyState()
                : _buildSortedAssignmentsList(),
          ),
          
          // 시뮬레이션 모드 버튼 (하단에 작게)
          if (!_isLoading && _assignments.isEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              child: Center(
                child: TextButton.icon(
                  onPressed: _runSimulation,
                  icon: const Icon(Icons.science, size: 16),
                  label: const Text(
                    '시뮬레이션 모드',
                    style: TextStyle(fontSize: 12),
                  ),
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.grey.shade600,
                    backgroundColor: Colors.grey.shade100,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSortedAssignmentsList() {
    // 안한 과제를 먼저, 완료된 과제를 나중에 배치
    final sortedAssignments = List<Assignment>.from(_assignments);
    sortedAssignments.sort((a, b) {
      // 안한 과제(❌)가 완료된 과제(✅)보다 앞에 오도록 정렬
      if (a.isIncomplete && !b.isIncomplete) return -1;
      if (!a.isIncomplete && b.isIncomplete) return 1;
      
      // 같은 상태 내에서는 과목명으로 정렬
      return a.course.compareTo(b.course);
    });

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: sortedAssignments.length,
      itemBuilder: (context, index) {
        final assignment = sortedAssignments[index];
        return _buildAssignmentCard(assignment);
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: const Color(0xFF667EEA).withOpacity(0.1),
              borderRadius: BorderRadius.circular(60),
            ),
            child: const Icon(
              Icons.check_circle_outline,
              size: 60,
              color: Color(0xFF667EEA),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            '모든 과제를 완료했어요!',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF667EEA),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '잘했어요! 다음 주에도 화이팅!',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAssignmentCard(Assignment assignment) {
    final isCompleted = assignment.status.contains('✅');
    final isIncomplete = assignment.isIncomplete;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: isIncomplete 
            ? Border.all(color: Colors.red.withOpacity(0.3), width: 2)
            : null,
        boxShadow: [
          BoxShadow(
            color: isIncomplete 
                ? Colors.red.withOpacity(0.1)
                : Colors.black.withOpacity(0.05),
            blurRadius: isIncomplete ? 15 : 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => _showAssignmentDetail(assignment),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // 상태 아이콘
                Stack(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: isCompleted 
                            ? Colors.green.withOpacity(0.1)
                            : Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: Icon(
                        isCompleted ? Icons.check_circle : Icons.assignment,
                        color: isCompleted ? Colors.green : Colors.red,
                        size: 24,
                      ),
                    ),
                    if (isIncomplete)
                      Positioned(
                        top: 0,
                        right: 0,
                        child: Container(
                          width: 16,
                          height: 16,
                          decoration: BoxDecoration(
                            color: Colors.red,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Icon(
                            Icons.priority_high,
                            color: Colors.white,
                            size: 10,
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(width: 16),
                
                // 과제 정보
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        assignment.course,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        assignment.activity,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        assignment.type,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // 상태 표시
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: isCompleted 
                        ? Colors.green.withOpacity(0.1)
                        : Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    assignment.status,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isCompleted ? Colors.green : Colors.red,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showAssignmentDetail(Assignment assignment) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 아이콘
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: assignment.status.contains('✅') 
                      ? Colors.green.withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: Icon(
                  assignment.status.contains('✅') 
                      ? Icons.check_circle 
                      : Icons.assignment,
                  color: assignment.status.contains('✅') 
                      ? Colors.green 
                      : Colors.red,
                  size: 30,
                ),
              ),
              const SizedBox(height: 16),
              
              // 제목
              Text(
                assignment.activity,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                assignment.course,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 16),
              
              // 상태
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: assignment.status.contains('✅') 
                      ? Colors.green.withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  assignment.status,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: assignment.status.contains('✅') 
                        ? Colors.green 
                        : Colors.red,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // 닫기 버튼
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF667EEA),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    '닫기',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 날짜/시간 포맷팅 함수
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return '방금 전';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}분 전';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}시간 전';
    } else {
      return '${dateTime.month}/${dateTime.day} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    }
  }

  // LearnUs 정보 자동 확인
  Future<void> _checkLearnUsCredentials() async {
    try {
      print('🔍 LearnUs 정보 자동 확인 중...');
      
      // Firebase에서 현재 사용자의 LearnUs 정보 조회
      final credentials = await FirebaseService.getLearnUsCredentials();
      
      if (credentials != null && credentials.isActive) {
        print('✅ LearnUs 정보 발견: ${credentials.username}');
        
        // 자동으로 로그인 상태로 설정
        setState(() {
          _isLoggedIn = true;
        });
        
        // 자동으로 과제 정보 로드
        await _loadAssignments();
        
        print('🎉 LearnUs 정보로 자동 로그인 완료!');
      } else {
        print('ℹ️ LearnUs 정보가 없습니다. 수동 로그인이 필요합니다.');
      }
    } catch (e) {
      print('❌ LearnUs 정보 확인 실패: $e');
    }
  }

  // 과제 정보 자동 로드
  Future<void> _loadAssignments() async {
    setState(() {
      _isLoading = true;
    });

    // 페이드 인 애니메이션
    _fadeController.forward();

    try {
      // 여러 서버 URL 시도
      final serverUrls = [
        'https://learnus-backend-986202706020.asia-northeast3.run.app', // Cloud Run 서비스
        'http://10.0.2.2:8000',  // 에뮬레이터용
        'http://localhost:8000', // 로컬호스트
        'http://127.0.0.1:8000', // 루프백
      ];

      bool success = false;
      for (String serverUrl in serverUrls) {
        try {
          print('🔍 서버 연결 시도: $serverUrl');
          
          final response = await http.get(
            Uri.parse('$serverUrl/assignments'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(const Duration(seconds: 10));

          if (response.statusCode == 200) {
            print('✅ 서버 연결 성공: $serverUrl');
            
            final data = json.decode(response.body);
            final assignmentsData = data['assignments'] as List;
            final totalCount = data['total_count'] ?? 0;
            final incompleteCount = data['incomplete_count'] ?? 0;
            final lastUpdate = data['last_update'];
            
            print('📊 assignment.txt 파일에서 데이터 로드 완료:');
            print('   총 과제: $totalCount개');
            print('   미완료: $incompleteCount개');
            print('   마지막 업데이트: $lastUpdate');
            
            setState(() {
              _assignments = assignmentsData.map((item) => Assignment(
                course: item['course'] ?? '',
                activity: item['activity'] ?? '',
                type: item['type'] ?? '과제',
                status: item['status'] ?? '❓ 상태 불명',
                url: item['url'] ?? '',
              )).toList();
              _lastUpdated = DateTime.now(); // 업데이트 시간 기록
            });
            
            print('✅ 실제 LearnUs 데이터 표시 완료!');
            success = true;
            break;
          }
        } catch (e) {
          print('❌ 서버 연결 실패: $serverUrl - $e');
          continue;
        }
      }

      if (!success) {
        print('❌ 모든 서버 연결 실패, 시뮬레이션 모드로 실행');
        await _runSimulation();
      }
    } catch (e) {
      print('❌ 과제 정보 로드 실패: $e');
      setState(() {
        _error = '과제 정보를 불러오는데 실패했습니다: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
