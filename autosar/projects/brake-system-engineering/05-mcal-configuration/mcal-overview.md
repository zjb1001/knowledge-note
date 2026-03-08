# MCAL配置总览 - 制动系统微控制器驱动

> **文档编号**: MCAL-BRAKE-001  
> **适用芯片**: Infineon TC397TP  
> **配置工具**: EB tresos Studio  
> **ASIL等级**: D

---

## 1. MCAL架构概述

### 1.1 MCAL在系统架构中的位置

```
┌─────────────────────────────────────────────────────────────┐
│                     AUTOSAR 软件架构                         │
├─────────────────────────────────────────────────────────────┤
│  应用层 (ASW)                                                │
│  ├── SWC_BrakePedal                                         │
│  ├── SWC_ABS                                                │
│  ├── SWC_ESC                                                │
│  └── ...                                                    │
├─────────────────────────────────────────────────────────────┤
│  运行时环境 (RTE)                                            │
├─────────────────────────────────────────────────────────────┤
│  基础软件 (BSW)                                              │
│  ├── 服务层 (COM/DCM/NVM)                                   │
│  ├── ECU抽象层 (IOHwAb/CANIF)                               │
│  └── 微控制器驱动 (MCAL) ◄── 本文档重点                      │
├─────────────────────────────────────────────────────────────┤
│  微控制器硬件 (TC397TP)                                      │
│  ├── CPU0: 主控制核 (ASIL-D)                                │
│  ├── CPU1: 安全监控核 (ASIL-D)                              │
│  └── 外设: ADC/PWM/CAN/GPT/DIO/WDG                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 MCAL模块清单

| 模块 | 功能 | ASIL | 用途 |
|------|------|------|------|
| **ADC** | 模数转换 | D | 踏板/压力传感器采集 |
| **PWM** | 脉宽调制 | D | 阀体/电机控制 |
| **ICU** | 输入捕获 | D | 轮速信号捕获 |
| **CAN** | CAN控制器 | D | 车辆网络通信 |
| **DIO** | 数字IO | D | 电磁阀控制 |
| **GPT** | 通用定时 | D | 任务时基 |
| **WDG** | 看门狗 | D | 安全监控 |
| **MCU** | 微控制器 | D | 时钟/复位 |

---

## 2. ADC配置详解

### 2.1 制动系统ADC需求分析

| 信号 | 通道 | 分辨率 | 采样率 | 精度要求 |
|------|------|--------|--------|----------|
| 踏板主传感器 | AN0 | 12bit | 10kHz | ±0.5% |
| 踏板副传感器 | AN1 | 12bit | 10kHz | ±0.5% |
| 主缸压力 | AN2 | 12bit | 1kHz | ±0.1bar |
| 轮缸压力FL | AN4 | 12bit | 1kHz | ±0.1bar |
| 轮缸压力FR | AN5 | 12bit | 1kHz | ±0.1bar |
| 轮缸压力RL | AN6 | 12bit | 1kHz | ±0.1bar |
| 轮缸压力RR | AN7 | 12bit | 1kHz | ±0.1bar |

### 2.2 ADC配置代码

```c
//=============================================================================
// ADC Driver Configuration for Brake System
// 文件: Adc_PBcfg.c (Post Build Configuration)
//=============================================================================

#include "Adc.h"

//-------------------- ADC General Configuration --------------------
const Adc_GeneralConfigurationType Adc_GeneralConfiguration = {
    .AdcDevErrorDetect = STD_ON,                    // 开发错误检测
    .AdcVersionInfoApi = STD_OFF,                   // 版本信息API
    .AdcEnableLimitCheck = STD_ON,                  // 使能限值检查
    .AdcEnableQueuing = STD_OFF,                    // 禁用队列
    .AdcPriorityImplementation = ADC_PRIORITY_HW,   // 硬件优先级
    .AdcGrpNotifCapability = STD_ON,                // 组通知能力
    .AdcHwTriggerApi = STD_ON,                      // 硬件触发API
    .AdcStartStopGroupApi = STD_ON                  // 启动停止组API
};

