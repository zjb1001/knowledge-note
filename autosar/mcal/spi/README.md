# SPI 模块 - 串行外设接口

> **学习日期**: 2026-03-04  
> **模块类型**: MCAL同步通信  
> **难度**: ⭐⭐⭐

---

## 核心概念: Job + Sequence + Channel

```
Sequence（序列）
    └── Job 1（任务）→ Channel A → Channel B
    └── Job 2（任务）→ Channel C
    └── Job 3（任务）→ Channel D → Channel A
```

- **Channel**: 最小传输单元，绑定到一个硬件SPI+片选信号
- **Job**: 一次片选有效期间的连续传输
- **Sequence**: 完整的传输序列，包含多个Job

---

## 关键API

```c
void Spi_Init(const Spi_ConfigType* ConfigPtr);
Std_ReturnType Spi_SyncTransmit(Spi_SequenceType Sequence);    // 同步传输
Std_ReturnType Spi_AsyncTransmit(Spi_SequenceType Sequence);   // 异步传输
Spi_StatusType Spi_GetStatus(void);
```

---

## CPOL/CPHA四种模式

| 模式 | CPOL | CPHA | 时钟空闲 | 采样边沿 |
|------|------|------|----------|----------|
| 0 | 0 | 0 | 低 | 上升沿 |
| 1 | 0 | 1 | 低 | 下降沿 |
| 2 | 1 | 0 | 高 | 下降沿 |
| 3 | 1 | 1 | 高 | 上升沿 |

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第7期*
