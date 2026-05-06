import os
import asyncio
import json
import chromadb
from typing import AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import redis.asyncio as redis
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles


load_dotenv()

# ---------- 配置 ----------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
RATE_LIMIT = 10        # 每分钟最多 10 次请求
RATE_WINDOW = 60       # 窗口 60 秒

@asynccontextmanager
async def lifespan(app: FastAPI):
    if collection.count() > 0:
        print("已有数据跳过索引")
    try:
        with open("fastapi_docs.txt", "r", encoding="utf-8") as f:
            content = f.read()
        chunks = split_text(content, chunk_size=300, overlap=50)
        embeddings = embed_model.encode(chunks).tolist()
        ids = [f"doc_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings, ids=ids)
        print(f"索引完成，共 {len(chunks)} 块")
    except FileNotFoundError:
        print("未找到 fastapi_docs.txt，跳过索引")

    yield

app = FastAPI(title="AI Chat + RAG Demo",lifespan=lifespan)

app.mount("/static111", StaticFiles(directory="static111"), name="static")

# Redis 连接（启动时创建）
redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

# ----- 向量检索引擎 -----
EMBED_MODEL_NAME = "BAAI/bge-small-zh"
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="fastapi_docs")

# ---------- 请求体 ----------
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户问题")

# ---------- 速率限制中间件 ----------
async def check_rate_limit(user_id: str) -> None:
    """简单的计数器限流，每个 user_id 每分钟最多 RATE_LIMIT 次"""
    key = f"rate_limit:{user_id}"
    current = await redis_client.get(key)
    if current is None:
        await redis_client.setex(key, RATE_WINDOW, 1)
    elif int(current) < RATE_LIMIT:
        await redis_client.incr(key)
    else:
        ttl = await redis_client.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请在 {ttl} 秒后重试"
        )


# ----- 检索上下文 -----
def retrieve_context(query: str, top_k: int = 3) -> str:
    query_embedding = embed_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents"]
    )
    docs = results["documents"][0]
    return "\n\n".join(docs)


# ---------- 流式生成器 ----------
async def generate_stream(message: str,context:str = "") -> AsyncGenerator[str, None]:
    """
    调用 DeepSeek API，将每个 chunk 的文本以 SSE 格式 yield
    """
    system_content = (
        "你是一个有帮助的助手。请根据以下参考信息回答问题。"
        "如果参考信息不足以回答，请诚实告知。\n\n"
        "参考信息：\n" + context
    )
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message}
        ],
        "stream": True,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream(
            "POST",
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                yield f"data: {json.dumps({'error': {'message': error_text.decode()}})}\n\n"
                yield "data: [DONE]\n\n"
                return


            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]   # 去掉 "data: " 前缀
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield f"data: {json.dumps({'content': content},ensure_ascii=False)}\n\n"
                    except Exception:
                        continue

    yield "data: [DONE]\n\n"

# ---------- 路由 ----------
@app.post("/chat")
async def chat(request: ChatRequest, http_request: Request):
    # 1. 获取用户标识（简单用客户端 IP，生产建议用 JWT 中的 user_id）
    user_id = http_request.client.host if http_request.client else "unknown"

    # 2. 速率检查
    await check_rate_limit(user_id)

    # 3. 检索相关文档
    context = retrieve_context(request.message, top_k=3)

    # 4. 返回流式响应
    return StreamingResponse(
        generate_stream(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",   # 禁用 Nginx 缓冲
        }
    )

# ----- 启动时索引文档 -----
def split_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

