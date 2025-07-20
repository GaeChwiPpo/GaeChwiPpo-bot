# Discord 자동화 봇

Python과 discord.py를 사용한 오픈소스 Discord 봇입니다.

[![Run on Replit](https://replit.com/badge/github/YOUR_USERNAME/YOUR_REPO_NAME)](https://replit.com/new/github/YOUR_USERNAME/YOUR_REPO_NAME)

## 🚀 빠른 시작 (1분 배포!)

### 옵션 1: Replit으로 즉시 실행 (추천)
1. 위의 "Run on Replit" 버튼 클릭
2. Replit 계정으로 로그인
3. 자동으로 프로젝트가 임포트됨
4. Secrets 탭에서 `DISCORD_BOT_TOKEN` 추가
5. Run 버튼 클릭!

### 24/7 실행 방법
1. Repl 실행 후 웹뷰 URL 복사
2. [UptimeRobot](https://uptimerobot.com)에서 5분마다 핑 설정
3. 봇이 24시간 실행됩니다!

## 설치 방법 (로컬)

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Discord 봇 토큰 설정:
   - `.env` 파일을 생성하고 `.env.example`을 참고하여 설정
   - `DISCORD_BOT_TOKEN`에 실제 봇 토큰을 입력
   - `ALLOWED_CHANNEL_ID`에 특정 채널 ID 입력 (선택사항, 비워두면 모든 채널에서 작동)

3. AWS Bedrock 설정 (Study 기능용, 선택사항):
   - `AWS_ACCESS_KEY_ID`와 `AWS_SECRET_ACCESS_KEY` 입력
   - `AWS_REGION` 설정 (기본값: us-east-1)
   - AWS Bedrock Claude 모델 액세스 권한 필요

## 봇 생성 및 초대

1. [Discord Developer Portal](https://discord.com/developers/applications)로 이동
2. "New Application" 클릭하여 새 애플리케이션 생성
3. "Bot" 섹션으로 이동
4. "Add Bot" 클릭
5. 봇 토큰 복사 (Reset Token 클릭 후 복사)
6. "OAuth2" → "URL Generator"로 이동
7. Scopes에서 "bot" 선택
8. Bot Permissions에서 필요한 권한 선택:
   - Send Messages
   - Read Message History
   - Embed Links
   - Manage Messages (clear 명령어용)
   - Read Messages/View Channels
9. 생성된 URL로 봇을 서버에 초대

## 실행 방법

```bash
python main.py
```

## 기본 명령어

- `!ping` - 봇의 응답 시간 확인
- `!hello` / `!안녕` - 인사
- `!info` - 봇 정보 표시
- `!echo [메시지]` - 메시지 따라하기
- `!help_custom` / `!도움말` - 명령어 목록

### General Cog 명령어
- `!server` / `!서버` - 서버 정보 표시
- `!user [@멤버]` / `!유저` - 사용자 정보 표시
- `!clear [숫자]` / `!청소` - 메시지 삭제 (관리자 권한 필요)

### Fun Cog 명령어
- `!dice [면수]` / `!주사위` - 주사위 굴리기
- `!choose [선택지1] [선택지2] ...` / `!선택` - 무작위 선택
- `!8ball [질문]` / `!질문` - 마법의 8ball
- `!coin` / `!동전` - 동전 던지기
- `!rps [가위/바위/보]` / `!가위바위보` - 가위바위보 게임

### Study Cog 명령어 (학습 시스템)
- `!question [backend/frontend]` / `!질문` / `!q` - 개발 질문 받기
- `!mystats` / `!내점수` / `!stats` - 학습 통계 보기
- 질문에 답글로 답변하면 자동으로 AI 피드백을 받습니다!

## 폴더 구조

```
discode-automation/
├── main.py          # 메인 봇 파일
├── cogs/           # 명령어 모듈
│   ├── general.py  # 일반 명령어
│   ├── fun.py      # 재미있는 명령어
│   └── study.py    # 학습 질문 시스템
├── keep_alive.py   # Replit 웹 서버
├── .env            # 환경 변수 (생성 필요)
├── .env.example    # 환경 변수 예시
└── requirements.txt # 필요한 패키지
```

## 추가 개발

새로운 명령어를 추가하려면 `cogs` 폴더에 새로운 파이썬 파일을 만들고 Cog 클래스를 작성하세요.