//-------------------- ADC Channel Configuration --------------------
// 踏板传感器通道 - 高速采样
const Adc_ChannelConfigurationType AdcChannelConfig_BrakePedal = {
    .AdcChannelId = ADC_CH_BRAKE_PEDAL_PRIMARY,     // 逻辑通道ID
    .AdcChannelAdcGroup = ADC_GROUP_PEDAL,          // 所属组
    .AdcChannelInputNumber = 0,                     // 物理通道AN0
    .AdcChannelResolution = ADC_RESOLUTION_12BIT,   // 12位分辨率
    .AdcChannelSamplingTime = ADC_SAMPLE_TIME_100NS,// 100ns采样时间
    .AdcChannelRange = ADC_RANGE_0V_5V,             // 0-5V量程
    .AdcChannelLimitCheck = STD_ON,                 // 使能限值检查
    .AdcChannelLimitCheckLow = 200,                 // 下限 (ADC值)
    .AdcChannelLimitCheckHigh = 4000                // 上限 (ADC值)
};

// 压力传感器通道 - 中速采样
const Adc_ChannelConfigurationType AdcChannelConfig_MasterCylPressure = {
    .AdcChannelId = ADC_CH_MASTER_CYL_PRESSURE,
    .AdcChannelAdcGroup = ADC_GROUP_PRESSURE,
    .AdcChannelInputNumber = 2,                     // AN2
    .AdcChannelResolution = ADC_RESOLUTION_12BIT,
    .AdcChannelSamplingTime = ADC_SAMPLE_TIME_500NS,// 500ns (高阻抗源)
    .AdcChannelRange = ADC_RANGE_0V_5V,
    .AdcChannelLimitCheck = STD_ON,
    .AdcChannelLimitCheckLow = 0,
    .AdcChannelLimitCheckHigh = 4095
};

//-------------------- ADC Group Configuration --------------------
// 踏板采样组 - 高速连续采样
const Adc_GroupConfigurationType AdcGroupConfig_Pedal = {
    .AdcGroupId = ADC_GROUP_PEDAL,
    .AdcGroupConversionMode = ADC_CONV_MODE_CONTINUOUS,  // 连续模式
    .AdcGroupTriggerSource = ADC_TRIG_SRC_HW,            // 硬件触发
    .AdcGroupHwTriggerSignal = ADC_HW_TRIG_GPT_CH0,      // GPT触发
    .AdcGroupPriority = 3,                               // 优先级3
    .AdcGroupChannelList = {
        ADC_CH_BRAKE_PEDAL_PRIMARY,
        ADC_CH_BRAKE_PEDAL_SECONDARY
    },
    .AdcGroupStreamingNumSamples = 1,
    .AdcGroupNotification = AdcNotification_PedalGroup,
    .AdcChannelLimitCheck = STD_ON
};

// 压力采样组 - 中速单次采样
const Adc_GroupConfigurationType AdcGroupConfig_Pressure = {
    .AdcGroupId = ADC_GROUP_PRESSURE,
    .AdcGroupConversionMode = ADC_CONV_MODE_ONESHOT,     // 单次模式
    .AdcGroupTriggerSource = ADC_TRIG_SRC_SW,            // 软件触发
    .AdcGroupPriority = 2,
    .AdcGroupChannelList = {
        ADC_CH_MASTER_CYL_PRESSURE,
        ADC_CH_WHEEL_PRESSURE_FL,
        ADC_CH_WHEEL_PRESSURE_FR,
        ADC_CH_WHEEL_PRESSURE_RL,
        ADC_CH_WHEEL_PRESSURE_RR
    },
    .AdcGroupStreamingNumSamples = 1,
    .AdcGroupNotification = AdcNotification_PressureGroup
};

//-------------------- ADC Notification Functions --------------------
void AdcNotification_PedalGroup(void)
{
    // 踏板组转换完成回调
    // 触发SWC_BrakePedal Runnable
    RTE_SetEvent_EV_AdcPedalComplete();
}

void AdcNotification_PressureGroup(void)
{
    // 压力组转换完成回调
    RTE_SetEvent_EV_AdcPressureComplete();
}
```

---

## 3. PWM配置详解

### 3.1 制动系统PWM需求

| 负载 | 通道 | 频率 | 分辨率 | 精度 |
|------|------|------|--------|------|
| 进油阀FL | PWM0 | 1kHz | 10bit | ±0.1% |
| 出油阀FL | PWM1 | 1kHz | 10bit | ±0.1% |
| 进油阀FR | PWM2 | 1kHz | 10bit | ±0.1% |
| 出油阀FR | PWM3 | 1kHz | 10bit | ±0.1% |
| ... | ... | ... | ... | ... |
| 泵电机 | PWM8 | 5kHz | 10bit | ±0.1% |
| EPB电机L | PWM9 | 10kHz | 10bit | ±0.1% |
| EPB电机R | PWM10 | 10kHz | 10bit | ±0.1% |

### 3.2 PWM配置代码

```c
//=============================================================================
// PWM Driver Configuration for Brake System
// 文件: Pwm_PBcfg.c
//=============================================================================

