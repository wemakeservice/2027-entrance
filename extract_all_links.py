import fitz
import json
import os

def extract_all_university_links():
    doc = fitz.open('2027 대학입학 시행계획 검색기-196교(배포용).pdf')
    page = doc[0]

    # 모든 지역명 목록 (PDF 헤더 기준)
    all_regions = [
        "서울특별시", "인천광역시", "경기도", "강원특별자치도", "충청북도", "충청남도", 
        "전북특별자치도", "전라남도", "광주광역시", "경상북도", "경상남도", 
        "대구광역시", "부산광역시", "울산광역시", "제주특별자치도", 
        "대전광역시", "세종특별자치시", "특수목적대학"
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
    
    university_links = []
    drive_links = []
    
    for link in links:
        uri = link.get('uri', '')
        rect = fitz.Rect(link['from'])
        
        if 'drive.google.com' in uri:
            drive_links.append({'rect': rect, 'uri': uri})
        elif uri:
            words = page.get_text("words", clip=rect)
            name = " ".join([w[4] for w in words]).strip()
            if name:
                university_links.append({'name': name, 'rect': rect, 'uri': uri})
    
    results = {region: [] for region in all_regions}
    
    for uni in university_links:
        my_region = None
        min_y_diff = 9999
        
        for region_name, r_bbox in region_bboxes.items():
            # X축 일치 확인 (열 단위)
            if r_bbox.x0 - 50 <= uni['rect'].x0 <= r_bbox.x1 + 50:
                if uni['rect'].y0 > r_bbox.y0:
                    y_diff = uni['rect'].y0 - r_bbox.y0
                    if y_diff < min_y_diff:
                        min_y_diff = y_diff
                        my_region = region_name
                        
        if my_region:
            my_drive_link = None
            for d_link in drive_links:
                y_overlap = min(uni['rect'].y1, d_link['rect'].y1) - max(uni['rect'].y0, d_link['rect'].y0)
                if y_overlap > 0 and d_link['rect'].x0 > uni['rect'].x0:
                    if my_drive_link is None or d_link['rect'].x0 < my_drive_link['rect'].x0:
                        my_drive_link = d_link
            
            if my_drive_link:
                results[my_region].append({
                    'name': uni['name'],
                    'drive_url': my_drive_link['uri']
                })
    
    with open('all_links.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"추출 완료: all_links.json 생성됨")

if __name__ == '__main__':
    extract_all_university_links()
