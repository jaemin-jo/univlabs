class Announcement {
  final String id;
  final String title;
  final String content;
  final String url;
  final String source;
  final DateTime publishedAt;
  final DateTime crawledAt;
  final List<String> tags;
  final String? imageUrl;
  final bool isImportant;
  final bool isRead;
  final Map<String, dynamic> metadata;
  
  // 기존 코드 호환성을 위한 필드들
  final AnnouncementType type;
  final String? department;
  final String? link;
  
  // 기존 코드에서 사용하는 getter
  DateTime get publishDate => publishedAt;

  Announcement({
    required this.id,
    required this.title,
    required this.content,
    required this.url,
    required this.source,
    required this.publishedAt,
    required this.crawledAt,
    this.tags = const [],
    this.imageUrl,
    this.isImportant = false,
    this.isRead = false,
    this.metadata = const {},
    this.type = AnnouncementType.general,
    this.department,
    this.link,
  });

  factory Announcement.fromFirestore(Map<String, dynamic> data) {
    return Announcement(
      id: data['id'] ?? '',
      title: data['title'] ?? '',
      content: data['content'] ?? '',
      url: data['url'] ?? '',
      source: data['source'] ?? '',
      publishedAt: data['publishedAt'] is DateTime 
          ? data['publishedAt'] 
          : DateTime.now(),
      crawledAt: data['crawledAt'] is DateTime 
          ? data['crawledAt'] 
          : DateTime.now(),
      tags: List<String>.from(data['tags'] ?? []),
      imageUrl: data['imageUrl'],
      isImportant: data['isImportant'] ?? false,
      isRead: data['isRead'] ?? false,
      metadata: Map<String, dynamic>.from(data['metadata'] ?? {}),
      type: _parseAnnouncementType(data['type']),
      department: data['department'],
      link: data['link'],
    );
  }
  
  static AnnouncementType _parseAnnouncementType(dynamic type) {
    if (type is String) {
      return AnnouncementType.values.firstWhere(
        (e) => e.name == type,
        orElse: () => AnnouncementType.general,
      );
    }
    return AnnouncementType.general;
  }

  Map<String, dynamic> toFirestore() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'url': url,
      'source': source,
      'publishedAt': publishedAt,
      'crawledAt': crawledAt,
      'tags': tags,
      'imageUrl': imageUrl,
      'isImportant': isImportant,
      'isRead': isRead,
      'metadata': metadata,
      'type': type.name,
      'department': department,
      'link': link,
    };
  }

  Announcement copyWith({
    String? title,
    String? content,
    String? url,
    String? source,
    DateTime? publishedAt,
    DateTime? crawledAt,
    List<String>? tags,
    String? imageUrl,
    bool? isImportant,
    bool? isRead,
    Map<String, dynamic>? metadata,
    AnnouncementType? type,
    String? department,
    String? link,
  }) {
    return Announcement(
      id: id,
      title: title ?? this.title,
      content: content ?? this.content,
      url: url ?? this.url,
      source: source ?? this.source,
      publishedAt: publishedAt ?? this.publishedAt,
      crawledAt: crawledAt ?? this.crawledAt,
      tags: tags ?? this.tags,
      imageUrl: imageUrl ?? this.imageUrl,
      isImportant: isImportant ?? this.isImportant,
      isRead: isRead ?? this.isRead,
      metadata: metadata ?? this.metadata,
      type: type ?? this.type,
      department: department ?? this.department,
      link: link ?? this.link,
    );
  }
}

enum AnnouncementType {
  academic,    // 학사
  scholarship, // 장학금
  contest,     // 공모전
  event,       // 행사
  dormitory,   // 기숙사
  employment,  // 취업
  general,     // 일반
}

extension AnnouncementTypeExtension on AnnouncementType {
  String get displayName {
    switch (this) {
      case AnnouncementType.academic:
        return '학사';
      case AnnouncementType.scholarship:
        return '장학금';
      case AnnouncementType.contest:
        return '공모전';
      case AnnouncementType.event:
        return '행사';
      case AnnouncementType.dormitory:
        return '기숙사';
      case AnnouncementType.employment:
        return '취업';
      case AnnouncementType.general:
        return '일반';
    }
  }

  String get icon {
    switch (this) {
      case AnnouncementType.academic:
        return '📚';
      case AnnouncementType.scholarship:
        return '💰';
      case AnnouncementType.contest:
        return '🏆';
      case AnnouncementType.event:
        return '🎉';
      case AnnouncementType.dormitory:
        return '🏠';
      case AnnouncementType.employment:
        return '💼';
      case AnnouncementType.general:
        return '📢';
    }
  }
}