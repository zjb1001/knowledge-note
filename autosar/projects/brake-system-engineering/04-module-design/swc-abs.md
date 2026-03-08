# SWC_ABS - 防抱死制动控制模块设计

> **模块编号**: SWC-ABS-001  
> **ASIL等级**: D  
> **运行周期**: 2ms  
> **核心算法**: 改进型PID + 滑模控制

---

## 1. 模块概述

### 1.1 功能描述

ABS（Anti-lock Braking System）防抱死制动系统，防止车轮在紧急制动时抱死：
- **滑移率控制**: 维持最佳滑移率 10-30%
- **轮缸压力调制**: 增压/保压/减压循环
- **泵电机控制**: 液压回路压力维持
- **多轮协调**: 低选/高选控制策略

### 1.2 控制目标

| 参数 | 目标值 | 说明 |
|------|--------|------|
| 滑移率范围 | 10-30% | 最佳附着系数区间 |
| 压力调节周期 | 60-120ms | ABS循环周期 |
| 压力调节精度 | ±0.5bar | 轮缸压力控制 |
| 响应时间 | < 20ms | 检测到滑移到开始调节 |

---

## 2. 端口接口定义

### 2.1 接收端口 (R-Port)

| 端口名称 | 数据类型 | 来源 | 描述 | 周期 |
|----------|----------|------|------|------|
| RPort_WheelSpeeds | array[4] | WheelSpeed | 四轮轮速 (m/s) | 2ms |
| RPort_ReferenceSpeed | uint16 | VehicleObserver | 参考车速 | 2ms |
| RPort_ABS_Enable | boolean | BrakeControl | ABS使能 | 2ms |
| RPort_TargetPressure | uint16 | BrakeControl | 目标压力 | 2ms |
| RPort_WheelPressures | array[4] | PressureSensor | 实际轮压 | 2ms |

### 2.2 发送端口 (P-Port)

| 端口名称 | 数据类型 | 目标 | 描述 | 周期 |
|----------|----------|------|------|------|
| PPort_ValveCmd_Inlet | array[4] | ValveControl | 进油阀PWM (0-1000) | 2ms |
| PPort_ValveCmd_Outlet | array[4] | ValveControl | 出油阀PWM (0-1000) | 2ms |
| PPort_PumpMotorCmd | uint8 | MotorControl | 泵电机命令 (0-100%) | 2ms |
| PPort_ABS_Active | boolean | DiagManager | ABS激活标志 | 2ms |
| PPort_ABS_Phase | array[4] | DiagManager | 各轮ABS阶段 | 2ms |

---

## 3. 核心算法设计

### 3.1 滑移率计算

```c
// 滑移率计算公式
// λ = (V_ref - V_wheel) / V_ref × 100%
// 其中:
//   λ: 滑移率 (0-100%)
//   V_ref: 参考车速
//   V_wheel: 轮速

void CalculateSlipRatio(float WheelSpeeds[4], float V_ref, float SlipRatio[4])
{
    uint8 i;
    for (i = 0; i < 4; i++) {
        if (V_ref > 2.0) {  // 车速 > 2m/s
            SlipRatio[i] = (V_ref - WheelSpeeds[i]) / V_ref * 100.0;
            
            // 限幅
            if (SlipRatio[i] < 0) SlipRatio[i] = 0;
            if (SlipRatio[i] > 100) SlipRatio[i] = 100;
        } else {
            SlipRatio[i] = 0;  // 车速过低，不计算滑移率
        }
    }
}
```

### 3.2 ABS控制状态机

