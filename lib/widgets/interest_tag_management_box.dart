import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/interest_tag_provider.dart';
import '../models/interest_tag.dart';

class InterestTagManagementBox extends StatefulWidget {
  const InterestTagManagementBox({super.key});

  @override
  State<InterestTagManagementBox> createState() => _InterestTagManagementBoxState();
}

class _InterestTagManagementBoxState extends State<InterestTagManagementBox> {

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<InterestTagProvider>(
      builder: (context, tagProvider, child) {
        final tags = tagProvider.tags;
        final matchedAnnouncements = tagProvider.matchedAnnouncements;

        return Container(
          margin: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 헤더
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.purple.shade100, Colors.blue.shade100],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.tag,
                      color: Colors.purple.shade700,
                      size: 24,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '관심사 태그 관리',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.purple.shade700,
                            ),
                          ),
                          Text(
                            'AI가 관련 공지사항을 찾아드립니다',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.purple.shade600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    // 크롤링 상태 표시
                    if (tagProvider.isCrawling)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade100,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            SizedBox(
                              width: 12,
                              height: 12,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.orange.shade600),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '검색중',
                              style: TextStyle(
                                color: Colors.orange.shade700,
                                fontSize: 10,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    const SizedBox(width: 8),
                    // 수동 크롤링 버튼
                    IconButton(
                      onPressed: tagProvider.isCrawling 
                          ? null 
                          : () => tagProvider.performManualCrawling(),
                      icon: Icon(
                        Icons.search,
                        color: tagProvider.isCrawling 
                            ? Colors.grey.shade400 
                            : Colors.purple.shade700,
                      ),
                      tooltip: '수동 검색',
                    ),
                    // 태그 추가 버튼
                    IconButton(
                      onPressed: () => _showAddTagDialog(context),
                      icon: Icon(
                        Icons.add,
                        color: Colors.purple.shade700,
                      ),
                      tooltip: '태그 추가',
                    ),
                  ],
                ),
              ),

              // 매칭된 공지사항 알림
              if (matchedAnnouncements.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.notifications_active,
                        color: Colors.red.shade600,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '${matchedAnnouncements.length}개의 관련 공지사항을 찾았습니다!',
                          style: TextStyle(
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          // 공지사항 상세 보기
                          _showMatchedAnnouncements(context, matchedAnnouncements);
                        },
                        child: Text(
                          '보기',
                          style: TextStyle(
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),


              // 태그 그리드
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _buildTagChips(tags),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  List<Widget> _buildTagChips(List<InterestTag> tags) {
    return tags.map((tag) => _buildTagChip(tag)).toList();
  }

  Widget _buildTagChip(InterestTag tag) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.purple.shade50,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.purple.shade200),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => _showTagDetailsDialog(context, tag),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.tag,
                size: 16,
                color: Colors.purple.shade600,
              ),
              const SizedBox(width: 6),
              Text(
                tag.name,
                style: TextStyle(
                  color: Colors.purple.shade700,
                  fontWeight: FontWeight.w500,
                  fontSize: 14,
                ),
              ),
              const SizedBox(width: 4),
              if (tag.url != null)
                Icon(
                  Icons.link,
                  size: 14,
                  color: Colors.purple.shade500,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCompactTagChip(InterestTag tag) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.purple.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.purple.shade200),
      ),
      child: Text(
        tag.name,
        style: TextStyle(
          color: Colors.purple.shade700,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  void _showAddTagDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const AddTagDialog(),
    );
  }

  void _showDeleteTagDialog(BuildContext context, InterestTag tag) {
    showDialog(
      context: context,
      builder: (context) => DeleteTagDialog(tag: tag),
    );
  }

  void _showTagDetailsDialog(BuildContext context, InterestTag tag) {
    showDialog(
      context: context,
      builder: (context) => TagDetailsDialog(
        tag: tag,
        onEdit: () => _showEditTagDialog(context, tag),
        onDelete: () => _showDeleteTagDialog(context, tag),
      ),
    );
  }

  void _showEditTagDialog(BuildContext context, InterestTag tag) {
    showDialog(
      context: context,
      builder: (context) => EditTagDialog(tag: tag),
    );
  }

  void _showMatchedAnnouncements(BuildContext context, List<InterestTag> announcements) {
    showDialog(
      context: context,
      builder: (context) => MatchedAnnouncementsDialog(announcements: announcements),
    );
  }
}

// 태그 삭제 확인 다이얼로그
class DeleteTagDialog extends StatelessWidget {
  final InterestTag tag;

  const DeleteTagDialog({super.key, required this.tag});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.delete_outline, color: Colors.red.shade600),
          const SizedBox(width: 8),
          const Text('태그 삭제'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '다음 태그를 삭제하시겠습니까?',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.purple.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.purple.shade200),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.tag,
                  size: 20,
                  color: Colors.purple.shade600,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    tag.name,
                    style: TextStyle(
                      color: Colors.purple.shade700,
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (tag.description != null) ...[
            const SizedBox(height: 8),
            Text(
              tag.description!,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 14,
              ),
            ),
          ],
          const SizedBox(height: 12),
          Text(
            '이 작업은 되돌릴 수 없습니다.',
            style: TextStyle(
              color: Colors.red.shade600,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('취소'),
        ),
        ElevatedButton(
          onPressed: () {
            context.read<InterestTagProvider>().removeTag(tag.id);
            Navigator.of(context).pop();
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('${tag.name} 태그가 삭제되었습니다'),
                backgroundColor: Colors.red.shade600,
                duration: const Duration(seconds: 2),
              ),
            );
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red.shade600,
            foregroundColor: Colors.white,
          ),
          child: const Text('삭제'),
        ),
      ],
    );
  }
}

