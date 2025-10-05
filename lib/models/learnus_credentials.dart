class LearnUsCredentials {
  final String uid; // Firebase 사용자 ID
  final String username; // LearnUs 아이디
  final String password; // LearnUs 비밀번호
  final String studentId; // 학번
  final String university; // 대학교명
  final bool isActive; // 활성화 상태
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastUsedAt; // 마지막 사용 시간

  LearnUsCredentials({
    required this.uid,
    required this.username,
    required this.password,
    required this.studentId,
    required this.university,
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
    this.lastUsedAt,
  });

  factory LearnUsCredentials.fromFirestore(Map<String, dynamic> data) {
    return LearnUsCredentials(
      uid: data['uid'] ?? '',
      username: data['username'] ?? '',
      password: data['password'] ?? '',
      studentId: data['studentId'] ?? '',
      university: data['university'] ?? '',
      isActive: data['isActive'] ?? true,
      createdAt: data['createdAt'] is DateTime 
          ? data['createdAt'] 
          : DateTime.now(),
      updatedAt: data['updatedAt'] is DateTime 
          ? data['updatedAt'] 
          : DateTime.now(),
      lastUsedAt: data['lastUsedAt'] is DateTime 
          ? data['lastUsedAt'] 
          : null,
    );
  }

  factory LearnUsCredentials.fromJson(Map<String, dynamic> json) {
    return LearnUsCredentials(
      uid: json['uid'] ?? '',
      username: json['username'] ?? '',
      password: json['password'] ?? '',
      studentId: json['studentId'] ?? '',
      university: json['university'] ?? '',
      isActive: json['isActive'] ?? true,
      createdAt: DateTime.parse(json['createdAt'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updatedAt'] ?? DateTime.now().toIso8601String()),
      lastUsedAt: json['lastUsedAt'] != null 
          ? DateTime.parse(json['lastUsedAt']) 
          : null,
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'uid': uid,
      'username': username,
      'password': password,
      'studentId': studentId,
      'university': university,
      'isActive': isActive,
      'createdAt': createdAt,
      'updatedAt': updatedAt,
      'lastUsedAt': lastUsedAt,
    };
  }

  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'username': username,
      'password': password,
      'studentId': studentId,
      'university': university,
      'isActive': isActive,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'lastUsedAt': lastUsedAt?.toIso8601String(),
    };
  }

  LearnUsCredentials copyWith({
    String? username,
    String? password,
    String? studentId,
    String? university,
    bool? isActive,
    DateTime? updatedAt,
    DateTime? lastUsedAt,
  }) {
    return LearnUsCredentials(
      uid: uid,
      username: username ?? this.username,
      password: password ?? this.password,
      studentId: studentId ?? this.studentId,
      university: university ?? this.university,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastUsedAt: lastUsedAt ?? this.lastUsedAt,
    );
  }
}

