#!/usr/bin/env python3
"""
MeetingMind v3.0 - 自迭代优化版本 (概念设计)
Evaluator Agent 反馈 → 自动优化 → 重新生成
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.evaluator import MeetingEvaluator


class SelfImprovingMeetingMind:
    """
    自迭代优化的会议纪要系统
    
    工作流程:
    1. 生成初稿
    2. Evaluator评分
    3. 如果分数<阈值，根据反馈自动优化
    4. 重新生成，直到达标或达到最大迭代次数
    """
    
    def __init__(self, threshold=85, max_iterations=3):
        self.evaluator = MeetingEvaluator()
        self.threshold = threshold  # 合格分数线
        self.max_iterations = max_iterations  # 最大迭代次数
        self.iteration_history = []
    
    def generate_and_improve(self, transcript: str, generate_func) -> dict:
        """
        生成并自动优化
        
        Args:
            transcript: 会议转录文本
            generate_func: 纪要生成函数 (可替换为LLM调用)
        
        Returns:
            包含最终纪要、评价结果、迭代历史的字典
        """
        current_minutes = None
        best_result = None
        best_score = 0
        
        print(f"🔄 启动自迭代优化 (目标分数: {self.threshold}, 最大迭代: {self.max_iterations})")
        print("=" * 70)
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n📍 第 {iteration}/{self.max_iterations} 轮迭代")
            print("-" * 70)
            
            # 第1轮：生成初稿
            # 后续轮次：根据反馈优化后重新生成
            if iteration == 1:
                current_minutes = generate_func(transcript)
                print("✅ 生成初稿")
            else:
                # 根据上一轮评价反馈优化
                feedback = self._build_improvement_prompt(best_result)
                current_minutes = generate_func(transcript, feedback=feedback)
                print("✅ 根据反馈优化后重新生成")
            
            # 评价
            result = self.evaluator.evaluate(transcript, current_minutes)
            
            print(f"📊 本轮评分: {result.overall_score}/100")
            print(f"   各维度: 完整性{result.dimensions['completeness']:.0f} | "
                  f"准确性{result.dimensions['accuracy']:.0f} | "
                  f"行动项{result.dimensions['action_items']:.0f}")
            
            # 记录历史
            self.iteration_history.append({
                'iteration': iteration,
                'score': result.overall_score,
                'dimensions': result.dimensions,
                'weaknesses': result.weaknesses
            })
            
            # 保存最佳结果
            if result.overall_score > best_score:
                best_score = result.overall_score
                best_result = result
                best_minutes = current_minutes
                print(f"⭐ 新最佳成绩！({best_score:.1f})")
            
            # 检查是否达标
            if result.overall_score >= self.threshold:
                print(f"\n🎉 达到目标分数！提前结束迭代")
                break
            
            if iteration < self.max_iterations:
                print(f"\n💡 准备根据以下反馈优化:")
                for suggestion in result.suggestions[:2]:
                    print(f"   - {suggestion}")
        
        # 输出最终结果
        print("\n" + "=" * 70)
        print(f"✨ 迭代完成！最佳评分: {best_score:.1f}")
        print(f"📈 迭代次数: {len(self.iteration_history)}")
        
        return {
            'final_minutes': best_minutes,
            'final_evaluation': best_result,
            'iteration_history': self.iteration_history,
            'improvement': best_score - self.iteration_history[0]['score'] if self.iteration_history else 0
        }
    
    def _build_improvement_prompt(self, evaluation_result) -> str:
        """
        根据评价结果构建优化提示词
        
        这部分可以接入 LLM，让 AI 根据反馈自动改进
        """
        weaknesses = evaluation_result.weaknesses
        suggestions = evaluation_result.suggestions
        
        prompt = "请根据以下反馈优化会议纪要:\n\n"
        
        if weaknesses:
            prompt += "需要改进的问题:\n"
            for w in weaknesses:
                prompt += f"- {w}\n"
        
        if suggestions:
            prompt += "\n具体建议:\n"
            for s in suggestions:
                prompt += f"- {s}\n"
        
        # 根据维度分数给出具体指导
        dims = evaluation_result.dimensions
        if dims['action_items'] < 80:
            prompt += "\n[重点] 确保每个行动项都有明确的负责人(Who)、任务描述(What)、截止时间(When)\n"
        
        if dims['completeness'] < 80:
            prompt += "\n[重点] 补充遗漏的议题讨论，确保覆盖会议所有重要内容\n"
        
        if dims['structure'] < 80:
            prompt += "\n[重点] 使用规范的Markdown格式，包括表格、列表、分隔线\n"
        
        return prompt


# 模拟的纪要生成函数 (实际应接入 LLM)
def mock_generate_minutes(transcript: str, feedback: str = None) -> str:
    """
    模拟纪要生成
    实际使用时替换为调用智谱GLM/Claude等LLM
    """
    # 根据反馈迭代改进的模拟逻辑
    base_minutes = """# Q2产品规划会议纪要

