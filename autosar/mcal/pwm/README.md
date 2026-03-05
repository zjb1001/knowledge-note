# PWM 模块 - 脉宽调制

> **学习日期**: 2026-03-03  
> **模块类型**: MCAL定时输出  
> **难度**: ⭐⭐

---

## 核心API

```c
void Pwm_Init(const Pwm_ConfigType* ConfigPtr);
void Pwm_SetDutyCycle(Pwm_ChannelType Channel, uint16 DutyCycle);  // 0x0000=0%, 0x8000=100%
void Pwm_SetPeriodAndDuty(Pwm_ChannelType Channel, Pwm_PeriodType Period, uint16 DutyCycle);
void Pwm_SetOutputToIdle(Pwm_ChannelType Channel);
void Pwm_EnableNotification(Pwm_ChannelType Channel, Pwm_EdgeNotificationType Notification);
```

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Channel | 独立PWM输出通道 |
| Period | PWM周期，频率=1/Period |
| DutyCycle | 占空比，AUTOSAR用`0x8000`表示100% |
| Polarity | 输出极性（高/低电平有效）|
| IdleState | 空闲状态电平 |

---

## 常见陷阱

- 占空比计算错误：混淆百分比和定点值（0x8000=100%）
- 极性配置错误：导致DutyCycle=0时输出电平与预期相反
- 与ADC相位失配：采样时刻不在期望的PWM周期位置

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第4期*
