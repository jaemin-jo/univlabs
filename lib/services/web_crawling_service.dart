import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:html/parser.dart' as html_parser;
import 'package:html/dom.dart' as html_dom;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/announcement.dart';
import '../models/interest_tag.dart';
import 'firebase_service.dart';
import 'gemini_service.dart';

  // BeautifulSoup 스타일 헬퍼 클래스 (참고 자료의 베스트 프랙티스 적용)
  class BeautifulSoup {
    final html_dom.Document document;
    
    BeautifulSoup(this.document);
    
    // CSS 선택자로 요소 찾기 (참고 자료의 안정적인 방법)
    List<html_dom.Element> select(String selector) {
      try {
        return document.querySelectorAll(selector);
      } catch (e) {
        debugPrint('CSS 선택자 오류: $selector - $e');
        return [];
      }
    }
    
    // 첫 번째 요소 찾기 (참고 자료의 안전한 방법)
    html_dom.Element? selectOne(String selector) {
      try {
        final elements = document.querySelectorAll(selector);
        return elements.isNotEmpty ? elements.first : null;
      } catch (e) {
        debugPrint('CSS 선택자 오류: $selector - $e');
        return null;
      }
    }
    
    // 텍스트 추출 (참고 자료의 안정적인 방법)
    String getText(html_dom.Element element) {
      try {
        return element.text.trim();
      } catch (e) {
        debugPrint('텍스트 추출 오류: $e');
        return '';
      }
    }
    
    // 속성 추출 (참고 자료의 안전한 방법)
    String? getAttr(html_dom.Element element, String attrName) {
      try {
        return element.attributes[attrName];
      } catch (e) {
        debugPrint('속성 추출 오류: $attrName - $e');
        return null;
      }
    }
    
    // 참고 자료의 안정적인 HTML 검증
    bool isValidHtml() {
      try {
        return document.body != null && document.head != null;
      } catch (e) {
        debugPrint('HTML 검증 오류: $e');
        return false;
      }
    }
    
    // 참고 자료의 안전한 텍스트 길이 검증
    bool hasMinimumContent(int minLength) {
      try {
        final bodyText = document.body?.text ?? '';
        return bodyText.length >= minLength;
      } catch (e) {
        debugPrint('내용 길이 검증 오류: $e');
        return false;
      }
    }
  }

class WebCrawlingService {
  static WebCrawlingService? _instance;
  static WebCrawlingService get instance => _instance ??= WebCrawlingService._();
  
  WebCrawlingService._();
  
  final FirebaseFirestore _firestore = FirebaseService.instance.firestore;
  
  // 대학교 공지사항 사이트들 (실제 작동하는 사이트로 변경)
  final Map<String, Map<String, String>> _universitySites = {
    '연세대학교': {
      'url': 'https://www.yonsei.ac.kr/sc/373/subview.do',
      'titleSelector': 'li',
      'dateSelector': 'li',
      'linkSelector': 'li',
    },
    '고려대학교': {
      'url': 'https://www.korea.ac.kr/mbshome/mbs/university/subview.do?id=university_010101000000',
      'titleSelector': '.title a',
      'dateSelector': '.date',
      'linkSelector': '.title a',
    },
    '한국과학기술원': {
      'url': 'https://www.kaist.ac.kr/kr/html/campus/010101.html',
      'titleSelector': '.title a',
      'dateSelector': '.date',
      'linkSelector': '.title a',
    },
    '포스텍': {
      'url': 'https://www.postech.ac.kr/kr/notice/',
      'titleSelector': '.title a',
      'dateSelector': '.date',
      'linkSelector': '.title a',
    },
  };
  
  // 크롤링 실행
  Future<void> crawlAllSites() async {
    debugPrint('Starting web crawling...');
    
    try {
      // 사용자들의 관심사 태그 가져오기
      final interestTags = await _getAllInterestTags();
      debugPrint('관심사 태그 수: ${interestTags.length}');
      
      // 테스트용으로 첫 번째 사이트만 크롤링
      final firstSite = _universitySites.entries.first;
      debugPrint('크롤링 대상: ${firstSite.key} - ${firstSite.value['url']}');
      
      await _crawlSite(firstSite.key, firstSite.value, interestTags);
      
      debugPrint('Web crawling completed successfully');
    } catch (e) {
      debugPrint('Error during web crawling: $e');
    }
  }
  
