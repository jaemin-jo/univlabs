class InterestTag {
  final String id;
  final String name;
  final String? url; // 웹사이트 URL (선택사항)
  final String? description; // 태그 설명
  final DateTime createdAt;
  final bool isActive; // 활성화 상태
  final List<String> keywords; // 관련 키워드들

  InterestTag({
    required this.id,
    required this.name,
    this.url,
    this.description,
    required this.createdAt,
    this.isActive = true,
    this.keywords = const [],
  });

  // JSON 변환
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'url': url,
      'description': description,
      'createdAt': createdAt.toIso8601String(),
      'isActive': isActive,
      'keywords': keywords,
    };
  }

  factory InterestTag.fromJson(Map<String, dynamic> json) {
    return InterestTag(
      id: json['id'],
      name: json['name'],
      url: json['url'],
      description: json['description'],
      createdAt: DateTime.parse(json['createdAt']),
      isActive: json['isActive'] ?? true,
      keywords: List<String>.from(json['keywords'] ?? []),
    );
  }

  // 복사본 생성
  InterestTag copyWith({
    String? id,
    String? name,
    String? url,
    String? description,
    DateTime? createdAt,
    bool? isActive,
    List<String>? keywords,
  }) {
    return InterestTag(
      id: id ?? this.id,
      name: name ?? this.name,
      url: url ?? this.url,
      description: description ?? this.description,
      createdAt: createdAt ?? this.createdAt,
      isActive: isActive ?? this.isActive,
      keywords: keywords ?? this.keywords,
    );
  }
}

