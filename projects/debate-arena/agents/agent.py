"""
辩论 Agent 基类
"""
from typing import List, Dict
from datetime import datetime
from api.zhipu import get_api


class DebateAgent:
    """辩论 Agent 基类"""
    
    def __init__(self, agent_id: str, name: str, system_prompt: str):
        self.id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.history = []
        self.api = get_api()
        
    def speak(self, prompt: str, temperature: float = 0.7) -> str:
        """Agent 发言"""
        response = self.api.chat(self.system_prompt, prompt, temperature)
        self.remember("user", prompt)
        self.remember("assistant", response)
        return response
    
    def speak_with_context(self, topic: str, phase: str, context: List[Dict] = None) -> str:
        """基于上下文发言"""
        prompt = f"辩题: {topic}\n当前阶段: {phase}\n"
        if context:
            prompt += "\n之前的讨论:\n"
            for item in context[-3:]:
                prompt += f"{item['speaker']}: {item['content'][:100]}...\n"
        prompt += f"\n请作为{self.name}进行发言:"
        return self.speak(prompt)
    
    def remember(self, role: str, content: str):
        """记录对话历史"""
        self.history.append({
            "role": role, "content": content,
            "timestamp": datetime.now().isoformat()
        })
