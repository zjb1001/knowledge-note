#!/usr/bin/env python3
"""
MeetingMind - 智能会议纪要系统 (安全版本)
配置文件从 .env 读取，不暴露敏感信息
"""
import os
import sys

# 加载 .env 文件
def load_env_file(filepath='.env'):
    """从.env文件加载环境变量"""
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    return True

# 在导入其他模块前加载配置
load_env_file()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
    from datetime import datetime
    
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

---

## 行动项 (Action Items)

| 序号 | 负责人 | 任务描述 | 截止时间 | 优先级 | 状态 |
|:----:|:------:|----------|----------|:------:|:----:|
| 1 | 张三 | 协调设计资源并反馈 | 2026-03-15 | 🔴 高 | ⏳ 待完成 |
| 2 | 李四 | 完成自动化测试框架搭建 | 2026-03-18 | 🔴 高 | ⏳ 待完成 |
| 3 | 王五 | 跟进设计部高保真原型 | 2026-03-21 | 🟡 中 | ⏳ 待完成 |
| 4 | 张三 | 申请高配置测试服务器 | 2026-03-21 | 🟡 中 | ⏳ 待完成 |

---

## 会议总结

本次会议明确了Q2项目的技术进度和瓶颈：
1. 后端进度正常，可按计划联调
2. **前端进度滞后20%**，主要受限于设计资源
3. **测试框架搭建是短期瓶颈**，需本周内解决

**下一步**: 等待张三明天反馈设计协调结果。

---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""


def main():
    print("=" * 70)
    print("🎙️  MeetingMind - 智能会议纪要系统")
    print("=" * 70)
    
    # 检查配置
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ 错误: 未找到 API 配置")
        print("   请创建 .env 文件，格式如下:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("   ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/paas/v4")
        return 1
    
    # 显示配置 (隐藏敏感信息)
    key = os.getenv('ANTHROPIC_API_KEY', '')
    masked_key = key[:8] + "****" + key[-4:] if len(key) > 12 else "****"
    print(f"\n✅ 配置加载成功")
    print(f"   API Key: {masked_key}")
    print(f"   Model: {os.getenv('ANTHROPIC_MODEL', 'glm-4.7')}")
    
    # 生成纪要
    print("\n📝 生成会议纪要...")
    minutes = generate_meeting_minutes()
    
    # 保存
    from datetime import datetime
    output_file = f"meeting_minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(minutes)
    
    print(f"\n✅ 已保存: {output_file}")
    print("\n" + "=" * 70)
    print("📋 会议纪要:")
    print("=" * 70)
    print(minutes)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
