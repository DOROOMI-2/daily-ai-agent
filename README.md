# 🤖 Daily AI Agent

매일 오전 6시에 날씨와 증시 정보를 수집하여 Google Gemini AI가 분석한 일일 보고서를 자동으로 생성하는 시스템입니다.

## ✨ 주요 기능

- 🌤️ **날씨 정보 수집**: 김포시와 강남구 테헤란로의 실시간 날씨 정보
- 📈 **증시 정보 수집**: 한국(KOSPI, KOSDAQ) 및 미국(S&P 500, NASDAQ, Dow Jones) 증시 현황
- 🤖 **AI 보고서 생성**: Google Gemini AI가 수집된 데이터를 분석하여 친근한 일일 보고서 작성
- 📧 **자동 알림**: 텔레그램, 이메일 및 콘솔을 통한 보고서 전송
- ⏰ **스케줄링**: 매일 오전 6시 자동 실행

## 🛠️ 시스템 구조

```
daily-ai-agent/
├── main.py                    # 메인 실행 파일
├── test_agent.py             # 테스트 스크립트
├── requirements.txt          # 의존성 목록
├── env_example.txt          # 환경 변수 예시
├── setup_guide.md           # 상세 설정 가이드
├── services/                # 핵심 서비스 모듈들
│   ├── weather_service.py   # 날씨 정보 수집
│   ├── stock_service.py     # 증시 정보 수집
│   ├── gemini_service.py    # Google Gemini AI 연동
│   └── notification_service.py # 알림 전송
└── reports/                 # 생성된 보고서 저장 폴더
```

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 필요한 API 키를 설정:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 3. 테스트 실행
```bash
python test_agent.py
```

### 4. 메인 시스템 실행
```bash
python main.py
```

## 🔑 필수 API 키

### Google Gemini API (필수)
- [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료 발급
- 일일 보고서 생성에 사용

### OpenWeatherMap API (필수)
- [OpenWeatherMap](https://openweathermap.org/api)에서 무료 발급
- 날씨 정보 수집에 사용

### 이메일 설정 (선택사항)
- Gmail 앱 비밀번호 설정으로 이메일 알림 활성화

### 텔레그램 설정 (선택사항)
- 텔레그램 봇 토큰과 Chat ID 설정으로 텔레그램 알림 활성화
- 자세한 설정 방법은 [telegram_setup_guide.md](telegram_setup_guide.md) 참고

## 📊 보고서 예시

```
# 🌅 오늘의 일일 브리핑

## 📊 날씨 정보
📍 김포시: 18°C (선선한), 맑음
📍 강남구 테헤란로: 19°C (선선한), 구름 조금

- 외출 시 가벼운 겉옷 준비 권장
- 전반적으로 좋은 날씨로 외출하기 좋은 날

## 📈 증시 동향
📈 KOSPI: 2,589 (+15, +0.58%)
📈 KOSDAQ: 743 (+8, +1.08%)
📉 S&P 500: 4,198 (-12, -0.29%)

- 한국 증시는 소폭 상승
- 미국 증시는 혼조세

## 💡 오늘의 추천사항
- 선선한 날씨를 활용한 야외 활동 추천
- 한국 증시 상승세 지속 관찰 필요
- 즐거운 하루 되세요! 😊
```

## 🔧 주요 기능

### WeatherService
- OpenWeatherMap API를 통한 실시간 날씨 정보
- 도시명, 위치, 좌표를 통한 다양한 조회 방식
- 온도, 습도, 바람, 가시거리 등 상세 정보 제공

### StockService
- yfinance를 활용한 실시간 증시 데이터
- 한국/미국 주요 지수 모니터링
- 전일 대비 변동률 및 거래량 정보

### GeminiService
- Google Gemini AI를 활용한 지능형 보고서 생성
- 수집된 데이터의 맥락적 분석
- 친근하고 실용적인 조언 제공

### NotificationService
- 콘솔, 이메일, 텔레그램을 통한 다중 알림 지원
- HTML 형식의 아름다운 이메일 템플릿
- 텔레그램 메시지 자동 분할 (4096자 제한)
- 오류 발생 시 자동 알림

## ⚠️ 주의사항

- API 키는 절대 공개하지 마세요
- `.env` 파일은 Git에 커밋하지 마세요
- 무료 API의 일일 사용량 제한을 확인하세요
- 24시간 실행을 위해서는 서버나 항상 켜진 컴퓨터가 필요합니다

## 📞 문제 해결

자세한 설정 방법과 문제 해결은 [setup_guide.md](setup_guide.md)를 참고하세요.
