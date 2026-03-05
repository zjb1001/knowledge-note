# CAN 模块 - CAN控制器驱动

> **学习日期**: 2026-03-04  
> **模块类型**: MCAL车载网络  
> **难度**: ⭐⭐⭐⭐

---

## CAN 2.0B vs CAN FD

| 特性 | CAN 2.0B | CAN FD |
|------|----------|--------|
| 数据长度 | 0-8字节 | 0-64字节 |
| 波特率 | 最高1Mbps | 数据段最高8Mbps |
| CRC | 15位 | 17/21位 |

---

## 核心API

```c
void Can_Init(const Can_ConfigType* ConfigPtr);
Can_ReturnType Can_Write(Can_HwHandleType Hth, const Can_PduType* PduInfo);
void Can_MainFunction_Write(void);   // 发送处理
void Can_MainFunction_Read(void);    // 接收处理
void Can_MainFunction_BusOff(void);  // BusOff恢复
```

---

## 常见陷阱

- 波特率配置错误：导致无法通信
- 邮箱配置不足：发送邮箱满时返回BUSY
- 中断优先级：CAN中断优先级需合理设置
- 终端电阻：CAN总线需两端各120Ω终端电阻

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第8期*
