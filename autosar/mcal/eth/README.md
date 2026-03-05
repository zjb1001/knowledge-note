# ETH 模块 - 以太网驱动

> **学习日期**: 2026-03-05  > **模块类型**: MCAL高速通信  > **难度**: ⭐⭐⭐⭐

---

## 核心应用场景

- ADAS数据流：摄像头/雷达原始数据传输
- OTA升级：大文件下载
- 诊断通信：DoIP（Diagnostic over IP）
- 域控制器互联

---

## 关键API

```c
void Eth_Init(const Eth_ConfigType* ConfigPtr);
Std_ReturnType Eth_Transmit(Eth_CtrlType CtrlIdx, Eth_BufIdxType BufIdx, uint16 Len);
void Eth_Receive(Eth_CtrlType CtrlIdx, Eth_BufIdxType BufIdx);
void Eth_SetControllerMode(Eth_CtrlType CtrlIdx, Eth_ModeType CtrlMode);
```

---

## 车规以太网标准

| 标准 | 速率 | 应用 |
|------|------|------|
| 100BASE-T1 | 100Mbps | 普通车载通信 |
| 1000BASE-T1 | 1Gbps | 摄像头/激光雷达 |

---

## 常见陷阱

- PHY地址错误：SMI地址配置错误导致Link Down
- 缓冲区未对齐：DMA缓冲区需32/64-bit对齐
- MAC地址重复：整车网络中MAC冲突
- Link Up检测：需显式检查PHY Link Status

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第13期*
