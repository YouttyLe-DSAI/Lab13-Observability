from __future__ import annotations

import os
from typing import Any
from openai import OpenAI
from dataclasses import dataclass

@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int

@dataclass
class LLMResponse:
    text: str
    usage: LLMUsage
    model: str

class OpenAILLM:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            
            text = response.choices[0].message.content or ""
            usage = LLMUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
            return LLMResponse(text=text, usage=usage, model=self.model)
        except Exception as e:
            # Re-raise to be caught by the agent/app for logging
            raise e
