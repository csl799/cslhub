from fastapi import FastAPI,Request,HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from RAG_function import *

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    chunks = split_to_chunks("")
    embeddings = [embed_chunk(chunk) for chunk in chunks]
    save_embeddings(chunks,embeddings)
    yield


app = FastAPI(title="",lifespan=lifespan)