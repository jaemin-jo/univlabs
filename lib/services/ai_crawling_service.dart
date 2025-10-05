import '../models/interest_tag.dart';
import '../models/announcement.dart';
import 'web_crawling_service.dart';
import 'gemini_service.dart';

class AICrawlingService {
  static final WebCrawlingService _webCrawlingService = WebCrawlingService.instance;

  // 관심사 태그에 관련된 공지사항 찾기
  static Future<List<InterestTag>> findRelevantAnnouncements(List<InterestTag> tags) async {
    try {
      // 모든 활성화된 태그의 키워드 수집
      final allKeywords = tags
          .where((tag) => tag.isActive)
          .expand((tag) => tag.keywords)
          .toList();

      if (allKeywords.isEmpty) return [];

      // 웹 크롤링으로 공지사항 가져오기
      final announcements = await _webCrawlingService.getAnnouncements();
      
      // AI를 사용하여 관련성 분석
      final relevantAnnouncements = await _analyzeRelevance(announcements, allKeywords);
      
      // InterestTag 형태로 변환
      return relevantAnnouncements.map((announcement) => InterestTag(
        id: announcement.id,
        name: announcement.title,
        description: announcement.content,
        createdAt: announcement.publishDate,
        keywords: _extractKeywords(announcement),
        isActive: true,
      )).toList();
    } catch (e) {
      print('AI 크롤링 오류: $e');
      return [];
    }
  }

  // 특정 태그에 대한 검색
  static Future<List<InterestTag>> searchForTag(InterestTag tag) async {
    try {
      // 웹 크롤링으로 공지사항 가져오기
      final announcements = await _webCrawlingService.getAnnouncements();
      
      // 태그 키워드로 필터링
      final relevantAnnouncements = announcements.where((announcement) {
        final title = announcement.title.toLowerCase();
        final content = announcement.content.toLowerCase();
        
        return tag.keywords.any((keyword) => 
          title.contains(keyword.toLowerCase()) || 
          content.contains(keyword.toLowerCase())
        );
      }).toList();
      
      // InterestTag 형태로 변환
      return relevantAnnouncements.map((announcement) => InterestTag(
        id: announcement.id,
        name: announcement.title,
        description: announcement.content,
        createdAt: announcement.publishDate,
        keywords: _extractKeywords(announcement),
        isActive: true,
      )).toList();
    } catch (e) {
      print('태그 검색 오류: $e');
      return [];
    }
  }

  // AI를 사용한 관련성 분석
  static Future<List<Announcement>> _analyzeRelevance(
    List<Announcement> announcements, 
    List<String> keywords
  ) async {
    try {
      final prompt = '''
다음 공지사항들 중에서 주어진 키워드들과 관련성이 높은 것들을 선별해주세요.

키워드: ${keywords.join(', ')}

공지사항들:
${announcements.map((a) => '제목: ${a.title}\n내용: ${a.content.substring(0, a.content.length > 200 ? 200 : a.content.length)}...').join('\n\n')}

관련성이 높은 공지사항의 ID만 쉼표로 구분해서 답변해주세요.
''';

      final response = await GeminiService.generateResponse(prompt, []);
      
      // 응답에서 ID 추출
      final relevantIds = response
          .split(',')
          .map((id) => id.trim())
          .where((id) => id.isNotEmpty)
          .toList();

      // 해당 ID의 공지사항들 반환
      return announcements.where((announcement) => 
        relevantIds.contains(announcement.id)
      ).toList();
    } catch (e) {
      print('AI 분석 오류: $e');
      // AI 분석 실패 시 키워드 기반 필터링으로 대체
      return _filterByKeywords(announcements, keywords);
    }
  }

  // 키워드 기반 필터링 (AI 분석 실패 시 대체)
  static List<Announcement> _filterByKeywords(
    List<Announcement> announcements, 
    List<String> keywords
  ) {
    return announcements.where((announcement) {
      final title = announcement.title.toLowerCase();
      final content = announcement.content.toLowerCase();
      
      return keywords.any((keyword) => 
        title.contains(keyword.toLowerCase()) || 
        content.contains(keyword.toLowerCase())
      );
    }).toList();
  }

  // 공지사항에서 키워드 추출
  static List<String> _extractKeywords(Announcement announcement) {
    final keywords = <String>[];
    
    // 제목에서 키워드 추출
    final titleWords = announcement.title.split(' ');
    keywords.addAll(titleWords.where((word) => word.length > 2));
    
    // 내용에서 키워드 추출 (처음 100자)
    final contentWords = announcement.content
        .substring(0, announcement.content.length > 100 ? 100 : announcement.content.length)
        .split(' ');
    keywords.addAll(contentWords.where((word) => word.length > 2));
    
    return keywords.take(10).toList(); // 최대 10개 키워드
  }
}
