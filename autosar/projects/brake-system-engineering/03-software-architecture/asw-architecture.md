# 制动系统 - 应用层 (ASW) 详细设计

> **文档编号**: BRAKE-ASW-001  
> **版本**: v1.0  
> **所属阶段**: 阶段4 - 应用软件开发

---

## 1. ASW架构总览

### 1.1 软件组件 (SWC) 架构图

```mermaid
graph TB
    subgraph 应用层_ASW["应用层 ASW - Application Layer"]
        
        subgraph 传感层["📡 传感与输入层"]
            SWC_PEDAL["SWC_BrakePedal<br/>制动踏板解析"]
            SWC_WSS["SWC_WheelSpeed<br/>轮速处理"]
            SWC_IMU["SWC_VehicleDynamics<br/>车辆动力学"]
            SWC_PRESSURE["SWC_HydPressure<br/>液压压力"]
        end
        
        subgraph 决策层["🧠 控制决策层"]
            SWC_BRAKE_CTRL["SWC_BrakeControl<br/>主制动控制"]
            SWC_ABS["SWC_ABS<br/>防抱死控制"]
            SWC_ESC["SWC_ESC<br/>稳定控制"]
            SWC_EBD["SWC_EBD<br/>力分配控制"]
        end
        
        subgraph 执行层["🔧 执行控制层"]
            SWC_VALVE_CTRL["SWC_ValveControl<br/>阀体控制"]
            SWC_MOTOR_CTRL["SWC_MotorControl<br/>电机控制"]
            SWC_PRESSURE_CTRL["SWC_PressureControl<br/>压力控制"]
        end
        
        subgraph 功能层["🎯 功能应用层"]
            SWC_EPB["SWC_EPB<br/>电子驻车"]
            SWC_AUTOHOLD["SWC_Autohold<br/>自动驻车"]
            SWC_AEB["SWC_AEB<br/>自动紧急制动"]
        end
        
        subgraph 管理层["⚙️ 系统管理层"]
            SWC_FAULT_MGR["SWC_FaultManager<br/>故障管理"]
            SWC_MODE_MGR["SWC_ModeManager<br/>模式管理"]
            SWC_DIAG_MGR["SWC_DiagManager<br/>诊断管理"]
        end
    end

    subgraph 外部接口["🔗 外部接口"]
        ADAS["ADAS系统"]
        CHASSIS["底盘域"]
        HMI["人机界面"]
    end

    SWC_PEDAL --> SWC_BRAKE_CTRL
    SWC_WSS --> SWC_BRAKE_CTRL
    SWC_IMU --> SWC_BRAKE_CTRL
    SWC_PRESSURE --> SWC_BRAKE_CTRL
    
    SWC_BRAKE_CTRL --> SWC_ABS
    SWC_BRAKE_CTRL --> SWC_ESC
    SWC_BRAKE_CTRL --> SWC_EBD
    
    SWC_ABS --> SWC_VALVE_CTRL
    SWC_ESC --> SWC_VALVE_CTRL
    SWC_EBD --> SWC_VALVE_CTRL
    
    SWC_VALVE_CTRL --> SWC_PRESSURE_CTRL
    SWC_BRAKE_CTRL --> SWC_MOTOR_CTRL
    
    SWC_BRAKE_CTRL --> SWC_EPB
    SWC_BRAKE_CTRL --> SWC_AUTOHOLD
    ADAS --> SWC_AEB
    SWC_AEB --> SWC_BRAKE_CTRL
    
    SWC_FAULT_MGR --> SWC_BRAKE_CTRL
    SWC_MODE_MGR --> SWC_BRAKE_CTRL
    SWC_BRAKE_CTRL --> SWC_DIAG_MGR

    style 决策层 fill:#e3f2fd
    style 功能层 fill:#fff3e0
```

### 1.2 SWC清单与ASIL分配

| SWC名称 | 功能描述 | ASIL等级 | 周期 | 核心算法 |
|---------|----------|----------|------|----------|
| SWC_BrakePedal | 踏板位移解析、梯度计算 | D | 2ms | 滤波、梯度 |
| SWC_WheelSpeed | 轮速处理、滑移率计算 | D | 2ms | ICU捕获、滑移率 |
| SWC_VehicleDynamics | 车辆状态估计 | D | 10ms | 卡尔曼滤波 |
| SWC_HydPressure | 液压压力处理 | D | 2ms | 滤波、补偿 |
| SWC_BrakeControl | 主制动控制逻辑 | D | 2ms | 状态机、仲裁 |
| SWC_ABS | 防抱死控制 | D | 2ms | PID、Bang-Bang |
| SWC_ESC | 稳定控制 | D | 2ms | 滑模控制、LQR |
| SWC_EBD | 制动力分配 | D | 2ms | 分配算法 |
| SWC_ValveControl | 阀体控制 | D | 2ms | PWM控制 |
| SWC_MotorControl | 电机控制 | D | 2ms | FOC、PWM |
| SWC_PressureControl | 压力闭环控制 | D | 2ms | PID |
| SWC_EPB | 电子驻车 | C | 10ms | 状态机 |
| SWC_Autohold | 自动驻车 | B | 10ms | 状态机 |
| SWC_AEB | AEB接口 | D | 2ms | 信号接口 |
| SWC_FaultManager | 故障管理 | D | 10ms | 诊断逻辑 |
| SWC_ModeManager | 模式管理 | D | 10ms | 状态机 |
| SWC_DiagManager | 诊断管理 | D | 50ms | UDS服务 |

