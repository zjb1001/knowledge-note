# FLS 模块 - Flash驱动

> **学习日期**: 2026-03-04  > **模块类型**: MCAL存储  > **难度**: ⭐⭐⭐⭐

---

## 核心功能

- 读取Flash数据
- 擦除Sector/Block
- 写入数据（按Page）
- 保护机制（写保护、读保护）

---

## 关键API

```c
void Fls_Init(const Fls_ConfigType* ConfigPtr);
Std_ReturnType Fls_Erase(Fls_AddressType TargetAddress, Fls_LengthType Length);
Std_ReturnType Fls_Write(Fls_AddressType TargetAddress, const uint8* SourceAddressPtr, Fls_LengthType Length);
Std_ReturnType Fls_Read(Fls_AddressType SourceAddress, uint8* TargetAddressPtr, Fls_LengthType Length);
void Fls_MainFunction(void);  // 异步操作处理
```

---

## 操作限制

1. **写入前必须先擦除**: Flash只能由1写0，擦除后全为1
2. **按Sector擦除**: 最小擦除单位是Sector（通常4KB/8KB）
3. **按Page写入**: 最小写入单位是Page（通常256字节）
4. **寿命限制**: 典型10万次擦写周期

---

## 常见陷阱

- 写入前未擦除：导致数据错误
- 擦写过程中断电：可能导致数据损坏
- 超过寿命：Flash可靠性下降
- 中断中操作Flash：可能导致时序违规

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第10期*
