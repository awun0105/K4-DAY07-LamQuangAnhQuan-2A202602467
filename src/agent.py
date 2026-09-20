from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."
            
        context_parts = []
        for i, res in enumerate(results, 1):
            source = res["metadata"].get("doc_id", "unknown source")
            content = res["content"]
            context_parts.append(f"[{i}] (Nguồn: {source}):\n{content}")
            
        context_str = "\n\n".join(context_parts)
        
        prompt = (
            f"Dựa vào các ngữ cảnh được cung cấp bên dưới, hãy trả lời câu hỏi: '{question}'.\n"
            f"Yêu cầu: Chỉ sử dụng thông tin trong ngữ cảnh. Khi sử dụng thông tin, phải trích dẫn số thứ tự của ngữ cảnh (ví dụ: [1]).\n"
            f"Nếu không có đủ thông tin, hãy nói 'Tôi không tìm thấy thông tin trong tài liệu'.\n\n"
            f"Ngữ cảnh:\n{context_str}"
        )
        
        return self.llm_fn(prompt)