```mermaid
stateDiagram-v2
    [*] --> INACTIVE: 系统启动/ABS未激活
    
    INACTIVE: 未激活
    INACTIVE --> INCREASE: 滑移率 > 15%且ABS使能
    
    INCREASE: 增压阶段
    INCREASE --> HOLD1: 滑移率 > 18%
    INCREASE --> INCREASE: 滑移率 ≤ 18%
    Note right of INCREASE: 进油阀: 全开<br/>出油阀: 关闭
    
    HOLD1: 保压阶段1
    HOLD1 --> DECREASE: 滑移率 > 22%
    HOLD1 --> INCREASE: 保压超时(40ms)且滑移率恢复
    Note right of HOLD1: 进油阀: 关闭<br/>出油阀: 关闭
    
    DECREASE: 减压阶段
    DECREASE --> HOLD2: 滑移率 < 12%
    DECREASE --> DECREASE: 滑移率 ≥ 12%
    Note right of DECREASE: 进油阀: 关闭<br/>出油阀: 全开<br/>泵电机: 工作
    
    HOLD2: 保压阶段2
    HOLD2 --> INCREASE: 轮速恢复且滑移率 < 10%
    HOLD2 --> HOLD2: 滑移率 ≥ 10%
    Note right of HOLD2: 进油阀: 关闭<br/>出油阀: 关闭
    
    INCREASE --> INACTIVE: ABS禁用或踏板释放
    HOLD1 --> INACTIVE: ABS禁用
    DECREASE --> INACTIVE: ABS禁用
    HOLD2 --> INACTIVE: ABS禁用
    
    style INCREASE fill:#69db7c
    style DECREASE fill:#ff6b6b,color:#fff
    style HOLD1 fill:#ffd43b
    style HOLD2 fill:#ffd43b
```

### 3.3 专家级控制算法实现

