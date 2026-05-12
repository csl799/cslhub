"""
Agent 侧 RAG：从项目目录下的 knowledge_docs 读取 .txt / .md，持久化向量索引，
由工具 search_knowledge_base 供 ReActAgent 调用。
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _round_mtime(ts: float) -> float:
    return round(ts, 6)


class KnowledgeIndexer:
    """按 knowledge_docs 文件变更增量感知；变更后全量重建 Chroma 集合。"""

    def __init__(self, project_root: str | Path) -> None:
        # 绑定项目根路径，并确定知识库文档目录与 Chroma 持久化目录。
        self.project_root = Path(project_root).resolve()
        self.docs_dir = self.project_root / "knowledge_docs"
        self.chroma_dir = self.project_root / ".rag_chroma"
        self.state_path = self.chroma_dir / "index_state.json"
        self._client: Any = None
        self._collection: Any = None
        self._embed_model: Any = None
        self._reranker: Any = None

    def _ensure_dirs(self) -> None:
        # 若不存在则创建知识库目录与向量库目录。
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    def _scan_docs(self) -> dict[str, float]:
        # 扫描 knowledge_docs 下所有 .txt/.md，返回「相对路径 → 修改时间」指纹表。
        if not self.docs_dir.is_dir():
            return {}
        out: dict[str, float] = {}
        for p in self.docs_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".txt", ".md"):
                rel = p.relative_to(self.docs_dir).as_posix()
                out[rel] = _round_mtime(p.stat().st_mtime)
        return out

    def _read_state(self) -> dict[str, float] | None:
        # 读取上次成功索引后保存的文档指纹，用于判断是否需要重建。
        if not self.state_path.is_file():
            return None
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            return {k: _round_mtime(float(v)) for k, v in raw.items()}
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return None

    def _write_state(self, fp: dict[str, float]) -> None:
        # 将当前文档指纹写入磁盘，供下次与扫描结果比对。
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(fp, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_embedder(self) -> None:
        # 懒加载句向量模型，用于文档与查询的向量化。
        if self._embed_model is None:
            from sentence_transformers import SentenceTransformer

            self._embed_model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

    def _load_reranker(self) -> None:
        # 懒加载交叉编码器，用于对召回片段按与查询的相关性重排。
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def _get_collection(self) -> Any:
        # 获取或打开持久化 Chroma 集合（agent_kb）。
        if self._collection is not None:
            return self._collection
        import chromadb

        self._ensure_dirs()
        self._client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self._collection = self._client.get_or_create_collection(
            name="agent_kb",
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    def _chunk_file(self, rel: str, text: str) -> list[tuple[str, str]]:
        # 将单个文件正文按段落与最大长度切成多条，并生成稳定 chunk id。
        parts = [p.strip() for p in text.split("\n\n")]
        chunks: list[str] = []
        max_len = 1200
        for para in parts:
            if not para:
                continue
            while para:
                piece = para[:max_len]
                chunks.append(piece)
                para = para[max_len:].lstrip()
        h = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:16]
        return [(f"{h}_{i}", c) for i, c in enumerate(chunks)]

    def _rebuild_index(self, fp: dict[str, float]) -> None:
        # 清空并重建向量索引：按当前指纹重新分片、嵌入并写入 Chroma。
        import chromadb

        self._ensure_dirs()
        self._load_embedder()

        self._client = chromadb.PersistentClient(path=str(self.chroma_dir))
        try:
            self._client.delete_collection("agent_kb")
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name="agent_kb",
            metadata={"hnsw:space": "cosine"},
        )

        if not fp:
            self._write_state({})
            return

        all_ids: list[str] = []
        all_docs: list[str] = []
        all_meta: list[dict[str, str]] = []

        for rel in sorted(fp.keys()):
            path = self.docs_dir / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for cid, chunk in self._chunk_file(rel, text):
                all_ids.append(cid)
                all_docs.append(chunk)
                all_meta.append({"source": rel})

        if not all_docs:
            self._write_state(fp)
            return

        embeddings = self._embed_model.encode(
            all_docs,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        self._collection.add(
            ids=all_ids,
            documents=all_docs,
            embeddings=embeddings.tolist(),
            metadatas=all_meta,
        )
        self._write_state(fp)

    def ensure_fresh(self) -> None:
        # 若磁盘上文档指纹与上次索引不一致，则触发全量重建。
        fp = self._scan_docs()
        prev = self._read_state()
        if prev is not None and prev == fp:
            self._get_collection()
            return
        self._rebuild_index(fp)

    def search(self, query: str, top_k: int = 5) -> str:
        # 保证索引最新后做向量召回与重排，返回格式化的文本片段供模型阅读。
        q = (query or "").strip()
        if not q:
            return "（检索失败：查询为空。）"

        self.ensure_fresh()
        fp = self._scan_docs()
        if not fp:
            return (
                "（知识库目录 knowledge_docs 中暂无 .txt 或 .md 文档；"
                "将文档放入该目录后会自动在下次检索时建立索引。）"
            )

        coll = self._get_collection()
        try:
            n_total = coll.count()
        except Exception:
            n_total = 0

        if n_total == 0:
            return (
                "（索引为空：请确认 knowledge_docs 下存在非空 UTF-8 文本，"
                "保存后再次调用本工具。）"
            )

        self._load_embedder()
        self._load_reranker()

        retrieve_k = min(max(top_k * 4, 12), max(n_total, 1))
        q_emb = self._embed_model.encode(q, convert_to_numpy=True).tolist()
        raw = coll.query(
            query_embeddings=[q_emb],
            n_results=retrieve_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = raw.get("documents", [[]])[0] or []
        metas = raw.get("metadatas", [[]])[0] or []

        if not docs:
            return "（未从向量库中召回到片段，可尝试改写查询或扩充知识库文档。）"

        pairs = [(q, d) for d in docs]
        scores = self._reranker.predict(pairs)
        order = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]

        blocks: list[str] = []
        for rank, i in enumerate(order, start=1):
            src = ""
            if i < len(metas) and metas[i]:
                src = metas[i].get("source", "") or ""
            head = f"[片段{rank}]"
            if src:
                head += f" 来源:{src}"
            blocks.append(f"{head}\n{docs[i]}")
        return "\n\n".join(blocks)


def build_search_knowledge_base_tool(project_root: str | Path) -> Callable[..., str]:
    """返回供 ReActAgent 注册的检索函数（闭包绑定 project_root）。"""

    indexer = KnowledgeIndexer(project_root)

    def search_knowledge_base(query: str, top_k: int = 5) -> str:
        """
        在本地知识库（knowledge_docs 目录下的 .txt/.md）中做语义检索并返回相关片段。
        当用户问题涉及项目/领域事实、政策、内部约定、文档内容等需要「有据可查」时使用；
        纯闲聊、纯数学推理、与知识库无关的通用常识可不调用。
        参数请使用位置参数，例如：search_knowledge_base("你的问题", 5) 或 search_knowledge_base("你的问题")。
        """
        tk = top_k
        if isinstance(tk, str):
            try:
                tk = int(float(tk.strip()))
            except ValueError:
                tk = 5
        elif not isinstance(tk, int):
            try:
                tk = int(tk)
            except (TypeError, ValueError):
                tk = 5
        tk = max(1, min(tk, 20))
        return indexer.search(str(query), tk)

    return search_knowledge_base
