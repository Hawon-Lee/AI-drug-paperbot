import schedule
import time
from datetime import datetime
from src.paper_tracker import PaperTracker

def daily_paper_check():
    """매일 실행될 논문 체크 함수"""
    print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 논문 체크 시작 ===")
    
    try:
        tracker = PaperTracker()
        new_count = tracker.check_and_send_new_papers(days_back=1, min_score=0.3)
        
        if new_count > 0:
            print(f"✅ {new_count}개의 새 논문을 Slack으로 전송했습니다.")
        else:
            print("📭 새로운 관련 논문이 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    print("=== 논문 체크 완료 ===\n")

def start_scheduler():
    """스케줄러 시작"""
    # 매일 오전 10시에 실행
    schedule.every().day.at("10:00").do(daily_paper_check)
    
    print("🤖 논문 알림 봇이 시작되었습니다!")
    print("⏰ 매일 오전 10시에 새 논문을 확인합니다.")
    print("🛑 중단하려면 Ctrl+C를 누르세요.")
    
    # 즉시 한 번 실행 (테스트용)
    print("\n📋 첫 실행을 진행합니다...")
    daily_paper_check()
    
    # 스케줄 대기
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 논문 알림 봇을 종료합니다.")