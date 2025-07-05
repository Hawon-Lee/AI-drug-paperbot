import os
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 로드
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
PUBMED_EMAIL = os.getenv('PUBMED_EMAIL')