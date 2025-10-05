#!/usr/bin/env python3
"""
자격증명 테스트 도구
연세대학교 LearnUs 로그인 자격증명을 테스트합니다.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.school_automation import SchoolAutomationService

async def test_credentials():
    """자격증명 테스트"""
    print("🧪 연세대학교 LearnUs 자격증명 테스트")
    print("=" * 50)
    
    # 사용자 입력 받기
    print("📝 로그인 정보를 입력해주세요:")
    university = "연세대학교"
    username = input("아이디 (학번): ").strip()
    password = input("비밀번호: ").strip()
    student_id = input("학번 (확인용): ").strip()
    
    if not username or not password:
        print("❌ 아이디와 비밀번호를 모두 입력해주세요.")
        return
    
    print(f"\n🔐 테스트 시작: {university}")
    print(f"   사용자: {username}")
    print(f"   학번: {student_id}")
    print("-" * 50)
    
    # 자동화 서비스 초기화
    automation_service = SchoolAutomationService()
    
    try:
        # 로그인 테스트
        print("1️⃣ LearnUs 메인 페이지 접속 중...")
        success = await automation_service.login(university, username, password, student_id)
        
        if success:
            print("✅ 로그인 성공!")
            print("2️⃣ 과제 정보 수집 테스트 중...")
            
            # 과제 정보 수집 테스트
            assignments = await automation_service.get_all_assignments()
            print(f"📚 과제 정보 수집 완료: {len(assignments)}개")
            
            if assignments:
                print("\n📋 수집된 과제 목록:")
                for i, assignment in enumerate(assignments[:5], 1):
                    print(f"   {i}. {assignment.title}")
                    print(f"      강의: {assignment.course_name}")
                    print(f"      마감: {assignment.due_date}")
                    print(f"      상태: {assignment.status.value}")
                    print()
            else:
                print("⚠️ 과제 정보가 없습니다.")
                
        else:
            print("❌ 로그인 실패!")
            print("💡 확인사항:")
            print("   - 아이디/비밀번호가 올바른지 확인")
            print("   - 연세대학교 계정이 활성화되어 있는지 확인")
            print("   - LearnUs 사이트 접근이 가능한지 확인")
            
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        print("💡 확인사항:")
        print("   - 인터넷 연결 상태 확인")
        print("   - Chrome 브라우저 설치 확인")
        print("   - 백엔드 서버 실행 상태 확인")
    
    finally:
        # 드라이버 정리
        if automation_service.driver:
            automation_service.driver.quit()
            print("🧹 브라우저 정리 완료")

if __name__ == "__main__":
    print("🚀 연세대학교 LearnUs 자격증명 테스트 도구")
    print("이 도구는 실제 로그인을 시도합니다.")
    print("개인정보 보호를 위해 테스트 후 브라우저를 자동으로 종료합니다.\n")
    
    try:
        asyncio.run(test_credentials())
    except KeyboardInterrupt:
        print("\n⏹️ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    
    print("\n🏁 테스트 완료!")
