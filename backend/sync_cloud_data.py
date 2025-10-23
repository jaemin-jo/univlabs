#!/usr/bin/env python3
"""
클라우드 서버에서 최신 과제 데이터를 로컬 assignment.txt 파일로 동기화하는 스크립트
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudDataSyncer:
    def __init__(self, cloud_server_url: str = "https://learnus-backend-986202706020.asia-northeast3.run.app"):
        self.cloud_server_url = cloud_server_url
        self.assignment_file = "assignment.txt"
    
    def fetch_cloud_data(self) -> Optional[Dict]:
        """클라우드 서버에서 과제 데이터 가져오기"""
        try:
            logger.info(f"🔍 클라우드 서버에서 데이터 가져오는 중: {self.cloud_server_url}")
            
            response = requests.get(
                f"{self.cloud_server_url}/assignments",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 클라우드 데이터 가져오기 성공: {data.get('total_count', 0)}개 과제")
                return data
            else:
                logger.error(f"❌ 클라우드 서버 응답 오류: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ 클라우드 서버 연결 시간 초과")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ 클라우드 서버 연결 실패")
            return None
        except Exception as e:
            logger.error(f"❌ 클라우드 데이터 가져오기 실패: {e}")
            return None
    
    def format_assignment_data(self, assignments: List[Dict]) -> str:
        """과제 데이터를 assignment.txt 형식으로 포맷팅"""
        if not assignments:
            return "📭 이번주 과제가 없습니다."
        
        content = "📚 이번주 해야 할 과제 목록\n"
        content += "=" * 50 + "\n\n"
        
        # 과목별로 그룹화
        course_groups = {}
        for assignment in assignments:
            course = assignment.get('course', '알 수 없는 과목')
            if course not in course_groups:
                course_groups[course] = []
            course_groups[course].append(assignment)
        
        # 과목별로 출력
        for course, activities in course_groups.items():
            content += f"📖 {course}\n"
            content += "-" * 40 + "\n"
            
            for activity in activities:
                activity_name = activity.get('activity', '알 수 없는 활동')
                status = activity.get('status', '❓ 상태 불명')
                activity_type = activity.get('type', '과제')
                url = activity.get('url', '')
                
                content += f"  • {activity_name} ({activity_type})\n"
                content += f"    상태: {status}\n"
                if url:
                    content += f"    URL: {url}\n"
                content += "\n"
            
            content += "\n"
        
        return content
    
    def save_to_local_file(self, cloud_data: Dict) -> bool:
        """클라우드 데이터를 로컬 assignment.txt 파일에 저장"""
        try:
            assignments = cloud_data.get('assignments', [])
            total_count = cloud_data.get('total_count', 0)
            incomplete_count = cloud_data.get('incomplete_count', 0)
            last_update = cloud_data.get('last_update')
            
            # 파일 내용 생성
            content = f"=== LearnUs 과제 정보 업데이트 ===\n"
            content += f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"클라우드 동기화 시간: {last_update or '알 수 없음'}\n\n"
            
            if assignments:
                content += f"📊 통계: 총 {total_count}개 과제, 미완료 {incomplete_count}개\n\n"
                content += self.format_assignment_data(assignments)
            else:
                content += "📭 이번주 과제가 없습니다.\n"
            
            # 파일에 저장
            with open(self.assignment_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ 로컬 파일 업데이트 완료: {self.assignment_file}")
            logger.info(f"   총 과제: {total_count}개, 미완료: {incomplete_count}개")
            return True
            
        except Exception as e:
            logger.error(f"❌ 로컬 파일 저장 실패: {e}")
            return False
    
    def sync(self) -> bool:
        """클라우드 데이터를 로컬로 동기화"""
        logger.info("🔄 클라우드 데이터 동기화 시작...")
        
        # 클라우드에서 데이터 가져오기
        cloud_data = self.fetch_cloud_data()
        if not cloud_data:
            logger.error("❌ 클라우드 데이터 가져오기 실패")
            return False
        
        # 로컬 파일에 저장
        success = self.save_to_local_file(cloud_data)
        if success:
            logger.info("🎉 클라우드 데이터 동기화 완료!")
        else:
            logger.error("❌ 클라우드 데이터 동기화 실패")
        
        return success
    
    def check_local_file(self) -> Dict:
        """로컬 assignment.txt 파일 상태 확인"""
        try:
            if not os.path.exists(self.assignment_file):
                return {
                    'exists': False,
                    'size': 0,
                    'last_modified': None,
                    'content_preview': None
                }
            
            stat = os.stat(self.assignment_file)
            with open(self.assignment_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'exists': True,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'content_preview': content[:200] + "..." if len(content) > 200 else content
            }
        except Exception as e:
            logger.error(f"로컬 파일 확인 실패: {e}")
            return {'exists': False, 'error': str(e)}

def main():
    """메인 실행 함수"""
    print("🔄 LearnUs 클라우드 데이터 동기화 도구")
    print("=" * 50)
    
    syncer = CloudDataSyncer()
    
    # 현재 로컬 파일 상태 확인
    print("\n📁 현재 로컬 파일 상태:")
    local_status = syncer.check_local_file()
    if local_status['exists']:
        print(f"   파일 존재: ✅")
        print(f"   파일 크기: {local_status['size']} bytes")
        print(f"   마지막 수정: {local_status['last_modified']}")
        print(f"   내용 미리보기:")
        print(f"   {local_status['content_preview']}")
    else:
        print(f"   파일 존재: ❌")
        if 'error' in local_status:
            print(f"   오류: {local_status['error']}")
    
    # 클라우드 데이터 동기화
    print("\n🔄 클라우드 데이터 동기화 중...")
    success = syncer.sync()
    
    if success:
        print("\n✅ 동기화 완료!")
        print("이제 Flutter 앱에서 최신 과제 정보를 확인할 수 있습니다.")
    else:
        print("\n❌ 동기화 실패!")
        print("클라우드 서버 연결을 확인해주세요.")

if __name__ == "__main__":
    main()





















