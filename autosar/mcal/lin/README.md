# LIN 模块 - LIN控制器驱动

> **学习日期**: 2026-03-04  
> **模块类型**: MCAL低成本通信  
003e **难度**: ⭐⭐

---

## LIN特点

- 单主多从结构
- 最大波特率20kbps
- 基于UART/SCI实现
- 成本低，用于门控、座椅等舒适系统

---

## 关键API

```c
void Lin_Init(const Lin_ConfigType* ConfigPtr);
Std_ReturnType Lin_SendHeader(uint8 Channel, uint8 Pid);      // 发送报头
Std_ReturnType Lin_SendResponse(uint8 Channel, const uint8* SduPtr);  // 发送响应
Std_ReturnType Lin_ReceiveResponse(uint8 Channel, uint8* SduPtr, uint8 Length);
```

---

## Master vs Slave

| 角色 | 功能 |
|------|------|
| Master | 发送报头（包含PID），控制总线时序 |
| Slave | 响应Master的报头，发送或接收数据 |

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第9期*
