# MeetingMind 独立运行指南

## 方法一：直接复制（最快）

```bash
# 1. 创建独立目录
mkdir ~/meetingmind
cd ~/meetingmind

# 2. 复制核心文件
cp /path/to/knowledge-note/projects/meetingmind/main.py .
cp /path/to/knowledge-note/projects/meetingmind/demo_v2.py .
cp /path/to/knowledge-note/projects/meetingmind/requirements.txt .
mkdir -p core
cp /path/to/knowledge-note/projects/meetingmind/core/*.py core/

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行
cd ~/meetingmind
python demo_v2.py
```

## 方法二：Git Subtree（保留历史）

```bash
# 1. 创建新仓库
git init meetingmind
cd meetingmind

# 2. 从 knowledge-note 拉取子目录
git remote add knowledge-note https://github.com/zjb1001/knowledge-note.git
git fetch knowledge-note
git checkout -b main

# 3. 使用 git-filter-repo 提取子目录历史
# 安装: pip install git-filter-repo
git filter-repo --path projects/meetingmind --path-rename projects/meetingmind:.

# 4. 推送到新远程（可选）
git remote add origin https://github.com/yourname/meetingmind.git
git push -u origin main
```

## 方法三：使用提供的脚本

```bash
cd /root/.openclaw/workspace/projects/meetingmind
chmod +x extract-meetingmind.sh
./extract-meetingmind.sh

# 运行
cd ~/meetingmind
python demo_v2.py
```

---

## 目录结构

摘取后的独立项目结构：

```
~/meetingmind/
├── main.py              # CLI入口
├── demo_v2.py           # v2.0演示
├── demo_v3_concept.py   # v3.0概念 (自迭代)
├── extract-meetingmind.sh  # 摘取脚本
├── requirements.txt     # 依赖
├── .gitignore          # Git忽略
├── README.md           # 文档
└── core/
    ├── __init__.py
    ├── recorder.py      # 音频录制
    ├── asr.py          # 语音识别
    ├── summarizer.py   # 纪要生成
    └── evaluator.py    # 🎯 Evaluator Agent
```

---

## 运行前准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 创建 .env 文件
cat > .env << EOF
ANTHROPIC_API_KEY=your_zhipu_key_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ANTHROPIC_MODEL=glm-4.7
EOF

# 添加到 .gitignore
echo ".env" >> .gitignore
```

### 3. 运行演示

```bash
# v1.0 基础版
python demo_full.py

# v2.0 带 Evaluator
python demo_v2.py

# v3.0 自迭代概念 (可选)
python demo_v3_concept.py
```

---

## 独立开发

摘取后，你可以：

```bash
# 1. 创建自己的 Git 仓库
git init
git add .
git commit -m "Initial commit"

# 2. 推送到 GitHub
git remote add origin https://github.com/yourname/meetingmind.git
git push -u origin main

# 3. 独立迭代开发
# 修改代码 → 测试 → commit → push
```

---

## 与原仓库的关系

| 方式 | 与原仓库关系 | 适用场景 |
|------|-------------|---------|
| 直接复制 | 完全独立 | 快速试用、不再同步 |
| Git Subtree | 可同步更新 | 需要定期拉取上游更新 |
| Fork | 保留关联 | 打算贡献回上游 |

---

## 快速开始

```bash
# 一键摘取并运行
cd /root/.openclaw/workspace/projects/meetingmind
./extract-meetingmind.sh
cd ~/meetingmind
python demo_v2.py
```
