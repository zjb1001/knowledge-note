"""
智谱 GLM-4.7 API 封装
"""
import os
from typing import List, Dict
from openai import OpenAI


class ZhipuAPI:
    """智谱 API 封装类"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = os.getenv("ANTHROPIC_MODEL", "glm-4.7")
        
    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """调用智谱 API 生成回复"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ API 调用失败: {e}")
            return f"[API 错误: {str(e)[:50]}...]"


_api_instance = None

def get_api() -> ZhipuAPI:
    """获取全局 API 实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = ZhipuAPI()
    return _api_instance
