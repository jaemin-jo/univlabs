import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/firebase_service.dart';
import '../models/learnus_credentials.dart';

class LearnUsSetupScreen extends StatefulWidget {
  const LearnUsSetupScreen({Key? key}) : super(key: key);

  @override
  State<LearnUsSetupScreen> createState() => _LearnUsSetupScreenState();
}

class _LearnUsSetupScreenState extends State<LearnUsSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _universityController = TextEditingController();
  
  bool _isLoading = false;
  bool _isPasswordVisible = false;
  LearnUsCredentials? _existingCredentials;

  @override
  void initState() {
    super.initState();
    _loadExistingCredentials();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _studentIdController.dispose();
    _universityController.dispose();
    super.dispose();
  }

  Future<void> _loadExistingCredentials() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        final credentials = await FirebaseService.instance.getLearnUsCredentials(user.uid);
        if (credentials != null) {
          setState(() {
            _existingCredentials = credentials;
            _usernameController.text = credentials.username;
            _studentIdController.text = credentials.studentId;
            _universityController.text = credentials.university;
            // 비밀번호는 보안상 표시하지 않음
          });
        }
      }
    } catch (e) {
      debugPrint('기존 인증 정보 로드 오류: $e');
    }
  }

  Future<void> _saveCredentials() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) {
        throw Exception('로그인이 필요합니다.');
      }

      final credentials = LearnUsCredentials(
        uid: user.uid,
        username: _usernameController.text.trim(),
        password: _passwordController.text,
        studentId: _studentIdController.text.trim(),
        university: _universityController.text.trim(),
        isActive: true,
        createdAt: _existingCredentials?.createdAt ?? DateTime.now(),
        updatedAt: DateTime.now(),
        lastUsedAt: DateTime.now(),
      );

      await FirebaseService.instance.saveLearnUsCredentials(credentials);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('LearnUs 인증 정보가 저장되었습니다!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('저장 실패: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LearnUs 설정'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.school, color: Colors.blue),
                          const SizedBox(width: 8),
                          Text(
                            'LearnUs 인증 정보',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '자동화를 위해 LearnUs 로그인 정보가 필요합니다.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // 대학교 선택
              TextFormField(
                controller: _universityController,
                decoration: const InputDecoration(
                  labelText: '대학교',
                  hintText: '예: 연세대학교',
                  prefixIcon: Icon(Icons.school),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return '대학교를 입력해주세요.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // 학번 입력
              TextFormField(
                controller: _studentIdController,
                decoration: const InputDecoration(
                  labelText: '학번',
                  hintText: '예: 2024123456',
                  prefixIcon: Icon(Icons.badge),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return '학번을 입력해주세요.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // LearnUs 아이디
              TextFormField(
                controller: _usernameController,
                decoration: const InputDecoration(
                  labelText: 'LearnUs 아이디',
                  hintText: 'LearnUs 로그인 아이디',
                  prefixIcon: Icon(Icons.person),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'LearnUs 아이디를 입력해주세요.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // LearnUs 비밀번호
              TextFormField(
                controller: _passwordController,
                obscureText: !_isPasswordVisible,
                decoration: InputDecoration(
                  labelText: 'LearnUs 비밀번호',
                  hintText: 'LearnUs 로그인 비밀번호',
                  prefixIcon: const Icon(Icons.lock),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() {
                        _isPasswordVisible = !_isPasswordVisible;
                      });
                    },
                  ),
                  border: const OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'LearnUs 비밀번호를 입력해주세요.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // 저장 버튼
              ElevatedButton(
                onPressed: _isLoading ? null : _saveCredentials,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        '인증 정보 저장',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
              const SizedBox(height: 16),

              // 기존 정보가 있는 경우
              if (_existingCredentials != null) ...[
                Card(
                  color: Colors.green[50],
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.check_circle, color: Colors.green),
                            const SizedBox(width: 8),
                            Text(
                              '기존 인증 정보',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.green[800],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text('대학교: ${_existingCredentials!.university}'),
                        Text('학번: ${_existingCredentials!.studentId}'),
                        Text('아이디: ${_existingCredentials!.username}'),
                        Text('마지막 업데이트: ${_existingCredentials!.updatedAt.toString().split('.')[0]}'),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

