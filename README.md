# 뉴스 요약, 실시간 검색어 웹 어플리케이션

## 설명
이 프로젝트는 뉴스 요약과 실시간 검색어 기능을 제공하는 웹 어플리케이션입니다. 유저는 해당 어플리케이션을 통해 검색한 키워드를 뉴스 요약본으로 확인할 수 있고, 실시간 검색어를 확인할 수 있습니다.

## 기능
1. **사용자 인증:**
   - 사용자는 회원가입 및 로그인을 통해 어플리케이션 기능에 접근할 수 있습니다.
   - 비밀번호는 SHA-256 암호화를 사용하여 안전하게 저장됩니다.

2. **뉴스 크롤링:**
   - 어플리케이션은 사용자의 검색 쿼리에 기반하여 네이버 뉴스에서 뉴스 기사를 수집합니다.
   - BeautifulSoup 및 requests 라이브러리를 사용하여 뉴스 기사 내용을 수집합니다.

3. **실시간 검색어:**
   - 어플리케이션은 네이트에서 실시간 검색어를 가져와 사용자에게 현재 핫한 주제에 대한 통찰력을 제공합니다.

4. **뉴스 요약:**
   - 요약 기능은 OpenAI의 GPT-3.5 모델을 사용하여 뉴스 기사의 간결한 요약을 생성합니다.
   - 각 뉴스 기사에 대해 3-4문장의 요약이 제공됩니다.

5. **데이터 처리:**
   - 뉴스 기사는 CSV 형식으로 처리되어 저장됩니다.
   - CSV 파일은 요약 및 추가 분석을 위해 텍스트 파일로 변환됩니다.

6. **웹 인터페이스:**
   - 사용자는 사용자 친화적인 웹 인터페이스를 통해 어플리케이션과 상호작용합니다.
   - 기능에는 뉴스 기사 검색, 요약 확인 및 실시간 검색어 등이 포함됩니다.

7. **데이터베이스 통합:**
   - 사용자 정보는 MySQL 데이터베이스에 저장됩니다.
   - Flask-MySQLDB를 사용하여 Flask 어플리케이션과의 원활한 통합이 이루어집니다.

## 사용된 기술
- Python
- Flask (웹 프레임워크)
- BeautifulSoup (웹 크롤링)
- OpenAI API (텍스트 요약)
- MySQL (데이터베이스)
- Flask-MySQLDB (데이터베이스 통합)
- Passlib (비밀번호 해싱)
- HTML/CSS
- JavaScript

## 실행 방법
1. MySQL 데이터베이스를 설정하고 Flask 어플리케이션에서 연결을 구성합니다.
2. `flask run`을 입력하여 Flask 어플리케이션을 실행합니다.
3. 웹 브라우저에서 `http://localhost:5000`에 접속하여 어플리케이션을 이용합니다.

## 기여자
- 최규원 : 뉴스 크롤링, 실시간 검색어, 뉴스 요약, 데이터 처리, 데이터베이스, 로그인 & 회원가입
- 홍정욱 : TTS(진행 중)

## 라이센스
[라이센스 정보 포함]

## 참고
어플리케이션을 실행하기 전에 적절한 API 키, 데이터베이스 구성 및 권한을 확인하세요.