import wikipedia

wikipedia.set_lang("vi")

def get_wiki_full_info(wiki_endpoint):
    if not wiki_endpoint: return None
    page_title = wiki_endpoint.split(':')[-1]
    
    try:
        # Tải toàn bộ trang (Page Object)
        # auto_suggest=False để tránh nó tự đoán sai sang trang khác
        page = wikipedia.page(page_title, auto_suggest=False)
        
        return {
            "title": page.title,
            "url": page.url,
            "summary": page.summary, # Tóm tắt ngắn
            "content": page.content, # Toàn bộ nội dung văn bản
            "images": page.images,   # Danh sách các link ảnh trong bài
        }

    except wikipedia.exceptions.DisambiguationError as e:
        # print(f"Lỗi: Từ khóa '{page_title}' chưa rõ ràng. Các gợi ý: {e.options[:5]}")
        return None
    except wikipedia.exceptions.PageError:
        # print(f"Lỗi: Không tìm thấy trang '{page_title}' trên Wikipedia.")
        return None
    except Exception as e:
        # print(f"Lỗi không xác định: {e}")
        return None

# info = get_wiki_full_info("vi:Nhà thờ Phùng Khoang")

# if info:
    print(f"=== TIÊU ĐỀ: {info['title']} ===")
    print(f"🔗 Link: {info['url']}")
    print("-" * 50)
    
    # In ra 500 ký tự đầu tiên của nội dung để xem thử
    print("NỘI DUNG (Trích đoạn):")
    print(info['content']) 
    
    print("-" * 50)
    print(f"📸 Tìm thấy {len(info['images'])} ảnh. Ảnh đầu tiên:")
    if info['images']:
        print(info['images'][0])