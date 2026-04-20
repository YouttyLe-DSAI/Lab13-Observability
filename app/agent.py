from __future__ import annotations

import os
import time
from dataclasses import dataclass

from . import metrics
from .llm import OpenAILLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text

# Sử dụng Langfuse Client v4 chuẩn
try:
    from langfuse import Langfuse
    langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST") or "https://eu.cloud.langfuse.com"
    )
    HAS_LANGFUSE = True
except Exception:
    HAS_LANGFUSE = False

@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float

class LabAgent:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.llm = OpenAILLM(model=model)

    def run(self, user_id: str, feature: str, session_id: str, message: str, turbo_mode: bool = False) -> AgentResult:
        started = time.perf_counter()
        docs = retrieve(message)
        
        # Optimization: Turbo mode uses a more concise prompt
        if turbo_mode:
            system_prompt = "You are a concise AI. Answer in 1 short sentence using the context."
            prompt = f"Context: {docs}\nQuestion: {message}"
        else:
            system_prompt = "You are a helpful AI assistant. Use the following context to answer the user request in detail."
            prompt = f"Feature={feature}\nSession={session_id}\nContext={docs}\n\nUser Question: {message}"
        
        response = self.llm.generate(prompt, system_prompt=system_prompt)
        
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)

        # Gửi dữ liệu Tracing theo chuẩn v4
        if HAS_LANGFUSE:
            try:
                # Trong v4, dùng start_as_current_observation để tạo Trace/Span gốc
                with langfuse_client.start_as_current_observation(
                    name="chat-processing",
                    input=message,
                    metadata={
                        "user_id_hash": hash_user_id(user_id),
                        "session_id": session_id,
                        "model": self.model,
                        "feature": feature,
                        "turbo_mode": turbo_mode,
                        "cost": cost_usd
                    }
                ) as trace:
                    trace.update(
                        output=response.text,
                        usage_details={
                            "input": response.usage.input_tokens,
                            "output": response.usage.output_tokens
                        }
                    )
            except Exception as e:
                print(f"⚠️ Tracing Error: {e}")

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Tính toán chi phí dựa trên model và số lượng token thực tế."""
        if self.model == "gpt-4o-mini":
            # $0.15 / 1M input, $0.60 / 1M output
            input_cost = (tokens_in / 1_000_000) * 0.15
            output_cost = (tokens_out / 1_000_000) * 0.60
        elif self.model == "gpt-4o":
            # $5.00 / 1M input, $15.00 / 1M output
            input_cost = (tokens_in / 1_000_000) * 5.0
            output_cost = (tokens_out / 1_000_000) * 15.0
        else:
            # Default fallback (claude-sonnet style pricing)
            input_cost = (tokens_in / 1_000_000) * 3.0
            output_cost = (tokens_out / 1_000_000) * 15.0
        
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