## 基本信息
- **会议时间**: 2026-03-14 14:00
- **参会人员**: 张三、李四、王五

## 讨论议题
### 1. 后端技术进度
- **负责人**: 李四
- **进度**: 80%完成

### 2. 前端技术进度
- **负责人**: 王五
- **进度**: 60%完成

## 行动项
| 序号 | 负责人 | 任务描述 | 截止时间 |
|:----:|:------:|----------|----------|
| 1 | 王五 | 跟进设计部原型 | 本周五 |
| 2 | 李四 | 完成测试框架 | 周三 |

## 会议总结
会议讨论了Q2进度。
"""
    
    # 如果有反馈，模拟改进
    if feedback:
        # 根据反馈添加更多细节 (模拟LLM改进效果)
        improved = """# Q2产品规划会议纪要

## 基本信息
- **会议时间**: 2026-03-14 14:00
- **参会人员**: 张三、李四、王五
- **会议主题**: Q2产品规划进度同步

---

## 讨论议题

### 1. 后端技术进度
- **负责人**: 李四
- **进度**: 80%完成
- **计划**: 下周开始联调
- **状态**: ✅ 正常

### 2. 前端技术进度
- **负责人**: 王五
- **进度**: 60%完成
- **瓶颈**: 图表组件复杂，需要高保真原型支持
- **状态**: ⚠️ 有风险

### 3. 测试准备情况
- **负责人**: 李四
- **进度**: 测试用例完成70%
- **问题**: 自动化测试框架尚未搭建
- **状态**: ⚠️ 需加急

---

## 行动项 (Action Items)

| 序号 | 负责人 | 任务描述 | 截止时间 | 优先级 | 状态 |
|:----:|:------:|----------|----------|:------:|:----:|
| 1 | 张三 | 协调设计资源并反馈 | 2026-03-15 | 🔴 高 | ⏳ 待完成 |
| 2 | 李四 | 完成自动化测试框架搭建 | 2026-03-18 | 🔴 高 | ⏳ 待完成 |
| 3 | 王五 | 跟进设计部高保真原型 | 2026-03-21 | 🟡 中 | ⏳ 待完成 |
| 4 | 张三 | 申请高配置测试服务器 | 2026-03-21 | 🟡 中 | ⏳ 待完成 |

---

## 风险与问题

| 问题 | 影响 | 应对措施 |
|------|------|----------|
| 前端进度滞后 | 可能导致延期 | 设计部优先支持 |
| 测试框架未搭建 | 影响测试进度 | 本周内完成 |

---

## 会议总结

本次会议明确了Q2项目的技术进度和瓶颈，确定了4个关键行动项。

---

*纪要生成时间: 2026-03-14 16:30:00*
"""
        return improved
    
    return base_minutes


def main():
    """演示自迭代优化"""
    print("=" * 70)
    print("🚀 MeetingMind v3.0 - 自迭代优化演示")
    print("=" * 70)
    
    # 模拟转录文本
    transcript = """张三: 大家好，今天我们讨论一下Q2的产品规划。
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
王五: 另外，我们还需要申请一台测试服务器，配置要高一点。
张三: 好的，我来申请，DDL也是本周五。
张三: 那今天的会先到这里，大家有问题随时沟通。
李四: 散会。"""
    
    # 创建自迭代系统
    mind = SelfImprovingMeetingMind(threshold=85, max_iterations=3)
    
    # 执行自迭代生成
    result = mind.generate_and_improve(transcript, mock_generate_minutes)
    
    # 输出最终结果
    print("\n" + "=" * 70)
    print("📈 迭代历史:")
    for h in result['iteration_history']:
        print(f"   第{h['iteration']}轮: {h['score']:.1f}分")
    
    print(f"\n📊 改进幅度: +{result['improvement']:.1f}分")
    
    print("\n" + "=" * 70)
    print("📝 最终生成的纪要:")
    print("=" * 70)
    print(result['final_minutes'])
    
    print("\n" + "=" * 70)
    print("🎯 最终评价报告:")
    print("=" * 70)
    print(result['final_evaluation'].summary)
    print(f"\n各维度得分:")
    for dim, score in result['final_evaluation'].dimensions.items():
        print(f"   {dim}: {score:.1f}")


if __name__ == '__main__':
    main()
