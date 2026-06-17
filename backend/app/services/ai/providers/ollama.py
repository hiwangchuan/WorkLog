import httpx

from app.services.ai.providers.base import AIProviderError, BaseAIProvider


class OllamaProvider(BaseAIProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        base_url = (self.config.base_url or "http://ollama:11434").rstrip("/")
        payload = {
            "model": self.config.model_name,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
        }
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(f"{base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise AIProviderError(f"Ollama 连接失败：{exc}") from exc
        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise AIProviderError("Ollama 响应格式不正确") from exc
