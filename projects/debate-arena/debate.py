#!/usr/bin/env python3
"""
Debate Arena - 多 Agent 辩论系统
基于 GStack + Claude Code + 智谱 GLM-4.7
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

class DebateAgent:
    """辩论 Agent 基类"""
    
    def __init__(self, agent_id: str, name: str, role: str, system_prompt: str):
        self.id = agent_id
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.history = []
        
    def speak(self, topic: str, context: List[Dict] = None) -> str:
        """生成发言内容"""
        # 这里调用 Claude Code 或智谱 API
        # 简化版本：返回模拟内容
        return f"[{self.name}] 关于'{topic}'的观点..."
    
    def remember(self, speaker: str, content: str):
        """记录对话历史"""
        self.history.append({
            "speaker": speaker,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })


class ProAgent(DebateAgent):
    """正方 Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="pro",
            name="正方",
            role="辩题支持者",
            system_prompt="""你是正方辩手。你的任务是坚定支持给定的辩题。

辩论风格:
- 逻辑严密，论据充分
- 善于引用案例和数据
- 积极回应对方质疑
- 语言有力但不失礼貌

你必须:
1. 首先明确阐述支持观点
2. 提供至少2-3个支撑论据
3. 预判反方论点并提前反驳
4. 在自由辩论中主动出击

记住: 你是为了说服观众和评委，不是为了争吵。"""
        )


class ConAgent(DebateAgent):
    """反方 Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="con",
            name="反方",
            role="辩题反对者",
            system_prompt="""你是反方辩手。你的任务是质疑和反对给定的辩题。

辩论风格:
- 批判性思维，善于发现问题
- 揭示逻辑漏洞和假设前提
- 提供反例和负面案例
- 保持理性和客观

你必须:
1. 首先明确阐述反对观点
2. 指出正方论点的漏洞
3. 提供反例或替代视角
4. 在自由辩论中抓住对方弱点

记住: 反对不等于否定一切，而是提供另一种思考角度。"""
        )


class ModeratorAgent(DebateAgent):
    """主持人 Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="moderator",
            name="主持人",
            role="流程把控者",
            system_prompt="""你是辩论主持人。你的任务是确保辩论有序、精彩、公平。

主持风格:
- 中立客观，不偏袒任何一方
- 把控节奏，确保双方机会均等
- 适时引导，让讨论深入
- 语言风趣，活跃气氛

你必须:
1. 开场清晰介绍辩题和规则
2. 每个环节严格把控时间
3. 适时打断过长发言
4. 总结时提炼双方核心观点
5. 点评时指出亮点和不足

记住: 你不是裁判，你是让辩论更精彩的人。"""
        )


