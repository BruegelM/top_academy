import logging
from typing import Dict, Any
import aiohttp
import asyncio
from config import AISettings

logger = logging.getLogger(__name__)

class ElizaAnalyzer:
    """Анализатор контента с использованием Eliza API"""
    
    def __init__(self, api_token: str, base_url: str, model: str, temperature: float):
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.session = aiohttp.ClientSession()
        
    async def analyze_content(self, content: str, prompt: str) -> Dict[str, Any]:
        """Анализ контента через Eliza API"""
        try:
            url = f"{self.base_url}/openai/v1/chat/completions"
            
            # Обработка токена - удаляем возможные пробелы и лишние символы
            cleaned_token = self.api_token.strip()
            if cleaned_token.startswith('y1_'):
                cleaned_token = cleaned_token[3:]
            
            headers = {
                "Authorization": f"OAuth {cleaned_token}",
                "Content-Type": "application/json",
                "Need-Raw-Answer": "true",
                "X-Ya-Service-Ticket": cleaned_token  # Дополнительный заголовок для авторизации
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{content}"
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": 1000
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    # Обработка ответа в формате OpenAI
                    if "choices" in result and len(result["choices"]) > 0:
                        return {
                            "status": "success",
                            "analysis_text": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {})
                        }
                    return {
                        "status": "error",
                        "error": "Invalid response format from Eliza API"
                    }
                else:
                    error = await response.text()
                    return {
                        "status": "error",
                        "error": f"API error: {response.status} - {error}"
                    }
                    
        except Exception as e:
            logger.error(f"Eliza API error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def close(self):
        """Явное закрытие сессии"""
        if not self.session.closed:
            await self.session.close()

    async def __del__(self):
        if hasattr(self, 'session') and not self.session.closed:
            await self.close()

class ZelibobaAnalyzer:
    """Анализатор контента с использованием Zeliboba API"""
    
    def __init__(self, api_token: str, base_url: str, model: str, temperature: float):
        self.api_token = api_token
        self.base_url = base_url.rstrip('/') if base_url else None
        self.model = model
        self.temperature = temperature
        self.session = aiohttp.ClientSession()
        
    async def create_summary(self, content: str) -> Dict[str, Any]:
        """Создание саммари через Zeliboba API"""
        try:
            url = f"{self.base_url}/v1/summarize" if self.base_url else "https://api.zeliboba.ai/v1/summarize"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "content": content,
                "temperature": self.temperature,
                "max_length": 1000
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "analysis_text": result.get("summary", ""),
                        "usage": result.get("usage", {})
                    }
                else:
                    error = await response.text()
                    return {
                        "status": "error",
                        "error": f"API error: {response.status} - {error}"
                    }
                    
        except Exception as e:
            logger.error(f"Zeliboba API error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def __del__(self):
        await self.session.close()