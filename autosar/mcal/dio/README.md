# DIO 模块 - 数字I/O驱动

> **学习日期**: 2026-03-03  
> **模块类型**: MCAL基础I/O  
> **难度**: ⭐

---

## 模块定位

DIO（Digital Input/Output）是MCAL层的数字I/O驱动，负责读写引脚的数字电平状态（0/1）。

**注意**: DIO只操作数据寄存器，不配置引脚属性（配置由PORT完成）。

---

## 核心API

```c
// 通道操作（单个引脚）
Dio_LevelType Dio_ReadChannel(Dio_ChannelType ChannelId);
void Dio_WriteChannel(Dio_ChannelType ChannelId, Dio_LevelType Level);
Dio_LevelType Dio_FlipChannel(Dio_ChannelType ChannelId);

// 端口操作（整个GPIO端口）
Dio_PortLevelType Dio_ReadPort(Dio_PortType PortId);
void Dio_WritePort(Dio_PortType PortId, Dio_PortLevelType Level);

// 通道组操作（按掩码）
Dio_PortLevelType Dio_ReadChannelGroup(const Dio_ChannelGroupType* ChannelGroupIdPtr);
void Dio_WriteChannelGroup(const Dio_ChannelGroupType* ChannelGroupIdPtr, Dio_PortLevelType Level);
```

---

## DIO vs PORT 职责分离

| 职责 | PORT | DIO |
|------|------|-----|
| 配置 | ✅ 方向/复用/电气特性 | ❌ 无配置能力 |
| 数据 | ❌ 不操作数据 | ✅ 读写数据寄存器 |
| 运行时 | ✅ 可改方向（若允许） | ✅ 读写电平 |

---

## 常见陷阱

1. **读取前未配置PORT**: 引脚未配为输入时，读值无效
2. **写入前未配置PORT**: 引脚未配为输出时，写入被硬件忽略
3. **混淆Channel/Port/ChannelGroup**: 
   - Channel = 单个引脚
   - Port = 整个GPIO端口（8/16/32位）
   - ChannelGroup = 按掩码指定的多个bit
4. **中断中调用DIO**: 非原子操作可能导致竞态

---

## 使用示例

```c
// LED闪烁（假设PORT已配置为输出）
void Led_Toggle(void) {
    Dio_FlipChannel(DioConf_LED_Channel);
}

// 读取按键（假设PORT已配置为输入+上拉）
boolean Key_Pressed(void) {
    return (Dio_ReadChannel(DioConf_KEY_Channel) == STD_LOW);
}
```

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第2期*
