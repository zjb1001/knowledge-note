# Sprint 1 PI 规划：制动控制器原型

**项目**: BrakeGuard 制动控制器  
**Sprint**: Sprint 1 (2026-03-14 ~ 2026-03-21)  
**目标**: 交付可演示的控制器原型  
**状态**: 🟢 已批准

---

## Sprint 目标（SMART）

**具体目标**: 
- 完成 Simulink 制动控制算法仿真
- 在 TC3x7 开发板部署单轮制动控制
- 实现 3 个基础测试场景验证

**成功标准**:
- [ ] 仿真响应时间 < 200ms
- [ ] 制动距离误差 < 5%
- [ ] 硬件循环测试通过 3 个场景
- [ ] Demo 视频录制完成

---

## 任务分解

### 阶段一：仿真验证 (D1-D3)

| ID | 任务 | 负责人 | 工时 | 状态 | 关联路径 |
|----|------|--------|------|------|----------|
| T1 | 搭建 Simulink 环境 | 算法工程师 | 4h | ⬜ | `/plan brake-controller/simulink` |
| T2 | 车辆动力学建模 | 算法工程师 | 8h | ⬜ | `/plan brake-controller/vehicle-model` |
| T3 | 制动控制算法设计 | 算法工程师 | 8h | ⬜ | `/plan brake-controller/algorithm` |
| T4 | 仿真测试用例设计 | 测试工程师 | 4h | ⬜ | `/plan brake-controller/test-cases` |
| T5 | 仿真验证与调优 | 算法工程师 | 8h | ⬜ | `/qa brake-controller/simulation` |

**阶段一里程碑** (D3 18:00):
- Simulink 模型运行通过
- 仿真报告输出
- 控制参数冻结

### 阶段二：硬件部署 (D4-D5)

| ID | 任务 | 负责人 | 工时 | 状态 | 关联路径 |
|----|------|--------|------|------|----------|
| T6 | TC3x7 开发环境搭建 | 嵌入式工程师 | 4h | ⬜ | `/plan brake-controller/mcal-setup` |
| T7 | MCAL 基础配置 (MCU/PORT/ADC/PWM) | 嵌入式工程师 | 12h | ⬜ | `/plan brake-controller/mcal-config` |
| T8 | 底层驱动开发 | 嵌入式工程师 | 8h | ⬜ | `/review brake-controller/drivers` |
| T9 | 代码生成工具链配置 | 嵌入式工程师 | 4h | ⬜ | `/plan brake-controller/codegen` |

**阶段二里程碑** (D5 18:00):
- 开发板 LED 闪烁测试通过
- MCAL 基础配置完成
- 编译工具链就绪

### 阶段三：算法集成 (D6-D7)

| ID | 任务 | 负责人 | 工时 | 状态 | 关联路径 |
|----|------|--------|------|------|----------|
| T10 | 控制算法 C 代码生成 | 算法工程师 | 4h | ⬜ | `/review brake-controller/algorithm-code` |
| T11 | 算法与驱动集成 | 嵌入式工程师 | 8h | ⬜ | `/review brake-controller/integration` |
| T12 | 基础诊断功能实现 | 嵌入式工程师 | 4h | ⬜ | `/qa brake-controller/diagnostics` |
| T13 | HIL 测试执行 | 测试工程师 | 8h | ⬜ | `/qa brake-controller/hil` |
| T14 | Demo 视频录制 | 全员 | 4h | ⬜ | `/ship brake-controller/demo` |
| T15 | 技术文档整理 | 全员 | 4h | ⬜ | `/ship brake-controller/docs` |

**阶段三里程碑** (D7 18:00):
- 单轮制动 Demo 可演示
- 3 个测试场景通过
- Demo 视频 + 技术文档

---

## 资源分配

### 人力
| 角色 | 人数 | 投入 |
|------|------|------|
| 控制算法工程师 | 1 | 100% (D1-D7) |
| 嵌入式工程师 | 1 | 100% (D1-D7) |
| 测试工程师 | 0.5 | 50% (D3-D7) |

### 硬件
| 设备 | 数量 | 到位时间 |
|------|------|----------|
| Infineon TC3x7 开发板 | 2 | D1 前 |
| 制动执行器模拟负载 | 1 | D4 前 |
| 压力传感器 | 2 | D4 前 |
| CAN 分析仪 | 1 | D4 前 |

### 软件工具
- MATLAB/Simulink R2023b
- EB tresos Studio 29.0
- Tasking VX-toolset for TriCore
- UDE v2023

---

## 风险登记册

| ID | 风险描述 | 概率 | 影响 | 缓解措施 | 负责人 |
|----|----------|------|------|----------|--------|
| R1 | 控制算法仿真不稳定 | 中 | 高 | 准备 fallback PID 方案；D3 冻结算法 | 算法工程师 |
| R2 | MCAL 配置复杂耗时 | 高 | 中 | D1-D2 专注环境搭建；准备模板工程 | 嵌入式工程师 |
| R3 | 开发板硬件故障 | 低 | 高 | 准备备用开发板；提前测试 | 嵌入式工程师 |
| R4 | 工具链授权问题 | 中 | 中 | 提前申请试用许可；准备开源替代 | 项目经理 |
| R5 | 进度延迟风险 | 中 | 中 | 每日站会；D3/D5 里程碑检查；允许降级到纯仿真 | 项目经理 |

---

## 质量标准

### 代码质量
- MISRA C:2012 合规（关键代码）
- 圈复杂度 < 10
- 单元测试覆盖率 > 80%

### 测试标准
- HIL 测试通过 3 个基础场景
- 故障注入测试通过（传感器断线）
- 代码审查通过（至少 1 人 review）

### 文档要求
- README 包含环境搭建步骤
- API 文档（关键接口）
- 测试报告（仿真 + HIL）

---

## 每日站会

**时间**: 每天早上 09:30  
**时长**: 15 分钟  
**形式**: 线下/线上

### 议程
1. 昨天完成了什么？
2. 今天计划做什么？
3. 有什么阻塞？

### 检查点
- **D3**: 仿真模型完成检查
- **D5**: 开发板环境就绪检查
- **D7**: Demo 演示准备检查

---

## 自动化命令

```bash
# 查看当前任务状态
./scripts/tasks.sh

# 更新任务进度
./scripts/update-task.sh T1 done

# 提交今日进度
./scripts/commit-progress.sh "完成 T1-T3：Simulink 环境搭建和车辆建模"

# 生成日报
./scripts/daily-report.sh

# 推送项目状态到知识库
./scripts/push-to-knowledge.sh
```

---

## 关联文档

- [需求规格说明书](./requirements.md)
- [架构设计文档](./architecture.md)
- [测试计划](./test-plan.md)
- [风险评估报告](./risk-assessment.md)

---

*自动生成于 2026-03-14*  
*最后更新: 2026-03-14 11:20*  
*项目路径: /projects/brake-controller/docs/planning/sprint-1.md*
