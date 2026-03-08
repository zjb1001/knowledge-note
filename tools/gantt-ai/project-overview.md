# Gantt Graph AI - AI增强甘特图项目实践

> **项目日期**: 2026-03-04  
> **项目类型**: AI+项目管理工具  
> **技术栈**: React + TypeScript + Python FastAPI + LLM

---

## 项目概述

一个结合AI能力的智能甘特图项目管理工具，能够：
- 通过自然语言输入自动生成项目计划
- AI智能分解任务并识别依赖关系
- 风险分析和进度预测
- 基于关键路径法(CPM)的工期计算

---

## 核心功能架构

### 1. AI任务分解流程

```
用户输入(自然语言)
    ↓
AI解析 → 识别技术要素 → 生成任务列表
    ↓
任务结构化(含依赖关系、工期估算)
    ↓
甘特图可视化展示
```

### 2. 技术要素识别

AI自动识别项目中的关键维度：
- ✅ 系统架构设计
- ✅ 硬件/传感器系统
- ✅ 执行机构/驱动
- ✅ 通信网络协议
- ✅ 核心功能开发
- ✅ 功能安全(ASIL)
- ✅ 测试验证

### 3. 风险管理

自动识别项目风险点：
- **进度风险**: 关键路径延期
- **依赖风险**: 任务间耦合度过高
- **资源风险**: 人员/设备不足
- **技术风险**: 新技术栈学习成本

---

## 实践案例

### 案例1: 汽车电子制动系统开发

**输入需求**:
```
开发一套完整的整车电子制动系统，包含：
- 主控制器：基于AUTOSAR架构的BCU
- 传感器系统：轮速、踏板位置、压力传感器  
- 执行机构：ESC模块、ABS阀体、EPB电机
- 核心功能：ABS、EBD、ESC、EPB、Autohold
- 技术要求：ASIL-D、ISO 26262、响应<200ms
- 开发周期：18个月，团队15人
```

**AI输出结果**:
- 7个开发阶段
- 28个具体任务
- 540天工期规划
- 任务依赖关系图
- 关键里程碑节点

**技术要素覆盖**:
| 维度 | 覆盖情况 |
|------|----------|
| 系统架构 | ✅ BCU设计、冗余方案 |
| 传感器 | ✅ 轮速、踏板、压力 |
| 执行机构 | ✅ ESC、ABS、EPB |
| 通信 | ✅ CAN FD、车载以太网 |
| 功能 | ✅ ABS/EBD/ESC/EPB |
| 功能安全 | ✅ ASIL-D、FMEDA |
| 测试 | ✅ HIL、实车、法规 |

---

## 项目结构

```
ganttGraph/
├── 📁 src/                      # 前端React源码
│   ├── components/              # 甘特图组件
│   ├── pages/                   # 页面路由
│   ├── stores/                  # Zustand状态管理
│   └── utils/                   # 工具函数(CPM算法等)
├── 📁 agent-service/            # AI后端服务
│   ├── enhanced_ai_service.py   # FastAPI服务主入口
│   ├── main.py                  # 基础服务
│   └── test_*.py                # 测试脚本
└── 📄 package.json              # 前端依赖
```

---

## 关键技术实现

### CPM关键路径算法

```python
def calculate_critical_path(tasks):
    """
    计算项目关键路径
    - 最早开始/结束时间(正向遍历)
    - 最晚开始/结束时间(反向遍历)
    - 总浮动时间 = 最晚开始 - 最早开始
    - 关键路径: 总浮动时间为0的任务链
    """
    # 正向: 计算最早时间
    for task in topological_sort(tasks):
        task.early_start = max(t.early_finish for t in task.predecessors)
        task.early_finish = task.early_start + task.duration
    
    # 反向: 计算最晚时间
    for task in reverse_topological_sort(tasks):
        task.late_finish = min(t.late_start for t in task.successors)
        task.late_start = task.late_finish - task.duration
    
    # 关键路径
    return [t for t in tasks if t.total_float == 0]
```

### AI Prompt工程

```python
SYSTEM_PROMPT = """
你是一位专业的项目管理专家，擅长：
1. 将自然语言需求分解为结构化任务
2. 识别任务间的依赖关系
3. 估算合理的工期
4. 识别项目风险点

输出格式要求：
- 任务列表(含ID、名称、工期、前置任务)
- 关键里程碑
- 风险分析
- 技术要素覆盖检查
"""
```

---

## 验证结果

| 功能项 | 状态 | 备注 |
|--------|------|------|
| API连接 | ✅ | LLM响应正常 |
| 任务分解 | ✅ | 支持专业技术项目 |
| 风险分析 | ✅ | 识别延期、依赖风险 |
| 进度预测 | ✅ | CPM算法+关键路径 |
| 可视化 | ✅ | 甘特图渲染正常 |

---

## 经验总结

### 做得好的地方
1. **AI+工具结合**: LLM负责理解意图，工具负责精确计算
2. **专业领域适配**: 针对汽车电子等专业领域优化Prompt
3. **算法验证**: CPM算法经过标准案例验证

### 改进方向
1. **多轮对话**: 支持任务细节的迭代优化
2. **模板库**: 积累行业项目模板
3. **数据反馈**: 实际vs预测工期对比学习

---

*项目实践记录*  
*关键词: AI项目管理、甘特图、CPM算法、任务分解*
