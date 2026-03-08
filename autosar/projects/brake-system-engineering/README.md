# 制动系统工程 - 项目索引

> **项目代号**: BRAKE-SYS-ENG-2026  
> **项目类型**: 汽车电子制动控制系统（ASIL-D）  
> **技术栈**: AUTOSAR Classic Platform  
> **文档版本**: v3.0 - 完整版

---

## 项目概述

本项目是一个完整的制动系统工程开发案例，从项目管理、系统设计到模块实现、测试验证，涵盖汽车电子制动控制系统的全生命周期。

### 项目目标

开发一套符合 ASIL-D 功能安全等级的电子制动控制系统，包括：
- **常规制动**: 驾驶员踏板控制
- **ABS**: 防抱死制动系统
- **ESC**: 电子稳定控制系统
- **EBD**: 电子制动力分配
- **EPB**: 电子驻车制动
- **Autohold**: 自动驻车功能

---

## 文档结构

```
autosar/projects/brake-system-engineering/
│
├── README.md                              # 项目索引和导航
│
├── 01-project-management/                 # 项目管理
│   └── project-plan.md                    # 24个月项目规划
│
├── 02-system-design/                      # 系统设计
│   └── system-architecture.md             # 专家级系统架构
│
├── 03-software-architecture/              # 软件架构
│   ├── asw-architecture.md                # 应用层架构
│   ├── bsw-architecture.md                # 服务层架构 (通信/诊断)
│   └── bsw-services-complete.md           # 服务层完整架构 ⭐推荐
│
├── 04-module-design/                      # 模块详细设计
│   ├── swc-brake-control.md               # 制动主控制SWC
│   ├── swc-abs.md                         # ABS控制SWC
│   └── swc-esc.md                         # ESC控制SWC
│
├── 05-mcal-configuration/                 # MCAL配置
│   └── mcal-overview.md                   # 微控制器驱动配置
│
├── 06-testing/                            # 测试验证
└── 07-release/                            # 发布交付
```

---

## 快速导航

### 1. 项目管理
- [项目总体规划](01-project-management/project-plan.md) - 24个月完整规划

### 2. 系统设计
- [系统架构设计](02-system-design/system-architecture.md) - 专家级架构设计

### 3. 软件架构
- [应用层架构](03-software-architecture/asw-architecture.md) - ASW详细设计
- [服务层架构-通信/诊断](03-software-architecture/bsw-architecture.md) - BSW通信/诊断/存储
- [服务层完整架构](03-software-architecture/bsw-services-complete.md) - **信号监控/服务降级/看门狗** ⭐推荐

### 4. 模块设计
- [SWC_BrakeControl](04-module-design/swc-brake-control.md) - 制动主控制
- [SWC_ABS](04-module-design/swc-abs.md) - 防抱死控制
- [SWC_ESC](04-module-design/swc-esc.md) - 稳定控制

### 5. MCAL配置
- [MCAL配置总览](05-mcal-configuration/mcal-overview.md) - 微控制器驱动配置

---

## 技术特点

### 功能安全
- **ASIL等级**: 全系统ASIL-D
- **安全机制**: E2E保护、安全监控、冗余设计
- **认证标准**: ISO 26262-2018

### 性能指标
- **控制周期**: 2ms
- **响应时间**: < 10ms (端到端)
- **故障响应**: < 50ms

### 软件架构
- **架构标准**: AUTOSAR Classic Platform
- **SWC数量**: 17个应用软件组件
- **代码规范**: MISRA C:2012

### 服务层完整性
- **通信服务**: COM/PDUR/CANIF/NM
- **诊断服务**: DCM/DEM/FIM
- **监控服务**: WDGM/信号监控/E2E
- **存储服务**: NVM/FEE/MEMIF (含冗余保护)
- **模式管理**: BSWM/ECUM (服务降级)
- **MCAL驱动**: ADC/PWM/ICU/CAN/WDG

---

## 文档统计

| 类别 | 文档数 | 代码行数 | 内容覆盖 |
|------|--------|----------|----------|
| 项目管理 | 1 | 10,940 | 24个月规划、甘特图 |
| 系统设计 | 1 | 26,415 | 端到端架构、时序分析 |
| 软件架构 | 3 | 62,303 | ASW + BSW通信 + BSW完整服务 |
| 模块设计 | 3 | 26,878 | BrakeControl + ABS + ESC |
| MCAL配置 | 1 | 15,986 | 完整MCAL配置 |
| **总计** | **9** | **~142,522行** | **完整系统工程** |

---

## 核心亮点

### 应用层
- ✅ 17个SWC完整架构
- ✅ SWC_BrakeControl: 多源仲裁、状态机
- ✅ SWC_ABS: 五阶段控制、滑移率算法
- ✅ SWC_ESC: 滑模控制、力矩分配

### 服务层 (完整)
- ✅ COM Stack: 优化配置、确定性传输
- ✅ DCM诊断: UDS服务、AES-128 CMAC
- ✅ **WDGM看门狗**: 任务监控、超时检测 ⭐
- ✅ **信号监控**: 范围/变化率/超时检查 ⭐
- ✅ **BSWM模式管理**: 服务降级、故障响应 ⭐
- ✅ **NVM存储**: 冗余保护、写入验证 ⭐

### 微控制器层
- ✅ ADC: 踏板10kHz、压力1kHz
- ✅ PWM: 阀1kHz、电机5kHz
- ✅ ICU: 轮速1μs精度
- ✅ CAN: 500kbps车辆网络
- ✅ WDG: 10-100ms安全监控

### 系统级
- ✅ 端到端控制时序 (5ms延迟)
- ✅ 功能安全分区 (ASIL-D/B/QM)
- ✅ E2E保护机制
- ✅ 故障响应 (<50ms)
- ✅ **服务降级矩阵** ⭐

---

## 使用指南

### 阅读顺序建议

1. **项目启动** → [项目总体规划](01-project-management/project-plan.md)
2. **系统理解** → [系统架构设计](02-system-design/system-architecture.md)
3. **软件设计** → [应用层架构](03-software-architecture/asw-architecture.md)
4. **服务理解** → [服务层完整架构](03-software-architecture/bsw-services-complete.md) ⭐推荐
5. **实现细节** → [模块详细设计](04-module-design/)
6. **配置参考** → [MCAL配置](05-mcal-configuration/)

### 适用读者

- 汽车电子系统工程师
- AUTOSAR软件工程师
- 功能安全工程师
- 制动系统开发人员
- 汽车电子专业学生

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-08 | 初始版本，项目规划 + 基础设计 |
| v2.0 | 2026-03-08 | 目录重构，专家级架构优化 |
| v3.0 | 2026-03-08 | 补充服务层完整架构 (监控/降级/存储) |

---

## 联系与贡献

本项目作为知识库文档，供团队内部学习参考。

---

*制动系统工程 - 完整开发案例*  
*面向汽车开发的主体命题*  
*从控制器专家视角的完整服务层设计*