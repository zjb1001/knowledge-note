"""
语音识别模块 - 智谱API
"""
import os
import base64
from openai import OpenAI


class ZhipuASR:
    """智谱语音识别"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY")
        
        self.client = OpenAI(
            base_url=os.getenv("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            api_key=api_key
        )
        self.model = os.getenv("ANTHROPIC_MODEL", "glm-4.7")
    
    def transcribe(self, audio_file: str) -> str:
        """
        将音频文件转为文本
        
        Args:
            audio_file: 音频文件路径 (wav格式)
            
        Returns:
            识别出的文本
        """
        try:
            # 读取音频文件
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # Base64编码
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 调用智谱API (模拟，实际需用专用ASR接口)
            # 智谱目前主要通过语音模型支持，这里用文本模拟
            # 实际应使用 whisper.cpp 或智谱的语音API
            
            # 简化方案：提示用户这是模拟
            print("   (注: MVP版本使用模拟文本，实际部署请接入Whisper.cpp或智谱语音API)")
            
            # 为了演示，我们模拟一个会议纪要
            return self._mock_transcript()
            
        except Exception as e:
            print(f"❌ ASR错误: {e}")
            return ""
    
    def _mock_transcript(self) -> str:
        """模拟会议文本 (用于演示)"""
        return """
张三: 大家好，今天我们讨论一下Q2的产品规划。

李四: 我先说一下技术进度。后端API已经开发完成80%，预计下周可以联调。

王五: 前端进度稍微滞后，目前完成了60%，主要是图表组件比较复杂。

张三: 那前端需要什么支持吗？

王五: 需要设计部尽快提供高保真原型，目前只有线框图。

张三: 好，我来跟设计部协调。李四，测试用例准备得怎么样了？

李四: 测试用例已经写了70%，但是自动化测试框架还没搭好。

张三: 这个优先级要提高，争取本周内搞定。那我们来明确一下行动项。

张三: 第一，王五负责跟进设计部原型，DDL是本周五。

王五: 收到。

张三: 第二，李四负责完成自动化测试框架搭建，DDL是本周三。

李四: 明白。

张三: 第三，我负责协调设计资源，明天给反馈。

张三: 那今天的会先到这里，大家有问题随时沟通。
"""
