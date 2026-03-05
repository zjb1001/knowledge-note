# ICU 模块 - 输入捕获

> **学习日期**: 2026-03-03  
> **模块类型**: MCAL信号测量  
> **难度**: ⭐⭐⭐

---

## 四种测量模式

1. **SIGNAL_EDGE_DETECT** - 边沿检测，触发回调
2. **SIGNAL_MEASUREMENT** - 信号测量，硬件自动计算周期和占空比
3. **TIMESTAMP** - 时间戳模式，记录每个边沿的原始时刻
4. **EDGE_COUNTER** - 边沿计数，统计脉冲个数

---

## 关键API

```c
void Icu_StartSignalMeasurement(Icu_ChannelType Channel);
void Icu_GetDutyCycleValues(Icu_ChannelType Channel, Icu_DutyCycleType* DutyCycleValues);
Icu_EdgeNumberType Icu_GetEdgeNumbers(Icu_ChannelType Channel);
```

---

## 常见陷阱

- 占空比测量结果为0：信号周期超过定时器溢出时间
- 中断风暴：高频信号+双边沿检测导致系统卡顿
- 与PWM资源冲突：eMIOS通道只能二选一

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第5期*
