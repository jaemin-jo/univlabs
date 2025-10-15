import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'screens/main_screen.dart';
import 'screens/intro_screen.dart';
import 'screens/login_screen.dart';
import 'screens/onboarding_screen.dart';
import 'providers/schedule_provider.dart';
import 'providers/announcement_provider.dart';
import 'providers/course_provider.dart';
import 'providers/interest_tag_provider.dart';
import 'providers/user_profile_provider.dart';
import 'providers/auth_provider.dart';
import 'services/notification_service.dart';
import 'services/firebase_service.dart';
import 'services/background_task_service.dart';
import 'widgets/global_ai_overlay.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('ko_KR', null);
  
  // Firebase 초기화
  await FirebaseService.instance.initialize();
  
  // 백그라운드 작업 초기화
  await BackgroundTaskService.initialize();
  
  // 알림 서비스 초기화
  await NotificationService().initialize();
  
  // 백그라운드 웹 크롤링 작업 예약
  await BackgroundTaskService.scheduleWebCrawling();
  
  runApp(const UniVerApp());
}

class UniVerApp extends StatelessWidget { 
  const UniVerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ScheduleProvider()),
        ChangeNotifierProvider(create: (_) => AnnouncementProvider()),
        ChangeNotifierProvider(create: (_) => CourseProvider()),
        ChangeNotifierProvider(create: (_) => InterestTagProvider()),
        ChangeNotifierProvider(create: (_) => UserProfileProvider()),
      ],
      child: MaterialApp(
        title: '유니버 - AI 대학생활',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF2196F3),
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          appBarTheme: const AppBarTheme(
            centerTitle: true,
            elevation: 0,
          ),
          cardTheme: CardThemeData(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const IntroScreen(),
          '/login': (context) => const LoginScreen(),
          '/onboarding': (context) => const OnboardingScreen(),
          '/main': (context) => Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              // 인증 상태 확인
              if (!authProvider.isAuthenticated) {
                // 인증되지 않은 경우 로그인 화면으로 리다이렉트
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  Navigator.pushReplacementNamed(context, '/login');
                });
                return const Scaffold(
                  body: Center(
                    child: CircularProgressIndicator(),
                  ),
                );
              }
              
              // 인증된 경우 메인 화면 표시
              return const Scaffold(
                body: Stack(
                  children: [
                    MainScreen(),
                    GlobalAIOverlay(),
                  ],
                ),
              );
            },
          ),
        },
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
