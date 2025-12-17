# embed_service.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel

app = FastAPI()

MODEL_NAME = "AITeamVN/Vietnamese_Embedding"  
MAX_LENGTH = 1024

class BatchRequest(BaseModel):
    texts: List[str]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

@app.post("/embed")
def embed_batch(req: BatchRequest):
    with torch.no_grad():
        inputs = tokenizer(
            req.texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=MAX_LENGTH
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy().tolist()
        return {"embeddings": embeddings}