---

## 2. 核心SWC详细设计

### 2.1 SWC_BrakeControl (主制动控制)

**功能**: 制动系统主控制逻辑，协调各子系统工作

**端口接口**:
```c
// 接收端口 (R-Port)
RPort_PedalPosition      // 踏板位置输入
RPort_WheelSpeeds        // 四轮轮速
RPort_VehicleAccel       // 车辆加速度
RPort_ADASRequest        // ADAS制动请求
RPort_EPBCmd             // EPB命令
RPort_AutoholdCmd        // Autohold命令

// 发送端口 (P-Port)
PPort_BrakeMode          // 制动模式输出
PPort_TargetDecel        // 目标减速度
PPort_TargetPressure     // 目标压力
PPort_ABS_Enable         // ABS使能
PPort_ESC_Enable         // ESC使能
PPort_EBD_Enable         // EBD使能
```

**内部行为**:
```mermaid
flowchart TD
    subgraph BrakeControlLogic["SWC_BrakeControl 内部逻辑"]
        Input[读取输入信号] --> ModeSel{模式选择}
        
        ModeSel -->|正常制动| NormalCalc[计算目标减速度]
        ModeSel -->|ADAS请求| ADASCalc[ADAS减速度]
        ModeSel -->|EPB激活| EPBCalc[EPB控制]
        ModeSel -->|AEB触发| AEBCalc[全制动]
        
        NormalCalc --> Arbitrate[减速度仲裁]
        ADASCalc --> Arbitrate
        AEBCalc --> Arbitrate
        
        Arbitrate --> PressureCalc[压力换算]
        EPBCalc --> ValveCtrl[直接阀控]
        
        PressureCalc --> Distribute[制动力分配]
        Distribute --> EBDReq[EBD请求]
        Distribute --> ABSCheck{滑移率检查}
        
        ABSCheck -->|超标| ABSReq[ABS请求]
        ABSCheck -->|稳定| ESCheck{稳定性检查}
        
        ESCheck -->|失稳| ESCReq[ESC请求]
        ESCheck -->|稳定| NormalOut[正常输出]
        
        ABSReq --> Output[输出控制量]
        ESCReq --> Output
        NormalOut --> Output
        ValveCtrl --> Output
    end
```

**Runnable设计**:
```c
// Runnable: BrakeControl_Main
// 周期: 2ms
// ASIL: D

void BrakeControl_Main(void) {
    // 1. 读取输入
    PedalPosition = Rte_Read_RPort_PedalPosition();
    WheelSpeeds = Rte_Read_RPort_WheelSpeeds();
    
    // 2. 计算目标减速度
    TargetDecel = CalculateTargetDeceleration(PedalPosition);
    
    // 3. 仲裁
    if (AEB_Active) {
        TargetDecel = AEB_Deceleration;  // 0.8g
    } else if (ADAS_Active) {
        TargetDecel = ADAS_Deceleration;
    }
    
    // 4. 转换为压力
    TargetPressure = DecelToPressure(TargetDecel);
    
    // 5. 子系统使能判断
    ABS_Enable = CheckABSCondition(WheelSpeeds);
    ESC_Enable = CheckESCCondition(YawRate, LatAccel);
    EBD_Enable = CheckEBDCondition();
    
    // 6. 输出
    Rte_Write_PPort_TargetPressure(TargetPressure);
    Rte_Write_PPort_ABS_Enable(ABS_Enable);
    Rte_Write_PPort_ESC_Enable(ESC_Enable);
}
```

### 2.2 SWC_ABS (防抱死控制)

**控制算法流程**:

```mermaid
flowchart LR
    subgraph ABSAlgorithm["ABS控制算法"]
        Input["输入:<br/>- 轮速<br/>- 参考车速<br/>- 目标压力"]
        
        CalcSlip["计算滑移率 λ"]
        SelectWheel["选择控制轮"]
        
        subgraph ControlLogic["控制逻辑"]
            direction TB
            Ph1["Phase 1:<br/>增压"]
            Ph2["Phase 2:<br/>保压"]
            Ph3["Phase 3:<br/>减压"]
            Ph4["Phase 4:<br/>保压"]
        end
        
        Output["输出:<br/>- 进油阀PWM<br/>- 出油阀PWM<br/>- 泵电机"]
    end

    Input --> CalcSlip
    CalcSlip --> SelectWheel
    SelectWheel --> Ph1
    Ph1 -->|λ > 15%| Ph2
    Ph2 -->|λ > 20%| Ph3
    Ph3 -->|λ < 10%| Ph4
    Ph4 -->|恢复| Ph1
    Ph1 -->|λ < 15%| Ph1
    
    Ph1 --> Output
    Ph2 --> Output
    Ph3 --> Output
    Ph4 --> Output
```

