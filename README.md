# Discord 자동화 봇

Python과 discord.py를 사용한 오픈소스 Discord 봇입니다.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🚀 빠른 시작

### Render.com으로 배포 (추천 - 무료 24/7 운영)
1. 이 리포지토리를 GitHub에 Fork 또는 Clone
2. [Render.com](https://render.com) 계정 생성 및 GitHub 연동
3. 새 Background Worker 생성
4. 환경 변수 설정 (아래 참조)
5. 배포 시작!

### 필수 환경 변수
- `DISCORD_BOT_TOKEN`: Discord 봇 토큰
- `ALLOWED_CHANNEL_ID`: 봇이 작동할 채널 ID (선택사항)
- `AWS_ACCESS_KEY_ID`: AWS 액세스 키 (AI 피드백용)
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키 (AI 피드백용)

자세한 배포 방법은 [DEPLOY_RENDER.md](DEPLOY_RENDER.md) 참조

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
- `!question [backend/frontend/general]` / `!문제` / `!q` - 개발 질문 받기
  - backend: 데이터베이스, API, 아키텍처, 성능, DevOps, 보안
  - frontend: React, 성능, 상태관리, CSS, TypeScript, 테스팅, 접근성
  - general: 프로그래밍 일반, 소프트스킬, 커리어
- `!mystats` / `!내점수` / `!stats` - 학습 통계 보기
- `!scheduler_status` / `!스케줄러` - 스케줄러 상태 확인
- `!post_daily` / `!일일질문` - 수동으로 일일 질문 게시 (관리자 전용)
- 답변 방법: 자동으로 생성되는 스레드에서 답변
- 스레드에서 답변하면 AI가 자동으로 피드백을 제공합니다!
- 총 900개의 다양한 질문이 준비되어 있습니다 (각 분야별 300개)

#### 🕐 자동 질문 스케줄러
- **매일 오전 10시**에 자동으로 질문이 게시됩니다
- **매일 3개의 질문** 게시: Backend, Frontend, General 각 1개씩
- 날짜 기반 인덱스로 순차적으로 질문이 선택됩니다
- Day 1 (2025-07-20): Backend/Frontend/General 모두 인덱스 0
- Day 2 (2025-07-21): Backend/Frontend/General 모두 인덱스 1
- Day 3 (2025-07-22): Backend/Frontend/General 모두 인덱스 2
- 모든 질문을 다 돌면 처음부터 다시 시작합니다

## 폴더 구조

```
discode-automation/
├── main.py          # 메인 봇 파일
├── cogs/           # 명령어 모듈
│   ├── general.py  # 일반 명령어
│   ├── fun.py      # 재미있는 명령어
│   └── study.py    # 학습 질문 시스템
├── data/           # 데이터 파일
│   └── questions.json # 질문 데이터베이스
├── render.yaml     # Render 배포 설정
├── .env            # 환경 변수 (생성 필요)
├── .env.example    # 환경 변수 예시
└── requirements.txt # 필요한 패키지
```

## 추가 개발

새로운 명령어를 추가하려면 `cogs` 폴더에 새로운 파이썬 파일을 만들고 Cog 클래스를 작성하세요.