```c
//=============================================================================
// ABS控制主程序
// 周期: 2ms
// ASIL: D
//=============================================================================

void ABS_Controller_Main(void)
{
    uint8 wheel;
    
    // 1. 读取输入
    WheelSpeeds = Rte_Read_RPort_WheelSpeeds();
    V_ref = Rte_Read_RPort_ReferenceSpeed();
    ABS_Enable = Rte_Read_RPort_ABS_Enable();
    TargetPressure = Rte_Read_RPort_TargetPressure();
    
    // 2. 计算滑移率
    CalculateSlipRatio(WheelSpeeds, V_ref, SlipRatio);
    
    // 3. 选择控制轮 (低选原则 - 附着系数小的轮)
    // 前轴选滑移率大的，后轴选滑移率小的
    for (wheel = 0; wheel < 4; wheel++) {
        if (ABS_Enable && SlipRatio[wheel] > SLIP_ENTRY_THRESHOLD) {
            // 更新ABS状态机
            ABS_StateMachine(wheel, SlipRatio[wheel]);
        } else {
            ABS_Phase[wheel] = ABS_PHASE_INACTIVE;
            ValveCmd_Inlet[wheel] = 0;   // 默认关闭
            ValveCmd_Outlet[wheel] = 0;  // 默认关闭
        }
    }
    
    // 4. 泵电机控制
    if (AnyWheelInDecreasePhase()) {
        PumpMotorCmd = 100;  // 泵全速
    } else if (AnyWheelInABS()) {
        PumpMotorCmd = 50;   // 泵半速维持
    } else {
        PumpMotorCmd = 0;    // 泵停止
    }
    
    // 5. 输出
    Rte_Write_PPort_ValveCmd_Inlet(ValveCmd_Inlet);
    Rte_Write_PPort_ValveCmd_Outlet(ValveCmd_Outlet);
    Rte_Write_PPort_PumpMotorCmd(PumpMotorCmd);
    Rte_Write_PPort_ABS_Active(AnyWheelInABS());
    Rte_Write_PPort_ABS_Phase(ABS_Phase);
}

//=============================================================================
// ABS状态机 - 单轮控制
//=============================================================================

void ABS_StateMachine(uint8 wheel, float slip_ratio)
{
    switch (ABS_Phase[wheel]) {
        
        case ABS_PHASE_INACTIVE:
            // 进入条件: 滑移率超过阈值
            if (slip_ratio > SLIP_ENTRY_THRESHOLD) {
                ABS_Phase[wheel] = ABS_PHASE_INCREASE;
                IncreaseCounter[wheel] = 0;
            }
            break;
            
        case ABS_PHASE_INCREASE:
            // 动作: 持续增压
            ValveCmd_Inlet[wheel] = 1000;   // 进油阀全开
            ValveCmd_Outlet[wheel] = 0;      // 出油阀关闭
            IncreaseCounter[wheel]++;
            
            // 转换条件: 滑移率过高，切换到保压
            if (slip_ratio > SLIP_HOLD1_THRESHOLD) {
                ABS_Phase[wheel] = ABS_PHASE_HOLD1;
                Hold1Timer[wheel] = 0;
            }
            break;
            
        case ABS_PHASE_HOLD1:
            // 动作: 保压观察
            ValveCmd_Inlet[wheel] = 0;       // 进油阀关闭
            ValveCmd_Outlet[wheel] = 0;      // 出油阀关闭
            Hold1Timer[wheel] += 2;          // 2ms步进
            
            // 转换条件1: 滑移率继续上升，需要减压
            if (slip_ratio > SLIP_DECREASE_THRESHOLD) {
                ABS_Phase[wheel] = ABS_PHASE_DECREASE;
                DecreaseCounter[wheel] = 0;
            }
            // 转换条件2: 保压超时且滑移率恢复，回到增压
            else if (Hold1Timer[wheel] > HOLD1_MAX_TIME && 
                     slip_ratio < SLIP_HOLD1_THRESHOLD * 0.8) {
                ABS_Phase[wheel] = ABS_PHASE_INCREASE;
            }
            break;
            
        case ABS_PHASE_DECREASE:
            // 动作: 减压
            ValveCmd_Inlet[wheel] = 0;       // 进油阀关闭
            ValveCmd_Outlet[wheel] = 1000;   // 出油阀全开
            DecreaseCounter[wheel]++;
            
            // 转换条件: 滑移率下降，切换到保压2
            if (slip_ratio < SLIP_HOLD2_THRESHOLD) {
                ABS_Phase[wheel] = ABS_PHASE_HOLD2;
                Hold2Timer[wheel] = 0;
            }
            break;
            
        case ABS_PHASE_HOLD2:
            // 动作: 保压等待恢复
            ValveCmd_Inlet[wheel] = 0;
            ValveCmd_Outlet[wheel] = 0;
            Hold2Timer[wheel] += 2;
            
            // 转换条件1: 轮速恢复，回到增压
            if (slip_ratio < SLIP_RECOVER_THRESHOLD && 
                WheelSpeeds[wheel] > V_ref * 0.9) {
                ABS_Phase[wheel] = ABS_PHASE_INCREASE;
            }
            // 转换条件2: 保压超时，回到增压
            else if (Hold2Timer[wheel] > HOLD2_MAX_TIME) {
                ABS_Phase[wheel] = ABS_PHASE_INCREASE;
            }
            break;
    }
}

//=============================================================================
// 专家调参 - 阈值定义
//=============================================================================

// 滑移率阈值 (%)
#define SLIP_ENTRY_THRESHOLD      15.0   // ABS进入阈值
#define SLIP_HOLD1_THRESHOLD      18.0   // 切换到保压1
#define SLIP_DECREASE_THRESHOLD   22.0   // 切换到减压
#define SLIP_HOLD2_THRESHOLD      12.0   // 切换到保压2
#define SLIP_RECOVER_THRESHOLD    10.0   // 恢复到增压

// 时间阈值 (ms)
#define HOLD1_MAX_TIME            40     // 保压1最大时间
#define HOLD2_MAX_TIME            80     // 保压2最大时间

// 压力阈值 (bar)
#define PRESSURE_INCREASE_RATE    50.0   // 增压速率 (bar/s)
#define PRESSURE_DECREASE_RATE    200.0  // 减压速率 (bar/s)
```

