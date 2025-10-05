#!/usr/bin/env python3
"""
연결 테스트 스크립트
"""

import requests
import time

def test_server_connection():
    """서버 연결 테스트"""
    try:
        print("🔍 서버 연결 테스트 시작...")
        
        # 서버가 실행 중인지 확인
        response = requests.get('http://localhost:8000/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ 서버 연결 성공!")
            print(f"응답: {response.json()}")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패: 서버가 실행되지 않았습니다")
        return False
    except Exception as e:
        print(f"❌ 연결 테스트 실패: {e}")
        return False

def test_selenium_automation():
    """Selenium 자동화 테스트"""
    try:
        print("\n🤖 Selenium 자동화 테스트 시작...")
        
        from test_real_automation_hybrid import setup_driver
        
        # 드라이버 설정
        print("   📱 Chrome 드라이버 설정 중...")
        driver = setup_driver()
        
        if driver:
            print("   ✅ 드라이버 설정 성공")
            
            # 간단한 테스트
            print("   🌐 LearnUs 페이지 접속 테스트...")
            driver.get("https://ys.learnus.org/")
            time.sleep(2)
            
            title = driver.title
            print(f"   📄 페이지 제목: {title}")
            
            driver.quit()
            print("   ✅ Selenium 테스트 완료")
            return True
        else:
            print("   ❌ 드라이버 설정 실패")
            return False
            
    except Exception as e:
        print(f"   ❌ Selenium 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 백엔드 연결 및 자동화 테스트")
    print("=" * 50)
    
    # 1. 서버 연결 테스트
    server_ok = test_server_connection()
    
    # 2. Selenium 자동화 테스트
    selenium_ok = test_selenium_automation()
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)
    print(f"서버 연결: {'✅ 성공' if server_ok else '❌ 실패'}")
    print(f"Selenium 자동화: {'✅ 성공' if selenium_ok else '❌ 실패'}")
    
    if not server_ok:
        print("\n🔧 서버 문제 해결 방법:")
        print("1. python backend/simple_server.py 실행")
        print("2. 포트 8000이 사용 중인지 확인")
        print("3. 방화벽 설정 확인")
    
    if not selenium_ok:
        print("\n🔧 Selenium 문제 해결 방법:")
        print("1. Chrome 브라우저 설치 확인")
        print("2. ChromeDriver 버전 확인")
        print("3. 네트워크 연결 확인")
