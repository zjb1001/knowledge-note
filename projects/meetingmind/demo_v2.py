#!/usr/bin/env python3
"""
MeetingMind v2.0 - 智能会议纪要系统 (带评价 Agent)
新增 Evaluator Agent 进行质量监督和评价
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.evaluator import MeetingEvaluator, evaluate_meeting_minutes


def print_banner():
    print("=" * 70)
    print("🎙️  MeetingMind v2.0 - 智能会议纪要系统")
    print("   新增: 🎯 Evaluator Agent 质量监督")
    print("=" * 70)
    print("\n📋 系统流程:")
    print("  1️⃣  音频录制")
    print("  2️⃣  语音识别 (ASR)")
    print("  3️⃣  智能摘要 (LLM)")
    print("  4️⃣  🎯 质量评价 (Evaluator Agent)")
    print("  5️⃣  生成结构化纪要 + 评价报告")
    print("=" * 70)
    print()


def mock_meeting_transcript():
    """模拟会议转录文本"""
    return """张三: 大家好，今天我们讨论一下Q2的产品规划。

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


def generate_meeting_minutes():
    """生成会议纪要"""
    return f"""# Q2产品规划会议纪要

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
- **依赖**: 设计部高保真原型
- **状态**: ⚠️ 有风险

### 3. 测试准备情况
- **负责人**: 李四
- **进度**: 测试用例完成70%
- **问题**: 自动化测试框架尚未搭建
- **状态**: ⚠️ 需加急

### 4. 资源申请
- 高配置测试服务器一台
- 设计部高保真原型

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
| 前端进度滞后 | 可能导致延期 | 设计部优先支持，张三协调 |
| 测试框架未搭建 | 影响测试进度 | 本周内完成，优先级提升 |

---

## 会议总结

本次会议明确了Q2项目的技术进度和瓶颈：
1. 后端进度正常，可按计划联调
2. **前端进度滞后20%**，主要受限于设计资源，需要重点关注
3. **测试框架搭建是短期瓶颈**，需本周内解决
4. 共确定4个行动项，其中2个高优先级

**下一步**: 等待张三明天反馈设计协调结果，李四周三完成测试框架。

---

*纪要生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*生成工具: MeetingMind AI*
"""


def main():
    print_banner()
    
    input("🎤 按回车开始模拟会议录音...")
    
    # 步骤1: 模拟录音
    print("\n🔴 [步骤1] 录音中...")
    import time
    time.sleep(0.5)
    print("   ✅ 录音完成: meeting_20260314_143052.wav")
    
    # 步骤2: 语音识别
    print("\n📝 [步骤2] 语音识别 (ASR)...")
    transcript = mock_meeting_transcript()
    print(f"   ✅ 识别完成: {len(transcript)} 字符")
    
    # 步骤3: 生成纪要
    print("\n🧠 [步骤3] 智能摘要生成...")
    minutes = generate_meeting_minutes()
    print("   ✅ 纪要生成完成")
    
    # 步骤4: 质量评价 (新增 Evaluator Agent)
    print("\n🎯 [步骤4] Evaluator Agent 质量评价...")
    evaluator = MeetingEvaluator()
    result = evaluator.evaluate(transcript, minutes)
    print(f"   ✅ 评价完成")
    print(f"   📊 总体评分: {result.overall_score}/100")
    print(f"   📋 行动项数: {result.action_items_quality['count']} 项")
    
    # 步骤5: 保存输出
    print("\n💾 [步骤5] 保存输出...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存会议纪要
    minutes_file = f"meeting_minutes_{timestamp}.md"
    with open(minutes_file, 'w', encoding='utf-8') as f:
        f.write(minutes)
    print(f"   ✅ 会议纪要: {minutes_file}")
    
    # 保存评价报告
    report = evaluator.generate_report(result, 'markdown')
    report_file = f"evaluation_report_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✅ 评价报告: {report_file}")
    
    # 保存 JSON 格式数据
    json_file = f"evaluation_result_{timestamp}.json"
    json_data = evaluator.generate_report(result, 'json')
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_data)
    print(f"   ✅ JSON数据: {json_file}")
    
    # 显示结果
    print("\n" + "=" * 70)
    print("📋 会议纪要预览:")
    print("=" * 70)
    print(minutes[:1500] + "...")
    
    print("\n" + "=" * 70)
    print("🎯 评价报告预览:")
    print("=" * 70)
    print(report)
    
    print("\n" + "=" * 70)
    print("✨ MeetingMind v2.0 演示完成!")
    print("=" * 70)
    print(f"\n📁 输出文件:")
    print(f"   - 会议纪要: {minutes_file}")
    print(f"   - 评价报告: {report_file}")
    print(f"   - JSON数据: {json_file}")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
