import fitz  # PyMuPDF
import os
import pandas as pd
import re

def extract_info_from_pdf(file_path):
    """
    PDF 파일에서 텍스트를 분석하여 핵심 전형 정보를 추출합니다.
    (키워드 기반의 확률적 추출 방식)
    """
    try:
        doc = fitz.open(file_path)
        # 보통 시행계획의 앞부분(1~15페이지)에 요약표가 위치함
        search_limit = min(15, len(doc))
        text_content = ""
        for i in range(search_limit):
            text_content += doc[i].get_text()
        doc.close()

        # 1. 수능 최저학력기준 유무 판별
        # '수능 최저', '최저학력기준' 등의 단어가 '미적용', '없음'과 결합되는지 확인
        has_csat = "없음"
        if "최저학력기준" in text_content or "수능 최저" in text_content:
            # 주변에 '미적용'이나 '없음'이 있는지 확인 (단순 키워드 매칭)
            if not re.search(r"(최저|수능).*?(미적용|없음|단,)", text_content):
                has_csat = "있음"

        # 2. 면접 유무 판별
        has_interview = "없음"
        if "면접" in text_content:
            if not re.search(r"면접.*?(미적용|없음|단계별 전형 제외)", text_content):
                has_interview = "있음"

        # 3. 전형 유형 판별 (파일 내용에서 가장 많이 언급되는 유형)
        admission_type = "학생부교과/종합"
        if text_content.count("교과") > text_content.count("종합"):
            admission_type = "학생부교과"
        elif text_content.count("종합") > text_content.count("교과"):
            admission_type = "학생부종합"

        # 4. 내신 반영 비율 (단순 추출)
        record_ratio = "100%"
        match = re.search(r"학생부.*?(\d{1,3})%", text_content)
        if match:
            record_ratio = f"{match.group(1)}%"

        return {
            "수능최저": has_csat,
            "면접": has_interview,
            "전형유형": admission_type,
            "내신반영": record_ratio
        }
    except Exception as e:
        return None

def build_database():
    regions = [
        "서울특별시", "인천광역시", "경기도", "강원특별자치도", "충청북도", "충청남도", 
        "전북특별자치도", "전라남도", "광주광역시", "경상북도", "경상남도", 
        "대구광역시", "부산광역시", "울산광역시", "제주특별자치도", 
        "대전광역시", "세종특별자치시", "특수목적대학"
    ]
    
    all_data = []
    
    print("데이터 추출을 시작합니다. 잠시만 기다려 주세요...")
    
    for region in regions:
        if not os.path.exists(region):
            continue
            
        files = [f for f in os.listdir(region) if f.endswith(".pdf")]
        for file in files:
            university_name = file.replace(".pdf", "").split("_")[0] # '명지대_1' 같은 경우 처리
            file_path = os.path.join(region, file)
            
            print(f"분석 중: [{region}] {university_name}")
            info = extract_info_from_pdf(file_path)
            
            if info:
                row = {
                    "대학명": university_name,
                    "지역": region,
                    "전형유형": info["전형유형"],
                    "수능최저": info["수능최저"],
                    "면접": info["면접"],
                    "내신반영": info["내신반영"],
                    "모집인원": 100 # 모집인원은 표 구조가 복잡하여 기본값 100으로 설정 (추후 정밀 분석 가능)
                }
                all_data.append(row)
    
    df = pd.DataFrame(all_data)
    df.to_csv("university_data.csv", index=False, encoding="utf-8-sig")
    print(f"\n총 {len(all_data)}개 대학 데이터 추출 완료! university_data.csv 생성됨.")

if __name__ == "__main__":
    build_database()
