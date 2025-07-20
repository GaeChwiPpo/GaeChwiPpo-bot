# 🤝 기여 가이드

Discord 봇 프로젝트에 기여해주셔서 감사합니다! 

## 🚀 빠른 시작

### 1. 프로젝트 Fork & Clone
```bash
# Fork 후 본인 저장소에서
git clone https://github.com/YOUR_USERNAME/discord-bot.git
cd discord-bot
```

### 2. 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발용 도구
```

### 3. 봇 테스트
```bash
# .env 파일 생성
cp .env.example .env
# 테스트용 봇 토큰 추가 (각자 생성)

# 봇 실행
python main.py
```

## 📝 기여 방법

### 1. Issue 확인
- 기존 Issue 확인
- 없다면 새 Issue 생성
- `good first issue` 라벨 추천!

### 2. 브랜치 생성
```bash
git checkout -b feature/기능명
# 또는
git checkout -b fix/버그명
```

### 3. 코드 작성
- Python 스타일 가이드 준수
- 주석은 한국어 OK
- 함수/클래스 docstring 필수

### 4. 테스트
```bash
# 코드 포맷팅
black .
isort .

# 린팅
flake8 .

# 테스트 실행
pytest tests/
```

### 5. Pull Request
- PR 템플릿 작성
- 스크린샷/GIF 첨부 (UI 변경 시)
- Issue 번호 연결

## 🏗️ 프로젝트 구조

```
discord-bot/
├── main.py          # 메인 봇 파일
├── cogs/            # 명령어 모듈
│   ├── general.py   # 일반 명령어
│   ├── fun.py       # 재미 명령어
│   └── admin.py     # 관리자 명령어
├── utils/           # 유틸리티
├── tests/           # 테스트
└── docs/            # 문서
```

## 🎯 개발 가이드라인

### 코드 스타일
- **Black** 포매터 사용 (line-length: 88)
- **isort** import 정렬
- **flake8** 린팅 통과

### 커밋 메시지
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가
chore: 기타 변경사항
```

### 명령어 추가 방법
1. `cogs/` 폴더에 새 파일 생성 또는 기존 파일 수정
2. 명령어 함수 작성:
```python
@commands.command(name='명령어명', aliases=['별칭'])
async def 함수명(self, ctx, *, 인자=None):
    """명령어 설명"""
    await ctx.send("응답")
```

## 🧪 테스트 작성

### 단위 테스트
```python
# tests/test_명령어.py
import pytest
from your_module import your_function

@pytest.mark.asyncio
async def test_명령어():
    result = await your_function()
    assert result == expected
```

## 🌐 다국어 지원

메시지 추가 시:
```python
# utils/messages.py
MESSAGES = {
    'ko': {
        'welcome': '환영합니다!',
        'error': '오류가 발생했습니다'
    },
    'en': {
        'welcome': 'Welcome!',
        'error': 'An error occurred'
    }
}
```

## 🔧 자주 사용하는 명령어

```bash
# 개발 서버 실행
python main.py

# 전체 테스트
pytest

# 코드 자동 정리
black . && isort .

# 타입 체크
mypy main.py

# 의존성 업데이트
pip-compile requirements.in
```

## 📋 체크리스트

PR 전 확인:
- [ ] 코드가 실행되는가?
- [ ] 테스트를 작성했는가?
- [ ] 문서를 업데이트했는가?
- [ ] 린팅을 통과했는가?
- [ ] 커밋 메시지가 명확한가?

## 🎉 기여자 혜택

- README에 기여자 목록 추가
- 디스코드 서버 특별 역할
- 월간 최우수 기여자 선정

## 💬 도움 요청

- Discord: [서버 링크]
- Issue: 질문 라벨 사용
- Discussion: 일반 토론

## 📜 라이선스

이 프로젝트는 MIT 라이선스입니다.
기여하신 코드도 동일한 라이선스가 적용됩니다.

---

🙏 모든 기여에 감사드립니다!