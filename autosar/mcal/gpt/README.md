# GPT 模块 - 通用定时器

> **学习日期**: 2026-03-04  > **模块类型**: MCAL定时基准  > **难度**: ⭐⭐

---

## 核心功能

- 提供微秒/毫秒级时间基准
- 周期性中断（如1ms系统时基）
- 单次延时/超时功能
- 为其他外设提供时钟源

---

## 两种模式

| 模式 | 说明 | 用途 |
|------|------|------|
| CONTINUOUS | 溢出后自动重载，持续产生中断 | OS Tick |
| ONESHOT | 计数到目标值后停止 | 单次延时 |

---

## 关键API

```c
void Gpt_Init(const Gpt_ConfigType* ConfigPtr);
void Gpt_StartTimer(Gpt_ChannelType Channel, Gpt_ValueType Value);
void Gpt_StopTimer(Gpt_ChannelType Channel);
Gpt_ValueType Gpt_GetTimeElapsed(Gpt_ChannelType Channel);
```

---

## Tick频率计算

```
实际Tick周期 = (Prescaler + 1) / GptClockFrequency
目标中断周期 = TargetValue × Tick周期

例：80MHz时钟，Prescaler=79，TargetValue=1000
Tick周期 = 80/80MHz = 1us
中断周期 = 1000 × 1us = 1ms
```

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第11期*
