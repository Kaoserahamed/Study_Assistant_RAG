"""Gemini generation client used after retrieval."""
import asyncio
import os
from typing import AsyncGenerator

import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Get it from https://ai.google.dev/")

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
# Use gemini-3.5-flash - current stable model as of August 2026
# gemini-2.5-flash is no longer available to new users
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
MAX_CONTEXT_CHARS = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "14000"))


class LLMService:
    @staticmethod
    def _build_request(question: str, context: str) -> dict:
        trimmed_context = context[:MAX_CONTEXT_CHARS].strip()
        source_text = trimmed_context or "(No relevant passages were retrieved.)"
        return {
            "systemInstruction": {"parts": [{"text": (
                "You are a careful student assistant. Answer the question based only on the SOURCE PASSAGES provided. "
                "Do NOT invent facts, citations, or page numbers. "
                "Do NOT include [Source X] citations in your answer - the system handles citations separately. "
                "When sources contain raw data (tables, metrics, numbers), summarize the key findings rather than copying data verbatim. "
                "Extract insights and trends from data. Be concise and direct in your response."
            )}]},
            "contents": [{"role": "user", "parts": [{"text": (
                f"SOURCE PASSAGES:\n---\n{source_text}\n---\n\nQUESTION: {question.strip()}"
            )}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500},
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ],
        }

    @staticmethod
    def _response_text(result: dict) -> str:
        candidates = result.get("candidates") or []
        if not candidates:
            reason = result.get("promptFeedback", {}).get("blockReason", "no candidate returned")
            raise ValueError(f"Gemini could not generate a response ({reason}).")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            reason = candidates[0].get("finishReason", "empty response")
            raise ValueError(f"Gemini returned no answer ({reason}).")
        return text

    @staticmethod
    async def generate_response_async(prompt: str, context: str = "") -> str:
        if not prompt or not prompt.strip():
            raise ValueError("A question is required.")
        
        print(f"[LLM] === GENERATE RESPONSE (ASYNC) ===")
        print(f"[LLM] Prompt length: {len(prompt)}")
        print(f"[LLM] Context length: {len(context)}")
        print(f"[LLM] Context preview (first 300 chars): {context[:300] if context else '(empty)'}")
        
        url = f"{API_ENDPOINT}/{GEMINI_MODEL}:generateContent"
        headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
        payload = LLMService._build_request(prompt, context)
        
        print(f"[LLM] Sending {len(context[:MAX_CONTEXT_CHARS])} context chars to {GEMINI_MODEL}")
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            for attempt in range(3):
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code not in (429, 500, 502, 503, 504) or attempt == 2:
                    break
                await asyncio.sleep(2 ** attempt)
        if response.status_code != 200:
            detail = response.text[:500]
            raise RuntimeError(f"Gemini API request failed ({response.status_code}): {detail}")
        return LLMService._response_text(response.json())

    @staticmethod
    def generate_response(prompt: str, context: str = "") -> str:
        return asyncio.run(LLMService.generate_response_async(prompt, context))

    @staticmethod
    async def stream_response_async(prompt: str, context: str = "") -> AsyncGenerator[str, None]:
        # The application does not currently expose a streaming endpoint. Keeping one
        # response path avoids two prompts that can drift and produce inconsistent answers.
        yield await LLMService.generate_response_async(prompt, context)

    @staticmethod
    async def check_connection_async() -> bool:
        try:
            await LLMService.generate_response_async("Reply with OK.", "[Source 1] Connection test.")
            return True
        except Exception:
            return False

    @staticmethod
    def check_connection() -> bool:
        return asyncio.run(LLMService.check_connection_async())


llm_service = LLMService()
