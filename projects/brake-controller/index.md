# BrakeGuard 制动控制器项目

**项目代号**: brake-controller  
**项目类型**: 嵌入式安全关键系统（ASIL-D）  
**PI 周期**: Sprint 1 (2026-03-14 ~ 2026-03-21)  
**状态**: 🟡 进行中

---

## 项目状态

| 指标 | 数值 |
|------|------|
| 总任务 | 15 |
| 已完成 | 0 |
| 进行中 | 0 |
| **完成率** | **0%** |

**进度**: ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 文档导航

### 规划文档
- [Sprint 1 PI 规划](./planning/sprint-1.md) - 完整的 Sprint 规划、任务分解、里程碑

### 需求文档
- [需求规格说明书](./requirements/specification.md)
- [用例文档](./requirements/use-cases.md)

### 设计文档
- [架构设计](./design/architecture.md)
- [接口定义](./design/interfaces.md)
- [MCAL 配置](./design/mcal-config.md)

### 测试文档
- [测试计划](./planning/test-plan.md)
- [测试报告](./reports/)

---

## 快速命令

```bash
# 初始化项目
./scripts/init.sh

# 查看任务
./scripts/tasks.sh

# 更新任务状态
./scripts/update-task.sh T1 done

# 提交进度（自动推送到知识库）
./scripts/commit-progress.sh "完成控制算法仿真"

# 手动推送到知识库
./scripts/push-to-knowledge.sh
```

---

## GStack 命令关联

| 命令 | 功能 | 关联文档 |
|------|------|----------|
| `/plan brake-controller` | 查看 PI 规划 | [sprint-1.md](./planning/sprint-1.md) |
| `/plan brake-controller/simulink` | 仿真环境规划 | - |
| `/plan brake-controller/mcal-config` | MCAL 配置规划 | - |
| `/review brake-controller/drivers` | 驱动代码审查 | - |
| `/review brake-controller/integration` | 集成审查 | - |
| `/qa brake-controller/simulation` | 仿真测试 | - |
| `/qa brake-controller/hil` | HIL 测试 | - |
| `/ship brake-controller/demo` | Demo 发布检查 | - |
| `/ship brake-controller/docs` | 文档发布 | - |

---

## 自动化同步

- **自动同步**: 每 4 小时自动同步项目状态到知识库
- **手动同步**: 运行 `./scripts/push-to-knowledge.sh`
- **提交时同步**: 运行 `./scripts/commit-progress.sh` 时自动同步

---

## 项目路径

本地路径: `/root/.openclaw/workspace/projects/brake-controller`  
知识库路径: `/projects/brake-controller`

---

*最后更新: 2026-03-14 11:25:00*  
*项目初始化完成*
