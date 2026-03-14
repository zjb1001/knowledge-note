"""
核心辩论场 - 管理整个辩论流程
"""
import json
import time
from datetime import datetime
from typing import List, Dict
from agents.roles import ProAgent, ConAgent, ModeratorAgent


class DebateArena:
    """辩论场"""
    
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
        print(f"\n[{speaker}] {content[:200]}...")
        
        # 让 Agent 记住
        if speaker == "正方":
            self.pro.remember("assistant", content)
        elif speaker == "反方":
            self.con.remember("assistant", content)
        else:
            self.moderator.remember("assistant", content)
    
    def _get_context(self) -> List[Dict]:
        """获取当前辩论上下文"""
        return [{"speaker": t["speaker"], "content": t["content"]} 
                for t in self.transcript[-5:]]
    
    def phase_opening(self):
        """开场"""
        self.current_phase = "开场"
        prompt = f"请开场介绍今天的辩题：{self.topic}"
        content = self.moderator.speak(prompt)
        self.log("主持人", content)
        time.sleep(1)
    
    def phase_statement(self):
        """立论"""
        self.current_phase = "立论"
        
        # 正方立论
        self.log("主持人", "请正方进行立论陈述。")
        pro_prompt = f"辩题：{self.topic}\n阶段：立论\n请进行3分钟的立论陈述。"
        pro_content = self.pro.speak(pro_prompt)
        self.log("正方", pro_content)
        time.sleep(2)
        
        # 反方立论
        self.log("主持人", "请反方进行立论陈述。")
        con_prompt = f"辩题：{self.topic}\n阶段：立论\n对方观点：{pro_content[:200]}...\n请进行3分钟的立论陈述。"
        con_content = self.con.speak(con_prompt)
        self.log("反方", con_content)
        time.sleep(2)
    
    def phase_attack(self):
        """攻辩"""
        self.current_phase = "攻辩"
        
        for round_num in range(1, 3):
            self.log("主持人", f"=== 攻辩第{round_num}轮 ===")
            
            # 正方提问
            context = self._get_context()
            pro_q_prompt = f"辩题：{self.topic}\n阶段：攻辩提问\n上下文：{str(context[-2:])}\n请向对方提问。"
            pro_q = self.pro.speak(pro_q_prompt)
            self.log("正方", f"提问：{pro_q}")
            time.sleep(1)
            
            # 反方回答
            con_a_prompt = f"辩题：{self.topic}\n阶段：攻辩回答\n对方问题：{pro_q}\n请回答。"
            con_a = self.con.speak(con_a_prompt)
            self.log("反方", f"回答：{con_a}")
            time.sleep(1)
            
            # 反方提问
            con_q_prompt = f"辩题：{self.topic}\n阶段：攻辩提问\n上下文：{str(context[-2:])}\n请向对方提问。"
            con_q = self.con.speak(con_q_prompt)
            self.log("反方", f"提问：{con_q}")
            time.sleep(1)
            
            # 正方回答
            pro_a_prompt = f"辩题：{self.topic}\n阶段：攻辩回答\n对方问题：{con_q}\n请回答。"
            pro_a = self.pro.speak(pro_a_prompt)
            self.log("正方", f"回答：{pro_a}")
            time.sleep(1)
    
    def phase_free_debate(self):
        """自由辩论"""
        self.current_phase = "自由辩论"
        self.log("主持人", "=== 自由辩论环节 ===")
        
        for i in range(self.rounds * 2):
            context = self._get_context()
            
            if i % 2 == 0:
                prompt = f"辩题：{self.topic}\n阶段：自由辩论\n上下文：{str(context[-3:])}\n请发言反驳对方。"
                content = self.pro.speak(prompt, temperature=0.8)
                self.log("正方", content)
            else:
                prompt = f"辩题：{self.topic}\n阶段：自由辩论\n上下文：{str(context[-3:])}\n请发言反驳对方。"
                content = self.con.speak(prompt, temperature=0.8)
                self.log("反方", content)
            
            time.sleep(1)
    
    def phase_summary(self):
        """总结"""
        self.current_phase = "总结"
        
        # 反方先总结
        self.log("主持人", "请反方进行总结陈词。")
        context = self._get_context()
        con_prompt = f"辩题：{self.topic}\n阶段：总结陈词\n全场讨论：{str(context[-5:])}\n请进行总结。"
        con_summary = self.con.speak(con_prompt)
        self.log("反方", con_summary)
        time.sleep(2)
        
        # 正方总结
        self.log("主持人", "请正方进行总结陈词。")
        pro_prompt = f"辩题：{self.topic}\n阶段：总结陈词\n全场讨论：{str(context[-5:])}\n请进行总结。"
        pro_summary = self.pro.speak(pro_prompt)
        self.log("正方", pro_summary)
        time.sleep(2)
    
    def phase_closing(self):
        """点评"""
        self.current_phase = "点评"
        context = self._get_context()
        mod_prompt = f"辩题：{self.topic}\n阶段：主持人点评\n全场讨论：{str(context[-8:])}\n请进行点评总结。"
        review = self.moderator.speak(mod_prompt)
        self.log("主持人", review)
        time.sleep(2)
    
    def start(self):
        """开始辩论"""
        print("=" * 60)
        print("🎙️  Debate Arena - AI 辩论赛")
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
            "transcript": self.transcript,
            "pro_history": self.pro.get_history(),
            "con_history": self.con.get_history(),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 辩论记录已保存: {filename}")
