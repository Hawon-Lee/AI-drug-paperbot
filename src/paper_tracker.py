import json
import os
from datetime import datetime
from typing import Set, List, Dict
from .paper_collector import PaperCollector
from .slack_message import send_paper_alert

class PaperTracker:
    def __init__(self, db_file: str = "sent_papers.json"):
        self.db_file = db_file
        self.sent_papers = self.load_sent_papers()
    
    def load_sent_papers(self) -> Set[str]:
        """이미 전송된 논문 목록 로드"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('sent_papers', []))
            except:
                return set()
        return set()
    
    def save_sent_papers(self):
        """전송된 논문 목록 저장"""
        data = {
            'sent_papers': list(self.sent_papers),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_paper_id(self, paper: Dict) -> str:
        """논문 고유 ID 생성 (DOI 또는 제목 기반)"""
        if paper.get('doi'):
            return paper['doi']
        return f"{paper['journal']}_{hash(paper['title'])}"
    
    def check_and_send_new_papers(self, days_back: int = 1, min_score: float = 0.3):
        """새 논문 확인 및 Slack 전송"""
        collector = PaperCollector()
        papers = collector.get_all_filtered_papers(days_back, min_score)
        
        new_papers = []
        for paper in papers:
            paper_id = self.get_paper_id(paper)
            if paper_id not in self.sent_papers:
                new_papers.append(paper)
                self.sent_papers.add(paper_id)
        
        if new_papers:
            print(f"{len(new_papers)}개의 새로운 관련 논문 발견!")
            
            for paper in new_papers:
                success = send_paper_alert(
                    title=paper['title'],
                    authors=paper['authors'],
                    journal=paper['journal'],
                    abstract=paper['abstract'],
                    doi=paper.get('doi')
                )
                
                if success:
                    print(f"✅ 전송 완료: {paper['title'][:50]}...")
                else:
                    print(f"❌ 전송 실패: {paper['title'][:50]}...")
            
            self.save_sent_papers()
        else:
            print("새로운 관련 논문이 없습니다.")
            
        return len(new_papers)

if __name__ == "__main__":
    tracker = PaperTracker()
    tracker.check_and_send_new_papers(days_back=30, min_score=0.3)  # 테스트용 30일