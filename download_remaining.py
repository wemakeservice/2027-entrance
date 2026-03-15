import json
import os
import time
import random
import requests
import re

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    # 브라우저처럼 보이게 하기 위한 헤더
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def download_remaining_files():
    with open('links.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 인천광역시와 경기도만 대상으로 함
    target_regions = ["인천광역시", "경기도"]
    
    for region in target_regions:
        universities = data.get(region, [])
        os.makedirs(region, exist_ok=True)
        
        print(f"\n--- [{region}] 다운로드 시작 ---")
        
        for uni in universities:
            name = uni['name']
            url_string = uni['drive_url']
            urls = [u.strip() for u in url_string.split(',')]
            
            for i, u in enumerate(urls):
                safe_name = name.replace('/', '_').replace(':', '_').replace('?', '_').replace('"', '')
                if len(urls) > 1:
                    safe_name = f"{safe_name}_{i+1}"
                
                output_path = os.path.join(region, f"{safe_name}.pdf")
                
                if not os.path.exists(output_path):
                    # URL에서 File ID 추출
                    match = re.search(r'/d/([^/]+)', u)
                    if not match:
                        match = re.search(r'id=([^&]+)', u)
                    
                    if match:
                        file_id = match.group(1)
                        print(f"다운로드 중: {safe_name}...", end=" ", flush=True)
                        try:
                            download_file_from_google_drive(file_id, output_path)
                            print("완료")
                            # 구글의 차단을 피하기 위해 무작위 대기 (3~7초)
                            time.sleep(random.uniform(3, 7))
                        except Exception as e:
                            print(f"실패 ({e})")
                    else:
                        print(f"ID 추출 실패: {u}")
                else:
                    print(f"이미 존재함: {safe_name}")

if __name__ == '__main__':
    download_remaining_files()
