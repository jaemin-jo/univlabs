class UserProfile {
  final String uid;
  final String name;
  final String studentId;
  final String major;
  final String email;
  final String? profileImageUrl;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic> preferences;
  final List<String> interestTags;
  final List<String> subscribedChannels;
  
  // 기존 코드 호환성을 위한 필드들
  final String? university;
  final String? department;
  final int? grade;
  final List<String> interests;
  final String? semesterInfo;
  final String? summaryInfo;

  UserProfile({
    required this.uid,
    required this.name,
    required this.studentId,
    required this.major,
    required this.email,
    this.profileImageUrl,
    required this.createdAt,
    required this.updatedAt,
    this.preferences = const {},
    this.interestTags = const [],
    this.subscribedChannels = const [],
    this.university,
    this.department,
    this.grade,
    this.interests = const [],
    this.semesterInfo,
    this.summaryInfo,
  });

  factory UserProfile.fromFirestore(Map<String, dynamic> data) {
    return UserProfile(
      uid: data['uid'] ?? '',
      name: data['name'] ?? '',
      studentId: data['studentId'] ?? '',
      major: data['major'] ?? '',
      email: data['email'] ?? '',
      profileImageUrl: data['profileImageUrl'],
      createdAt: data['createdAt'] is DateTime 
          ? data['createdAt'] 
          : DateTime.now(),
      updatedAt: data['updatedAt'] is DateTime 
          ? data['updatedAt'] 
          : DateTime.now(),
      preferences: Map<String, dynamic>.from(data['preferences'] ?? {}),
      interestTags: List<String>.from(data['interestTags'] ?? []),
      subscribedChannels: List<String>.from(data['subscribedChannels'] ?? []),
      university: data['university'],
      department: data['department'],
      grade: data['grade'],
      interests: List<String>.from(data['interests'] ?? []),
      semesterInfo: data['semesterInfo'],
      summaryInfo: data['summaryInfo'],
    );
  }
  
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      uid: json['uid'] ?? '',
      name: json['name'] ?? '',
      studentId: json['studentId'] ?? '',
      major: json['major'] ?? '',
      email: json['email'] ?? '',
      profileImageUrl: json['profileImageUrl'],
      createdAt: DateTime.parse(json['createdAt'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updatedAt'] ?? DateTime.now().toIso8601String()),
      preferences: Map<String, dynamic>.from(json['preferences'] ?? {}),
      interestTags: List<String>.from(json['interestTags'] ?? []),
      subscribedChannels: List<String>.from(json['subscribedChannels'] ?? []),
      university: json['university'],
      department: json['department'],
      grade: json['grade'],
      interests: List<String>.from(json['interests'] ?? []),
      semesterInfo: json['semesterInfo'],
      summaryInfo: json['summaryInfo'],
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'uid': uid,
      'name': name,
      'studentId': studentId,
      'major': major,
      'email': email,
      'profileImageUrl': profileImageUrl,
      'createdAt': createdAt,
      'updatedAt': updatedAt,
      'preferences': preferences,
      'interestTags': interestTags,
      'subscribedChannels': subscribedChannels,
      'university': university,
      'department': department,
      'grade': grade,
      'interests': interests,
      'semesterInfo': semesterInfo,
      'summaryInfo': summaryInfo,
    };
  }
  
  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'name': name,
      'studentId': studentId,
      'major': major,
      'email': email,
      'profileImageUrl': profileImageUrl,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'preferences': preferences,
      'interestTags': interestTags,
      'subscribedChannels': subscribedChannels,
      'university': university,
      'department': department,
      'grade': grade,
      'interests': interests,
      'semesterInfo': semesterInfo,
      'summaryInfo': summaryInfo,
    };
  }

  UserProfile copyWith({
    String? name,
    String? studentId,
    String? major,
    String? email,
    String? profileImageUrl,
    DateTime? updatedAt,
    Map<String, dynamic>? preferences,
    List<String>? interestTags,
    List<String>? subscribedChannels,
    String? university,
    String? department,
    int? grade,
    List<String>? interests,
    String? semesterInfo,
    String? summaryInfo,
  }) {
    return UserProfile(
      uid: uid,
      name: name ?? this.name,
      studentId: studentId ?? this.studentId,
      major: major ?? this.major,
      email: email ?? this.email,
      profileImageUrl: profileImageUrl ?? this.profileImageUrl,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      preferences: preferences ?? this.preferences,
      interestTags: interestTags ?? this.interestTags,
      subscribedChannels: subscribedChannels ?? this.subscribedChannels,
      university: university ?? this.university,
      department: department ?? this.department,
      grade: grade ?? this.grade,
      interests: interests ?? this.interests,
      semesterInfo: semesterInfo ?? this.semesterInfo,
      summaryInfo: summaryInfo ?? this.summaryInfo,
    );
  }
}