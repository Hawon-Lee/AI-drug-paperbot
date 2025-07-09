import schedule
import time
from datetime import datetime
from src.paper_tracker import PaperTracker

def daily_paper_check():
    """매일 실행될 논문 체크 함수"""
    current_time = datetime.now()
    weekday = current_time.weekday()  # 월요일=0, 일요일=6
    
    # 주말 체크 (토요일=5, 일요일=6)
    if weekday in [5, 6]:
        print(f"\n=== {current_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print("🏖️ 주말입니다. 논문 체크를 건너뜁니다.")
        print("📅 월요일에 주말 논문까지 함께 확인합니다.")
        return
    
    print(f"\n=== {current_time.strftime('%Y-%m-%d %H:%M:%S')} 논문 체크 시작 ===")
    
    try:
        tracker = PaperTracker()
        
        # 월요일이면 3일치 확인 (금,토,일), 평일이면 1일치
        if weekday == 0:  # 월요일
            print("📅 월요일입니다. 주말 논문까지 함께 확인합니다. (3일치)")
            days_back = 3
        else:  # 화~금요일
            days_back = 1
        
        new_count = tracker.check_and_send_new_papers(days_back=days_back, min_score=0.3)
        
        if new_count > 0:
            print(f"✅ {new_count}개의 새 논문을 Slack으로 전송했습니다.")
        else:
            print("📭 새로운 관련 논문이 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    print("=== 논문 체크 완료 ===\n")

def start_scheduler():
    """스케줄러 시작"""
    from src.config import validate_config
    
    # 환경변수 검증
    if not validate_config():
        print("\n🛑 환경변수 설정을 완료한 후 다시 실행해주세요.")
        return
    
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
        time.sleep(60)

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 논문 알림 봇을 종료합니다.")