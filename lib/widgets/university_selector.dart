import 'package:flutter/material.dart';
import '../models/university.dart';
import '../services/university_service.dart';

class UniversitySelector extends StatefulWidget {
  final University? selectedUniversity;
  final Function(University) onUniversitySelected;
  final String? label;
  final String? hint;

  const UniversitySelector({
    super.key,
    this.selectedUniversity,
    required this.onUniversitySelected,
    this.label,
    this.hint,
  });


  @override
  State<UniversitySelector> createState() => _UniversitySelectorState();
}

class _UniversitySelectorState extends State<UniversitySelector> {
  final TextEditingController _searchController = TextEditingController();
  List<University> _filteredUniversities = [];
  bool _isSearching = false;
  University? _tempSelectedUniversity; // 임시 선택된 대학교

  @override
  void initState() {
    super.initState();
    _filteredUniversities = UniversityService.getAllUniversities();
    if (widget.selectedUniversity != null) {
      _searchController.text = widget.selectedUniversity!.name;
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    setState(() {
      _isSearching = query.isNotEmpty;
      _filteredUniversities = UniversityService.searchUniversities(query);
    });
  }

  void _selectUniversity(University university) {
    setState(() {
      _searchController.text = university.name;
      _isSearching = false;
      _tempSelectedUniversity = university; // 임시 선택 저장
    });
    // 미리보기로만 표시 (실제 저장은 "선택" 버튼에서)
    widget.onUniversitySelected(university);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.label != null) ...[
          Text(
            widget.label!,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
        ],
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: widget.hint ?? '대학교를 검색하세요',
            prefixIcon: const Icon(Icons.search),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _searchController.clear();
                      _onSearchChanged('');
                    },
                  )
                : null,
            border: const OutlineInputBorder(),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          onChanged: _onSearchChanged,
          onTap: () {
            if (!_isSearching) {
              _onSearchChanged(_searchController.text);
            }
          },
        ),
        if (_isSearching && _filteredUniversities.isNotEmpty) ...[
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _filteredUniversities.length,
              itemBuilder: (context, index) {
                final university = _filteredUniversities[index];
                return ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    radius: 16,
                    backgroundColor: _getUniversityColor(university.type),
                    child: Text(
                      university.name.substring(0, 1),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  title: Text(
                    university.name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  subtitle: Text(
                    '${university.region} • ${_getUniversityTypeText(university.type)}',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 12,
                    ),
                  ),
                  trailing: university.ranking <= 10
                      ? Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.orange.shade100,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            'TOP ${university.ranking}',
                            style: TextStyle(
                              color: Colors.orange.shade800,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        )
                      : null,
                  onTap: () => _selectUniversity(university),
                );
              },
            ),
          ),
        ],
        if (_isSearching && _filteredUniversities.isEmpty) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
              color: Colors.grey.shade50,
            ),
            child: Row(
              children: [
                Icon(Icons.search_off, color: Colors.grey.shade400),
                const SizedBox(width: 8),
                Text(
                  '검색 결과가 없습니다',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Color _getUniversityColor(String type) {
    switch (type) {
      case 'national':
        return Colors.blue;
      case 'private':
        return Colors.green;
      case 'special':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  String _getUniversityTypeText(String type) {
    switch (type) {
      case 'national':
        return '국립';
      case 'private':
        return '사립';
      case 'special':
        return '특수';
      default:
        return '기타';
    }
  }
}
