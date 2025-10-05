class University {
  final String id;
  final String name;
  final String fullName;
  final String region;
  final String website;
  final String scheduleUrl;
  final String type; // 'national', 'private', 'special'
  final int ranking;
  final List<String> campuses;
  final String? logoUrl;

  const University({
    required this.id,
    required this.name,
    required this.fullName,
    required this.region,
    required this.website,
    required this.scheduleUrl,
    required this.type,
    required this.ranking,
    required this.campuses,
    this.logoUrl,
  });

  factory University.fromJson(Map<String, dynamic> json) {
    return University(
      id: json['id'] as String,
      name: json['name'] as String,
      fullName: json['fullName'] as String,
      region: json['region'] as String,
      website: json['website'] as String,
      scheduleUrl: json['scheduleUrl'] as String,
      type: json['type'] as String,
      ranking: json['ranking'] as int,
      campuses: List<String>.from(json['campuses'] as List),
      logoUrl: json['logoUrl'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'fullName': fullName,
      'region': region,
      'website': website,
      'scheduleUrl': scheduleUrl,
      'type': type,
      'ranking': ranking,
      'campuses': campuses,
      'logoUrl': logoUrl,
    };
  }

  @override
  String toString() => fullName;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is University && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  // Firestore 변환 메서드
  factory University.fromFirestore(Map<String, dynamic> data) {
    return University(
      id: data['id'] as String,
      name: data['name'] as String,
      fullName: data['fullName'] as String,
      region: data['region'] as String,
      website: data['website'] as String,
      scheduleUrl: data['scheduleUrl'] as String,
      type: data['type'] as String,
      ranking: data['ranking'] as int,
      campuses: List<String>.from(data['campuses'] as List),
      logoUrl: data['logoUrl'] as String?,
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'id': id,
      'name': name,
      'fullName': fullName,
      'region': region,
      'website': website,
      'scheduleUrl': scheduleUrl,
      'type': type,
      'ranking': ranking,
      'campuses': campuses,
      'logoUrl': logoUrl,
    };
  }
}
