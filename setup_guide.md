# Daily AI Agent 설정 가이드

## 📋 개요
Daily AI Agent는 매일 오전 6시에 날씨와 증시 정보를 수집하여 AI가 분석한 보고서를 생성하는 자동화 시스템입니다.

## 🛠️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`env_example.txt` 파일을 참고하여 `.env` 파일을 생성하고 다음 API 키를 설정하세요:

#### 필수 API 키:
- **GEMINI_API_KEY**: Google Gemini AI API 키
  - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료로 발급 가능
  
- **OPENWEATHER_API_KEY**: OpenWeatherMap API 키
  - [OpenWeatherMap](https://openweathermap.org/api)에서 무료로 발급 가능

#### 선택 사항 (이메일 알림):
- **EMAIL_USER**: Gmail 주소
- **EMAIL_PASSWORD**: Gmail 앱 비밀번호
- **EMAIL_RECIPIENT**: 보고서를 받을 이메일 주소

### 3. .env 파일 예시
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
OPENWEATHER_API_KEY=your_actual_openweather_api_key_here
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@gmail.com
```

## 🔑 API 키 발급 방법

### Google Gemini API 키
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키를 복사하여 `.env` 파일에 입력

### OpenWeatherMap API 키
1. [OpenWeatherMap](https://openweathermap.org/api) 접속
2. 회원가입 또는 로그인
3. "API Keys" 메뉴에서 키 생성
4. 생성된 키를 복사하여 `.env` 파일에 입력

### Gmail 앱 비밀번호 (이메일 알림용)
1. Google 계정의 2단계 인증 활성화
2. [앱 비밀번호 생성](https://myaccount.google.com/apppasswords)
3. "메일" 앱 선택 후 비밀번호 생성
4. 생성된 16자리 비밀번호를 `.env` 파일에 입력

## 🚀 실행 방법

### 테스트 실행
```bash
python test_agent.py
```
모든 서비스가 정상 작동하는지 확인할 수 있습니다.

### 실제 실행
```bash
python main.py
```
매일 오전 6시에 자동으로 보고서를 생성합니다.

### 즉시 보고서 생성 (테스트용)
`main.py` 파일의 162번째 줄 주석을 해제하면 즉시 보고서를 생성할 수 있습니다:
```python
# 즉시 테스트 실행 (선택사항)
self.run_daily_report()  # 이 줄의 주석을 해제
```

## 📁 프로젝트 구조
```
daily-ai-agent/
├── main.py                    # 메인 실행 파일
├── test_agent.py             # 테스트 스크립트
├── requirements.txt          # 의존성 목록
├── env_example.txt          # 환경 변수 예시
├── setup_guide.md           # 설정 가이드
├── services/                # 서비스 모듈들
│   ├── __init__.py
│   ├── weather_service.py   # 날씨 정보 수집
│   ├── stock_service.py     # 증시 정보 수집
│   ├── gemini_service.py    # AI 보고서 생성
│   └── notification_service.py # 알림 전송
└── reports/                 # 생성된 보고서 저장 (자동 생성)
```

## ⚠️ 주의사항
1. API 키는 절대 공개하지 마세요
2. `.env` 파일은 Git에 커밋하지 마세요
3. 무료 API의 일일 사용량 제한을 확인하세요
4. 시스템이 24시간 실행되어야 스케줄링이 작동합니다

## 🔧 문제 해결
- API 키 오류: `.env` 파일의 키 값을 다시 확인하세요
- 네트워크 오류: 인터넷 연결을 확인하세요
- 이메일 전송 실패: Gmail 2단계 인증과 앱 비밀번호를 확인하세요
- 증시 데이터 오류: 주말이나 휴장일에는 데이터가 제한될 수 있습니다
