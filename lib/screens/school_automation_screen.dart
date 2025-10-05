import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/school_automation_service.dart';
import '../models/assignment.dart';
import '../widgets/assignment_card.dart';
import '../widgets/loading_widget.dart';

/// 학교 자동화 설정 및 관리 화면
class SchoolAutomationScreen extends StatefulWidget {
  const SchoolAutomationScreen({super.key});

  @override
  State<SchoolAutomationScreen> createState() => _SchoolAutomationScreenState();
}

class _SchoolAutomationScreenState extends State<SchoolAutomationScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _universityController = TextEditingController();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _studentIdController = TextEditingController();
  
  // 테스트 화면용 컨트롤러
  final _testSchoolController = TextEditingController();
  final _testUsernameController = TextEditingController();
  final _testPasswordController = TextEditingController();
  
  late TabController _tabController;
  
  bool _isLoading = false;
  bool _isAutomationRunning = false;
  bool _isTesting = false;
  String _testResult = '';
  String _firebaseStatus = '';
  String _selectedTestUniversity = '';
  List<Assignment> _assignments = [];
  List<Assignment> _newAssignments = [];
  List<Assignment> _upcomingAssignments = [];
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadSavedCredentials();
    _checkAutomationStatus();
    _checkFirebaseConnection();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    _universityController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _studentIdController.dispose();
    _testSchoolController.dispose();
    _testUsernameController.dispose();
    _testPasswordController.dispose();
    super.dispose();
  }
  
  // Firebase 연결 상태 확인
  Future<void> _checkFirebaseConnection() async {
    try {
      setState(() {
        _firebaseStatus = '✅ Firebase 연결 성공';
      });
    } catch (e) {
      setState(() {
        _firebaseStatus = '❌ Firebase 연결 실패: $e';
      });
    }
  }

  // 학교별 사이트 링크 정보
  Map<String, Map<String, String>> _getUniversityInfo() {
    return {
      '연세대학교': {
        'name': '연세대학교',
        'platform': 'LearnUs',
        'url': 'https://ys.learnus.org/',
        'description': '연세대학교 온라인 학습 플랫폼',
      },
      '고려대학교': {
        'name': '고려대학교',
        'platform': 'LMS',
        'url': 'https://lms.korea.ac.kr/',
        'description': '고려대학교 학습관리시스템',
      },
      '서울대학교': {
        'name': '서울대학교',
        'platform': 'Blackboard',
        'url': 'https://snu.blackboard.com/',
        'description': '서울대학교 블랙보드 시스템',
      },
      '한국과학기술원': {
        'name': '한국과학기술원',
        'platform': 'KLMS',
        'url': 'https://klms.kaist.ac.kr/',
        'description': 'KAIST 학습관리시스템',
      },
      '포스텍': {
        'name': '포스텍',
        'platform': 'LMS',
        'url': 'https://lms.postech.ac.kr/',
        'description': '포스텍 학습관리시스템',
      },
      '성균관대학교': {
        'name': '성균관대학교',
        'platform': 'LMS',
        'url': 'https://lms.skku.edu/',
        'description': '성균관대학교 학습관리시스템',
      },
      '한양대학교': {
        'name': '한양대학교',
        'platform': 'LMS',
        'url': 'https://lms.hanyang.ac.kr/',
        'description': '한양대학교 학습관리시스템',
      },
      '중앙대학교': {
        'name': '중앙대학교',
        'platform': 'LMS',
        'url': 'https://lms.cau.ac.kr/',
        'description': '중앙대학교 학습관리시스템',
      },
      '경희대학교': {
        'name': '경희대학교',
        'platform': 'LMS',
        'url': 'https://lms.khu.ac.kr/',
        'description': '경희대학교 학습관리시스템',
      },
      '동국대학교': {
        'name': '동국대학교',
        'platform': 'LMS',
        'url': 'https://lms.dongguk.edu/',
        'description': '동국대학교 학습관리시스템',
      },
    };
  }

  // 저장된 자격 증명 로드
  Future<void> _loadSavedCredentials() async {
    try {
      final credentials = await SchoolAutomationService.instance.getUserCredentials();
      if (credentials != null) {
        setState(() {
          _universityController.text = credentials['university'] ?? '';
          _usernameController.text = credentials['username'] ?? '';
          _passwordController.text = credentials['password'] ?? '';
          _studentIdController.text = credentials['studentId'] ?? '';
        });
      }
    } catch (e) {
      _showErrorSnackBar('자격 증명 로드 오류: $e');
    }
  }
  
  // 자격 증명 저장
  Future<void> _saveCredentials() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      await SchoolAutomationService.instance.saveUserCredentials(
        university: _universityController.text.trim(),
        username: _usernameController.text.trim(),
        password: _passwordController.text.trim(),
        studentId: _studentIdController.text.trim(),
      );
      
      _showSuccessSnackBar('자격 증명이 저장되었습니다');
    } catch (e) {
      _showErrorSnackBar('자격 증명 저장 오류: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  // 로그인 테스트
  Future<void> _testLogin() async {
    setState(() => _isLoading = true);
    
    try {
      final success = await SchoolAutomationService.instance.loginToSchool();
      
      if (success) {
        _showSuccessSnackBar('로그인 성공!');
        await _loadAssignments();
      } else {
        _showErrorSnackBar('로그인 실패. 자격 증명을 확인해주세요.');
      }
    } catch (e) {
      _showErrorSnackBar('로그인 오류: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  // 과제 정보 로드
  Future<void> _loadAssignments() async {
    try {
      final assignments = await SchoolAutomationService.instance.fetchAssignments();
      final newAssignments = await SchoolAutomationService.instance.checkNewAssignments();
      final upcomingAssignments = await SchoolAutomationService.instance.checkUpcomingDeadlines();
      
      setState(() {
        _assignments = assignments;
        _newAssignments = newAssignments;
        _upcomingAssignments = upcomingAssignments;
      });
    } catch (e) {
      _showErrorSnackBar('과제 정보 로드 오류: $e');
    }
  }
  
  // 자동화 상태 확인
  Future<void> _checkAutomationStatus() async {
    try {
      final status = await SchoolAutomationService.instance.getAutomationStatus();
      setState(() {
        _isAutomationRunning = status['status'] == 'running';
      });
    } catch (e) {
      debugPrint('자동화 상태 확인 오류: $e');
    }
  }
  
  
  // 자동화 시작/중지
  Future<void> _toggleAutomation() async {
    setState(() => _isLoading = true);
    
    try {
      bool success;
      if (_isAutomationRunning) {
        success = await SchoolAutomationService.instance.stopAutomation();
        if (success) {
          _showSuccessSnackBar('자동화가 중지되었습니다');
        }
      } else {
        success = await SchoolAutomationService.instance.startAutomation();
        if (success) {
          _showSuccessSnackBar('자동화가 시작되었습니다');
        }
      }
      
      if (success) {
        setState(() {
          _isAutomationRunning = !_isAutomationRunning;
        });
      }
    } catch (e) {
      _showErrorSnackBar('자동화 제어 오류: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  // 자격 증명 삭제
  Future<void> _clearCredentials() async {
    try {
      await SchoolAutomationService.instance.clearUserCredentials();
      setState(() {
        _universityController.clear();
        _usernameController.clear();
        _passwordController.clear();
        _studentIdController.clear();
      });
      _showSuccessSnackBar('자격 증명이 삭제되었습니다');
    } catch (e) {
      _showErrorSnackBar('자격 증명 삭제 오류: $e');
    }
  }
  
  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }
  
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('학교 자동화'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(
              icon: Icon(Icons.school),
              text: '자동화 설정',
            ),
            Tab(
              icon: Icon(Icons.science),
              text: '테스트',
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAssignments,
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // 자동화 설정 탭
          _buildAutomationTab(),
          // 테스트 탭
          _buildTestTab(),
        ],
      ),
    );
  }

  Widget _buildAutomationTab() {
    return _isLoading
        ? const LoadingWidget()
        : SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 자격 증명 설정
                _buildCredentialsSection(),
                const SizedBox(height: 24),
                
                // 자동화 제어
                _buildAutomationSection(),
                const SizedBox(height: 24),
                
                // 테스트 결과
                if (_testResult.isNotEmpty) _buildTestResultSection(),
                if (_testResult.isNotEmpty) const SizedBox(height: 24),
                
                // 과제 정보
                _buildAssignmentsSection(),
              ],
            ),
          );
  }
  
  Widget _buildCredentialsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '학교 자격 증명 설정',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Form(
              key: _formKey,
              child: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _universityController.text.isNotEmpty ? _universityController.text : null,
                    decoration: const InputDecoration(
                      labelText: '대학교',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: '연세대학교', child: Text('연세대학교 (LearnUs)')),
                      DropdownMenuItem(value: '고려대학교', child: Text('고려대학교 (LMS)')),
                      DropdownMenuItem(value: '서울대학교', child: Text('서울대학교 (Blackboard)')),
                      DropdownMenuItem(value: '한국과학기술원', child: Text('한국과학기술원 (KLMS)')),
                      DropdownMenuItem(value: '포스텍', child: Text('포스텍 (LMS)')),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _universityController.text = value ?? '';
                      });
                    },
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '대학교를 선택해주세요';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _usernameController,
                    decoration: const InputDecoration(
                      labelText: '아이디',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '아이디를 입력해주세요';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _passwordController,
                    decoration: const InputDecoration(
                      labelText: '비밀번호',
                      border: OutlineInputBorder(),
                    ),
                    obscureText: true,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '비밀번호를 입력해주세요';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _studentIdController,
                    decoration: const InputDecoration(
                      labelText: '학번',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '학번을 입력해주세요';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _saveCredentials,
                          child: const Text('저장'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isTesting ? null : _testAutomation,
                          icon: _isTesting 
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.science),
                          label: Text(_isTesting ? '테스트 중...' : '자동화 테스트'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.orange,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: _clearCredentials,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.red,
                      ),
                      child: const Text('자격 증명 삭제'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAutomationSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '자동화 제어',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _toggleAutomation,
                    icon: Icon(_isAutomationRunning ? Icons.stop : Icons.play_arrow),
                    label: Text(_isAutomationRunning ? '자동화 중지' : '자동화 시작'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isAutomationRunning ? Colors.red : Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _loadAssignments,
                    icon: const Icon(Icons.refresh),
                    label: const Text('수동 업데이트'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _isAutomationRunning ? Colors.green.shade50 : Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _isAutomationRunning ? Colors.green : Colors.grey,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _isAutomationRunning ? Icons.check_circle : Icons.cancel,
                    color: _isAutomationRunning ? Colors.green : Colors.grey,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _isAutomationRunning ? '자동화 실행 중' : '자동화 중지됨',
                    style: TextStyle(
                      color: _isAutomationRunning ? Colors.green : Colors.grey,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAssignmentsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '과제 정보',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // 통계 정보
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    '전체 과제',
                    _assignments.length.toString(),
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    '새로운 과제',
                    _newAssignments.length.toString(),
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    '마감 임박',
                    _upcomingAssignments.length.toString(),
                    Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // 새로운 과제
            if (_newAssignments.isNotEmpty) ...[
              const Text(
                '새로운 과제',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              ..._newAssignments.take(3).map((assignment) => 
                AssignmentCard(assignment: assignment)
              ),
              const SizedBox(height: 16),
            ],
            
            // 마감 임박 과제
            if (_upcomingAssignments.isNotEmpty) ...[
              const Text(
                '마감 임박 과제',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              ..._upcomingAssignments.take(3).map((assignment) => 
                AssignmentCard(assignment: assignment)
              ),
            ],
            
            // 과제가 없는 경우
            if (_assignments.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Text(
                    '과제 정보가 없습니다.\n로그인 후 과제 정보를 불러와주세요.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTestResultSection() {
    return Card(
      color: _testResult.contains('성공') ? Colors.green.shade50 : Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _testResult.contains('성공') ? Icons.check_circle : Icons.error,
                  color: _testResult.contains('성공') ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                const Text(
                  '테스트 결과',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Text(
                _testResult,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () {
                    setState(() {
                      _testResult = '';
                    });
                  },
                  child: const Text('닫기'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Firebase 상태 표시
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.cloud_done,
                        color: Colors.blue.shade600,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Firebase 연결 상태',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _firebaseStatus,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.blue.shade700,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // 테스트 입력 폼
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '간단 자동화 테스트',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: _testSchoolController.text.isNotEmpty ? _testSchoolController.text : null,
                      decoration: const InputDecoration(
                        labelText: '대학교 선택',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.school),
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: '연세대학교',
                          child: Text('연세대학교 (LearnUs)'),
                        ),
                        DropdownMenuItem(
                          value: '고려대학교',
                          child: Text('고려대학교 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '서울대학교',
                          child: Text('서울대학교 (Blackboard)'),
                        ),
                        DropdownMenuItem(
                          value: '한국과학기술원',
                          child: Text('한국과학기술원 (KLMS)'),
                        ),
                        DropdownMenuItem(
                          value: '포스텍',
                          child: Text('포스텍 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '성균관대학교',
                          child: Text('성균관대학교 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '한양대학교',
                          child: Text('한양대학교 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '중앙대학교',
                          child: Text('중앙대학교 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '경희대학교',
                          child: Text('경희대학교 (LMS)'),
                        ),
                        DropdownMenuItem(
                          value: '동국대학교',
                          child: Text('동국대학교 (LMS)'),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _testSchoolController.text = value ?? '';
                          _selectedTestUniversity = value ?? '';
                        });
                      },
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return '대학교를 선택해주세요';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _testUsernameController,
                      decoration: const InputDecoration(
                        labelText: '아이디',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '아이디를 입력해주세요';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _testPasswordController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: '비밀번호',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.lock),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '비밀번호를 입력해주세요';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isLoading ? null : _testAutomation,
                        icon: _isLoading 
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.science),
                        label: Text(_isLoading ? '테스트 중...' : '자동화 테스트'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // 선택된 학교 정보 표시
          if (_selectedTestUniversity.isNotEmpty) _buildUniversityInfoCard(),
          if (_selectedTestUniversity.isNotEmpty) const SizedBox(height: 24),
          
          // 테스트 결과 표시
          if (_testResult.isNotEmpty) _buildTestResultSection(),
        ],
      ),
    );
  }

  Widget _buildUniversityInfoCard() {
    final universityInfo = _getUniversityInfo()[_selectedTestUniversity];
    if (universityInfo == null) return const SizedBox.shrink();

    return Card(
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.school,
                  color: Colors.blue.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  '선택된 학교 정보',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow('학교명', universityInfo['name']!),
            _buildInfoRow('플랫폼', universityInfo['platform']!),
            _buildInfoRow('설명', universityInfo['description']!),
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '사이트 링크',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.blue.shade600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  GestureDetector(
                    onTap: () => _launchURL(universityInfo['url']!),
                    child: Text(
                      universityInfo['url']!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.blue.shade700,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _launchURL(universityInfo['url']!),
                icon: const Icon(Icons.open_in_browser, size: 16),
                label: const Text('사이트 열기'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue.shade600,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 60,
            child: Text(
              '$label:',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.blue.shade600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 12,
                color: Colors.blue.shade700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _launchURL(String url) async {
    try {
      final Uri uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('링크를 열 수 없습니다: $url'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('링크 열기 오류: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _testAutomation() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _testResult = '크롤링 시도 중...';
    });

    try {
      final result = await SchoolAutomationService.instance.testLogin(
        _testSchoolController.text,
        _testUsernameController.text,
        _testPasswordController.text,
        'N/A', // 학번은 선택사항
      );

      setState(() {
        _testResult = result['message'] ?? '알 수 없는 결과';
        if (result['success'] == true) {
          _testResult += '\n과제 수: ${result['assignments_count']}';
          if (result['assignments'] != null && result['assignments'].isNotEmpty) {
            _testResult += '\n첫 5개 과제:';
            for (var assignment in result['assignments']) {
              _testResult += '\n- ${assignment['title']} (강의: ${assignment['course']})';
            }
          }
        } else {
          _testResult += '\n오류: ${result['error']}';
        }
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['success'] == true ? '✅ 크롤링 테스트 성공!' : '❌ 크롤링 테스트 실패!'),
            backgroundColor: result['success'] == true ? Colors.green : Colors.red,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _testResult = '크롤링 테스트 중 오류 발생: $e';
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ 크롤링 테스트 중 오류 발생: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildStatCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