#include "Pwm.h"

//-------------------- PWM General Configuration --------------------
const Pwm_GeneralConfigurationType Pwm_GeneralConfiguration = {
    .PwmDevErrorDetect = STD_ON,
    .PwmDutycycleUpdatedEndperiod = STD_OFF,  // 立即更新
    .PwmIndex = 0
};

//-------------------- PWM Channel Configuration --------------------
// 进油阀PWM - 1kHz, 占空比控制
const Pwm_ChannelConfigurationType PwmChannelConfig_InletValve_FL = {
    .PwmChannelId = PWM_CH_INLET_VALVE_FL,
    .PwmHwChannel = PWM_EMIOS0_CH0,           // eMIOS通道0
    .PwmPeriodDefault = 1000,                 // 1000 ticks = 1kHz (假设时钟1MHz)
    .PwmDutyCycleDefault = 0,                 // 默认0% (关闭)
    .PwmPolarity = PWM_HIGH,                  // 高电平有效
    .PwmIdleState = PWM_LOW,                  // 空闲低电平
    .PwmClassRef = NULL                       // 无专用类
};

// 出油阀PWM - 1kHz, 占空比控制
const Pwm_ChannelConfigurationType PwmChannelConfig_OutletValve_FL = {
    .PwmChannelId = PWM_CH_OUTLET_VALVE_FL,
    .PwmHwChannel = PWM_EMIOS0_CH1,
    .PwmPeriodDefault = 1000,
    .PwmDutyCycleDefault = 0,
    .PwmPolarity = PWM_HIGH,
    .PwmIdleState = PWM_LOW
};

// 泵电机PWM - 5kHz, 高频率减少转矩脉动
const Pwm_ChannelConfigurationType PwmChannelConfig_PumpMotor = {
    .PwmChannelId = PWM_CH_PUMP_MOTOR,
    .PwmHwChannel = PWM_GTM_TOM0_CH0,         // GTM TOM通道
    .PwmPeriodDefault = 200,                  // 200 ticks = 5kHz
    .PwmDutyCycleDefault = 0,
    .PwmPolarity = PWM_HIGH,
    .PwmIdleState = PWM_LOW
};

//-------------------- PWM Power State Configuration --------------------
const Pwm_PowerStateConfigurationType Pwm_PowerStateConfiguration = {
    .PwmPowerState = PWM_FULL_POWER,          // 全功率模式
    .PwmPowerStateReadyCb = NULL              // 无回调
};

//-------------------- PWM Notification Functions --------------------
void PwmNotification_InletValve(void)
{
    // 进油阀周期结束回调
    // 可用于电流采样
}
```

---

## 4. ICU配置详解

### 4.1 轮速传感器接口

| 轮速信号 | 通道 | 捕获模式 | 分辨率 |
|----------|------|----------|--------|
| 轮速FL | ICU0 | 周期测量 | 1μs |
| 轮速FR | ICU1 | 周期测量 | 1μs |
| 轮速RL | ICU2 | 周期测量 | 1μs |
| 轮速RR | ICU3 | 周期测量 | 1μs |

### 4.2 ICU配置代码

```c
//=============================================================================
// ICU Driver Configuration for Wheel Speed Sensors
// 文件: Icu_PBcfg.c
//=============================================================================

#include "Icu.h"

//-------------------- ICU General Configuration --------------------
const Icu_GeneralConfigurationType Icu_GeneralConfiguration = {
    .IcuDevErrorDetect = STD_ON,
    .IcuIndex = 0,
    .IcuOptionalApis = {
        .IcuSetModeApi = STD_ON,
        .IcuDisableWakeupApi = STD_ON,
        .IcuEnableWakeupApi = STD_ON,
        .IcuGetInputStateApi = STD_ON,
        .IcuTimestampApi = STD_OFF,
        .IcuEdgeCountApi = STD_OFF,
        .IcuSignalMeasurementApi = STD_ON,    // 信号测量API
        .IcuGetTimeElapsedApi = STD_ON,
        .IcuGetDutyCycleApi = STD_ON
    }
};

