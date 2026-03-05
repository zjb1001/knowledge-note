# OCU 模块 - 输出比较

> **学习日期**: 2026-03-03  
> **模块类型**: MCAL定时控制  
> **难度**: ⭐⭐⭐

---

## 与PWM的区别

| 特性 | PWM | OCU |
|------|-----|-----|
| 输出 | 周期性波形 | 单点/离散时刻控制 |
| 用途 | 固定频率可变占空比 | 灵活的单脉冲或相位控制 |
| 典型应用 | 电机调速、LED调光 | 多路PWM相位同步、步进电机 |

---

## 关键API

```c
void Ocu_SetCompareValue(Ocu_ChannelType Channel, Ocu_ValueType CompareValue);
void Ocu_SetPinAction(Ocu_ChannelType Channel, Ocu_PinActionType Action);  // SET/CLEAR/TOGGLE
```

---

## 关键概念

- **Compare Value**: 比较阈值，计数器等于该值时触发动作
- **Pin Action**: 匹配时的引脚动作（置高/置低/翻转/无动作）
- **Counter Bus**: eMIOS的计数器总线（A/B/C/D）

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第6期*
