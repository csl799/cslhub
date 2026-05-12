from typing import List
from sentence_transformers import SentenceTransformer,CrossEncoder
import chromadb

embedding_model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
cross_encoder = CrossEncoder("BAAI/bge-reranker-v2-m3")
chromadb_client = chromadb.EphemeralClient()
chromadb_collection = chromadb_client.get_or_create_collection(name="default")


# 索引部分
def split_to_chunks(doc_file:str) -> List[str]:
    """将文件内容按段落分片"""
    with open(doc_file,"r") as f:
        content = f.read()
        return [chunk for chunk in content.split("\n\n")]

def embed_chunk(chunk:str) -> List[float]:
    """将分片向量化"""
    embedding = embedding_model.encode(chunk)
    return embedding.tolist()

def save_embeddings(chunks:List[str],embeddings:List[List[float]]) -> None:
    """将所有的片段内容和对应的向量存入向量数据库"""
    ids = [str(i) for i in range(len(chunks))]
    chromadb_collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )


# 召回 重排 生成
def retrieve(query:str,top_k:int) -> List[str]:
    """返回与用户内容最相似的前top_k个结果"""
    query_embedding = embed_chunk(query)
    results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results["documents"][0]

def rerank(query:str,retrieved_chunks:List[str],top_k:int) -> List[str]:
    """对召回的结果进行评估重排相似度，返回前top_k个相似度最高结果"""
    pairs = [(query,chunk) for chunk in retrieved_chunks]
    scores = cross_encoder.predict(pairs)

    chunk_with_score_list = [(chunk,score)
                             for chunk,score in zip(retrieved_chunks,scores)]
    chunk_with_score_list.sort(key=lambda pair:pair[1],reverse=True)
    return [chunk for chunk,_ in chunk_with_score_list][:top_k]