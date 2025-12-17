import pandas as pd
import json
import sys, os

# Ensure project root is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.wiki import get_wiki_full_info
# Đường dẫn đến file CSV của bạn
file_path = '/media/sda3/startup/hanoi_places_osm.csv'
out_path = '/media/sda3/startup/wiki_info.json'
try:
    df = pd.read_csv(file_path)

    all_name_address = df['name'].dropna().str.split(';').explode().str.strip()
    all_address = df['address'].dropna().str.split(';').explode().str.strip()
    print("len(all_name_address)):", len(all_name_address))
    from tqdm import tqdm
    for name, address in tqdm(zip(all_name_address, all_address),desc="Processing", total=len(all_name_address)):
        if 'bank' in name.lower():
            wiki_endpoint = f"vi:{name} {address}"
            print("wiki_endpoint:", wiki_endpoint)
            print(get_wiki_full_info(wiki_endpoint))

except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file tại {file_path}")
except Exception as e:
    print(f"Lỗi: {e}")