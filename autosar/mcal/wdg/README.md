# WDG 模块 - 看门狗驱动

> **学习日期**: 2026-03-04  > **模块类型**: MCAL系统监控  > **难度**: ⭐⭐

---

## 看门狗类型

| 类型 | 说明 |
|------|------|
| Internal WDG | 芯片内置，时钟独立 |
| External WDG | 通过SPI/I2C控制的外部芯片 |
| Window WDG | 必须在时间窗口内喂狗 |

---

## 三种工作模式

| 模式 | 用途 | 超时时间 |
|------|------|----------|
| OFF_MODE | 调试/刷写 | 禁用 |
| SLOW_MODE | 正常运行 | 较长（如100ms）|
| FAST_MODE | 启动阶段 | 较短（如10ms）|

---

## 关键API

```c
void Wdg_Init(const Wdg_ConfigType* ConfigPtr);
void Wdg_SetMode(Wdg_ModeType Mode);
void Wdg_SetTriggerCondition(uint16 Timeout);  // 喂狗
```

---

## 最佳实践

```c
// 在主循环中喂狗，不要在中断中喂
void Cyclic_10ms_Task(void) {
    Wdg_SetTriggerCondition(50);  // 重置超时计数器
}
```

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第12期*
