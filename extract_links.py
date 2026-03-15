import fitz
import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

def extract_university_links():
    doc = fitz.open('2027 대학입학 시행계획 검색기-196교(배포용).pdf')
    page = doc[0]

    # 지역명 목록 (PDF에 표기된 헤더)
    target_regions = ["서울특별시", "인천광역시", "경기도"]
    all_regions = target_regions + [
        "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도", 
        "광주광역시", "경상북도", "경상남도", "대구광역시", "부산광역시", 
        "울산광역시", "제주특별자치도", "대전광역시", "세종특별자치시", "특수목적대학"
    ]

    # 모든 텍스트 블록 가져오기
    blocks = page.get_text("dict")["blocks"]
    
    region_bboxes = {}
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if text in all_regions:
                        region_bboxes[text] = fitz.Rect(s["bbox"])

    # 링크 가져오기
    links = page.get_links()
    
    # 1. 대학 이름(링크) 찾기 (구글 드라이브 링크가 아닌 것들)
    # 대학 이름 링크의 위치를 기반으로 대학 이름 텍스트 추출
    university_links = []
    drive_links = []
    
    for link in links:
        uri = link.get('uri', '')
        rect = fitz.Rect(link['from'])
        
        if 'drive.google.com' in uri:
            drive_links.append({'rect': rect, 'uri': uri})
        elif uri:
            # 텍스트 추출
            words = page.get_text("words", clip=rect)
            name = " ".join([w[4] for w in words]).strip()
            if name:
                university_links.append({'name': name, 'rect': rect, 'uri': uri})
    
    results = {region: [] for region in target_regions}
    
    # 각 대학이 어느 지역에 속하는지 판별하고, 구글 드라이브 링크를 매칭
    for uni in university_links:
        # 1) 지역 판별 (가장 가까운 위쪽 헤더 찾기, X축 겹침 확인)
        my_region = None
        min_y_diff = 9999
        
        for region_name, r_bbox in region_bboxes.items():
            # X좌표가 비슷한 열(Column)에 있는지 확인 (여유폭 50)
            if r_bbox.x0 - 50 <= uni['rect'].x0 <= r_bbox.x1 + 50:
                # 대학 이름이 지역 헤더보다 아래에 있어야 함
                if uni['rect'].y0 > r_bbox.y0:
                    y_diff = uni['rect'].y0 - r_bbox.y0
                    if y_diff < min_y_diff:
                        min_y_diff = y_diff
                        my_region = region_name
                        
        if my_region in target_regions:
            # 2) 해당하는 구글 드라이브 링크 찾기 (y좌표가 비슷하고, x좌표가 오른쪽에 있는 것)
            my_drive_link = None
            for d_link in drive_links:
                # Y축이 겹치는지 확인
                y_overlap = min(uni['rect'].y1, d_link['rect'].y1) - max(uni['rect'].y0, d_link['rect'].y0)
                if y_overlap > 0 and d_link['rect'].x0 > uni['rect'].x0:
                    # 너무 멀리 떨어져 있지 않은지 확인 (가장 가까운 것)
                    if my_drive_link is None or d_link['rect'].x0 < my_drive_link['rect'].x0:
                        my_drive_link = d_link
            
            if my_drive_link:
                results[my_region].append({
                    'name': uni['name'],
                    'drive_url': my_drive_link['uri']
                })
    
    with open('links.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    extract_university_links()
