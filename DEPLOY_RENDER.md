# Render.com 배포 가이드

Discord 봇을 Render.com에 배포하는 방법입니다.

## 사전 준비

1. [Render.com](https://render.com) 계정 생성
2. GitHub 계정 연동
3. 이 리포지토리를 GitHub에 푸시

## 환경 변수 설정

Render 대시보드에서 다음 환경 변수를 설정해야 합니다:

- `DISCORD_BOT_TOKEN`: Discord 봇 토큰
- `ALLOWED_CHANNEL_ID`: 봇이 작동할 채널 ID
- `AWS_ACCESS_KEY_ID`: AWS 액세스 키 (AI 피드백용)
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키 (AI 피드백용)

## 배포 단계

### 1. 새 서비스 생성

1. Render 대시보드에서 "New +" 클릭
2. "Background Worker" 선택
3. GitHub 리포지토리 연결

### 2. 설정

- **Name**: discode-bot (원하는 이름)
- **Region**: Oregon (US West)
- **Branch**: main
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

### 3. 환경 변수 추가

Environment 탭에서 위의 환경 변수들을 추가

### 4. 배포

"Create Background Worker" 클릭하여 배포 시작

## 모니터링

- Render 대시보드에서 실시간 로그 확인 가능
- 봇 상태는 Discord에서 `!ping` 명령어로 확인

## 주의사항

- Render 무료 플랜은 월 750시간 제공
- 자동 배포가 활성화되어 있어 GitHub push시 자동 재배포
- 봇이 오프라인이 되면 Render 대시보드에서 수동으로 재시작 가능

## 문제 해결

### 봇이 시작되지 않는 경우
1. 환경 변수가 모두 설정되었는지 확인
2. 로그에서 에러 메시지 확인
3. Discord 봇 토큰이 유효한지 확인

### 스케줄러가 작동하지 않는 경우
1. `ALLOWED_CHANNEL_ID`가 올바르게 설정되었는지 확인
2. 봇이 해당 채널에 메시지 전송 권한이 있는지 확인
3. `!scheduler_status` 명령어로 상태 확인