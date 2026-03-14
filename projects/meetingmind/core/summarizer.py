"""
会议纪要生成器 - 使用LLM提取结构化信息
"""
import os
from openai import OpenAI


class MeetingSummarizer:
    """会议纪要生成器"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY")
        
        self.client = OpenAI(
            base_url=os.getenv("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            api_key=api_key
        )
        self.model = os.getenv("ANTHROPIC_MODEL", "glm-4.7")
    
    def generate(self, transcript: str) -> str:
        """
        从会议转录文本生成结构化纪要
        
        Args:
            transcript: 会议转录文本
            
        Returns:
            Markdown格式的会议纪要
        """
        prompt = f"""你是一个专业的会议纪要助手。请将以下会议转录文本转换为结构化的会议纪要。

要求：
1. 提取参会人员列表
2. 总结主要讨论议题（每个议题用一句话概括）
3. **重点提取行动项**：谁(Who) + 做什么(What) + 截止时间(When)
4. 使用Markdown格式输出
5. 如果会议中有明确的时间点（如"下周三"），请转换为具体日期（假设今天是2026年3月14日）

输出格式：
```markdown
# 会议纪要

## 基本信息
- 会议时间: YYYY-MM-DD HH:MM
- 参会人员: xxx, xxx, xxx

## 讨论议题
1. **议题名称**: 简要描述
2. **议题名称**: 简要描述

## 行动项
| 负责人 | 任务描述 | 截止时间 | 状态 |
|--------|----------|----------|------|
| 张三 | xxx | 2026-03-20 | ⏳ 待完成 |
| 李四 | xxx | 2026-03-18 | ⏳ 待完成 |

## 会议总结
用2-3句话总结会议核心结论
```

以下是会议转录文本：
---
{transcript}
---

请生成会议纪要："""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的会议纪要助手，擅长从会议记录中提取关键信息和行动项。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 如果输出被代码块包裹，提取内容
            if content.startswith("```markdown"):
                content = content[11:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return content.strip()
            
        except Exception as e:
            print(f"❌ 生成纪要错误: {e}")
            return self._fallback_format(transcript)
    
    def _fallback_format(self, transcript: str) -> str:
        """降级格式化"""
        return f"""# 会议纪要

## 原始转录

{transcript}

---
*注: 由于API错误，仅提供原始转录文本*
"""