**状态机设计**:
```mermaid
stateDiagram-v2
    [*] --> INACTIVE: 系统启动
    
    INACTIVE: 未激活
    INACTIVE --> ACTIVE: 制动踏板踩下<br/>&滑移率>阈值
    
    ACTIVE: ABS激活
    ACTIVE --> INCREASE: 压力增加
    
    INCREASE: 增压阶段
    INCREASE --> HOLD1: 滑移率>15%
    INCREASE --> INCREASE: 滑移率<15%
    
    HOLD1: 保压1
    HOLD1 --> DECREASE: 滑移率>20%
    
    DECREASE: 减压阶段
    DECREASE --> HOLD2: 滑移率<10%
    
    HOLD2: 保压2
    HOLD2 --> INCREASE: 轮速恢复<br/>滑移率<10%
    
    ACTIVE --> INACTIVE: 制动释放<br/>或车速<阈值
    
    INACTIVE --> [*]: 系统关闭
```

---

## 3. RTE接口设计

### 3.1 数据类型定义

```c
// 标准类型定义
#ifndef RTE_TYPE_H
#define RTE_TYPE_H

// 踏板位置
typedef uint16_t Rte_PedalPosition_Type;    // 0-1000 (0-100%)

// 轮速
typedef uint16_t Rte_WheelSpeed_Type;       // 0-65000 (0-650km/h, 0.01km/h/bit)

// 液压压力
typedef uint16_t Rte_HydraulicPressure_Type; // 0-30000 (0-300bar, 0.01bar/bit)

// 减速度
typedef sint16_t Rte_Deceleration_Type;     // -2000-0 (-2g-0, 0.001g/bit)

// 控制模式
enum Rte_BrakeMode_Enum {
    BRAKE_MODE_INACTIVE = 0,
    BRAKE_MODE_NORMAL,
    BRAKE_MODE_ABS,
    BRAKE_MODE_ESC,
    BRAKE_MODE_AEB,
    BRAKE_MODE_EPB,
    BRAKE_MODE_FAULT
};

// 故障等级
enum Rte_FaultLevel_Enum {
    FAULT_NONE = 0,
    FAULT_LEVEL_1,    // 警告
    FAULT_LEVEL_2,    // 功能降级
    FAULT_LEVEL_3     // 系统关闭
};

#endif
```

### 3.2 端口接口矩阵

| 发送SWC | 接收SWC | 接口名称 | 数据类型 | 周期 | ASIL |
|---------|---------|----------|----------|------|------|
| BrakePedal | BrakeControl | PedalPosition | uint16 | 2ms | D |
| WheelSpeed | BrakeControl | WheelSpeeds | array[4] | 2ms | D |
| VehicleDynamics | BrakeControl | YawRate, LatAccel | sint16 | 10ms | D |
| BrakeControl | ABS | ABS_Enable, TargetPressure | struct | 2ms | D |
| BrakeControl | ESC | ESC_Enable, TargetYaw | struct | 2ms | D |
| ABS | ValveControl | ValveCmd_Front, ValveCmd_Rear | struct | 2ms | D |
| ESC | ValveControl | ValveCmd_ESC | struct | 2ms | D |
| ValveControl | PressureControl | TargetPressure_Wheel | array[4] | 2ms | D |
| EPB | ValveControl | EPB_ValveCmd | struct | 10ms | C |
| AEB | BrakeControl | AEB_Request, AEB_Decel | struct | 2ms | D |
| FaultManager | All SWCs | FaultStatus | struct | 10ms | D |
| ModeManager | All SWCs | SystemMode | enum | 10ms | D |

---

## 4. 实现策略

### 4.1 代码组织

```
ASW_BrakeSystem/
├── src/
│   ├── SWC_BrakePedal.c
│   ├── SWC_WheelSpeed.c
│   ├── SWC_VehicleDynamics.c
│   ├── SWC_BrakeControl.c
│   ├── SWC_ABS.c
│   ├── SWC_ESC.c
│   ├── SWC_EBD.c
│   ├── SWC_ValveControl.c
│   ├── SWC_MotorControl.c
│   ├── SWC_EPB.c
│   ├── SWC_Autohold.c
│   ├── SWC_FaultManager.c
│   ├── SWC_ModeManager.c
│   └── ...
├── include/
│   ├── Rte_BrakeSystem.h
│   ├── SWC_BrakePedal.h
│   └── ...
├── lib/
│   └── math_lib.a
└── test/
    └── unit_tests/
```

### 4.2 开发规范

- **编码标准**: MISRA C:2012
- **文档标准**: Doxygen注释
- **单元测试**: 覆盖率>90%
- **静态分析**: Polyspace/QAC
- **版本控制**: Git + 分支策略

---

*应用层 (ASW) 详细设计文档*  
*面向汽车开发的主体命题 - 制动系统工程*