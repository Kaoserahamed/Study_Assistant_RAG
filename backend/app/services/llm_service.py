# app/services/llm_service.py
import os
import requests
from typing import List, Generator
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Get it from https://ai.google.dev/")

# Use REST API directly for more stability
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"


class LLMService:
    """Service for interacting with Google's Gemini API via REST"""
    
    @staticmethod
    def _get_model() -> str:
        """Get available model name"""
        return "gemini-3.5-flash"
    
    @staticmethod
    def generate_response(prompt: str, context: str = "") -> str:
        """Generate response from Gemini
        
        Args:
            prompt: User's question
            context: Retrieved context from documents
            
        Returns:
            Generated response from the model
        """
        try:
            print(f"\n[LLM] === GENERATE RESPONSE ===")
            print(f"[LLM] Prompt: {prompt[:80]}...")
            print(f"[LLM] Context length: {len(context)} chars")
            print(f"[LLM] Model: gemini-3.5-flash")
            
            if context:
                print(f"[LLM] Context preview:")
                print(f"[LLM]   {context[:300]}...")
            else:
                print(f"[LLM] WARNING: NO CONTEXT PROVIDED TO LLM!")
            
            # Build the full prompt with context
            full_prompt = f"""Based on the following context from uploaded documents, answer the question accurately and concisely.

Context:
{context if context else "No specific context provided"}

Question: {prompt}

Answer:"""
            
            model = LLMService._get_model()
            url = f"{API_ENDPOINT}/{model}:generateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            }
            
            print(f"[LLM] Sending request to Gemini...")
            import time
            start = time.time()
            
            response = requests.post(url, json=payload, timeout=60)
            
            elapsed = time.time() - start
            print(f"[LLM] Response received in {elapsed:.2f}s (status: {response.status_code})")
            
            if response.status_code != 200:
                print(f"[LLM] Error: {response.text[:200]}")
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            result = response.json()
            print(f"[LLM] Response has candidates: {'candidates' in result}")
            
            if "candidates" in result and len(result["candidates"]) > 0:
                response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"[LLM] Success! Response length: {len(response_text)} chars")
                print(f"[LLM] First 100 chars: {response_text[:100]}")
                return response_text
            else:
                print(f"[LLM] Error: No candidates in response")
                raise Exception("No response from Gemini API")
            
        except Exception as e:
            print(f"[LLM] ERROR: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    @staticmethod
    def stream_response(prompt: str, context: str = "") -> Generator[str, None, None]:
        """Stream response from Gemini
        
        Yields:
            Response tokens as they are generated
        """
        try:
            full_prompt = f"""Based on the following context from uploaded documents, answer the question accurately and concisely.

Context:
{context if context else "No specific context provided"}

Question: {prompt}

Answer:"""
            
            model = LLMService._get_model()
            url = f"{API_ENDPOINT}/{model}:streamGenerateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=30, stream=True)
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            for line in response.iter_lines():
                if line:
                    import json
                    try:
                        data = json.loads(line)
                        if "candidates" in data and len(data["candidates"]) > 0:
                            if "content" in data["candidates"][0]:
                                if "parts" in data["candidates"][0]["content"]:
                                    for part in data["candidates"][0]["content"]["parts"]:
                                        if "text" in part:
                                            yield part["text"]
                    except json.JSONDecodeError:
                        continue
                    
        except Exception as e:
            print(f"Error streaming response: {str(e)}")
            raise Exception(f"Failed to stream response: {str(e)}")
    
    @staticmethod
    def check_connection() -> bool:
        """Check if Gemini API is accessible"""
        try:
            model = LLMService._get_model()
            url = f"{API_ENDPOINT}/{model}:generateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Hello"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Gemini connection error: {str(e)}")
            return False


llm_service = LLMService()

