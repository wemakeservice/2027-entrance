from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os

app = FastAPI(title="2027 Admissions Navigator API")

# 프론트엔드 연동을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 개발 중에는 모두 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 로드 함수
def load_data():
    csv_path = "../university_data.csv"
    json_path = "../all_links.json"
    
    # CSV 읽기
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # nan 값을 None으로 변경 (JSON 변환을 위해)
        df = df.where(pd.notnull(df), None)
        universities = df.to_dict(orient="records")
    else:
        universities = []

    # JSON 링크 읽기
    links_dict = {}
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)
            for region, unis in links_data.items():
                for uni in unis:
                    # 대학명을 키로 하여 URL 저장 (가장 첫 번째 URL만 사용)
                    urls = [u.strip() for u in uni['drive_url'].split(',')]
                    links_dict[uni['name']] = urls[0] if urls else ""
    
    # CSV 데이터에 링크 정보 병합
    for uni in universities:
        # 명지대_1 같은 이름에서 실제 대학명 추출 시도
        original_name = uni['대학명'].split('_')[0]
        uni['drive_url'] = links_dict.get(original_name, "")
        
    return universities

# 메모리에 데이터 캐싱
UNIVERSITIES_DATA = load_data()

@app.get("/api/universities")
def get_universities():
    """
    모든 대학의 전형 정보 및 PDF 링크를 반환합니다.
    """
    return {"data": UNIVERSITIES_DATA}

@app.get("/api/regions")
def get_regions():
    """
    고유 지역 목록을 반환합니다.
    """
    regions = sorted(list(set(u["지역"] for u in UNIVERSITIES_DATA if u["지역"])))
    return {"data": regions}

@app.get("/api/admission-types")
def get_admission_types():
    """
    고유 전형 유형 목록을 반환합니다.
    """
    types = sorted(list(set(u["전형유형"] for u in UNIVERSITIES_DATA if u["전형유형"])))
    return {"data": types}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
