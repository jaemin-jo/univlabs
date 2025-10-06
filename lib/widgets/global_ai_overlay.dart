import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/schedule_provider.dart';
import 'global_ai_chat_dialog.dart';

class GlobalAIOverlay extends StatefulWidget {
  const GlobalAIOverlay({super.key});

  @override
  State<GlobalAIOverlay> createState() => _GlobalAIOverlayState();
}

class _GlobalAIOverlayState extends State<GlobalAIOverlay>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _floatController;
  late AnimationController _snapController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _floatAnimation;
  late Animation<Offset> _snapAnimation;
  
  bool _isDragging = false;
  Offset _position = const Offset(0.8, 0.3); // 화면 오른쪽 상단
  bool _isOnLeft = false;

  @override
  void initState() {
    super.initState();
    
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    
    _floatController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    );
    
    _snapController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    _floatAnimation = Tween<double>(
      begin: -5.0,
      end: 5.0,
    ).animate(CurvedAnimation(
      parent: _floatController,
      curve: Curves.easeInOut,
    ));

    _snapAnimation = Tween<Offset>(
      begin: Offset.zero,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _snapController,
      curve: Curves.easeOutCubic,
    ));

    _pulseController.repeat(reverse: true);
    _floatController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _floatController.dispose();
    _snapController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final urgentSchedules = context.watch<ScheduleProvider>().urgentSchedules;
    final hasUrgentSchedules = urgentSchedules.isNotEmpty;

    return AnimatedBuilder(
      animation: Listenable.merge([_pulseAnimation, _floatAnimation, _snapAnimation]),
      builder: (context, child) {
        final currentPosition = _isDragging 
            ? _position 
            : (_snapController.isAnimating ? _snapAnimation.value : _position);
        
        return Positioned(
          left: _isOnLeft ? 20 : null,
          right: _isOnLeft ? null : 20,
          top: currentPosition.dy * screenSize.height,
          child: GestureDetector(
            onPanStart: (details) {
              setState(() {
                _isDragging = true;
              });
            },
            onPanUpdate: (details) {
              setState(() {
                _position = Offset(
                  details.globalPosition.dx / screenSize.width,
                  details.globalPosition.dy / screenSize.height,
                );
              });
            },
            onPanEnd: (details) {
              setState(() {
                _isDragging = false;
              });
              
              // 가장 가까운 가장자리로 부드럽게 스냅
              final targetPosition = _position.dx < 0.5 
                  ? Offset(0.05, _position.dy)
                  : Offset(0.95, _position.dy);
              
              final newIsOnLeft = _position.dx < 0.5;
              
              // 스냅 애니메이션 설정
              _snapAnimation = Tween<Offset>(
                begin: _position,
                end: targetPosition,
              ).animate(CurvedAnimation(
                parent: _snapController,
                curve: Curves.easeOutCubic,
              ));
              
              _snapController.forward().then((_) {
                setState(() {
                  _position = targetPosition;
                  _isOnLeft = newIsOnLeft;
                });
                _snapController.reset();
              });
            },
            child: Transform.translate(
              offset: Offset(0, _isDragging ? 0 : _floatAnimation.value),
              child: Transform.scale(
                scale: _isDragging ? 1.0 : _pulseAnimation.value,
                child: Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: hasUrgentSchedules 
                            ? Colors.red.withOpacity(0.4)
                            : Colors.purple.withOpacity(0.4),
                        spreadRadius: 2,
                        blurRadius: 10,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(35),
                      onTap: () => _showAIChatDialog(context),
                      child: Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: LinearGradient(
                            colors: hasUrgentSchedules
                                ? [Colors.red.shade400, Colors.red.shade600]
                                : [Colors.purple.shade400, Colors.purple.shade600],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                        ),
                        child: Stack(
                          children: [
                            // AI 서클 (uiverse.io 스타일 적용)
                            Center(
                              child: Container(
                                width: 65,
                                height: 65,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  gradient: LinearGradient(
                                    colors: hasUrgentSchedules
                                        ? [Color(0xFFFF6B6B), Color(0xFFEE5A52)]
                                        : [Color(0xFF667eea), Color(0xFF764ba2)],
                                    begin: Alignment.topLeft,
                                    end: Alignment.bottomRight,
                                  ),
                                  boxShadow: [
                                    // 외부 그림자
                                    BoxShadow(
                                      color: (hasUrgentSchedules ? Color(0xFFFF6B6B) : Color(0xFF667eea)).withOpacity(0.4),
                                      blurRadius: 20,
                                      offset: const Offset(0, 8),
                                    ),
                                    // 내부 그림자
                                    BoxShadow(
                                      color: Colors.white.withOpacity(0.2),
                                      blurRadius: 1,
                                      offset: const Offset(0, 1),
                                    ),
                                  ],
                                ),
                                child: Center(
                                  child: Icon(
                                    hasUrgentSchedules ? Icons.warning_rounded : Icons.psychology_rounded,
                                    color: Colors.white,
                                    size: 32,
                                  ),
                                ),
                              ),
                            ),
                            // 긴급 알림 배지
                            if (hasUrgentSchedules)
                              Positioned(
                                top: 5,
                                right: 5,
                                child: Container(
                                  width: 20,
                                  height: 20,
                                  decoration: BoxDecoration(
                                    color: Colors.red,
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: Colors.white,
                                      width: 2,
                                    ),
                                  ),
                                  child: Center(
                                    child: Text(
                                      '${urgentSchedules.length}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            // 음성 대화 표시 아이콘
                            Positioned(
                              bottom: 5,
                              right: 5,
                              child: Container(
                                width: 16,
                                height: 16,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: Colors.purple.shade300,
                                    width: 1,
                                  ),
                                ),
                                child: Icon(
                                  Icons.mic,
                                  size: 10,
                                  color: Colors.purple.shade600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  void _showAIChatDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (context) => const GlobalAIChatDialog(),
    );
  }

}