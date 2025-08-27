# 📱 텔레그램 봇 설정 가이드

Daily AI Agent의 보고서를 텔레그램으로 받기 위한 설정 방법입니다.

## 🤖 1단계: 텔레그램 봇 생성

### BotFather와 대화하기
1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색
2. BotFather와 대화 시작
3. `/newbot` 명령어 입력
4. 봇의 이름 입력 (예: Daily AI Agent)
5. 봇의 사용자명 입력 (예: daily_ai_agent_bot)
   - 반드시 `bot`으로 끝나야 함
   - 다른 사람이 사용 중이면 다른 이름 선택

### 봇 토큰 받기
성공적으로 봇을 생성하면 다음과 같은 메시지를 받습니다:
```
Done! Congratulations on your new bot.
You will find it in your contacts. 
Don't forget to add the bot to a group as a member.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

**중요**: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ` 같은 토큰을 복사해 두세요.

## 👤 2단계: Chat ID 찾기

### 방법 1: 봇과 직접 대화
1. 새로 만든 봇을 찾아서 대화 시작
2. `/start` 명령어 입력
3. 아무 메시지나 전송

### 방법 2: 그룹에 봇 추가 (권장)
1. 텔레그램 그룹 생성 또는 기존 그룹 사용
2. 그룹에 봇을 멤버로 추가
3. 그룹에서 아무 메시지나 전송

### Chat ID 확인하기
다음 URL을 브라우저에서 접속:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

예시:
```
https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ/getUpdates
```

응답 예시:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,
          "first_name": "홍길동"
        },
        "chat": {
          "id": -1001234567890,  // 이것이 Chat ID입니다!
          "title": "AI 보고서 그룹",
          "type": "supergroup"
        },
        "date": 1640000000,
        "text": "안녕하세요"
      }
    }
  ]
}
```

**Chat ID 찾기:**
- 개인 채팅: `"id": 987654321` (양수)
- 그룹 채팅: `"id": -1001234567890` (음수, 보통 -100으로 시작)

## ⚙️ 3단계: 환경 변수 설정

`.env` 파일에 다음 내용 추가:

```env
# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHAT_ID=-1001234567890
```

**주의사항:**
- `TELEGRAM_BOT_TOKEN`에는 BotFather에서 받은 토큰 전체를 입력
- `TELEGRAM_CHAT_ID`에는 찾은 Chat ID를 정확히 입력 (음수 포함)

## 🔧 4단계: 텔레그램 라이브러리 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install python-telegram-bot==20.7
```

## 🧪 5단계: 테스트

```bash
python test_agent.py
```

텔레그램 관련 상태를 확인할 수 있습니다:
- `텔레그램 라이브러리: True` - 라이브러리 설치 확인
- `텔레그램 활성화: True` - 봇 토큰과 Chat ID 설정 확인

## 📋 전송 방법 설정

### 텔레그램만 사용
```python
notification_service.send_report(report, method="telegram")
```

### 모든 채널 사용 (기본값)
```python
notification_service.send_report(report, method="all")  # 콘솔 + 이메일 + 텔레그램
```

## 🔍 문제 해결

### "텔레그램 활성화: False" 오류
1. `.env` 파일에 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`가 올바르게 설정되었는지 확인
2. Chat ID가 정확한지 확인 (음수 포함)
3. 봇 토큰이 유효한지 확인

### "텔레그램 라이브러리: False" 오류
```bash
pip install python-telegram-bot==20.7
```

### 메시지가 오지 않는 경우
1. 봇이 차단되지 않았는지 확인
2. 그룹에서 봇이 메시지를 보낼 권한이 있는지 확인
3. Chat ID가 올바른지 다시 확인

### 긴 메시지 분할
텔레그램은 메시지 길이를 4096자로 제한합니다. 
시스템에서 자동으로 긴 메시지를 분할하여 여러 개의 메시지로 전송합니다.

## 💡 추천 설정

### 개인용
- 개인 채팅으로 봇과 대화
- Chat ID는 양수

### 팀용
- 전용 그룹 생성
- 봇을 그룹에 추가
- Chat ID는 음수

---

이제 매일 오전 6시에 AI가 생성한 날씨와 증시 보고서를 텔레그램으로 받을 수 있습니다! 🎉