// 태그 편집 다이얼로그
class EditTagDialog extends StatefulWidget {
  final InterestTag tag;

  const EditTagDialog({super.key, required this.tag});

  @override
  State<EditTagDialog> createState() => _EditTagDialogState();
}

class _EditTagDialogState extends State<EditTagDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _urlController;
  late TextEditingController _descriptionController;
  late TextEditingController _keywordsController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.tag.name);
    _urlController = TextEditingController(text: widget.tag.url ?? '');
    _descriptionController = TextEditingController(text: widget.tag.description ?? '');
    _keywordsController = TextEditingController(text: widget.tag.keywords.join(', '));
  }

  @override
  void dispose() {
    _nameController.dispose();
    _urlController.dispose();
    _descriptionController.dispose();
    _keywordsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.edit, color: Colors.blue.shade600),
          const SizedBox(width: 8),
          const Text('태그 편집'),
        ],
      ),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: '태그 이름',
                hintText: '예: 수강신청, 기숙사, 장학금',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '태그 이름을 입력해주세요';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: '관련 URL (선택사항)',
                hintText: 'https://example.com',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: '설명 (선택사항)',
                hintText: '태그에 대한 간단한 설명',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _keywordsController,
              decoration: const InputDecoration(
                labelText: '관련 키워드 (쉼표로 구분)',
                hintText: '수강신청, 수강신청기간, 수강신청안내',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('취소'),
        ),
        ElevatedButton(
          onPressed: _updateTag,
          child: const Text('수정'),
        ),
      ],
    );
  }

  void _updateTag() {
    if (_formKey.currentState!.validate()) {
      final keywords = _keywordsController.text
          .split(',')
          .map((keyword) => keyword.trim())
          .where((keyword) => keyword.isNotEmpty)
          .toList();

      final updatedTag = widget.tag.copyWith(
        name: _nameController.text,
        url: _urlController.text.isEmpty ? null : _urlController.text,
        description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
        keywords: keywords,
      );

      context.read<InterestTagProvider>().updateTag(updatedTag);
      Navigator.of(context).pop();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${updatedTag.name} 태그가 수정되었습니다'),
          backgroundColor: Colors.blue.shade600,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
}

// 태그 추가 다이얼로그
class AddTagDialog extends StatefulWidget {
  const AddTagDialog({super.key});

  @override
  State<AddTagDialog> createState() => _AddTagDialogState();
}

class _AddTagDialogState extends State<AddTagDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _urlController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('새 태그 추가'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: '태그 이름',
                hintText: '예: 수강신청, 기숙사, 장학금',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '태그 이름을 입력해주세요';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: '관련 URL (선택사항)',
                hintText: 'https://example.com',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('취소'),
        ),
        ElevatedButton(
          onPressed: _addTag,
          child: const Text('추가'),
        ),
      ],
    );
  }

  void _addTag() {
    if (_formKey.currentState!.validate()) {
      final tag = InterestTag(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: _nameController.text,
        url: _urlController.text.isEmpty ? null : _urlController.text,
        createdAt: DateTime.now(),
        keywords: [_nameController.text], // 태그 이름을 기본 키워드로 사용
      );

      context.read<InterestTagProvider>().addTag(tag);
      Navigator.of(context).pop();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${tag.name} 태그가 추가되었습니다'),
          backgroundColor: Colors.green.shade600,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
}

// 태그 상세 다이얼로그
class TagDetailsDialog extends StatelessWidget {
  final InterestTag tag;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const TagDetailsDialog({
    super.key, 
    required this.tag,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.tag, color: Colors.purple.shade600),
          const SizedBox(width: 8),
          Text(tag.name),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (tag.description != null) ...[
            Text(
              '설명',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 4),
            Text(tag.description!),
            const SizedBox(height: 16),
          ],
          if (tag.url != null) ...[
            Text(
              'URL',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 4),
            InkWell(
              onTap: () {
                // URL 열기 로직
              },
              child: Text(
                tag.url!,
                style: TextStyle(
                  color: Colors.blue.shade600,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          if (tag.keywords.isNotEmpty) ...[
            Text(
              '관련 키워드',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: tag.keywords.map((keyword) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.purple.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  keyword,
                  style: TextStyle(
                    color: Colors.purple.shade700,
                    fontSize: 12,
                  ),
                ),
              )).toList(),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('닫기'),
        ),
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
            onEdit();
          },
          style: TextButton.styleFrom(foregroundColor: Colors.blue),
          child: const Text('편집'),
        ),
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
            onDelete();
          },
          style: TextButton.styleFrom(foregroundColor: Colors.red),
          child: const Text('삭제'),
        ),
      ],
    );
  }
}

// 매칭된 공지사항 다이얼로그
class MatchedAnnouncementsDialog extends StatelessWidget {
  final List<InterestTag> announcements;

  const MatchedAnnouncementsDialog({super.key, required this.announcements});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.notifications_active, color: Colors.red.shade600),
          const SizedBox(width: 8),
          const Text('관련 공지사항'),
        ],
      ),
      content: SizedBox(
        width: double.maxFinite,
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: announcements.length,
          itemBuilder: (context, index) {
            final announcement = announcements[index];
            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: Icon(
                  Icons.article,
                  color: Colors.red.shade600,
                ),
                title: Text(
                  announcement.name,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: announcement.description != null 
                    ? Text(announcement.description!)
                    : null,
                trailing: IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () {
                    context.read<InterestTagProvider>().removeMatchedAnnouncement(announcement.id);
                  },
                ),
                onTap: () {
                  // 공지사항 상세 보기
                },
              ),
            );
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            context.read<InterestTagProvider>().clearMatchedAnnouncements();
            Navigator.of(context).pop();
          },
          child: const Text('모두 지우기'),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('닫기'),
        ),
      ],
    );
  }
}