//-------------------- ICU Channel Configuration --------------------
// 轮速信号测量 - 周期测量模式
const Icu_ChannelConfigurationType IcuChannelConfig_WSS_FL = {
    .IcuChannelId = ICU_CH_WSS_FL,
    .IcuHwChannel = ICU_EMIOS0_CH2,           // eMIOS通道2
    .IcuDefaultStartEdge = ICU_RISING_EDGE,   // 上升沿开始
    .IcuMeasurementMode = ICU_MODE_SIGNAL_MEASUREMENT,
    .IcuSignalMeasurementProperty = ICU_PERIOD_TIME,  // 测量周期
    .IcuNotification = IcuNotification_WSS_FL
};

const Icu_ChannelConfigurationType IcuChannelConfig_WSS_FR = {
    .IcuChannelId = ICU_CH_WSS_FR,
    .IcuHwChannel = ICU_EMIOS0_CH3,
    .IcuDefaultStartEdge = ICU_RISING_EDGE,
    .IcuMeasurementMode = ICU_MODE_SIGNAL_MEASUREMENT,
    .IcuSignalMeasurementProperty = ICU_PERIOD_TIME,
    .IcuNotification = IcuNotification_WSS_FR
};

const Icu_ChannelConfigurationType IcuChannelConfig_WSS_RL = {
    .IcuChannelId = ICU_CH_WSS_RL,
    .IcuHwChannel = ICU_EMIOS0_CH4,
    .IcuDefaultStartEdge = ICU_RISING_EDGE,
    .IcuMeasurementMode = ICU_MODE_SIGNAL_MEASUREMENT,
    .IcuSignalMeasurementProperty = ICU_PERIOD_TIME,
    .IcuNotification = IcuNotification_WSS_RL
};

const Icu_ChannelConfigurationType IcuChannelConfig_WSS_RR = {
    .IcuChannelId = ICU_CH_WSS_RR,
    .IcuHwChannel = ICU_EMIOS0_CH5,
    .IcuDefaultStartEdge = ICU_RISING_EDGE,
    .IcuMeasurementMode = ICU_MODE_SIGNAL_MEASUREMENT,
    .IcuSignalMeasurementProperty = ICU_PERIOD_TIME,
    .IcuNotification = IcuNotification_WSS_RR
};

//-------------------- ICU Notification Functions --------------------
void IcuNotification_WSS_FL(void)
{
    Icu_DutyCycleType duty_cycle;
    
    // 读取周期测量结果
    Icu_GetDutyCycleValues(ICU_CH_WSS_FL, &duty_cycle);
    
    // 计算轮速: V = K / Period
    // K为传感器齿数相关的常数
    WheelSpeed_FL = WSS_CALIBRATION_K / duty_cycle.PeriodTime;
    
    // 通知SWC_WheelSpeed
    RTE_SetEvent_EV_WheelSpeedUpdate();
}

void IcuNotification_WSS_FR(void) { /* 同上 */ }
void IcuNotification_WSS_RL(void) { /* 同上 */ }
void IcuNotification_WSS_RR(void) { /* 同上 */ }
```

---

## 5. CAN配置详解

### 5.1 CAN网络配置

| 网络 | 波特率 | 用途 | 节点数 |
|------|--------|------|--------|
| CAN1 (底盘域) | 500kbps | 制动/转向/底盘 | 8 |
| CAN2 (动力域) | 500kbps | 发动机/电机 | 6 |
| CAN3 (诊断) | 500kbps | 诊断/刷写 | 2 |

### 5.2 CAN配置代码

```c
//=============================================================================
// CAN Driver Configuration
// 文件: Can_PBcfg.c
//=============================================================================

#include "Can.h"

//-------------------- CAN General Configuration --------------------
const Can_GeneralConfigurationType Can_GeneralConfiguration = {
    .CanDevErrorDetect = STD_ON,
    .CanIndex = 0,
    .CanTimeoutDuration = 1000,           // 超时1000us
    .CanMultiplexedTransmission = STD_OFF,
    .CanPublicIcomSupport = STD_OFF
};

