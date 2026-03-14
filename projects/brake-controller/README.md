# 嵌入式制动控制器项目

**项目代号**: BrakeGuard  
**项目类型**: 嵌入式安全关键系统（ASIL-D）  
**PI 周期**: Sprint 1 (2026-03-14 ~ 2026-03-21)  
**状态**: 🟡 规划中

---

## 项目目标

在 1 周内交付可演示的制动控制器原型，验证核心控制算法可行性，建立功能安全开发基础。

## 技术栈

- **MCU**: Infineon TC3x7 (Aurix)
- **开发环境**: EB tresos + Tasking
- **建模仿真**: MATLAB/Simulink
- **调试工具**: UDE / Lauterbach
- **版本控制**: Git + GitHub
- **项目管理**: GStack + 自动化脚本

## 项目结构

```
brake-controller/
├── docs/              # 文档
│   ├── requirements/  # 需求文档
│   ├── design/        # 设计文档
│   └── api/           # API 文档
├── src/               # 源代码
│   ├── mcal/          # MCAL 配置
│   ├── bsw/           # 基础软件
│   ├── asw/           # 应用软件
│   └── app/           # 应用层
├── tests/             # 测试
│   ├── unit/          # 单元测试
│   ├── integration/   # 集成测试
│   └── hil/           # HIL 测试
├── scripts/           # 自动化脚本
└── .github/           # CI/CD 配置
```

## 快速开始

```bash
# 克隆项目
git clone git@github.com:zjb1001/brake-controller.git
cd brake-controller

# 初始化环境
./scripts/init.sh

# 查看任务
./scripts/tasks.sh

# 提交进度
./scripts/commit-progress.sh "完成控制算法仿真"
```

## GStack 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `/plan` | 查看 PI 规划 | `/plan brake-controller` |
| `/review` | 代码审查 | `/review src/mcal` |
| `/ship` | 发布检查 | `/ship v0.1.0` |
| `/qa` | 测试状态 | `/qa tests/hil` |
| `/retro` | 复盘 | `/retro sprint-1` |

---

*自动生成于 2026-03-14*  
*项目路径: /root/.openclaw/workspace/projects/brake-controller*
