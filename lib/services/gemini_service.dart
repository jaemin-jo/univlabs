import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class GeminiService {
  static const String _apiKey = 'AIzaSyAwxEI92CtK1bomNALSOU2AzvH1aiwJ7ko';
  static GenerativeModel? _model;
  
  static GenerativeModel get model {
    if (_model == null) {
      _model = GenerativeModel(
        model: 'gemini-1.5-flash',
        apiKey: _apiKey,
        generationConfig: GenerationConfig(
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: 1024,
        ),
      );
    }
    return _model!;
  }
  
  // AI와 채팅하는 메서드
  static Future<String> chatWithAI(String userMessage) async {
    try {
      final chat = model.startChat();
      final response = await chat.sendMessage(Content.text(userMessage));
      return response.text ?? '죄송합니다. 응답을 생성할 수 없습니다.';
    } catch (e) {
      return 'AI 서비스에 연결할 수 없습니다: $e';
    }
  }
  
  // 대학생활 관련 질문에 특화된 AI 응답
  static Future<String> getStudentLifeAdvice(String question) async {
    final prompt = '''
당신은 대학생활 전문 AI 어시스턴트입니다. 
다음 질문에 대해 친근하고 도움이 되는 답변을 해주세요:

$question

답변은 한국어로 해주시고, 대학생에게 실용적인 조언을 포함해주세요.
''';
    
    return await chatWithAI(prompt);
  }
  
  // 일정 관련 AI 조언
  static Future<String> getScheduleAdvice(String scheduleInfo) async {
    final prompt = '''
당신은 대학생 일정 관리 전문 AI입니다.
다음 일정 정보를 바탕으로 조언을 해주세요:

$scheduleInfo

효과적인 시간 관리와 우선순위 설정에 대한 조언을 한국어로 해주세요.
''';
    
    return await chatWithAI(prompt);
  }
  
  // 대화 히스토리 저장
  static Future<void> saveChatHistory(List<ChatMessage> messages) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final messagesJson = messages.map((msg) => {
        'text': msg.text,
        'isUser': msg.isUser,
        'timestamp': msg.timestamp.toIso8601String(),
      }).toList();
      
      await prefs.setString('chat_history', jsonEncode(messagesJson));
    } catch (e) {
      print('채팅 히스토리 저장 실패: $e');
    }
  }
  
  // 대화 히스토리 로드
  static Future<List<ChatMessage>> loadChatHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString('chat_history');
      
      if (historyJson != null) {
        final List<dynamic> messagesData = jsonDecode(historyJson);
        return messagesData.map((data) => ChatMessage(
          text: data['text'],
          isUser: data['isUser'],
          timestamp: DateTime.parse(data['timestamp']),
        )).toList();
      }
    } catch (e) {
      print('채팅 히스토리 로드 실패: $e');
    }
    
    return [];
  }
  
  // AI 응답 생성 (대화 컨텍스트 포함)
  static Future<String> generateResponse(String userMessage, List<ChatMessage> chatHistory) async {
    try {
      // 현재 날짜와 시간 정보 가져오기
      final now = DateTime.now();
      final currentDate = '${now.year}년 ${now.month}월 ${now.day}일';
      final currentWeekday = _getWeekdayName(now.weekday);
      final currentTime = '${now.hour}시 ${now.minute}분';
      
      // 대화 컨텍스트를 포함한 프롬프트 생성
      String contextPrompt = '''
당신은 유니버(Univer)라는 대학생활 AI 어시스턴트입니다.
대학생의 학업, 일정 관리, 생활 전반에 대해 도움을 주는 친근한 AI입니다.

**중요: 현재 날짜와 시간 정보**
- 현재 날짜: $currentDate ($currentWeekday)
- 현재 시간: $currentTime
- 현재 연도: ${now.year}년
- 현재 월: ${now.month}월
- 현재 일: ${now.day}일

**답변 원칙:**
- 질문의 의도와 맥락을 정확히 파악하여 적절한 수준의 답변 제공
- 간단한 사실 질문에는 간결하게, 복잡한 문제에는 상세하게
- 사용자의 상황과 필요에 맞는 실용적인 조언 제공
- 친근하지만 전문적인 톤으로 대화
- 불확실한 정보는 추측하지 말고 명확히 표현

이전 대화 내용:
''';
      
      // 최근 5개 메시지만 컨텍스트로 포함
      final recentMessages = chatHistory.length > 5 
          ? chatHistory.sublist(chatHistory.length - 5)
          : chatHistory;
          
      for (final msg in recentMessages) {
        contextPrompt += '\n${msg.isUser ? "사용자" : "AI"}: ${msg.text}';
      }
      
      contextPrompt += '''

현재 사용자 질문: $userMessage

위 질문에 대해 대학생에게 도움이 되는 친근하고 실용적인 답변을 한국어로 해주세요.
날짜나 시간 관련 질문이 있다면 위의 정확한 현재 날짜/시간 정보를 사용해주세요.

**짧고 간결한 답변 원칙:**
- 모든 답변을 2-3문장 이내로 간결하게 작성
- 핵심 정보만 전달하고 불필요한 설명 생략
- 간단한 질문: "오늘 몇일이야?" → "2025년 9월 23일 화요일입니다"
- 복잡한 질문도 핵심만 2-3문장으로 요약
- 긴 설명 대신 핵심 포인트만 전달
- 이모지나 과도한 표현 최소화
''';
      
      return await chatWithAI(contextPrompt);
    } catch (e) {
      return '죄송합니다. AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  
  // 요일 이름 반환
  static String _getWeekdayName(int weekday) {
    switch (weekday) {
      case 1: return '월요일';
      case 2: return '화요일';
      case 3: return '수요일';
      case 4: return '목요일';
      case 5: return '금요일';
      case 6: return '토요일';
      case 7: return '일요일';
      default: return '알 수 없음';
    }
  }
}

// 채팅 메시지 모델
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  
  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
  });
}