import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/announcement.dart';
import '../providers/announcement_provider.dart';
import '../widgets/announcement_card.dart';

class AnnouncementsScreen extends StatefulWidget {
  const AnnouncementsScreen({super.key});

  @override
  State<AnnouncementsScreen> createState() => _AnnouncementsScreenState();
}

class _AnnouncementsScreenState extends State<AnnouncementsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('공지사항'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: '맞춤 추천', icon: Icon(Icons.person)),
            Tab(text: '중요 공지', icon: Icon(Icons.priority_high)),
            Tab(text: '전체 공지', icon: Icon(Icons.list)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: _showSearchDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<AnnouncementProvider>().refreshAnnouncements();
            },
          ),
        ],
      ),
      body: Consumer<AnnouncementProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('오류가 발생했습니다: ${provider.error}'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => provider.refreshAnnouncements(),
                    child: const Text('다시 시도'),
                  ),
                ],
              ),
            );
          }

          return TabBarView(
            controller: _tabController,
            children: [
              _buildPersonalizedAnnouncements(provider),
              _buildImportantAnnouncements(provider),
              _buildAllAnnouncements(provider),
            ],
          );
        },
      ),
    );
  }

  Widget _buildPersonalizedAnnouncements(AnnouncementProvider provider) {
    final matchedAnnouncements = provider.getMatchedAnnouncements();
    
    if (matchedAnnouncements.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('맞춤 추천 공지사항이 없습니다'),
            SizedBox(height: 8),
            Text('관심사 태그를 설정하면 관련 공지사항을 추천해드립니다'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: matchedAnnouncements.length,
      itemBuilder: (context, index) {
        final announcement = matchedAnnouncements[index];
        return AnnouncementCard(
          announcement: announcement,
          onTap: () => _launchURL(announcement.url),
          onToggleImportance: () => provider.toggleImportance(announcement.id),
        );
      },
    );
  }

  Widget _buildImportantAnnouncements(AnnouncementProvider provider) {
    final importantAnnouncements = provider.importantAnnouncements;
    
    if (importantAnnouncements.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.priority_high, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('중요 공지사항이 없습니다'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: importantAnnouncements.length,
      itemBuilder: (context, index) {
        final announcement = importantAnnouncements[index];
        return AnnouncementCard(
          announcement: announcement,
          onTap: () => _launchURL(announcement.url),
          onToggleImportance: () => provider.toggleImportance(announcement.id),
        );
      },
    );
  }

  Widget _buildAllAnnouncements(AnnouncementProvider provider) {
    final allAnnouncements = provider.announcements;
    
    if (allAnnouncements.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.list, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('공지사항이 없습니다'),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: allAnnouncements.length,
      itemBuilder: (context, index) {
        final announcement = allAnnouncements[index];
        return AnnouncementCard(
          announcement: announcement,
          onTap: () => _launchURL(announcement.url),
          onToggleImportance: () => provider.toggleImportance(announcement.id),
        );
      },
    );
  }

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('공지사항 검색'),
        content: TextField(
          decoration: const InputDecoration(
            hintText: '검색어를 입력하세요',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            setState(() {
              _searchQuery = value;
            });
          },
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              setState(() {
                _searchQuery = '';
              });
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _performSearch();
            },
            child: const Text('검색'),
          ),
        ],
      ),
    );
  }

  void _performSearch() async {
    if (_searchQuery.isEmpty) return;

    final provider = context.read<AnnouncementProvider>();
    final results = await provider.searchAnnouncements(_searchQuery);

    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('"$_searchQuery" 검색 결과'),
          content: SizedBox(
            width: double.maxFinite,
            height: 400,
            child: results.isEmpty
                ? const Center(child: Text('검색 결과가 없습니다'))
                : ListView.builder(
                    itemCount: results.length,
                    itemBuilder: (context, index) {
                      final announcement = results[index];
                      return ListTile(
                        title: Text(announcement.title),
                        subtitle: Text(announcement.source),
                        onTap: () {
                          Navigator.of(context).pop();
                          _launchURL(announcement.url);
                        },
                      );
                    },
                  ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('닫기'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _launchURL(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('링크를 열 수 없습니다: $url')),
        );
      }
    }
  }
}