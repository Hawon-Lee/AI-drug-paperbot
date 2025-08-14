# AI 신약개발 논문 알림봇 🧬🤖

bioRxiv, JCIM, JCTC 저널에서 AI 기반 신약개발 관련 논문을 모니터링하고, 매일 오전 10시에 관련 논문의 초록을 Slack으로 전송하는 봇입니다.

## 주요 기능

- 📚 **다중 소스 수집**: bioRxiv RSS + PubMed API (JCIM/JCTC)
- 🎯 **키워드 필터링**: AI 신약개발 관련 논문만 선별
- 📱 **Slack 연동**: 개인 채널로 논문 정보 전송
- ⏰ **자동 스케줄링**: 매일 오전 10시 자동 실행

## 대상 연구 분야

- 단백질-단백질 상호작용 (PPI)
- 분자 모델링 및 시뮬레이션
- 기하학적/그래프 신경망 기반 신약개발
- 물리학 기반 머신러닝
- 구조생물학 및 단백질 설계
- ...

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/Hawon-Lee/AI-drug-paperbot.git
cd AI-drug-paperbot
```

### 2. 의존성 설치
```bash
# pip 사용
pip install -r requirements.txt

# uv 사용
uv venv
source .venv/bin/activate # In case of linux/macos
uv pip install -r requirements.txt
```

### 3. Slack 웹훅 설정
3-1. Slack 앱 생성
- https://api.slack.com/apps 접속\
- "Create New App" 클릭\
- "From scratch" 선택\
- App Name: "Paper Alert Bot" (원하는 이름)\
- Workspace: 알림받을 워크스페이스 선택\
- "Create App" 클릭

3-2. Incoming Webhooks 설정

- 좌측 메뉴에서 "Incoming Webhooks" 클릭\
- "Activate Incoming Webhooks" 토글을 On으로 변경\
- 하단의 "Add New Webhook to Workspace" 클릭\
- 메시지를 받을 채널 선택 (개인 DM 권장)\
- "Allow" 클릭

### 4. 환경변수 설정
```bash
cp .env.example .env
```

`.env` 파일 편집:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PUBMED_EMAIL=your_email@example.com  # any email
```


### 5. 실행
```bash
python main.py
```


## 설정 변경

### 키워드 필터링 조정
`src/paper_collector.py`에서 키워드 수정:
```python
self.primary_keywords = [
    'protein-protein interaction',
    'molecular modeling',
    # 원하는 키워드 추가
]
```

### 전송 시간 변경
`main.py`에서 스케줄 수정:
```python
schedule.every().day.at("10:00").do(daily_paper_check)  # 시간 변경
```

### 수집 범위 조정
```python
tracker.check_and_send_new_papers(days_back=1, min_score=0.3)
# days_back: 과거 며칠까지 수집 (기본값: 1일)
# min_score: 관련도 최소 점수 (기본값: 0.3, 낮을수록 더 많은 논문)
```

## 예시 출력

관련 논문 발견 시 Slack 메시지:

> **🧬 새로운 AI Drug Discovery 논문**
> 
> **📄 제목:** Physics-informed Geometric Learning for Protein-Protein Interactions
> 
> **👥 저자:** Jiahua Rao, Deqin Liu, et al.
> 
> **📚 저널:** bioRxiv
> 
> **📝 Abstract:** AlphaFold has set a new standard for predicting...

## 문제 해결

**PubMed API 오류**
- `.env`에서 이메일 주소 확인
- 인터넷 연결 상태 확인

**Slack 전송 실패**
- 웹훅 URL 확인
- Slack 앱 권한 확인

**논문이 안 나옴**
- `min_score` 값을 낮춰보세요 (0.2 정도)
- `days_back` 값을 늘려보세요 (7일 정도)

## 폴더 구조

```
AI-drug-paperbot/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 패키지 의존성
├── .env.example           # 환경변수 템플릿
└── src/
    ├── paper_collector.py  # 논문 수집 및 필터링
    ├── paper_tracker.py    # 중복 추적 및 Slack 전송
    └── config.py           # 설정 관리
```

## 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 기여하기

1. Fork 후 feature 브랜치 생성
2. 변경사항 커밋
3. Pull Request 생성