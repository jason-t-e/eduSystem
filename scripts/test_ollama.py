# scripts/test_ollama.py  (delete after testing)
import asyncio
from pathlib import Path
import sys

import httpx

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import Settings

settings = Settings()


async def test_ollama():
    print(f"Testing Ollama at: {settings.ollama_base_url}")
    print(f"Model: {settings.ollama_model}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test 1: Is Ollama reachable?
        try:
            resp = await client.get(f"{settings.ollama_base_url}/api/version")
            print(f"[OK] Ollama reachable - version: {resp.json()}")
        except Exception as e:
            print(f"[FAIL] Ollama NOT reachable: {e}")
            print("  -> Check: is 'ollama serve' running?")
            print("  -> Check: is OLLAMA_BASE_URL correct in .env?")
            return

        # Test 2: Is the model available?
        try:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            models = [m["name"] for m in resp.json()["models"]]
            if settings.ollama_model in models:
                print(f"[OK] Model found: {settings.ollama_model}")
            else:
                print(f"[FAIL] Model NOT found. Available: {models}")
                print(f"  -> Run: ollama pull {settings.ollama_model}")
                return
        except Exception as e:
            print(f"[FAIL] Could not list models: {e}")
            return

        # Test 3: Does the model respond?
        try:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": [
                        {"role": "user", "content": "Say 'OK' and nothing else."}
                    ],
                    "stream": False,
                },
            )
            content = resp.json()["message"]["content"]
            print(f"[OK] Model responded: '{content.strip()}'")
        except Exception as e:
            print(f"[FAIL] Model did not respond: {e}")


if __name__ == "__main__":
    asyncio.run(test_ollama())