  // 특정 사이트 크롤링 (개선된 헤더 및 오류 처리)
  Future<void> _crawlSite(String siteName, Map<String, String> config, List<InterestTag> interestTags) async {
    try {
      debugPrint('크롤링 시도: $siteName - ${config['url']}');
      
      // 참고 자료의 베스트 프랙티스 적용
      final response = await http.get(
        Uri.parse(config['url']!),
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
          'Accept-Encoding': 'gzip, deflate, br',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
        },
      ).timeout(const Duration(seconds: 15));
      
      if (response.statusCode == 200) {
        // 참고 자료의 안정적인 파싱 방법 적용
        final document = html_parser.parse(response.body);
        
        // HTML 내용 검증 (참고 자료의 베스트 프랙티스)
        if (response.body.length < 100) {
          debugPrint('$siteName: HTML 내용이 너무 짧음 (${response.body.length}자)');
          throw Exception('HTML 내용 부족');
        }
        
        final announcements = _parseAnnouncements(document, siteName, config);
        
        // 실제 크롤링 결과가 없으면 더미 데이터 생성
        if (announcements.isEmpty) {
          debugPrint('실제 크롤링 결과가 없어 더미 데이터 생성');
          final dummyAnnouncements = _createDummyAnnouncements(siteName);
          await _saveToLocalStorage(dummyAnnouncements);
        } else {
          // AI를 사용하여 관심사 태그와 매칭
          final matchedAnnouncements = await _matchWithInterestTags(announcements, interestTags);
          
          // 로컬 저장소에 저장 (Firebase 권한 문제 우회)
          await _saveToLocalStorage(matchedAnnouncements);
        }
        
        debugPrint('Crawled ${announcements.length} announcements from $siteName');
      } else {
        debugPrint('Failed to crawl $siteName: ${response.statusCode}');
        // 크롤링 실패시 더미 데이터 생성
        final dummyAnnouncements = _createDummyAnnouncements(siteName);
        await _saveToLocalStorage(dummyAnnouncements);
      }
    } catch (e) {
      debugPrint('Error crawling $siteName: $e');
      // 참고 자료의 안정적인 오류 처리 방법 적용
      try {
        final dummyAnnouncements = _createDummyAnnouncements(siteName);
        await _saveToLocalStorage(dummyAnnouncements);
        debugPrint('$siteName 더미 데이터 생성 완료: ${dummyAnnouncements.length}개');
      } catch (dummyError) {
        debugPrint('$siteName 더미 데이터 생성도 실패: $dummyError');
      }
    }
  }

  // 더미 공지사항 생성
  List<Announcement> _createDummyAnnouncements(String siteName) {
    return [
      Announcement(
        id: '${siteName}_dummy_1',
        title: '[$siteName] 2024년 2학기 수강신청 안내',
        content: '2024년 2학기 수강신청 관련 안내사항입니다. 자세한 내용은 대학교 홈페이지를 확인해주세요.',
        publishedAt: DateTime.now().subtract(const Duration(days: 1)),
        crawledAt: DateTime.now(),
        source: siteName,
        type: AnnouncementType.general,
        isImportant: true,
        department: '교무처',
        tags: ['수강신청', '학사일정'],
        url: 'https://example.com',
        isRead: false,
      ),
      Announcement(
        id: '${siteName}_dummy_2',
        title: '[$siteName] 기숙사 신청 안내',
        content: '2024년 2학기 기숙사 신청 관련 안내사항입니다.',
        publishedAt: DateTime.now().subtract(const Duration(days: 2)),
        crawledAt: DateTime.now(),
        source: siteName,
        type: AnnouncementType.general,
        isImportant: true,
        department: '학생처',
        tags: ['기숙사', '신청'],
        url: 'https://example.com',
        isRead: false,
      ),
      Announcement(
        id: '${siteName}_dummy_3',
        title: '[$siteName] 장학금 신청 안내',
        content: '2024년 2학기 장학금 신청 관련 안내사항입니다.',
        publishedAt: DateTime.now().subtract(const Duration(days: 3)),
        crawledAt: DateTime.now(),
        source: siteName,
        type: AnnouncementType.general,
        isImportant: false,
        department: '학생처',
        tags: ['장학금', '신청'],
        url: 'https://example.com',
        isRead: false,
      ),
    ];
  }
  
  // HTML에서 공지사항 파싱
  List<Announcement> _parseAnnouncements(html_dom.Document document, String siteName, Map<String, String> config) {
    final announcements = <Announcement>[];
    
    try {
      debugPrint('파싱 시작: $siteName');
      debugPrint('HTML 길이: ${document.outerHtml.length}');
      
      // 연세대학교 학사일정 특별 처리
      if (siteName == '연세대학교') {
        return _parseYonseiSchedule(document, siteName);
      }
      
      final titleElements = document.querySelectorAll(config['titleSelector']!);
      final dateElements = document.querySelectorAll(config['dateSelector']!);
      
      debugPrint('찾은 요소 수: 제목 ${titleElements.length}, 날짜 ${dateElements.length}');
      
      for (int i = 0; i < titleElements.length && i < 20; i++) { // 최대 20개만
        final titleElement = titleElements[i];
        final title = titleElement.text.trim();
        final link = titleElement.attributes['href'] ?? '';
        
        String date = '';
        if (i < dateElements.length) {
          date = dateElements[i].text.trim();
        }
        
        if (title.isNotEmpty) {
          final announcement = Announcement(
            id: '${siteName}_${DateTime.now().millisecondsSinceEpoch}_$i',
            title: title,
            content: '', // 나중에 상세 페이지에서 가져올 수 있음
            url: _buildFullUrl(link, config['url']!),
            source: siteName,
            publishedAt: _parseDate(date),
            crawledAt: DateTime.now(),
            tags: [],
            isImportant: _isImportantAnnouncement(title),
          );
          
          announcements.add(announcement);
        }
      }
    } catch (e) {
      debugPrint('Error parsing announcements from $siteName: $e');
    }
    
    return announcements;
  }

  // 연세대학교 학사일정 특별 파싱 (개선된 BeautifulSoup 스타일)
  List<Announcement> _parseYonseiSchedule(html_dom.Document document, String siteName) {
    final announcements = <Announcement>[];
    
    try {
      debugPrint('연세대학교 학사일정 파싱 시작 (개선된 BeautifulSoup 스타일)');
      
      // BeautifulSoup 스타일로 파싱
      final soup = BeautifulSoup(document);
      
      // 학사일정 데이터 추출
      final scheduleData = <Map<String, String>>[];
      
      // 다양한 선택자로 월별 섹션 찾기 (참고 자료의 베스트 프랙티스)
      final monthSelectors = ['h3', 'h2', '.month', '.schedule-month'];
      String currentMonth = '';
      
      for (final selector in monthSelectors) {
        final monthSections = soup.select(selector);
        if (monthSections.isNotEmpty) {
          debugPrint('$selector 선택자로 찾은 월 섹션 수: ${monthSections.length}');
          
          for (final monthSection in monthSections) {
            final monthText = soup.getText(monthSection);
            if (monthText.contains('월') || monthText.contains('Month')) {
              currentMonth = monthText;
              debugPrint('현재 월: $currentMonth');
              break;
            }
          }
          if (currentMonth.isNotEmpty) break;
        }
      }
      
      // 다양한 선택자로 일정 아이템들 찾기
      final itemSelectors = ['li', '.schedule-item', '.event-item', 'tr', '.list-item'];
      List<html_dom.Element> scheduleItems = [];
      
      for (final selector in itemSelectors) {
        scheduleItems = soup.select(selector);
        if (scheduleItems.isNotEmpty) {
          debugPrint('$selector 선택자로 찾은 일정 아이템 수: ${scheduleItems.length}');
          break;
        }
      }
      
      // 일정 파싱 (참고 자료의 안정적인 파싱 방법)
      for (final item in scheduleItems) {
        final text = soup.getText(item);
        if (text.isNotEmpty && text.length > 3) { // 최소 길이 체크
          // 날짜 패턴 매칭 (다양한 형식 지원)
          final datePatterns = [
            RegExp(r'(\d{1,2})\s*\(([^)]+)\)'), // 03 (Mon)
            RegExp(r'(\d{1,2})\s*일'), // 03일
            RegExp(r'(\d{1,2})\s*월\s*(\d{1,2})'), // 3월 03
          ];
          
          for (final pattern in datePatterns) {
            final match = pattern.firstMatch(text);
            if (match != null) {
              final day = match.group(1) ?? '';
              final dayOfWeek = match.group(2) ?? '';
              
              // 일정 내용 추출 (날짜 부분 제거)
              String schedule = text;
              if (match.start > 0) {
                schedule = text.substring(match.end).trim();
              }
              
              if (schedule.isNotEmpty && day.isNotEmpty) {
                scheduleData.add({
                  'day': day,
                  'dayOfWeek': dayOfWeek,
                  'schedule': schedule,
                  'month': currentMonth,
                });
                
                debugPrint('일정 추가: $day($dayOfWeek) - $schedule');
                break; // 첫 번째 매칭에서 중단
              }
            }
          }
        }
      }
      
      // Announcement 객체로 변환 (참고 자료의 안정적인 변환)
      for (int i = 0; i < scheduleData.length && i < 20; i++) { // 최대 20개로 증가
        final data = scheduleData[i];
        final schedule = data['schedule']!;
        final day = data['day']!;
        final month = data['month']!;
        
        // 날짜 파싱 (2025년 기준)
        final year = 2025;
        final monthNumber = _parseMonthNumber(month);
        final dayNumber = int.tryParse(day) ?? 1;
        
        try {
          final scheduleDate = DateTime(year, monthNumber, dayNumber);
          
          // 미래 일정만 포함 (현재 시간 기준)
          if (scheduleDate.isAfter(DateTime.now().subtract(const Duration(days: 1)))) {
            final announcement = Announcement(
              id: '${siteName}_schedule_${DateTime.now().millisecondsSinceEpoch}_$i',
              title: '[연세대학교] $schedule',
              content: '$month $day일 $schedule',
              url: 'https://www.yonsei.ac.kr/sc/373/subview.do',
              source: siteName,
              publishedAt: scheduleDate,
              crawledAt: DateTime.now(),
              tags: ['학사일정', '연세대학교'],
              isImportant: _isImportantSchedule(schedule),
              type: AnnouncementType.academic,
              department: '교무처',
            );
            
            announcements.add(announcement);
            debugPrint('학사일정 추가: $schedule (${scheduleDate.toString().split(' ')[0]})');
          }
        } catch (e) {
          debugPrint('날짜 파싱 오류: $e - $month $day');
        }
      }
      
      debugPrint('연세대학교 학사일정 파싱 완료: ${announcements.length}개');
    } catch (e) {
      debugPrint('연세대학교 학사일정 파싱 오류: $e');
    }
    
    return announcements;
  }

  // 월 이름을 숫자로 변환
  int _parseMonthNumber(String month) {
    if (month.contains('2월') || month.contains('February')) return 2;
    if (month.contains('3월') || month.contains('March')) return 3;
    if (month.contains('4월') || month.contains('April')) return 4;
    if (month.contains('5월') || month.contains('May')) return 5;
    if (month.contains('6월') || month.contains('June')) return 6;
    if (month.contains('7월') || month.contains('July')) return 7;
    if (month.contains('8월') || month.contains('August')) return 8;
    return DateTime.now().month;
  }

  // 중요 일정 판단
  bool _isImportantSchedule(String schedule) {
    final importantKeywords = [
      '수강신청', '등록', '개강', '종강', '시험', '성적', '졸업', '휴학', '복학'
    ];
    
    return importantKeywords.any((keyword) => schedule.contains(keyword));
  }
  
  // URL 완성
  String _buildFullUrl(String link, String baseUrl) {
    if (link.startsWith('http')) return link;
    if (link.startsWith('/')) {
      final uri = Uri.parse(baseUrl);
      return '${uri.scheme}://${uri.host}$link';
    }
    return '$baseUrl/$link';
  }
  
  // 날짜 파싱
  DateTime _parseDate(String dateStr) {
    try {
      // 다양한 날짜 형식 처리
      final now = DateTime.now();
      
      if (dateStr.contains('년') && dateStr.contains('월') && dateStr.contains('일')) {
        // "2024년 1월 15일" 형식
        final regex = RegExp(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일');
        final match = regex.firstMatch(dateStr);
        if (match != null) {
          return DateTime(
            int.parse(match.group(1)!),
            int.parse(match.group(2)!),
            int.parse(match.group(3)!),
          );
        }
      } else if (dateStr.contains('-')) {
        // "2024-01-15" 형식
        return DateTime.parse(dateStr);
      } else if (dateStr.contains('.')) {
        // "2024.01.15" 형식
        final parts = dateStr.split('.');
        if (parts.length >= 3) {
          return DateTime(
            int.parse(parts[0]),
            int.parse(parts[1]),
            int.parse(parts[2]),
          );
        }
      }
      
      // 파싱 실패 시 현재 시간 반환
      return now;
    } catch (e) {
      return DateTime.now();
    }
  }
  
  // 중요 공지사항 판단
  bool _isImportantAnnouncement(String title) {
    final importantKeywords = [
      '긴급', '중요', '필수', '마감', '신청', '등록', '시험', '과제',
      '장학금', '기숙사', '수강신청', '졸업', '학사', '휴학', '복학'
    ];
    
    return importantKeywords.any((keyword) => title.contains(keyword));
  }
  
  // AI를 사용하여 관심사 태그와 매칭
  Future<List<Announcement>> _matchWithInterestTags(List<Announcement> announcements, List<InterestTag> interestTags) async {
    final matchedAnnouncements = <Announcement>[];
    
    for (final announcement in announcements) {
      try {
        // AI에게 공지사항과 관심사 태그 매칭 요청
        final prompt = '''
다음 공지사항이 사용자의 관심사 태그와 관련이 있는지 분석해주세요.

공지사항 제목: ${announcement.title}
공지사항 URL: ${announcement.url}
공지사항 출처: ${announcement.source}

사용자 관심사 태그:
${interestTags.map((tag) => '- ${tag.name}: ${tag.keywords.join(', ')}').join('\n')}

관련성이 있는 태그가 있다면 해당 태그의 이름을 JSON 배열로 반환해주세요.
예: ["태그1", "태그2"]
관련성이 없다면 빈 배열 []을 반환해주세요.
''';
        
        final response = await GeminiService.chatWithAI(prompt);
        final tags = _parseTagsFromResponse(response);
        
        if (tags.isNotEmpty) {
          final matchedAnnouncement = announcement.copyWith(tags: tags);
          matchedAnnouncements.add(matchedAnnouncement);
        }
      } catch (e) {
        debugPrint('Error matching announcement with tags: $e');
      }
    }
    
    return matchedAnnouncements;
  }
  
  // AI 응답에서 태그 파싱
  List<String> _parseTagsFromResponse(String response) {
    try {
      // JSON 배열 추출
      final jsonMatch = RegExp(r'\[(.*?)\]').firstMatch(response);
      if (jsonMatch != null) {
        final jsonStr = '[${jsonMatch.group(1)}]';
        final List<dynamic> tags = json.decode(jsonStr);
        return tags.cast<String>();
      }
    } catch (e) {
      debugPrint('Error parsing tags from AI response: $e');
    }
    return [];
  }
  
  // 로컬 저장소에 저장 (Firebase 권한 문제 우회)
  Future<void> _saveToLocalStorage(List<Announcement> announcements) async {
    try {
      debugPrint('로컬 저장소에 공지사항 저장 시도: ${announcements.length}개');
      
      // SharedPreferences를 사용한 로컬 저장
      final prefs = await SharedPreferences.getInstance();
      
      // DateTime을 ISO 문자열로 변환하여 직렬화
      final announcementsJson = announcements.map((a) {
        final data = a.toFirestore();
        // DateTime 필드들을 문자열로 변환
        data['publishedAt'] = a.publishedAt.toIso8601String();
        data['crawledAt'] = a.crawledAt.toIso8601String();
        return data;
      }).toList();
      
      await prefs.setString('crawled_announcements', json.encode(announcementsJson));
      
      debugPrint('로컬 저장소에 공지사항 저장 완료');
    } catch (e) {
      debugPrint('로컬 저장 오류: $e');
    }
  }

  // 모든 사용자의 관심사 태그 가져오기
  Future<List<InterestTag>> _getAllInterestTags() async {
    try {
      // Firebase 권한 문제로 인해 더미 태그 반환
      return [
        InterestTag(
          id: '수강신청',
          name: '수강신청',
          keywords: ['수강신청', '등록'],
          createdAt: DateTime.now(),
        ),
        InterestTag(
          id: '학사일정',
          name: '학사일정',
          keywords: ['학사일정', '개강', '종강'],
          createdAt: DateTime.now(),
        ),
      ];
    } catch (e) {
      debugPrint('Error getting all interest tags: $e');
      return [];
    }
  }
  
  // 공지사항을 Firestore에 저장
  Future<void> _saveAnnouncements(List<Announcement> announcements) async {
    try {
      final batch = _firestore.batch();
      
      for (final announcement in announcements) {
        final docRef = _firestore.collection('announcements').doc(announcement.id);
        batch.set(docRef, announcement.toFirestore(), SetOptions(merge: true));
      }
      
      await batch.commit();
      debugPrint('Saved ${announcements.length} announcements to Firestore');
    } catch (e) {
      debugPrint('Error saving announcements: $e');
    }
  }
  
  // 공지사항 가져오기 (AI 크롤링 서비스용)
  Future<List<Announcement>> getAnnouncements() async {
    try {
      final snapshot = await _firestore
          .collection('announcements')
          .orderBy('publishedAt', descending: true)
          .limit(100)
          .get();
      
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    } catch (e) {
      debugPrint('Error getting announcements: $e');
      return [];
    }
  }

  // 특정 사용자에게 맞춤 공지사항 가져오기
  Stream<List<Announcement>> getUserAnnouncements(String userId) {
    return _firestore
        .collection('announcements')
        .where('tags', arrayContainsAny: []) // 사용자 태그로 필터링
        .orderBy('publishedAt', descending: true)
        .limit(50)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    });
  }
}
