#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import json
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('http_lecture_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HTTPLectureExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """HTTP 세션 설정"""
        # User-Agent 설정 (봇 감지 방지)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def login_to_learnus(self, username, password):
        """LearnUs 로그인 (HTTP Request 방식)"""
        try:
            logger.info("🔐 LearnUs 로그인 시도...")
            
            # 1단계: 메인 페이지 접속
            main_url = "https://ys.learnus.org/"
            response = self.session.get(main_url)
            logger.info(f"메인 페이지 응답: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"메인 페이지 접속 실패: {response.status_code}")
                return False
            
            # 2단계: 로그인 링크 찾기
            soup = BeautifulSoup(response.text, 'html.parser')
            login_link = soup.find('a', href=lambda x: x and 'login' in x.lower())
            
            if not login_link:
                # 직접 로그인 페이지 시도
                login_url = "https://ys.learnus.org/login/index.php"
            else:
                login_url = login_link.get('href')
                if not login_url.startswith('http'):
                    login_url = "https://ys.learnus.org" + login_url
            
            logger.info(f"로그인 URL: {login_url}")
            
            # 3단계: 로그인 페이지 접속
            response = self.session.get(login_url)
            logger.info(f"로그인 페이지 응답: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"로그인 페이지 접속 실패: {response.status_code}")
                return False
            
            # 4단계: 로그인 폼 데이터 추출
            soup = BeautifulSoup(response.text, 'html.parser')
            login_form = soup.find('form', {'id': 'login'}) or soup.find('form')
            
            if not login_form:
                logger.error("로그인 폼을 찾을 수 없습니다")
                logger.info("페이지 내용 일부:")
                logger.info(response.text[:500])
                return False
            
            # 폼 데이터 수집
            form_data = {}
            for input_tag in login_form.find_all('input'):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                input_type = input_tag.get('type', 'text')
                
                if name and input_type != 'submit':
                    form_data[name] = value
            
            # 로그인 정보 추가
            form_data['username'] = username
            form_data['password'] = password
            
            logger.info(f"폼 데이터: {list(form_data.keys())}")
            
            # 5단계: 로그인 요청
            action_url = login_form.get('action', login_url)
            if not action_url.startswith('http'):
                action_url = "https://ys.learnus.org" + action_url
            
            login_response = self.session.post(action_url, data=form_data, allow_redirects=True)
            logger.info(f"로그인 응답: {login_response.status_code}")
            logger.info(f"리다이렉트 URL: {login_response.url}")
            
            # 6단계: 로그인 성공 확인
            if "dashboard" in login_response.url or "main" in login_response.url or "course" in login_response.url:
                logger.info("✅ 로그인 성공!")
                return True
            elif "login" in login_response.url:
                logger.warning("⚠️ 로그인 실패 - 로그인 페이지로 리다이렉트됨")
                return False
            else:
                # 응답 내용 확인
                if "logout" in login_response.text.lower() or "dashboard" in login_response.text.lower():
                    logger.info("✅ 로그인 성공! (내용 확인)")
                    return True
                else:
                    logger.warning("⚠️ 로그인 상태 불명확")
                    return False
                
        except Exception as e:
            logger.error(f"❌ 로그인 오류: {e}")
            return False
    
    def get_course_list(self):
        """과목 목록 가져오기"""
        try:
            logger.info("📚 과목 목록 수집 중...")
            
            # 메인 페이지에서 과목 목록 가져오기
            main_url = "https://ys.learnus.org/"
            response = self.session.get(main_url)
            
            if response.status_code != 200:
                logger.error(f"메인 페이지 접속 실패: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 과목 링크 찾기
            course_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/course/view.php?id=' in href:
                    course_name = link.get_text().strip()
                    if course_name and len(course_name) > 3:
                        course_links.append({
                            'name': course_name,
                            'url': href if href.startswith('http') else f"https://ys.learnus.org{href}",
                            'course_id': re.search(r'id=(\d+)', href).group(1) if re.search(r'id=(\d+)', href) else None
                        })
            
            logger.info(f"📚 {len(course_links)}개 과목 발견")
            return course_links
            
        except Exception as e:
            logger.error(f"❌ 과목 목록 수집 오류: {e}")
            return []
    
    def get_course_content(self, course_url):
        """과목 페이지 내용 가져오기"""
        try:
            response = self.session.get(course_url)
            
            if response.status_code != 200:
                logger.warning(f"과목 페이지 접속 실패: {response.status_code}")
                return None
            
            return BeautifulSoup(response.text, 'html.parser')
            
        except Exception as e:
            logger.error(f"❌ 과목 페이지 로드 오류: {e}")
            return None
    
    def find_this_week_section(self, soup, course_name):
        """이번주 강의 섹션 찾기"""
        try:
            # 섹션 찾기
            sections = soup.find_all('li', class_='section main')
            logger.info(f"   {course_name}: {len(sections)}개 섹션 발견")
            
            for idx, section in enumerate(sections):
                try:
                    # 섹션 제목 확인
                    section_title = section.find('h3') or section.find('div', class_='section-title')
                    if section_title:
                        title_text = section_title.get_text().strip().lower()
                        logger.info(f"   섹션 {idx+1}: {title_text}")
                        
                        # 이번주 강의 키워드 확인
                        if any(keyword in title_text for keyword in [
                            "이번주 강의", "이번주", "current week", "week", "주차", "이번 주"
                        ]):
                            if "개요" not in title_text and "overview" not in title_text:
                                logger.info(f"   ✅ '이번주 강의' 섹션 발견: {title_text}")
                                return section
                    
                    # 섹션 전체 텍스트로도 확인
                    section_text = section.get_text().lower()
                    if any(keyword in section_text for keyword in [
                        "이번주 강의", "이번주", "current week", "week", "주차"
                    ]):
                        if "개요" not in section_text and "overview" not in section_text:
                            logger.info(f"   ✅ '이번주 강의' 섹션 발견 (텍스트)")
                            return section
                            
                except Exception as e:
                    logger.debug(f"   섹션 {idx+1} 분석 실패: {e}")
                    continue
            
            # 키워드로 찾지 못했으면 두 번째 섹션 시도
            if len(sections) > 1:
                logger.info(f"   🔍 키워드로 찾지 못함, 두 번째 섹션 사용")
                return sections[1]
            
            # 마지막 수단: 첫 번째 섹션
            if sections:
                logger.info(f"   🔍 첫 번째 섹션 사용")
                return sections[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 섹션 찾기 오류: {e}")
            return None
    
    def extract_activities_from_section(self, section, course_name):
        """섹션에서 활동 추출"""
        activities = []
        
        try:
            # 모든 링크 찾기
            links = section.find_all('a', href=True)
            logger.info(f"   {len(links)}개 링크 발견")
            
            for link in links:
                try:
                    activity_name = link.get_text().strip()
                    activity_url = link.get('href', '')
                    
                    if not activity_name or not activity_url:
                        continue
                    
                    # 의미없는 링크 제외
                    if any(skip in activity_name.lower() for skip in [
                        "더보기", "more", "자세히", "detail", "보기", "view"
                    ]):
                        continue
                    
                    # URL 완성
                    if not activity_url.startswith('http'):
                        activity_url = f"https://ys.learnus.org{activity_url}"
                    
                    # 활동 타입 판별
                    activity_type = "기타"
                    if "mod/assign/" in activity_url:
                        activity_type = "과제"
                    elif "mod/vod/" in activity_url:
                        activity_type = "동영상"
                    elif "mod/resource/" in activity_url or "mod/ubfile/" in activity_url:
                        activity_type = "PDF 자료"
                    elif "mod/ubboard/" in activity_url:
                        activity_type = "게시판"
                    elif "mod/quiz/" in activity_url:
                        activity_type = "퀴즈"
                    
                    activity_info = {
                        "course": course_name,
                        "activity": activity_name,
                        "type": activity_type,
                        "url": activity_url
                    }
                    
                    activities.append(activity_info)
                    logger.info(f"     ✅ {activity_name} ({activity_type})")
                    
                except Exception as e:
                    logger.debug(f"     링크 처리 실패: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"   활동 추출 실패: {e}")
        
        return activities
    
    def extract_all_lectures(self):
        """모든 과목의 이번주 강의 추출"""
        try:
            logger.info("🔍 이번주 강의 정보 수집 시작...")
            
            # 과목 목록 가져오기
            courses = self.get_course_list()
            if not courses:
                logger.warning("과목 목록을 가져올 수 없습니다")
                return []
            
            all_lectures = []
            
            for i, course in enumerate(courses[:5]):  # 처음 5개 과목만 테스트
                try:
                    course_name = course['name']
                    course_url = course['url']
                    
                    logger.info(f"\n📖 과목 {i+1}: {course_name}")
                    
                    # 과목 페이지 가져오기
                    soup = self.get_course_content(course_url)
                    if not soup:
                        logger.warning(f"   ⚠️ {course_name} 페이지 로드 실패")
                        continue
                    
                    # 이번주 강의 섹션 찾기
                    this_week_section = self.find_this_week_section(soup, course_name)
                    
                    if this_week_section:
                        # 섹션에서 활동 추출
                        course_activities = self.extract_activities_from_section(this_week_section, course_name)
                        
                        if course_activities:
                            all_lectures.extend(course_activities)
                            logger.info(f"   📚 {len(course_activities)}개 활동 발견")
                        else:
                            logger.info(f"   📭 활동 없음")
                    else:
                        logger.info(f"   📭 '이번주 강의' 섹션 없음")
                    
                    # 요청 간격 조절 (서버 부하 방지)
                    time.sleep(1)
                        
                except Exception as e:
                    logger.warning(f"   ❌ 과목 {i+1} 처리 실패: {e}")
                    continue
            
            return all_lectures
            
        except Exception as e:
            logger.error(f"❌ 강의 추출 오류: {e}")
            return []
    
    def save_to_file(self, lectures):
        """결과를 파일로 저장"""
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 이번주 강의 활동 목록 (HTTP Request 방식)\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 활동 수: {len(lectures)}개\n\n")
                
                if lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, activities in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 40 + "\n")
                        
                        for activity in activities:
                            f.write(f"  • {activity['activity']} ({activity['type']})\n")
                            f.write(f"    URL: {activity['url']}\n\n")
                        
                        f.write("\n")
                else:
                    f.write("❌ 수집된 이번주 강의 활동이 없습니다.\n")
                    f.write("🔍 디버깅 정보:\n")
                    f.write("- 로그인 상태를 확인해보세요.\n")
                    f.write("- 로그 파일(http_lecture_extractor.log)을 확인해보세요.\n")
                
            logger.info("💾 assignment.txt 파일에 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            return False
    
    def run(self, username=None, password=None):
        """메인 실행 함수"""
        print("🚀 HTTP Request 방식 이번주 강의 추출기")
        print("=" * 60)
        
        # 로그인 정보 입력
        if not username or not password:
            print("📝 자동화 테스트를 위한 정보 입력")
            print("------------------------------")
            university_input = input("대학교 (예: 연세대학교) 또는 9887: ").strip()
            
            if university_input == "9887":
                # 개발자 모드: 자동 설정
                username = "2024248012"
                password = "cjm9887@"
                print("🚀 개발자 모드: 연세대학교 자동 설정!")
                print(f"   학번: {username}")
                print(f"   비밀번호: {password}")
            else:
                username = input("아이디/학번: ").strip()
                password = input("비밀번호: ").strip()
        
        if not username or not password:
            print("❌ 로그인 정보가 누락되었습니다")
            return False
        
        try:
            # 로그인
            if not self.login_to_learnus(username, password):
                print("❌ 로그인 실패")
                return False
            
            # 이번주 강의 정보 수집
            lectures = self.extract_all_lectures()
            
            # 결과 저장
            if self.save_to_file(lectures):
                print(f"\n✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                print("📄 assignment.txt 파일을 확인하세요.")
                print("⚡ HTTP Request 방식으로 훨씬 빠르게 처리되었습니다!")
            else:
                print("\n❌ 파일 저장 실패")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 실행 오류: {e}")
            return False

def main():
    extractor = HTTPLectureExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