### 3.4 改进型控制策略

```c
//=============================================================================
// 自适应压力调节 - 专家级优化
//=============================================================================

// 根据路面附着系数自适应调节压力
void AdaptivePressureControl(uint8 wheel, float slip_ratio)
{
    static float Mu_estimate[4];  // 估计附着系数
    float pressure_rate;
    
    // 估计路面附着系数 (基于滑移率曲线)
    Mu_estimate[wheel] = EstimateFrictionCoefficient(slip_ratio);
    
    // 根据附着系数调整压力变化率
    if (Mu_estimate[wheel] > 0.7) {
        // 高附着路面 (干燥柏油路)
        pressure_rate = PRESSURE_HIGH_MU_RATE;
    } else if (Mu_estimate[wheel] > 0.4) {
        // 中附着路面 (湿滑路面)
        pressure_rate = PRESSURE_MED_MU_RATE;
    } else {
        // 低附着路面 (冰雪路面)
        pressure_rate = PRESSURE_LOW_MU_RATE;
    }
    
    // 应用调节后的压力变化率
    if (ABS_Phase[wheel] == ABS_PHASE_INCREASE) {
        ValveCmd_Inlet[wheel] = CalculatePWM(pressure_rate);
    } else if (ABS_Phase[wheel] == ABS_PHASE_DECREASE) {
        ValveCmd_Outlet[wheel] = CalculatePWM(pressure_rate * 4);  // 减压更快
    }
}

// PWM占空比计算
uint16 CalculatePWM(float pressure_rate)
{
    // PWM与压力变化率的关系 (需标定)
    // PWM = Kp × pressure_rate + Offset
    uint16 pwm;
    
    pwm = (uint16)(KP_PRESSURE * pressure_rate + PWM_OFFSET);
    
    // 限幅
    if (pwm > 1000) pwm = 1000;
    if (pwm < 0) pwm = 0;
    
    return pwm;
}
```

---

## 4. 诊断与监控

### 4.1 内部监控

| 监控项 | 检查内容 | 故障处理 |
|--------|----------|----------|
| 阀响应监控 | 阀PWM输出 vs 压力响应 | 超时故障，ABS禁用 |
| 泵电机监控 | 电机电流、转速 | 过流保护，泵禁用 |
| 循环时间监控 | ABS周期 60-120ms | 异常报警 |
| 滑移率合理性 | 滑移率 0-100% | 传感器故障 |

### 4.2 DTC定义

| DTC编号 | 故障描述 | 触发条件 | 恢复条件 |
|---------|----------|----------|----------|
| C00301 | 进油阀故障 | PWM输出≠压力响应 | 连续3周期正常 |
| C00302 | 出油阀故障 | PWM输出≠压力响应 | 连续3周期正常 |
| C00303 | 泵电机故障 | 电流异常或堵转 | 电流正常 |
| C00304 | ABS循环异常 | 周期<50ms或>150ms | 周期正常 |
| C00305 | 滑移率计算异常 | 滑移率>100%或<0 | 计算正常 |

---

## 5. 性能验证

### 5.1 HIL测试场景

| 场景ID | 测试场景 | 输入条件 | 预期结果 |
|--------|----------|----------|----------|
| ABS-001 | 高附着路面紧急制动 | 80km/h→0, μ=0.8 | 滑移率10-30%, 制动距离≤40m |
| ABS-002 | 低附着路面制动 | 40km/h→0, μ=0.2 | 滑移率稳定, 方向可控 |
| ABS-003 | 对开路面制动 | 左轮μ=0.8, 右轮μ=0.2 | 低选控制, 横摆<2°/s |
| ABS-004 | 阶跃附着系数 | μ 0.8→0.2突变 | 快速适应, 2周期内稳定 |
| ABS-005 | 阀故障降级 | 单阀故障 | 禁用ABS, 故障报警 |

---

*SWC_ABS - 防抱死制动控制模块设计*