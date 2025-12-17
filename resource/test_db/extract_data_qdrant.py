import pandas as pd
import json
import sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tqdm import tqdm

# Ensure project root is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.wiki import get_wiki_full_info

file_path = '/media/sda3/startup/hanoi_places_osm.csv'
out_path = '/media/sda3/startup/wiki_info.json'
not_found = '/media/sda3/startup/wiki_info_not_found.json'

# Lock để đồng bộ khi thêm vào list
data_lock = Lock()
all_data = []
not_found_data = []

def process_place(name, address, place_id, osm_id):
    """Hàm xử lý một địa điểm"""
    try:
        wiki_endpoint = ""
        if 'bank' in name.lower():
            wiki_endpoint = f"vi:{name} {address}"
        else:
            wiki_endpoint = f"vi:{name}"
        
        data_extract = get_wiki_full_info(wiki_endpoint)
        
        with data_lock:
            if data_extract:
                data_extract['id'] = f"{place_id}_{osm_id}"
                all_data.append(data_extract)
            else:
                not_found_data.append({
                    'place_id': place_id,
                    'osm_id': osm_id,
                    'name': name,
                    'address': address,
                })
        
        return True
    except Exception as e:
        print(f"Lỗi khi xử lý {name}: {e}")
        return False

def split_and_preserve_empty(value, delimiter=';'):
    """Split giá trị và giữ nguyên vị trí các giá trị rỗng"""
    if pd.isna(value):
        return []
    parts = str(value).split(delimiter)
    # Strip whitespace nhưng giữ nguyên empty strings
    return [p.strip() for p in parts]

def main():
    try:
        df = pd.read_csv(file_path)
        
        # Tạo danh sách tasks bằng cách xử lý từng hàng
        tasks = []
        
        for idx, row in df.iterrows():
            # Split các giá trị và giữ nguyên empty strings
            names = split_and_preserve_empty(row.get('name', ''))
            addresses = split_and_preserve_empty(row.get('address', ''))
            place_ids = split_and_preserve_empty(row.get('place_id', ''))
            osm_ids = split_and_preserve_empty(row.get('osm_id', ''))
            
            # Tìm độ dài tối đa
            max_len = max(len(names), len(addresses), len(place_ids), len(osm_ids))
            
            # Nếu tất cả đều rỗng thì skip
            if max_len == 0:
                continue
            
            # Pad các list ngắn hơn với empty string
            names += [''] * (max_len - len(names))
            addresses += [''] * (max_len - len(addresses))
            place_ids += [''] * (max_len - len(place_ids))
            osm_ids += [''] * (max_len - len(osm_ids))
            
            # Tạo tasks từ các giá trị đã được align
            for name, address, place_id, osm_id in zip(names, addresses, place_ids, osm_ids):
                # Chỉ thêm nếu name không rỗng (vì name là trường quan trọng nhất)
                if name:
                    tasks.append((
                        name,
                        address if address else '',  # Dùng empty string nếu rỗng
                        place_id if place_id else '',
                        osm_id if osm_id else ''
                    ))
        
        print(f"Total tasks: {len(tasks)}")
        
        # Sử dụng ThreadPoolExecutor với số workers tùy chỉnh
        max_workers = 10  # Có thể điều chỉnh số lượng threads
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tất cả tasks
            futures = {
                executor.submit(process_place, name, address, place_id, osm_id): (name, address)
                for name, address, place_id, osm_id in tasks
            }
            
            # Hiển thị progress bar
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
                try:
                    future.result()
                except Exception as e:
                    name, address = futures[future]
                    print(f"Exception for {name}: {e}")
        
        print(f"\nTotal extracted wiki info: {len(all_data)}")
        print(f"Total not found: {len(not_found_data)}")
        
        # Ghi kết quả ra file
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        with open(not_found, 'w', encoding='utf-8') as f:
            json.dump(not_found_data, f, ensure_ascii=False, indent=4)
        
        print(f"Đã lưu kết quả vào {out_path} và {not_found}")
        
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại {file_path}")
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