//-------------------- CAN Controller Configuration --------------------
// CAN0 - 底盘域 (500kbps)
const Can_ControllerConfigurationType CanControllerConfig_Chassis = {
    .CanControllerId = CAN_CTRL_CHASSIS,
    .CanControllerBaseAddress = 0xF0200000,  // 控制器基地址
    .CanTxProcessing = CAN_INTERRUPT,        // 中断发送
    .CanRxProcessing = CAN_INTERRUPT,        // 中断接收
    .CanBusoffProcessing = CAN_INTERRUPT,    // 中断处理Busoff
    .CanWakeupProcessing = CAN_INTERRUPT,
    .CanControllerDefaultBaudrate = 500000,  // 500kbps
    .CanControllerBaudrateConfig = {
        .CanControllerPrescaler = 4,         // 预分频
        .CanControllerTimeSeg1 = 13,         // 时间段1
        .CanControllerTimeSeg2 = 2,          // 时间段2
        .CanControllerSyncJumpWidth = 1      // 同步跳转宽度
    },
    .CanControllerTxErrorCounter = 0,
    .CanControllerRxErrorCounter = 0,
    .CanControllerFdBaudrateConfig = NULL    // 非CAN FD
};

//-------------------- CAN Hardware Object Configuration --------------------
// TX Hardware Object
const Can_HardwareObjectConfigurationType CanHOConfig_Tx = {
    .CanObjectId = CAN_HO_TX_CHASSIS,
    .CanHandleType = CAN_BASIC,              // 基本类型
    .CanIdType = CAN_STANDARD,               // 标准ID
    .CanObjectType = CAN_TRANSMIT,           // 发送
    .CanControllerRef = CAN_CTRL_CHASSIS,
    .CanHwObjectCount = 8                    // 8个发送缓冲
};

// RX Hardware Object
const Can_HardwareObjectConfigurationType CanHOConfig_Rx = {
    .CanObjectId = CAN_HO_RX_CHASSIS,
    .CanHandleType = CAN_FULL,               // 完整类型
    .CanIdType = CAN_STANDARD,
    .CanObjectType = CAN_RECEIVE,            // 接收
    .CanControllerRef = CAN_CTRL_CHASSIS,
    .CanHwObjectCount = 16,                  // 16个接收缓冲
    .CanHwFilterCode = 0x000,                // 过滤码
    .CanHwFilterMask = 0x000                 // 接收所有
};
```

---

## 6. 系统集成配置

### 6.1 时钟配置

```c
//=============================================================================
// MCU Clock Configuration
//=============================================================================

#include "Mcu.h"

const Mcu_ClockConfigurationType McuClockConfig = {
    .McuClockSettingId = 0,
    .McuClockReferencePoint = {
        // 系统时钟: 300MHz
        .McuClockReferencePointFrequency = 300000000,
        .McuClockReferencePointPrescaler = 1
    },
    // 外设时钟配置
    .McuPeripheralClockConfig = {
        // ADC时钟: 80MHz
        {.McuPeripheralId = MCU_PERIPH_ADC, .McuPeripheralClockDiv = 3},
        // PWM/GPT时钟: 100MHz
        {.McuPeripheralId = MCU_PERIPH_GTM, .McuPeripheralClockDiv = 3},
        // CAN时钟: 80MHz
        {.McuPeripheralId = MCU_PERIPH_CAN, .McuPeripheralClockDiv = 3}
    }
};
```

### 6.2 看门狗配置

```c
//=============================================================================
// WDG Configuration
//=============================================================================

#include "Wdg.h"

const Wdg_ConfigType WdgConfig = {
    .WdgIndex = 0,
    .WdgSettings = {
        [WDG_MODE_SLOW] = {
            .WdgTimeout = 100,        // 100ms超时
            .WdgWindow = 50           // 50ms窗口
        },
        [WDG_MODE_FAST] = {
            .WdgTimeout = 10,         // 10ms超时 (调试/启动)
            .WdgWindow = 5
        }
    },
    .WdgNotification = WdgNotification_Warning
};
```

---

## 7. 配置验证清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| ADC采样率 | ✅ | 踏板10kHz, 压力1kHz |
| PWM频率 | ✅ | 阀1kHz, 电机5-10kHz |
| CAN波特率 | ✅ | 500kbps |
| ICU分辨率 | ✅ | 1μs |
| 时钟配置 | ✅ | 系统300MHz |
| 看门狗 | ✅ | 10-100ms |
| 中断优先级 | ✅ | 安全相关最高 |
| 内存保护 | ✅ | MPU配置 |

---

*MCAL配置总览 - 制动系统微控制器驱动*