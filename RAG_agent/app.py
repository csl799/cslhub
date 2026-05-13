from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """占位生命周期；向量索引由 CLI Agent 的 rag_knowledge 在检索时维护。"""
    yield


app = FastAPI(title="rag-agent", lifespan=lifespan)