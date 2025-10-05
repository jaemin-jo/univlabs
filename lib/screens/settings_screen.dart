import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/user_profile_provider.dart';
import '../providers/auth_provider.dart';
import '../models/university.dart';
import '../services/university_service.dart';
import '../widgets/university_selector.dart';
import 'learnus_setup_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _aiRecommendationsEnabled = true;
  bool _darkModeEnabled = false;
  String _selectedLanguage = '한국어';
  University? _selectedUniversityData;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('설정'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: ListView(
        children: [
          _buildProfileSection(),
          _buildNotificationSection(),
          _buildAISection(),
          _buildAppearanceSection(),
          _buildGeneralSection(),
          _buildAboutSection(),
        ],
      ),
    );
  }

  Widget _buildProfileSection() {
    return Consumer<UserProfileProvider>(
      builder: (context, userProvider, child) {
        return Container(
          margin: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Theme.of(context).colorScheme.primary.withOpacity(0.1),
                Theme.of(context).colorScheme.secondary.withOpacity(0.05),
              ],
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 프로필 헤더
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Theme.of(context).colorScheme.primary,
                            Theme.of(context).colorScheme.secondary,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.person,
                        size: 28,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            userProvider.hasProfile ? userProvider.userProfile!.name : '프로필 없음',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              userProvider.hasProfile ? userProvider.userSummary : '프로필을 설정해주세요',
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.primary,
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                
                // 프로필 정보 섹션
                _buildProfileInfoSection(context, userProvider),
                if (_selectedUniversityData != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.blue.shade50,
                          Colors.indigo.shade50,
                        ],
                      ),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: Colors.blue.shade200,
                        width: 1.5,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.blue.withOpacity(0.1),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                Colors.blue.shade600,
                                Colors.indigo.shade600,
                              ],
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            Icons.school,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _selectedUniversityData!.fullName,
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue.shade800,
                                  fontSize: 16,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade100,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '${_selectedUniversityData!.region} • ${_getUniversityTypeText(_selectedUniversityData!.type)}',
                                  style: TextStyle(
                                    color: Colors.blue.shade700,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildNotificationSection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.notifications,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                const Text(
                  '알림 설정',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          SwitchListTile(
            title: const Text('푸시 알림'),
            subtitle: const Text('중요한 일정과 공지사항 알림'),
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
          ),
          SwitchListTile(
            title: const Text('이메일 알림'),
            subtitle: const Text('주요 일정 변경사항 이메일 발송'),
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
          ),
          SwitchListTile(
            title: const Text('일정 리마인더'),
            subtitle: const Text('일정 1시간 전 알림'),
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAISection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.psychology,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                const Text(
                  'AI 기능',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          SwitchListTile(
            title: const Text('AI 추천'),
            subtitle: const Text('개인화된 일정 및 공지사항 추천'),
            value: _aiRecommendationsEnabled,
            onChanged: (value) {
              setState(() {
                _aiRecommendationsEnabled = value;
              });
            },
          ),
          ListTile(
            title: const Text('AI 학습 데이터'),
            subtitle: const Text('개인화를 위한 데이터 수집 설정'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showAIDataDialog();
            },
          ),
          ListTile(
            title: const Text('추천 정확도'),
            subtitle: const Text('현재 정확도: 85%'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showAccuracyDialog();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAppearanceSection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.palette,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                const Text(
                  '화면 설정',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          SwitchListTile(
            title: const Text('다크 모드'),
            subtitle: const Text('어두운 테마 사용'),
            value: _darkModeEnabled,
            onChanged: (value) {
              setState(() {
                _darkModeEnabled = value;
              });
            },
          ),
          ListTile(
            title: const Text('언어'),
            subtitle: Text(_selectedLanguage),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showLanguageDialog();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildGeneralSection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.settings,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                const Text(
                  '일반',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          ListTile(
            title: const Text('대학교'),
            subtitle: Text(_selectedUniversityData?.name ?? '대학교 미선택'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showUniversityDialog();
            },
          ),
          ListTile(
            title: const Text('LearnUs 설정'),
            subtitle: const Text('자동화를 위한 LearnUs 로그인 정보'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const LearnUsSetupScreen(),
                ),
              );
            },
          ),
          ListTile(
            title: const Text('데이터 백업'),
            subtitle: const Text('클라우드에 데이터 백업'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showBackupDialog();
            },
          ),
          ListTile(
            title: const Text('데이터 동기화'),
            subtitle: const Text('다른 기기와 데이터 동기화'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showSyncDialog();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAboutSection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  Icons.info,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                const Text(
                  '앱 정보',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          ListTile(
            title: const Text('버전'),
            subtitle: const Text('1.0.0'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showVersionDialog();
            },
          ),
          ListTile(
            title: const Text('개발자 정보'),
            subtitle: const Text('유니버 개발팀'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showDeveloperDialog();
            },
          ),
          ListTile(
            title: const Text('개인정보처리방침'),
            subtitle: const Text('개인정보 보호 정책'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showPrivacyDialog();
            },
          ),
          ListTile(
            title: const Text('이용약관'),
            subtitle: const Text('서비스 이용 약관'),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () {
              _showTermsDialog();
            },
          ),
          
          // 로그아웃 버튼
          const Divider(),
          ListTile(
            title: const Text(
              '로그아웃',
              style: TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.w500,
              ),
            ),
            subtitle: const Text('계정에서 로그아웃합니다'),
            leading: const Icon(
              Icons.logout,
              color: Colors.red,
            ),
            onTap: () {
              _showLogoutDialog();
            },
          ),
        ],
      ),
    );
  }


  void _showAIDataDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('AI 학습 데이터'),
        content: const Text(
          'AI가 더 나은 추천을 제공하기 위해 다음 데이터를 수집합니다:\n\n'
          '• 수강신청 이력\n'
          '• 관심 분야\n'
          '• 일정 패턴\n'
          '• 공지사항 읽기 이력\n\n'
          '모든 데이터는 익명화되어 처리되며, 개인을 식별할 수 없습니다.',
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

  void _showAccuracyDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('추천 정확도'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('현재 AI 추천 정확도: 85%'),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: 0.85,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(
                Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              '더 많은 데이터를 수집할수록 정확도가 향상됩니다.',
              style: TextStyle(fontSize: 12),
            ),
          ],
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

  void _showLanguageDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('언어 선택'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('한국어'),
              value: '한국어',
              groupValue: _selectedLanguage,
              onChanged: (value) {
                setState(() {
                  _selectedLanguage = value!;
                });
                Navigator.of(context).pop();
              },
            ),
            RadioListTile<String>(
              title: const Text('English'),
              value: 'English',
              groupValue: _selectedLanguage,
              onChanged: (value) {
                setState(() {
                  _selectedLanguage = value!;
                });
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showUniversityDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('대학교 선택'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('서울대학교'),
              value: '서울대학교',
              groupValue: _selectedUniversityData?.name,
              onChanged: (value) {
                setState(() {
                  _selectedUniversityData = University(
                    id: 'snu',
                    name: '서울대학교',
                    fullName: '서울대학교',
                    region: '서울',
                    website: 'https://www.snu.ac.kr/',
                    scheduleUrl: 'https://www.snu.ac.kr/',
                    type: 'national',
                    ranking: 1,
                    campuses: ['관악캠퍼스'],
                  );
                });
                Navigator.of(context).pop();
              },
            ),
            RadioListTile<String>(
              title: const Text('연세대학교'),
              value: '연세대학교',
              groupValue: _selectedUniversityData?.name,
              onChanged: (value) {
                setState(() {
                  _selectedUniversityData = University(
                    id: 'yonsei',
                    name: '연세대학교',
                    fullName: '연세대학교',
                    region: '서울',
                    website: 'https://www.yonsei.ac.kr/',
                    scheduleUrl: 'https://www.yonsei.ac.kr/sc/notice/',
                    type: 'private',
                    ranking: 1,
                    campuses: ['신촌캠퍼스'],
                  );
                });
                Navigator.of(context).pop();
              },
            ),
            RadioListTile<String>(
              title: const Text('고려대학교'),
              value: '고려대학교',
              groupValue: _selectedUniversityData?.name,
              onChanged: (value) {
                setState(() {
                  _selectedUniversityData = University(
                    id: 'korea',
                    name: '고려대학교',
                    fullName: '고려대학교',
                    region: '서울',
                    website: 'https://www.korea.ac.kr/',
                    scheduleUrl: 'https://www.korea.ac.kr/',
                    type: 'private',
                    ranking: 2,
                    campuses: ['안암캠퍼스'],
                  );
                });
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showBackupDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('데이터 백업'),
        content: const Text('클라우드에 데이터를 백업하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('백업이 완료되었습니다')),
              );
            },
            child: const Text('백업'),
          ),
        ],
      ),
    );
  }

  void _showSyncDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('데이터 동기화'),
        content: const Text('다른 기기와 데이터를 동기화하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('동기화가 완료되었습니다')),
              );
            },
            child: const Text('동기화'),
          ),
        ],
      ),
    );
  }

  void _showVersionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('버전 정보'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('유니버 v1.0.0'),
            SizedBox(height: 8),
            Text('대학생활 AI 어시스턴트'),
            SizedBox(height: 8),
            Text('최신 업데이트: 2024.01.15'),
          ],
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

  void _showDeveloperDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('개발자 정보'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('유니버 개발팀'),
            SizedBox(height: 8),
            Text('이메일: support@univer.com'),
            SizedBox(height: 8),
            Text('웹사이트: www.univer.com'),
          ],
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

  void _showPrivacyDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('개인정보처리방침'),
        content: const SingleChildScrollView(
          child: Text(
            '유니버는 사용자의 개인정보를 보호하기 위해 최선을 다하고 있습니다.\n\n'
            '수집하는 정보:\n'
            '• 기본 프로필 정보 (이름, 학과, 학년)\n'
            '• 일정 및 과목 정보\n'
            '• 앱 사용 패턴 (익명화)\n\n'
            '정보 사용 목적:\n'
            '• 개인화된 서비스 제공\n'
            '• AI 추천 기능 개선\n'
            '• 앱 기능 향상\n\n'
            '정보 보호:\n'
            '• 모든 데이터는 암호화되어 저장됩니다\n'
            '• 제3자와 공유하지 않습니다\n'
            '• 사용자가 언제든 삭제할 수 있습니다',
          ),
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

  void _showTermsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('이용약관'),
        content: const SingleChildScrollView(
          child: Text(
            '유니버 서비스 이용약관\n\n'
            '제1조 (목적)\n'
            '본 약관은 유니버 서비스의 이용과 관련하여 필요한 사항을 규정합니다.\n\n'
            '제2조 (서비스 내용)\n'
            '유니버는 대학생활 일정관리 및 AI 추천 서비스를 제공합니다.\n\n'
            '제3조 (이용자의 의무)\n'
            '• 정확한 정보 제공\n'
            '• 서비스 이용 규칙 준수\n'
            '• 타인의 권리 침해 금지\n\n'
            '제4조 (서비스 제공자의 의무)\n'
            '• 안정적인 서비스 제공\n'
            '• 개인정보 보호\n'
            '• 지속적인 서비스 개선',
          ),
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

  String _getUniversityTypeText(String type) {
    switch (type) {
      case 'national':
        return '국립';
      case 'private':
        return '사립';
      case 'special':
        return '특수';
      default:
        return '기타';
    }
  }

  void _showUniversitySelector(BuildContext context, UserProfileProvider userProvider) {
    University? tempSelectedUniversity = userProvider.selectedUniversity;
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('대학교 선택'),
        content: SizedBox(
          width: double.maxFinite,
          height: 400,
          child: UniversitySelector(
            selectedUniversity: tempSelectedUniversity,
            onUniversitySelected: (university) {
              // 임시 선택 저장
              tempSelectedUniversity = university;
            },
            label: '소속 대학교',
            hint: '대학교를 검색하여 선택하세요',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (tempSelectedUniversity != null) {
                try {
                  await userProvider.updateUniversity(tempSelectedUniversity!);
                  Navigator.of(context).pop();
                  
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${tempSelectedUniversity!.name}이(가) 선택되었습니다.'),
                        backgroundColor: Colors.green,
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('대학교 변경 중 오류가 발생했습니다: $e'),
                        backgroundColor: Colors.red,
                        duration: const Duration(seconds: 3),
                      ),
                    );
                  }
                }
              } else {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('대학교를 선택해주세요.'),
                      backgroundColor: Colors.orange,
                      duration: Duration(seconds: 2),
                    ),
                  );
                }
              }
            },
            child: const Text('선택'),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileInfoSection(BuildContext context, UserProfileProvider userProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 대학교 (전체 너비) - 맨 위로 이동
        _buildCompactUniversityField(context, userProvider),
        const SizedBox(height: 8),
        
        // 기본 정보 (2열 그리드)
        Row(
          children: [
            Expanded(
              child: _buildCompactField(
                context,
                '이름',
                userProvider.userProfile?.name ?? '이름',
                Icons.person,
                (value) => userProvider.updateProfileFields(name: value),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildCompactField(
                context,
                '학번',
                userProvider.userProfile?.studentId ?? '학번',
                Icons.badge,
                (value) => userProvider.updateProfileFields(studentId: value),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        
        // 전공/학과 (2열 그리드)
        Row(
          children: [
            Expanded(
              child: _buildCompactField(
                context,
                '전공',
                userProvider.userProfile?.major ?? '전공',
                Icons.school,
                (value) => userProvider.updateProfileFields(major: value),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildCompactField(
                context,
                '학과',
                userProvider.userProfile?.department ?? '학과',
                Icons.account_balance,
                (value) => userProvider.updateProfileFields(department: value),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        
        // 이메일 (전체 너비)
        _buildCompactField(
          context,
          '이메일',
          userProvider.userProfile?.email ?? '이메일',
          Icons.email,
          (value) => userProvider.updateProfileFields(email: value),
        ),
        const SizedBox(height: 8),
        
        // 학년/학기 (2열 그리드)
        Row(
          children: [
            Expanded(
              child: _buildCompactGradeField(context, userProvider),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildCompactSemesterField(context, userProvider),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCompactField(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Function(String) onChanged,
  ) {
    return InkWell(
      onTap: () => _showEditDialog(context, label, value, onChanged),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.grey.shade50,
              Colors.grey.shade100,
            ],
          ),
          border: Border.all(
            color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
            width: 1.5,
          ),
          borderRadius: BorderRadius.circular(10),
          boxShadow: [
            BoxShadow(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    Theme.of(context).colorScheme.secondary.withOpacity(0.1),
                  ],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon, 
                size: 16, 
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 11,
                      color: Theme.of(context).colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: value == label ? Colors.grey[500] : Colors.black87,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(
                Icons.edit, 
                size: 12, 
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompactUniversityField(BuildContext context, UserProfileProvider userProvider) {
    return InkWell(
      onTap: () => _showUniversitySelector(context, userProvider),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.blue.shade50,
              Colors.indigo.shade50,
            ],
          ),
          border: Border.all(
            color: Colors.blue.shade200,
            width: 1.5,
          ),
          borderRadius: BorderRadius.circular(10),
          boxShadow: [
            BoxShadow(
              color: Colors.blue.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.blue.shade600,
                    Colors.indigo.shade600,
                  ],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.school, 
                size: 16, 
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '대학교',
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.blue.shade700,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    userProvider.selectedUniversity != null 
                        ? userProvider.currentUniversityName
                        : '대학교 선택',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: userProvider.selectedUniversity != null 
                          ? Colors.blue.shade800
                          : Colors.blue.shade500,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.blue.shade100,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(
                Icons.edit, 
                size: 12, 
                color: Colors.blue.shade700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEditableField(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Function(String) onChanged,
  ) {
    return InkWell(
      onTap: () => _showEditDialog(context, label, value, onChanged),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: Colors.grey[600]),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.edit, size: 16, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildCompactGradeField(BuildContext context, UserProfileProvider userProvider) {
    return InkWell(
      onTap: () => _showGradeDialog(context, userProvider),
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Row(
          children: [
            Icon(Icons.grade, size: 16, color: Colors.grey[600]),
            const SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '학년',
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    '${userProvider.userProfile?.grade ?? 1}학년',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.edit, size: 12, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildGradeField(BuildContext context, UserProfileProvider userProvider) {
    return InkWell(
      onTap: () => _showGradeDialog(context, userProvider),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(Icons.grade, size: 20, color: Colors.grey[600]),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '학년',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${userProvider.userProfile?.grade ?? 1}학년',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.edit, size: 16, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildCompactSemesterField(BuildContext context, UserProfileProvider userProvider) {
    return InkWell(
      onTap: () => _showSemesterDialog(context, userProvider),
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
            const SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '학기',
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    userProvider.userProfile?.semesterInfo ?? '2024-1학기',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Icon(Icons.edit, size: 12, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildSemesterField(BuildContext context, UserProfileProvider userProvider) {
    return InkWell(
      onTap: () => _showSemesterDialog(context, userProvider),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, size: 20, color: Colors.grey[600]),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '학기',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    userProvider.userProfile?.semesterInfo ?? '2024-1학기',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.edit, size: 16, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  void _showEditDialog(BuildContext context, String label, String currentValue, Function(String) onChanged) {
    final controller = TextEditingController(text: currentValue);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('$label 수정'),
        content: TextField(
          controller: controller,
          decoration: InputDecoration(
            hintText: '$label을 입력하세요',
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              // 개별 필드 업데이트
              await onChanged(controller.text);
              Navigator.of(context).pop();
              
              // 성공 메시지 표시
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('$label이 수정되었습니다.'),
                    backgroundColor: Colors.green,
                    duration: const Duration(seconds: 2),
                  ),
                );
              }
            },
            child: const Text('완료'),
          ),
        ],
      ),
    );
  }

  void _showGradeDialog(BuildContext context, UserProfileProvider userProvider) {
    int selectedGrade = userProvider.userProfile?.grade ?? 1;
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('학년 선택'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: List.generate(4, (index) {
              final grade = index + 1;
              return RadioListTile<int>(
                title: Text('${grade}학년'),
                value: grade,
                groupValue: selectedGrade,
                onChanged: (value) {
                  setState(() {
                    selectedGrade = value!;
                  });
                },
              );
            }),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('취소'),
            ),
            ElevatedButton(
              onPressed: () async {
                await userProvider.updateProfileFields(grade: selectedGrade);
                Navigator.of(context).pop();
                
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('학년이 수정되었습니다.'),
                      backgroundColor: Colors.green,
                      duration: Duration(seconds: 2),
                    ),
                  );
                }
              },
              child: const Text('완료'),
            ),
          ],
        ),
      ),
    );
  }

  void _showSemesterDialog(BuildContext context, UserProfileProvider userProvider) {
    String selectedSemester = userProvider.userProfile?.semesterInfo ?? '2024-1학기';
    final semesters = ['2024-1학기', '2024-2학기', '2025-1학기', '2025-2학기'];
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('학기 선택'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: semesters.map((semester) {
              return RadioListTile<String>(
                title: Text(semester),
                value: semester,
                groupValue: selectedSemester,
                onChanged: (value) {
                  setState(() {
                    selectedSemester = value!;
                  });
                },
              );
            }).toList(),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('취소'),
            ),
            ElevatedButton(
              onPressed: () async {
                await userProvider.updateProfileFields(semesterInfo: selectedSemester);
                Navigator.of(context).pop();
                
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('학기가 수정되었습니다.'),
                      backgroundColor: Colors.green,
                      duration: Duration(seconds: 2),
                    ),
                  );
                }
              },
              child: const Text('완료'),
            ),
          ],
        ),
      ),
    );
  }

  // 로그아웃 확인 다이얼로그
  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('로그아웃'),
        content: const Text(
          '정말로 로그아웃하시겠습니까?\n\n'
          '로그아웃하면 다음에 다시 로그인해야 합니다.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.of(context).pop(); // 다이얼로그 닫기
              await _handleLogout();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('로그아웃'),
          ),
        ],
      ),
    );
  }

  // 로그아웃 처리
  Future<void> _handleLogout() async {
    try {
      final authProvider = context.read<AuthProvider>();
      await authProvider.signOut();
      
      if (mounted) {
        // 로그인 화면으로 이동
        Navigator.pushNamedAndRemoveUntil(
          context,
          '/login',
          (route) => false,
        );
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('로그아웃되었습니다.'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('로그아웃 중 오류가 발생했습니다: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }
}