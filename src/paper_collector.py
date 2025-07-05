import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time
from dateutil import parser
import re
from Bio import Entrez
import xml.etree.ElementTree as ET
from .config import PUBMED_EMAIL

class KeywordFilter:
    def __init__(self):
        # 1차 필터: 핵심 키워드 (하나라도 있으면 통과)
        self.primary_keywords = [
            'protein-protein interaction', 'ppi', 'protein interaction',
            'molecular modeling', 'molecular dynamics', 'md simulation',
            'drug discovery', 'drug design', 'drug development',
            'geometric learning', 'graph neural network', 'gnn',
            'structural biology', 'protein structure', 'protein complex',
            'docking', 'binding affinity', 'binding prediction',
            'deep learning', 'machine learning', 'neural network',
            'AI'
        ]
        
        # 2차 필터: 보너스 키워드 (점수 가산)
        self.bonus_keywords = [
            'se(3)', 'geometric invariant', 'invariant learning',
            'alphafold', 'protein folding', 'structural prediction',
            'contact prediction', 'interface prediction',
            'complementarity', 'trigonometric constraint'
        ]
        
        # 제외 키워드 (명확히 다른 분야)
        self.exclude_keywords = [
            'plant protein', 'agricultural', 'photosynthesis',
            'clinical trial', 'patient', 'hospital'
        ]
    
    def calculate_relevance_score(self, text: str) -> float:
        """텍스트의 관련도 점수 계산 (0-1 범위)"""
        text_lower = text.lower()
        score = 0.0
        
        # 제외 키워드 체크
        for keyword in self.exclude_keywords:
            if keyword in text_lower:
                return 0.0  # 즉시 제외
        
        # 1차 키워드 체크 (필수)
        primary_found = False
        for keyword in self.primary_keywords:
            if keyword in text_lower:
                primary_found = True
                score += 0.3  # 기본 점수
                break
        
        if not primary_found:
            return 0.0  # 1차 키워드 없으면 제외
        
        # 2차 키워드 체크 (보너스)
        for keyword in self.bonus_keywords:
            if keyword in text_lower:
                score += 0.2
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def filter_papers(self, papers: List[Dict], min_score: float = 0.3) -> List[Dict]:
        """논문 리스트를 필터링하여 관련 논문만 반환"""
        filtered_papers = []
        
        for paper in papers:
            # 제목 + 초록으로 점수 계산
            search_text = f"{paper['title']} {paper['abstract']}"
            score = self.calculate_relevance_score(search_text)
            
            if score >= min_score:
                paper['relevance_score'] = score
                filtered_papers.append(paper)
        
        # 점수순으로 정렬
        filtered_papers.sort(key=lambda x: x['relevance_score'], reverse=True)
        return filtered_papers


