# MeetingMind - 独立应用部署指南

## 🚀 快速开始 (3步)

### 1. 摘取项目

```bash
# 方法1: 使用一键脚本
cd /path/to/knowledge-note/projects/meetingmind
./extract-meetingmind.sh

# 方法2: 手动复制
mkdir ~/meetingmind
cp -r /path/to/knowledge-note/projects/meetingmind/* ~/meetingmind/
```

### 2. 安装依赖

```bash
cd ~/meetingmind
chmod +x install.sh
./install.sh
```

### 3. 运行应用

```bash
# 启动演示
./start.sh

# 包含架构评审
./start.sh --arch-review

# 查看版本
./start.sh --version
```

---

## 📁 项目结构

```
meetingmind/                    # 项目根目录
├── main.py                     # 主入口 (v2.1.0)
├── start.sh                    # 快速启动脚本 ⭐
├── install.sh                  # 一键安装脚本 ⭐
├── requirements.txt            # Python依赖
├── .env                        # 环境配置 (需创建)
├── .gitignore                  # Git忽略
├── README.md                   # 项目文档
├── EXTRACT_GUIDE.md            # 摘取指南
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── recorder.py             # 音频录制
│   ├── asr.py                  # 语音识别
│   ├── summarizer.py           # 纪要生成
│   ├── evaluator.py            # 质量评价 Agent
│   └── architecture_expert.py  # 架构评审 Agent
├── output/                     # 输出目录
│   ├── meeting_minutes_*.md
│   ├── evaluation_report_*.md
│   └── architecture_review_*.md
└── venv/                       # Python虚拟环境
```

---

## ⚙️ 配置说明

### API Key 配置

编辑 `.env` 文件：

```bash
# 智谱 AI (推荐)
ANTHROPIC_API_KEY=your_zhipu_key_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ANTHROPIC_MODEL=glm-4.7

# 或 OpenAI
# ANTHROPIC_API_KEY=your_openai_key
# ANTHROPIC_BASE_URL=https://api.openai.com/v1
# ANTHROPIC_MODEL=gpt-4
```

获取 API Key: https://www.bigmodel.cn/

---

## 🎯 使用场景

### 场景1: 快速演示 (无需API Key)
```bash
./start.sh
# 使用内置模拟数据，展示完整功能
```

### 场景2: 处理真实会议
```bash
# 1. 配置音频设备 (macOS示例)
brew install blackhole-2ch
# 系统设置 → 音频 → 输出 → BlackHole 2ch

# 2. 启动录制
./start.sh --live

# 3. 开始会议，音频自动捕获
# 4. 会议结束按 Ctrl+C，自动生成纪要
```

### 场景3: 技术评审会议
```bash
./start.sh --arch-review
# 额外生成架构评审报告
# 识别技术债务、架构风险
```

---

## 📊 输出文件说明

每次运行生成以下文件：

| 文件 | 说明 |
|------|------|
| `meeting_minutes_*.md` | 结构化会议纪要 |
| `evaluation_report_*.md` | 质量评价报告 |
| `architecture_review_*.md` | 架构评审报告 (加 --arch-review) |
| `meeting_data_*.json` | 结构化数据 |

---

## 🛠️ 高级用法

### 作为库使用

```python
from core.evaluator import MeetingEvaluator
from core.architecture_expert import ArchitectureExpert

# 评价会议纪要
evaluator = MeetingEvaluator()
result = evaluator.evaluate(transcript, minutes)
print(f"评分: {result.overall_score}/100")

# 架构评审
expert = ArchitectureExpert()
review = expert.review_meeting_architecture(minutes)
```

### 批量处理

```bash
# 批量处理历史录音
for file in ./recordings/*.wav; do
    python3 main.py --input "$file" --output-dir ./output
done
```

---

## 🔧 故障排除

### 问题: ModuleNotFoundError
```bash
# 解决: 确保在虚拟环境中
source venv/bin/activate
```

### 问题: API 调用失败
```bash
# 检查 API Key
cat .env
# 确认网络连接
curl https://open.bigmodel.cn/api/paas/v4/models
```

### 问题: 录音无声
```bash
# macOS: 检查音频设备
system_profiler SPAudioDataType | grep "BlackHole"
# 确认系统音频输出已切换到虚拟设备
```

---

## 📦 打包分发

如果想把 MeetingMind 分享给他人：

```bash
# 1. 清理临时文件
rm -rf output/*.md __pycache__ .pytest_cache

# 2. 打包
tar czvf meetingmind-v2.1.0.tar.gz \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='output/*.md' \
    meetingmind/

# 3. 接收方解压后运行
./install.sh
./start.sh
```

---

## 📝 更新日志

### v2.1.0 (2026-03-15)
- ✅ 重构为专业版，移除demo命名
- ✅ 新增 Architecture Expert Agent
- ✅ 添加 install.sh / start.sh 脚本
- ✅ 完善命令行参数支持

### v2.0 (2026-03-14)
- ✅ 新增 Evaluator Agent 质量评价
- ✅ 5维度评分系统

### v1.0 (2026-03-14)
- ✅ MVP核心功能
- ✅ 音频录制 → ASR → 纪要生成

---

## 📞 支持

遇到问题？
1. 查看 `EXTRACT_GUIDE.md` 详细摘取指南
2. 运行 `./start.sh --help` 查看使用帮助
3. 检查 `main.py --version` 确认版本

---

**MeetingMind v2.1.0** - AI驱动的智能会议纪要系统