class DebateArena:
    """辩论场 - 管理整个辩论流程"""
    
    def __init__(self, topic: str, rounds: int = 3):
        self.topic = topic
        self.rounds = rounds
        self.pro = ProAgent()
        self.con = ConAgent()
        self.moderator = ModeratorAgent()
        self.transcript = []
        self.current_phase = "准备"
        
    def log(self, speaker: str, content: str):
        """记录辩论内容"""
        entry = {
            "phase": self.current_phase,
            "speaker": speaker,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.transcript.append(entry)
        print(f"\n[{speaker}] {content}")
        
        # 让 Agent 记住
        if speaker == "正方":
            self.pro.remember(speaker, content)
        elif speaker == "反方":
            self.con.remember(speaker, content)
        else:
            self.moderator.remember(speaker, content)
    
    def phase_opening(self):
        """开场环节"""
        self.current_phase = "开场"
        self.log("主持人", f"欢迎来到辩论赛场！今天的辩题是：{self.topic}")
        self.log("主持人", "辩论规则：")
        self.log("主持人", "1. 立论环节：双方各3分钟阐述观点")
        self.log("主持人", "2. 攻辩环节：双方互相质询")
        self.log("主持人", "3. 自由辩论：双方交替发言")
        self.log("主持人", "4. 总结陈词：双方各2分钟总结")
        time.sleep(1)
    
    def phase_statement(self):
        """立论环节"""
        self.current_phase = "立论"
        
        # 正方立论
        self.log("主持人", "请正方进行立论陈述，时间3分钟。")
        pro_statement = self._generate_statement("pro")
        self.log("正方", pro_statement)
        time.sleep(2)
        
        # 反方立论
        self.log("主持人", "请反方进行立论陈述，时间3分钟。")
        con_statement = self._generate_statement("con")
        self.log("反方", con_statement)
        time.sleep(2)
    
    def phase_attack(self):
        """攻辩环节"""
        self.current_phase = "攻辩"
        
        for round_num in range(1, 3):
            self.log("主持人", f"=== 攻辩第{round_num}轮 ===")
            
            # 正方提问
            self.log("主持人", "正方提问")
            pro_question = self._generate_attack("pro", "question")
            self.log("正方", pro_question)
            time.sleep(1)
            
            # 反方回答
            con_response = self._generate_attack("con", "response", pro_question)
            self.log("反方", con_response)
            time.sleep(1)
            
            # 反方提问
            self.log("主持人", "反方提问")
            con_question = self._generate_attack("con", "question")
            self.log("反方", con_question)
            time.sleep(1)
            
            # 正方回答
            pro_response = self._generate_attack("pro", "response", con_question)
            self.log("正方", pro_response)
            time.sleep(1)
    
    def phase_free_debate(self):
        """自由辩论环节"""
        self.current_phase = "自由辩论"
        self.log("主持人", "=== 自由辩论环节 ===")
        
        for i in range(self.rounds * 2):
            if i % 2 == 0:
                content = self._generate_free("pro", self.con.history[-1] if self.con.history else None)
                self.log("正方", content)
            else:
                content = self._generate_free("con", self.pro.history[-1] if self.pro.history else None)
                self.log("反方", content)
            time.sleep(1)
    
    def phase_summary(self):
        """总结陈词环节"""
        self.current_phase = "总结"
        
        # 反方先总结（后发制人）
        self.log("主持人", "请反方进行总结陈词，时间2分钟。")
        con_summary = self._generate_summary("con")
        self.log("反方", con_summary)
        time.sleep(2)
        
        # 正方总结
        self.log("主持人", "请正方进行总结陈词，时间2分钟。")
        pro_summary = self._generate_summary("pro")
        self.log("正方", pro_summary)
        time.sleep(2)
    
    def phase_closing(self):
        """点评环节"""
        self.current_phase = "点评"
        self.log("主持人", "=== 主持人点评 ===")
        
        review = self._generate_review()
        self.log("主持人", review)
        time.sleep(2)
    
    # ===== 内容生成方法（简化版，实际应调用API） =====
    
    def _generate_statement(self, side: str) -> str:
        """生成立论陈述"""
        if side == "pro":
            return f"我方坚定支持'{self.topic}'这一观点。首先，从历史发展来看...其次，从现实数据来说...最后，从未来趋势分析..."
        else:
            return f"我方坚决反对'{self.topic}'这一观点。第一，该观点忽视了...第二，实际情况恰恰相反...第三，长远来看风险极大..."
    
    def _generate_attack(self, side: str, mode: str, context: str = None) -> str:
        """生成攻辩内容"""
        if mode == "question":
            if side == "pro":
                return "请问反方，您如何解释近年来该领域取得的突破性进展？"
            else:
                return "请问正方，您如何看待该方案在实施过程中的重大失败案例？"
        else:
            return f"针对对方的问题，我方认为...（回应{context[:20] if context else ''}）"
    
    def _generate_free(self, side: str, last_opponent: Dict = None) -> str:
        """生成自由辩论内容"""
        if side == "pro":
            responses = [
                "对方辩友刚才的论述存在一个根本性错误...",
                "我方要强调的是，数据说明一切...",
                "请对方不要回避核心问题...",
                "从逻辑上讲，对方的推论无法成立..."
            ]
        else:
            responses = [
                "正方始终回避了最关键的问题...",
                "实际情况与正方的设想完全相反...",
                "我方提供的案例已经充分说明了...",
                "请问正方如何解释这个明显的矛盾？"
            ]
        import random
        return random.choice(responses)
    
    def _generate_summary(self, side: str) -> str:
        """生成总结陈词"""
        if side == "pro":
            return "综上所述，我方从三个层面论证了观点的正确性..."
        else:
            return "总结全场辩论，对方的几处致命漏洞..."
    
    def _generate_review(self) -> str:
        """生成主持人点评"""
        return f"今天的辩论非常精彩！双方围绕'{self.topic}'展开了深入探讨。正方的亮点在于...反方的优势在于...感谢双方辩手！"
    
    # ===== 流程控制 =====
    
    def start(self):
        """开始辩论"""
        print("=" * 60)
        print("🎙️  Debate Arena - 多 Agent 辩论系统")
        print("=" * 60)
        print(f"\n辩题：{self.topic}\n")
        
        try:
            self.phase_opening()
            self.phase_statement()
            self.phase_attack()
            self.phase_free_debate()
            self.phase_summary()
            self.phase_closing()
        except KeyboardInterrupt:
            print("\n\n⚠️  辩论被中断")
        
        print("\n" + "=" * 60)
        print("🏁 辩论结束")
        print("=" * 60)
    
    def save_transcript(self, filename: str = None):
        """保存辩论记录"""
        if filename is None:
            filename = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "topic": self.topic,
            "rounds": self.rounds,
            "start_time": self.transcript[0]["timestamp"] if self.transcript else None,
            "end_time": datetime.now().isoformat(),
            "transcript": self.transcript
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 辩论记录已保存: {filename}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Debate Arena - 多 Agent 辩论系统')
    parser.add_argument('--topic', '-t', type=str, default='人工智能是否会取代人类工作',
                        help='辩题')
    parser.add_argument('--rounds', '-r', type=int, default=3,
                        help='自由辩论轮数')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出文件')
    
    args = parser.parse_args()
    
    # 创建辩论场
    arena = DebateArena(topic=args.topic, rounds=args.rounds)
    
    # 开始辩论
    arena.start()
    
    # 保存记录
    arena.save_transcript(args.output)


if __name__ == '__main__':
    main()