class PaperCollector:
    def __init__(self):
        self.biorxiv_rss_url = "https://connect.biorxiv.org/biorxiv_xml.php?subject=bioinformatics"
        self.filter = KeywordFilter()
        
        # PubMed 설정
        Entrez.email = PUBMED_EMAIL  # 실제 이메일로 변경하세요
        self.journals = {
            'JCIM': 'J Chem Inf Model',
            'JCTC': 'J Chem Theory Comput'
        }
        
    def collect_biorxiv_papers(self, days_back: int = 1) -> List[Dict]:
        """bioRxiv에서 최근 논문 수집"""
        try:
            print("bioRxiv RSS 피드 수집 중...")
            feed = feedparser.parse(self.biorxiv_rss_url)
            papers = []
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                # 날짜 파싱 개선
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'published'):
                    try:
                        # 문자열 날짜 파싱 시도
                        from dateutil import parser
                        pub_date = parser.parse(entry.published)
                    except:
                        pub_date = datetime.now()  # 파싱 실패시 현재 시간
                else:
                    pub_date = datetime.now()  # 날짜 정보 없으면 현재 시간
                
                # 날짜 필터링 (일단 모든 논문 수집하도록 임시 수정)
                # if pub_date >= cutoff_date:
                paper = {
                    'title': entry.title,
                    'authors': entry.author if hasattr(entry, 'author') else 'Unknown',
                    'abstract': entry.summary,
                    'journal': 'bioRxiv',
                    'doi': entry.id if hasattr(entry, 'id') else None,
                    'published_date': pub_date,
                    'url': entry.link
                }
                papers.append(paper)
            
            print(f"bioRxiv에서 {len(papers)}개 논문 수집 완료")
            return papers
            
        except Exception as e:
            print(f"bioRxiv 수집 실패: {e}")
            return []


    def collect_pubmed_papers(self, journal_abbrev: str, days_back: int = 1) -> List[Dict]:
        """PubMed에서 특정 저널의 최근 논문 수집"""
        try:
            print(f"{journal_abbrev} 논문 수집 중...")
            
            # 검색 쿼리 구성
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            search_query = f'("{self.journals[journal_abbrev]}"[Journal]) AND ("{start_date.strftime("%Y/%m/%d")}"[Date - Publication] : "{end_date.strftime("%Y/%m/%d")}"[Date - Publication])'
            
            # PubMed 검색
            search_handle = Entrez.esearch(db="pubmed", term=search_query, retmax=100)
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            id_list = search_results["IdList"]
            if not id_list:
                print(f"{journal_abbrev}에서 새 논문을 찾지 못했습니다.")
                return []
            
            # 상세 정보 가져오기
            fetch_handle = Entrez.efetch(db="pubmed", id=id_list, rettype="xml")
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            papers = []
            for article in fetch_results['PubmedArticle']:
                try:
                    medline = article['MedlineCitation']
                    article_info = medline['Article']
                    
                    # 기본 정보 추출
                    title = article_info['ArticleTitle']
                    
                    # 저자 정보
                    authors = []
                    if 'AuthorList' in article_info:
                        for author in article_info['AuthorList'][:5]:  # 최대 5명
                            if 'LastName' in author and 'ForeName' in author:
                                authors.append(f"{author['ForeName']} {author['LastName']}")
                    authors_str = ", ".join(authors) if authors else "Unknown"
                    
                    # 초록
                    abstract = ""
                    if 'Abstract' in article_info and 'AbstractText' in article_info['Abstract']:
                        abstract_parts = article_info['Abstract']['AbstractText']
                        if isinstance(abstract_parts, list):
                            abstract = " ".join([str(part) for part in abstract_parts])
                        else:
                            abstract = str(abstract_parts)
                    
                    # DOI
                    doi = None
                    if 'ELocationID' in article_info:
                        for elocation in article_info['ELocationID']:
                            if elocation.attributes.get('EIdType') == 'doi':
                                doi = str(elocation)
                                break
                    
                    # 발행일
                    pub_date = datetime.now()
                    if 'ArticleDate' in article_info:
                        date_info = article_info['ArticleDate'][0]
                        try:
                            pub_date = datetime(
                                int(date_info['Year']),
                                int(date_info['Month']),
                                int(date_info['Day'])
                            )
                        except:
                            pass
                    
                    paper = {
                        'title': title,
                        'authors': authors_str,
                        'abstract': abstract,
                        'journal': journal_abbrev,
                        'doi': doi,
                        'published_date': pub_date,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{medline['PMID']}/"
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"논문 파싱 오류: {e}")
                    continue
            
            print(f"{journal_abbrev}에서 {len(papers)}개 논문 수집 완료")
            return papers
            
        except Exception as e:
            print(f"{journal_abbrev} 수집 실패: {e}")
            return []
    
    def get_all_filtered_papers(self, days_back: int = 1, min_score: float = 0.3) -> List[Dict]:
        """모든 소스에서 필터링된 논문 수집"""
        all_papers = []
        
        # bioRxiv 수집
        biorxiv_papers = self.collect_biorxiv_papers(days_back)
        all_papers.extend(biorxiv_papers)
        
        # JCIM 수집
        jcim_papers = self.collect_pubmed_papers('JCIM', days_back)
        all_papers.extend(jcim_papers)
        
        # JCTC 수집
        jctc_papers = self.collect_pubmed_papers('JCTC', days_back)
        all_papers.extend(jctc_papers)
        
        # 필터링
        filtered = self.filter.filter_papers(all_papers, min_score)
        
        print(f"전체 필터링 결과: {len(all_papers)}개 중 {len(filtered)}개 관련 논문 발견")
        return filtered

    def get_filtered_papers(self, days_back: int = 1, min_score: float = 0.3) -> List[Dict]:
        """필터링된 논문 수집"""
        papers = self.collect_biorxiv_papers(days_back)
        filtered = self.filter.filter_papers(papers, min_score)
        
        print(f"필터링 결과: {len(papers)}개 중 {len(filtered)}개 관련 논문 발견")
        return filtered


if __name__ == "__main__":
    collector = PaperCollector()
    
    # 실제 이메일 주소로 변경 필요
    Entrez.email = "your_email@gmail.com"  # 여기에 실제 이메일 입력
    
    papers = collector.get_all_filtered_papers(days_back=30, min_score=0.3)  # 30일로 늘려서 테스트
    
    for paper in papers:
        print(f"제목: {paper['title']}")
        print(f"저널: {paper['journal']}")
        print(f"관련도: {paper['relevance_score']:.2f}")
        print(f"초록: {paper['abstract'][:200]}...")
        print("-" * 50)