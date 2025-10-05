"""
학사일정 파서 서비스
1학기와 2학기 학사일정을 통합하여 관리
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ScheduleParser:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.schedule_data = {}
        self._load_schedule_data()
    
    def _load_schedule_data(self):
        """학사일정 데이터 로드"""
        try:
            # 1학기와 2학기 학사일정 모두 로드
            schedule_files = [
                "yonsei_schedule_2025_1st_semester.json",
                "yonsei_schedule_2025_2nd_semester.json"
            ]
            
            all_schedules = []
            for filename in schedule_files:
                schedule_file = self.data_dir / filename
                if schedule_file.exists():
                    with open(schedule_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_schedules.extend(data.get('schedule', []))
                    logger.info(f"{filename} 학사일정 데이터 로드 완료")
                else:
                    logger.warning(f"{filename} 학사일정 데이터 파일을 찾을 수 없습니다")
            
            # 통합된 학사일정 데이터 구성
            self.schedule_data = {
                'university': '연세대학교',
                'semester': '2025-1학기, 2025-2학기',
                'schedule': all_schedules
            }
            
            logger.info(f"총 {len(all_schedules)}개 월별 학사일정 로드 완료")
            
        except Exception as e:
            logger.error(f"학사일정 데이터 로드 오류: {e}")
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """모든 학사일정 반환"""
        all_schedules = []
        
        try:
            for month_data in self.schedule_data.get('schedule', []):
                month = month_data.get('month', '')
                month_en = month_data.get('month_en', '')
                
                for event in month_data.get('events', []):
                    schedule = {
                        'id': f"yonsei_2nd_{len(all_schedules)}",
                        'title': event.get('event', ''),
                        'description': f"{month} {event.get('date', '')} - {event.get('event', '')}",
                        'date': self._parse_schedule_date(event.get('date', ''), month),
                        'month': month,
                        'month_en': month_en,
                        'type': event.get('type', ''),
                        'priority': event.get('priority', 'medium'),
                        'university': '연세대학교',
                        'semester': '2025-2학기',
                        'is_important': self._is_important_schedule(event.get('event', '')),
                        'tags': self._generate_schedule_tags(event.get('event', ''), event.get('type', '')),
                    }
                    all_schedules.append(schedule)
            
            logger.info(f"2학기 학사일정 {len(all_schedules)}개 로드 완료")
            return all_schedules
            
        except Exception as e:
            logger.error(f"학사일정 파싱 오류: {e}")
            return []
    
    def get_upcoming_schedules(self, days: int = 30) -> List[Dict[str, Any]]:
        """다가오는 학사일정 반환"""
        all_schedules = self.get_all_schedules()
        upcoming_schedules = []
        
        try:
            current_date = datetime.now()
            target_date = current_date + timedelta(days=days)
            
            for schedule in all_schedules:
                schedule_date = schedule.get('date')
                if schedule_date and current_date <= schedule_date <= target_date:
                    upcoming_schedules.append(schedule)
            
            # 날짜순으로 정렬
            upcoming_schedules.sort(key=lambda x: x.get('date', datetime.now()))
            
            logger.info(f"다가오는 학사일정 {len(upcoming_schedules)}개 반환")
            return upcoming_schedules
            
        except Exception as e:
            logger.error(f"다가오는 학사일정 조회 오류: {e}")
            return []
    
    def get_important_schedules(self) -> List[Dict[str, Any]]:
        """중요한 학사일정 반환"""
        all_schedules = self.get_all_schedules()
        important_schedules = []
        
        try:
            for schedule in all_schedules:
                if schedule.get('is_important', False):
                    important_schedules.append(schedule)
            
            logger.info(f"중요 학사일정 {len(important_schedules)}개 반환")
            return important_schedules
            
        except Exception as e:
            logger.error(f"중요 학사일정 조회 오류: {e}")
            return []
    
    def get_schedules_by_type(self, schedule_type: str) -> List[Dict[str, Any]]:
        """타입별 학사일정 반환"""
        all_schedules = self.get_all_schedules()
        filtered_schedules = []
        
        try:
            for schedule in all_schedules:
                if schedule.get('type', '') == schedule_type:
                    filtered_schedules.append(schedule)
            
            logger.info(f"{schedule_type} 학사일정 {len(filtered_schedules)}개 반환")
            return filtered_schedules
            
        except Exception as e:
            logger.error(f"타입별 학사일정 조회 오류: {e}")
            return []
    
    def _parse_schedule_date(self, date_str: str, month: str) -> datetime:
        """학사일정 날짜 파싱"""
        try:
            current_year = 2025
            
            # 월 번호 매핑
            month_mapping = {
                '8월': 8, '9월': 9, '10월': 10, '11월': 11, '12월': 12,
                '1월': 1, '2월': 2, '3월': 3, '4월': 4, '5월': 5, '6월': 6, '7월': 7
            }
            
            month_num = month_mapping.get(month, 1)
            
            # 날짜 문자열에서 일 추출
            if '~' in date_str:
                # 기간인 경우 시작일 사용
                start_date = date_str.split('~')[0].strip()
                day_str = start_date.split('(')[0].strip()
            else:
                day_str = date_str.split('(')[0].strip()
            
            day = int(day_str)
            
            # 2026년 1-2월은 2026년으로 처리
            if month_num <= 2:
                year = 2026
            else:
                year = current_year
            
            return datetime(year, month_num, day)
            
        except Exception as e:
            logger.error(f"날짜 파싱 오류: {e}")
            return datetime.now()
    
    def _is_important_schedule(self, event_name: str) -> bool:
        """중요한 학사일정 여부 판단"""
        important_keywords = [
            '수강신청', '등록', '개강', '종강', '시험', '성적', '졸업', '휴학', '복학',
            '추가등록', '수강철회', '중간시험', '학기말', '방학', '계절제'
        ]
        
        return any(keyword in event_name for keyword in important_keywords)
    
    def _generate_schedule_tags(self, event_name: str, event_type: str) -> List[str]:
        """학사일정 태그 생성"""
        tags = []
        
        # 이벤트 타입 기반 태그
        type_tags = {
            '수강신청': ['수강신청', '등록'],
            '등록': ['등록', '수강신청'],
            '시험': ['시험', '성적'],
            '휴학': ['휴학', '복학'],
            '복학': ['복학', '휴학'],
            '졸업': ['졸업', '학위'],
            '휴일': ['휴일', '공휴일'],
            '전과': ['전과', '전공'],
            '성적': ['성적', '시험'],
        }
        
        if event_type in type_tags:
            tags.extend(type_tags[event_type])
        
        # 이벤트명 기반 태그
        if '수강신청' in event_name:
            tags.append('수강신청')
        if '등록' in event_name:
            tags.append('등록')
        if '시험' in event_name:
            tags.append('시험')
        if '휴학' in event_name:
            tags.append('휴학')
        if '복학' in event_name:
            tags.append('복학')
        if '졸업' in event_name:
            tags.append('졸업')
        
        # 기본 태그
        if not tags:
            tags.append('학사일정')
        
        return list(set(tags))  # 중복 제거
