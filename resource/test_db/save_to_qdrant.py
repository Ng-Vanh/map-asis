import os
import torch
import uuid
import json
import gc
from tqdm import tqdm
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams


class VietnameseEmbeddingModel:
    def __init__(self, model_name='AITeamVN/Vietnamese_Embedding', max_length=1024):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.max_length = max_length

    def encode(self, texts: List[str]) -> List[List[float]]:
        with torch.no_grad():
            inputs = self.tokenizer(texts, padding=True, truncation=True,
                                    return_tensors='pt', max_length=self.max_length)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token
            return embeddings.cpu().tolist()


def count_tokens(text: str) -> int:
    return len(embedding_model.tokenizer(text)["input_ids"])


def chunk_text(text: str, max_tokens: int = 1024, min_remaining_tokens: int = 96) -> List[str]:
    sentences = text.split(". ")
    chunks, current_chunk = [], ""

    for sentence in sentences:
        candidate_chunk = current_chunk + sentence + ". "
        if count_tokens(candidate_chunk) <= max_tokens:
            current_chunk = candidate_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk and count_tokens(current_chunk) >= min_remaining_tokens:
        chunks.append(current_chunk.strip())

    return chunks


def save_to_qdrant(
    embedding_model: VietnameseEmbeddingModel, 
    chunks: List[str], 
    doc_id: str,
    metadata: Dict
):
    """
    Lưu chunks vào Qdrant với metadata đầy đủ
    
    Args:
        embedding_model: Model embedding
        chunks: Danh sách các chunk text
        doc_id: ID gốc từ document JSON
        metadata: Dictionary chứa metadata (title, url, summary, images, etc.)
    """
    # Kiểm tra chunks có rỗng không
    if not chunks:
        print(f" Document {doc_id} không có chunks, bỏ qua")
        return
    
    try:
        vectors = embedding_model.encode(chunks)
        
        # Kiểm tra vectors có khớp với chunks không
        if len(vectors) != len(chunks):
            print(f" Lỗi: số vectors ({len(vectors)}) != số chunks ({len(chunks)}) cho doc {doc_id}")
            return
        
        points = []
        
        for idx, (vec, txt) in enumerate(zip(vectors, chunks)):
            # Tạo payload đầy đủ với metadata
            payload = {
                # Text chunk
                "text": txt,
                "chunk_index": idx,
                
                # Document info
                "document_id": doc_id,
                "title": metadata.get("title", ""),
                "url": metadata.get("url", ""),
                "summary": metadata.get("summary", ""),
                
                # Images (quan trọng!)
                "images": metadata.get("images", []),
                "image_count": len(metadata.get("images", [])),
                
                # Additional metadata (optional)
                "has_images": len(metadata.get("images", [])) > 0
            }
            
            # Thêm các trường tùy chọn nếu có
            if "categories" in metadata:
                payload["categories"] = metadata["categories"]
            
            if "tags" in metadata:
                payload["tags"] = metadata["tags"]
            
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec,
                    payload=payload
                )
            )
        
        client.upsert(collection_name="map_assistant_v2", points=points)
        print(f"✓ Saved {len(points)} chunks for doc {doc_id} (images: {len(metadata.get('images', []))})")
        
    except Exception as e:
        print(f" Lỗi khi lưu doc {doc_id} lên Qdrant: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'vectors' in locals():
            del vectors
        if 'points' in locals():
            del points
        torch.cuda.empty_cache()
        gc.collect()


def run(path: str, batch_size: int = 8):
    """
    Xử lý file JSON và lưu vào Qdrant với metadata đầy đủ
    
    Args:
        path: Đường dẫn file JSON
        batch_size: Số lượng documents xử lý cùng lúc
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_chunks = 0
    skipped_docs = 0
    total_images = 0

    print(f"\n{'='*80}")
    print(f" Đang xử lý {len(data)} documents từ {path}")
    print(f"{'='*80}\n")

    for i in tqdm(range(0, len(data), batch_size), desc="Processing batches"):
        batch = data[i:i + batch_size]
        
        for item in batch:
            # Lấy ID từ document
            doc_id = item.get("id", None)
            
            if not doc_id:
                skipped_docs += 1
                continue
            
            # Lấy content
            text_content = item.get("content", "")
            
            # Kiểm tra content có hợp lệ không
            if not text_content or not isinstance(text_content, str):
                skipped_docs += 1
                continue
            
            # Kiểm tra content có đủ dài không (tránh content quá ngắn)
            if len(text_content.strip()) < 10:
                skipped_docs += 1
                continue
            
            # Chunk text
            chunks = chunk_text(text_content)
            
            # Chỉ lưu nếu có chunks
            if chunks:
                # Chuẩn bị metadata
                metadata = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "summary": item.get("summary", ""),
                    "images": item.get("images", [])  # Lấy danh sách images
                }
                
                # Đếm images
                total_images += len(metadata["images"])
                
                # Lưu vào Qdrant
                total_chunks += len(chunks)
                save_to_qdrant(embedding_model, chunks, doc_id, metadata)
            else:
                skipped_docs += 1

    print(f"\n{'='*80}")
    print(f"THỐNG KÊ KẾT QUẢ")
    print(f"{'='*80}")
    print(f"Tổng số chunks đã xử lý: {total_chunks}")
    print(f"tổng số images: {total_images}")
    print(f"Số documents bị bỏ qua: {skipped_docs}")
    print(f"{'='*80}\n")


def init_qdrant():
    """Khởi tạo collection Qdrant"""
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if "map_assistant_v2" not in existing:
        print("Tạo Qdrant collection: map_assistant_v2")
        client.create_collection(
            collection_name="map_assistant_v2",
            vectors_config=VectorParams(
                size=1024,            
                distance="Cosine"
            )
        )
        print("Collection đã được tạo")
    else:
        print("Collection 'map_assistant_v2' đã tồn tại")


def verify_data_sample():
    """Kiểm tra mẫu dữ liệu đã lưu"""
    print(f"\n{'='*80}")
    print(" KIỂM TRA MẪU DỮ LIỆU")
    print(f"{'='*80}\n")
    
    try:
        # Lấy 1 point ngẫu nhiên
        scroll_result = client.scroll(
            collection_name="map_assistant_v2_v2",
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        
        if scroll_result[0]:
            point = scroll_result[0][0]
            print(f" Point ID: {point.id}")
            print(f" Payload:")
            for key, value in point.payload.items():
                if key == "text":
                    # Hiển thị text ngắn gọn
                    text_preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"   • {key}: {text_preview}")
                elif key == "images":
                    # Hiển thị số lượng và một vài images
                    print(f"   • {key}: {len(value)} images")
                    for i, img in enumerate(value[:3], 1):
                        print(f"      {i}. {img}")
                    if len(value) > 3:
                        print(f"      ... và {len(value) - 3} images khác")
                else:
                    print(f"   • {key}: {value}")
        else:
            print("  Không tìm thấy dữ liệu trong collection")
            
    except Exception as e:
        print(f" Lỗi khi kiểm tra dữ liệu: {e}")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print(f"\n{'='*80}")
    print(" QDRANT DATA UPLOAD WITH METADATA")
    print(f"{'='*80}\n")
    
    # Khởi tạo model và client
    print("Đang khởi tạo embedding model...")
    embedding_model = VietnameseEmbeddingModel()
    
    print("Đang kết nối Qdrant...")
    client = QdrantClient(url="http://localhost:6333")
    
    # Khởi tạo collection
    init_qdrant()
    
    # Xử lý file
    file_path = "/media/sda3/Workspace/map-assis/wiki_info_clean.json"
    
    if not os.path.exists(file_path):
        print(f"File không tồn tại: {file_path}")
        exit(1)
    
    print(f"\nĐường dẫn file: {file_path}")
    
    # Xử lý
    run(file_path, batch_size=2)
    
    # Kiểm tra mẫu dữ liệu
    verify_data_sample()
    
    print("HOÀN TẤT!")