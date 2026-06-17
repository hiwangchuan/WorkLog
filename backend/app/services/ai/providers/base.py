from dataclasses import dataclass


@dataclass
class ProviderConfig:
    provider: str
    base_url: str | None
    api_key: str | None
    model_name: str
    temperature: float
    max_tokens: int
    timeout_seconds: int


class AIProviderError(RuntimeError):
    pass


class BaseAIProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    async def test(self) -> dict:
        output = await self.generate("你是连接测试助手。", "请仅回复 ok")
        return {"ok": bool(output), "output": output[:200]}
