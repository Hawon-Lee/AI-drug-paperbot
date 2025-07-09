import os
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
PUBMED_EMAIL = os.getenv('PUBMED_EMAIL')

def validate_config():
    """환경변수 설정 검증"""
    errors = []
    
    if not SLACK_WEBHOOK_URL:
        errors.append("❌ SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
    elif not SLACK_WEBHOOK_URL.startswith('https://hooks.slack.com/'):
        errors.append("❌ SLACK_WEBHOOK_URL 형식이 올바르지 않습니다.")
    
    if not PUBMED_EMAIL:
        errors.append("❌ PUBMED_EMAIL이 설정되지 않았습니다.")
    elif '@' not in PUBMED_EMAIL:
        errors.append("❌ PUBMED_EMAIL 형식이 올바르지 않습니다.")
    
    if errors:
        print("\n🚫 환경변수 설정 오류:")
        for error in errors:
            print(f"   {error}")
        print("\n📋 해결 방법:")
        print("   1. .env 파일이 존재하는지 확인")
        print("   2. .env 파일에 올바른 값이 설정되었는지 확인")
        print("   3. README.md의 설정 가이드 참조")
        return False
    
    print("✅ 환경변수 설정이 올바릅니다.")
    return True