import requests
import os
from .config import SLACK_WEBHOOK_URL


def send_message_slack(text: str = "코드 실행 완료") -> None:
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            },
        ],
    }
    # requests.post (WebhookUrl. SLACK_WEBHOOK_URL, json=payload)

    requests.post (SLACK_WEBHOOK_URL, json=payload)


def send_paper_alert(title: str, authors: str, journal: str, abstract: str, 
                    doi: str = None, relevance_score: float = 0, 
                    matched_keywords: list[str] = None) -> bool:
    """논문 정보를 Slack으로 전송"""
    try:
        # Abstract 길이 조정
        abstract_truncated = abstract[:1200] + "..." if len(abstract) > 1200 else abstract
        
        text = f"*🧬 새로운 AI Drug Discovery 논문*\n\n"
        text += f"*📄 제목:* {title}\n"
        text += f"*👥 저자:* {authors}\n"
        text += f"*📚 저널:* {journal}\n"
        if doi:
            text += f"*🔗 DOI:* {doi}\n"
        
        # 관련도 점수와 키워드 정보 추가
        text += f"*📊 관련도 점수:* {relevance_score:.2f}/1.00\n"
        if matched_keywords:
            keywords_str = ", ".join(matched_keywords[:5])  # 최대 5개
            text += f"*🎯 매칭된 키워드:* {keywords_str}\n"
        
        text += f"\n*📝 Abstract:*\n{abstract_truncated}"
        
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text,
                    },
                },
            ],
        }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Slack 전송 실패: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        send_message_slack(text=sys.argv[1])
    else:
        # 논문 알림 테스트
        send_paper_alert(
            title="Accurate Protein-Protein Interactions Modeling through Physics-informed Geometric Invariant Learning",
            authors="Jiahua Rao, Deqin Liu, Xiaolong Zhou, et al.",
            journal="bioRxiv",
            abstract="AlphaFold has set a new standard for predicting protein structures from primary sequences; however, it faces challenges with protein complexes across species...",
            doi="10.1101/2025.07.01.662544"
        )