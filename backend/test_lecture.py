#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def main():
    print("🚀 이번주 강의 추출 테스트")
    print("=" * 50)
    
    # Chrome 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome 드라이버 초기화 완료")
    except Exception as e:
        print(f"❌ Chrome 드라이버 초기화 실패: {e}")
        return
    
    try:
        # LearnUs 메인 페이지 접속
        print("🌐 LearnUs 메인 페이지 접속 중...")
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        # 페이지 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # h3 태그로 과목 찾기
        course_elements = soup.find_all('h3')
        print(f"📚 {len(course_elements)}개 과목 발견")
        
        all_lectures = []
        
        for i, course_element in enumerate(course_elements[:3]):  # 처음 3개 과목만 테스트
            try:
                course_name = course_element.get_text().strip()
                if not course_name or len(course_name) < 3:
                    continue
                
                print(f"\n📖 과목 {i+1}: {course_name}")
                
                # 과목 클릭
                try:
                    selenium_course_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                    selenium_course_element.click()
                    time.sleep(2)
                    print(f"   ✅ 과목 페이지 진입")
                except Exception as e:
                    print(f"   ⚠️ 과목 클릭 실패: {e}")
                    continue
                
                # 현재 페이지 분석
                current_page_source = driver.page_source
                current_soup = BeautifulSoup(current_page_source, 'html.parser')
                
                # 모든 섹션 찾기
                sections = current_soup.find_all('li', class_='section main')
                print(f"   📋 {len(sections)}개 섹션 발견")
                
                # 각 섹션 확인
                for idx, section in enumerate(sections):
                    section_text = section.get_text().lower()
                    print(f"   섹션 {idx+1}: {section_text[:50]}...")
                    
                    # "이번주 강의" 키워드가 있는 섹션 찾기
                    if any(keyword in section_text for keyword in [
                        "이번주 강의", "이번주", "current week", "week", "주차"
                    ]):
                        if "개요" not in section_text and "overview" not in section_text:
                            print(f"   ✅ '이번주 강의' 섹션 발견!")
                            
                            # 섹션 내의 링크들 찾기
                            links = section.find_all('a', href=True)
                            print(f"   🔗 {len(links)}개 링크 발견")
                            
                            for link in links:
                                activity_name = link.get_text().strip()
                                activity_url = link.get('href', '')
                                if activity_name and activity_url:
                                    print(f"     • {activity_name}")
                                    all_lectures.append({
                                        "course": course_name,
                                        "activity": activity_name,
                                        "url": activity_url
                                    })
                            break
                
                # 메인 페이지로 돌아가기
                try:
                    driver.back()
                    time.sleep(1)
                except:
                    driver.get("https://ys.learnus.org/")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"   ❌ 과목 {i+1} 처리 실패: {e}")
                continue
        
        # 결과 저장
        print(f"\n📊 총 {len(all_lectures)}개 활동 수집 완료")
        
        with open('assignment.txt', 'w', encoding='utf-8') as f:
            f.write("📚 이번주 강의 활동 목록\n")
            f.write("=" * 50 + "\n\n")
            
            if all_lectures:
                for lecture in all_lectures:
                    f.write(f"📖 {lecture['course']}\n")
                    f.write(f"  • {lecture['activity']}\n")
                    f.write(f"    URL: {lecture['url']}\n\n")
            else:
                f.write("❌ 수집된 활동이 없습니다.\n")
        
        print("💾 assignment.txt 파일에 저장 완료")
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
    finally:
        try:
            driver.quit()
            print("🔚 드라이버 종료")
        except:
            pass

if __name__ == "__main__":
    main()

































