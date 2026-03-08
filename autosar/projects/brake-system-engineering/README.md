# 制动系统工程 - 项目索引

> **项目代号**: BRAKE-SYS-ENG-2026  
> **项目类型**: 汽车电子制动控制系统（ASIL-D）  
003e **技术栈**: AUTOSAR Classic Platform  
> **文档版本**: v2.0

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
├── 01-project-management/          # 项目管理
│   └── project-plan.md            # 24个月项目规划
│                                   # - 阶段划分
│                                   # - 里程碑定义
│                                   # - 团队组织
│                                   # - 甘特图
│
├── 02-system-design/              # 系统设计
│   └── system-architecture.md     # 系统架构设计
│                                   # - 端到端系统架构
│                                   # - 功能安全分区
│                                   # - 端到端控制时序
│                                   # - 故障响应时序
│
├── 03-software-architecture/      # 软件架构
│   ├── asw-architecture.md        # 应用层架构
│   │                               # - 17个SWC架构
│   │                               # - SWC运行时行为
│   │                               # - RTE接口矩阵
│   │
│   └── bsw-architecture.md        # 服务层架构
│                                   # - BSW分层架构
│                                   # - COM Stack配置
│                                   # - DCM诊断服务
│                                   # - NVM存储设计
│
├── 04-module-design/              # 模块详细设计
│   ├── swc-brake-control.md       # 制动主控制SWC
│   ├── swc-abs.md                 # ABS控制SWC
│   ├── swc-esc.md                 # ESC控制SWC
│   ├── swc-epb.md                 # EPB控制SWC
│   └── swc-safety-monitor.md      # 安全监控SWC
│
├── 05-mcal-configuration/         # MCAL配置
│   ├── mcal-overview.md           # MCAL总览
│   ├── adc-configuration.md       # ADC配置
│   ├── pwm-configuration.md       # PWM配置
│   ├── can-configuration.md       # CAN配置
│   └── icu-configuration.md       # ICU配置
│
├── 06-testing/                    # 测试验证
│   ├── test-strategy.md           # 测试策略
│   ├── test-plans/                # 测试计划
│   └── test-reports/              # 测试报告
│
└── 07-release/                    # 发布交付
    └── release-notes.md           # 发布说明
```

---

## 快速导航

### 1. 项目管理
- [项目总体规划](01-project-management/project-plan.md) - 24个月完整规划

### 2. 系统设计
- [系统架构设计](02-system-design/system-architecture.md) - 专家级架构设计

### 3. 软件架构
- [应用层架构](03-software-architecture/asw-architecture.md) - ASW详细设计
- [服务层架构](03-software-architecture/bsw-architecture.md) - BSW详细设计

### 4. 模块设计
- [SWC_BrakeControl](04-module-design/swc-brake-control.md) - 制动主控制
- SWC_ABS - 防抱死控制 (待补充)
- SWC_ESC - 稳定控制 (待补充)
- SWC_EPB - 电子驻车 (待补充)

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

---

## 使用指南

### 阅读顺序建议

1. **项目启动** → [项目总体规划](01-project-management/project-plan.md)
2. **系统理解** → [系统架构设计](02-system-design/system-architecture.md)
3. **软件设计** → [应用层架构](03-software-architecture/asw-architecture.md)
4. **实现细节** → [模块详细设计](04-module-design/)
5. **配置参考** → [MCAL配置](05-mcal-configuration/)

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

---

## 联系与贡献

本项目作为知识库文档，供团队内部学习参考。

---

*制动系统工程 - 完整开发案例*  
*面向汽车开发的主体命题*