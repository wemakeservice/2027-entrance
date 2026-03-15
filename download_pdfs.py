import json
import os
import gdown

def download_files():
    with open('links.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for region, universities in data.items():
        os.makedirs(region, exist_ok=True)
        
        for uni in universities:
            url_string = uni['drive_url']
            urls = [u.strip() for u in url_string.split(',')]
            
            for i, u in enumerate(urls):
                name = uni['name']
                safe_name = name.replace('/', '_').replace(':', '_').replace('?', '_').replace('"', '')
                
                if len(urls) > 1:
                    safe_name = f"{safe_name}_{i+1}"
                
                output_path = os.path.join(region, f"{safe_name}.pdf")
                
                # 이미 다운로드된 파일은 건너뜀
                if not os.path.exists(output_path):
                    print(f"재시도 중: [{region}] {safe_name}")
                    try:
                        # id 대신 전체 url과 fuzzy=True 옵션을 사용해 우회 시도
                        gdown.download(url=u, output=output_path, quiet=True, fuzzy=True)
                    except Exception as e:
                        print(f"{safe_name} 다운로드 실패: {e}")

if __name__ == '__main__':
    download_files()
