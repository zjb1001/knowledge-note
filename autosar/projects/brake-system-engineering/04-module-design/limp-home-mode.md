# 跛行回家模式设计 - Limp Home Mode

> **文档编号**: LIMP-HOME-001  
003e **模式目的**: 系统故障时允许有限功能驾驶  
003e **安全前提**: 基础制动功能可用  
003e **速度限制**: 50-100 km/h 根据等级

---

## 1. 跛行回家模式概述

### 1.1 设计目标

```mermaid
graph LR
    subgraph Normal["正常运行"]
        N1["全部功能可用
        ABS/ESC/EPB/ADAS"]
    end
    
    subgraph Degraded["降级模式"]
        D1["部分功能受限
        性能下降"]
    end
    
    subgraph LimpHome["跛行回家模式"]
        L1["基础功能
        安全驶离"]
    end
    
    subgraph SafeState["安全状态"]
        S1["仅停车
        等待救援"]
    end
    
    N1 --> D1: 轻微故障
    D1 --> L1: 中等故障
    L1 --> S1: 严重故障
    N1 --> L1: 关键故障
    N1 --> S1: 致命故障

    style LimpHome fill:#ffd43b
    style SafeState fill:#ff6b6b,color:#fff
```

### 1.2 跛行等级定义

| 等级 | 条件 | 速度限制 | 可用功能 | 禁用功能 |
|------|------|----------|----------|----------|
| **Level 0** | 正常 | 无限制 | 全部 | 无 |
| **Level 1** | ABS失效 | 200 km/h | 基础制动+ESC | ABS/Autohold |
| **Level 2** | ESC失效 | 100 km/h | 基础制动 | ABS/ESC/AEB |
| **Level 3** | 部分传感器失效 | 50 km/h | 基础制动+跛行 | ADAS/ABS/ESC |
| **Level 4** | 严重故障 | 0 km/h | 停车 | 全部 |

---

## 2. 跛行回家触发条件

### 2.1 触发条件矩阵

```c
//=============================================================================
// 跛行回家触发条件
//=============================================================================

typedef enum {
    LIMP_HOME_NONE = 0,            // 无跛行
    LIMP_HOME_LEVEL_1,             // 一级跛行
    LIMP_HOME_LEVEL_2,             // 二级跛行
    LIMP_HOME_LEVEL_3,             // 三级跛行
    LIMP_HOME_LEVEL_4              // 四级跛行 (停车)
} LimpHomeLevelType;

// 触发条件结构
typedef struct {
    FaultType Fault;               // 故障类型
    LimpHomeLevelType Level;       // 对应跛行等级
    boolean Immediate;             // 是否立即触发
    uint32 DebounceTime;           // 消抖时间 (ms)
    const char* Description;       // 描述
} LimpHomeTriggerType;

// 触发条件表
const LimpHomeTriggerType LimpHomeTriggers[] = {
    // Level 1 - 轻微故障
    {FAULT_ABS_FAILED,              LIMP_HOME_LEVEL_1, FALSE, 100, "ABS失效"},
    {FAULT_WSS_FL_DEGRADED,         LIMP_HOME_LEVEL_1, FALSE, 500, "单轮速降级"},
    {FAULT_PEDAL_REDUNDANCY_LOSS,   LIMP_HOME_LEVEL_1, FALSE, 200, "踏板冗余丢失"},
    
    // Level 2 - 中等故障
    {FAULT_ESC_FAILED,              LIMP_HOME_LEVEL_2, FALSE, 100, "ESC失效"},
    {FAULT_2WHEEL_PRESSURE_FAILED,  LIMP_HOME_LEVEL_2, FALSE, 50,  "两路压力失效"},
    {FAULT_COM_BUS_OFF,             LIMP_HOME_LEVEL_2, TRUE,  0,   "通信故障"},
    {FAULT_AEB_FAILED,              LIMP_HOME_LEVEL_2, FALSE, 200, "AEB失效"},
    
    // Level 3 - 严重故障
    {FAULT_3WHEEL_PRESSURE_FAILED,  LIMP_HOME_LEVEL_3, TRUE,  0,   "三路压力失效"},
    {FAULT_PEDAL_PRIMARY_FAILED,    LIMP_HOME_LEVEL_3, TRUE,  0,   "踏板主传感器失效"},
    {FAULT_WSS_3WHEEL_FAILED,       LIMP_HOME_LEVEL_3, TRUE,  0,   "三轮速失效"},
    
    // Level 4 - 停车
    {FAULT_LOSS_OF_BRAKING,         LIMP_HOME_LEVEL_4, TRUE,  0,   "制动丧失"},
    {FAULT_PEDAL_BOTH_FAILED,       LIMP_HOME_LEVEL_4, TRUE,  0,   "踏板双传感器失效"},
    {FAULT_4WHEEL_PRESSURE_FAILED,  LIMP_HOME_LEVEL_4, TRUE,  0,   "四路压力失效"}
};
```

### 2.2 跛行等级决策逻辑

```c
//=============================================================================
// 跛行等级决策
//=============================================================================

LimpHomeLevelType DetermineLimpHomeLevel(FaultBitmapType fault_bitmap)
{
    LimpHomeLevelType max_level = LIMP_HOME_NONE;
    
    // 检查所有激活故障
    for (int i = 0; i < FAULT_COUNT; i++) {
        if (fault_bitmap & (1 << i)) {
            // 查找该故障对应的跛行等级
            LimpHomeLevelType fault_level = GetFaultLimpHomeLevel(i);
            
            // 取最高等级
            if (fault_level > max_level) {
                max_level = fault_level;
            }
        }
    }
    
    // 组合故障处理
    // 多个Level 1故障 → 升级为Level 2
    uint8 level1_count = CountActiveFaultsAtLevel(fault_bitmap, LIMP_HOME_LEVEL_1);
    if (level1_count >= 3 && max_level < LIMP_HOME_LEVEL_2) {
        max_level = LIMP_HOME_LEVEL_2;
    }
    
    return max_level;
}
```

---

## 3. 跛行回家控制策略

### 3.1 主控程序

```c
//=============================================================================
// 跛行回家主控程序
//=============================================================================

typedef struct {
    LimpHomeLevelType Level;
    boolean Active;
    uint32 EntryTime;
    uint32 Duration;
    float SpeedLimit;
    float MaxDecel;
    boolean WarningIssued;
} LimpHomeControlType;

static LimpHomeControlType LimpHomeCtrl = {
    .Level = LIMP_HOME_NONE,
    .Active = FALSE
};

void LimpHomeControl_Main(void)
{
    // 1. 检查当前故障状态
    FaultBitmapType active_faults = GetActiveFaultBitmap();
    
    // 2. 确定跛行等级
    LimpHomeLevelType new_level = DetermineLimpHomeLevel(active_faults);
    
    // 3. 处理等级变化
    if (new_level != LimpHomeCtrl.Level) {
        if (new_level > LimpHomeCtrl.Level) {
            // 故障恶化，升级跛行等级
            EnterLimpHomeLevel(new_level);
        } else if (new_level < LimpHomeCtrl.Level) {
            // 故障恢复，降级
            ExitLimpHomeLevel(new_level);
        }
    }
    
    // 4. 执行当前跛行等级策略
    if (LimpHomeCtrl.Active) {
        ExecuteLimpHomeStrategy();
    }
}

// 进入跛行等级
void EnterLimpHomeLevel(LimpHomeLevelType level)
{
    // 记录旧等级
    LimpHomeLevelType old_level = LimpHomeCtrl.Level;
    
    // 更新等级
    LimpHomeCtrl.Level = level;
    LimpHomeCtrl.Active = (level > LIMP_HOME_NONE);
    LimpHomeCtrl.EntryTime = GetSystemTime();
    
    // 记录事件
    Dem_SetEventStatus(DTC_LIMP_HOME_ENTERED + level, DEM_EVENT_STATUS_FAILED);
    
    switch (level) {
        case LIMP_HOME_LEVEL_1:
            EnterLimpHomeLevel1();
            break;
        case LIMP_HOME_LEVEL_2:
            EnterLimpHomeLevel2();
            break;
        case LIMP_HOME_LEVEL_3:
            EnterLimpHomeLevel3();
            break;
        case LIMP_HOME_LEVEL_4:
            EnterLimpHomeLevel4();
            break;
        default:
            break;
    }
    
    // 通知相关模块
    NotifyLimpHomeEntry(level, old_level);
}
```

### 3.2 各等级控制策略

```c
//=============================================================================
// 跛行回家 Level 1 - ABS失效
//=============================================================================

void EnterLimpHomeLevel1(void)
{
    // 1. 禁用ABS
    DisableABS();
    
    // 2. 保持ESC可用
    EnableESC();
    
    // 3. 设置速度限制 (200 km/h)
    LimpHomeCtrl.SpeedLimit = 200.0;
    Rte_Write_PPort_VehicleSpeedLimit(200.0);
    
    // 4. 设置减速度限制
    LimpHomeCtrl.MaxDecel = 8.0;  // 8 m/s²
    
    // 5. 仪表警告
    Rte_Write_PPort_WarningLamp(LAMP_BRAKE_SYSTEM);
    Rte_Write_PPort_HMIWarning("ABS故障，请谨慎驾驶");
    
    // 6. 限制ADAS功能
    Rte_Write_PPort_ADAS_Limitation(ADAS_LIMIT_NO_ABS);
}

//=============================================================================
// 跛行回家 Level 2 - ESC失效
//=============================================================================

void EnterLimpHomeLevel2(void)
{
    // 1. 禁用ABS和ESC
    DisableABS();
    DisableESC();
    
    // 2. 禁用AEB和Autohold
    DisableAEB();
    DisableAutohold();
    
    // 3. 设置速度限制 (100 km/h)
    LimpHomeCtrl.SpeedLimit = 100.0;
    Rte_Write_PPort_VehicleSpeedLimit(100.0);
    
    // 4. 设置减速度限制
    LimpHomeCtrl.MaxDecel = 6.0;  // 6 m/s²
    
    // 5. 限制制动力分配比例 (防止后轮抱死)
    SetRearBrakeLimit(0.6);  // 后轮制动力限制60%
    
    // 6. 仪表警告
    Rte_Write_PPort_WarningLamp(LAMP_BRAKE_SYSTEM);
    Rte_Write_PPort_HMIWarning("制动系统性能受限，请减速慢行");
    
    // 7. 通知ADAS
    Rte_Write_PPort_ADAS_Limitation(ADAS_LIMIT_NO_ESC);
}

//=============================================================================
// 跛行回家 Level 3 - 严重故障
//=============================================================================

void EnterLimpHomeLevel3(void)
{
    // 1. 禁用所有高级功能
    DisableABS();
    DisableESC();
    DisableEPB();
    DisableAutohold();
    DisableAEB();
    
    // 2. 切换到简化控制算法
    SwitchToSimplifiedControl();
    
    // 3. 设置速度限制 (50 km/h)
    LimpHomeCtrl.SpeedLimit = 50.0;
    Rte_Write_PPort_VehicleSpeedLimit(50.0);
    
    // 4. 设置减速度限制
    LimpHomeCtrl.MaxDecel = 4.0;  // 4 m/s²
    
    // 5. 仪表警告 (更醒目)
    Rte_Write_PPort_WarningLamp(LAMP_BRAKE_SYSTEM_URGENT);
    Rte_Write_PPort_HMIWarning("制动系统严重故障，请尽快停车检修");
    Rte_Write_PPort_SoundWarning(TONE_URGENT);
    
    // 6. 激活危险报警灯
    Rte_Write_PPort_HazardLampRequest(TRUE);
    
    // 7. 记录严重事件
    Dem_SetEventStatus(DTC_LIMP_HOME_LEVEL3, DEM_EVENT_STATUS_FAILED);
}

//============================================================================-
// 跛行回家 Level 4 - 停车
//=============================================================================

void EnterLimpHomeLevel4(void)
{
    // 1. 立即执行安全停车
    LimpHomeCtrl.SpeedLimit = 0.0;
    
    // 2. 通知驾驶员
    Rte_Write_PPort_HMIWarning("制动系统故障，请立即停车");
    Rte_Write_PPort_EmergencyMessage("请安全停车并联系救援");
    
    // 3. 如果车辆仍在移动，尝试安全停车
    if (VehicleSpeed > 5.0) {
        // 使用EPB或残余制动力减速停车
        EmergencySafeStop();
    }
    
    // 4. 进入安全状态
    EnterSafeState();
}
```

---

## 4. 跛行回家控制算法

### 4.1 简化制动控制

```c
//=============================================================================
// 跛行模式简化制动控制
//=============================================================================

float CalculateLimpHomeBrakeDemand(float pedal_position)
{
    // 跛行模式下使用简化的线性映射
    // 踏板位置 → 制动力 (无ABS/ESC干预)
    
    // 基础映射
    float brake_demand = pedal_position * MAX_LIMP_HOME_DECEL / 100.0;
    
    // 应用减速度限制
    if (brake_demand > LimpHomeCtrl.MaxDecel) {
        brake_demand = LimpHomeCtrl.MaxDecel;
    }
    
    return brake_demand;
}

// 简化压力控制 (开环+简单闭环)
void ExecuteLimpHomePressureControl(float target_pressure, uint8 wheel)
{
    // 跛行模式下不使用复杂的压力闭环
    // 使用简化的PWM映射
    
    // 查表: 目标压力 → PWM占空比
    uint16 pwm = PressureToPWM_Table(target_pressure);
    
    // 简单反馈修正
    float actual_pressure = GetWheelPressure(wheel);
    float error = target_pressure - actual_pressure;
    
    // 比例修正 (增益较小，保守控制)
    int16 pwm_correction = (int16)(error * 5.0);  // 保守增益
    
    pwm += pwm_correction;
    
    // 限制
    if (pwm > 800) pwm = 800;  // 跛行模式限制最大PWM
    
    // 输出
    ValvePWM_Inlet[wheel] = pwm;
}

// 压力查表 (预标定)
uint16 PressureToPWM_Table(float pressure)
{
    // 预标定表: 压力(bar) → PWM
    const uint16 pressure_points[] = {0, 5, 10, 20, 30, 50, 100};
    const uint16 pwm_values[] =      {0, 100, 180, 300, 420, 600, 800};
    
    // 线性插值
    for (int i = 0; i < 6; i++) {
        if (pressure <= pressure_points[i+1]) {
            float ratio = (pressure - pressure_points[i]) / 
                         (pressure_points[i+1] - pressure_points[i]);
            return pwm_values[i] + (uint16)(ratio * (pwm_values[i+1] - pwm_values[i]));
        }
    }
    
    return pwm_values[6];  // 最大值
}
```

### 4.2 速度限制执行

```c
//=============================================================================
// 跛行模式速度限制
//=============================================================================

void EnforceSpeedLimit(void)
{
    if (!LimpHomeCtrl.Active) return;
    
    float current_speed = GetVehicleSpeed();
    
    // 1. 向动力域发送限速请求
    if (current_speed > LimpHomeCtrl.SpeedLimit * 1.1) {
        // 超速10%，请求限制扭矩
        float torque_limit = CalculateTorqueLimitForSpeed(LimpHomeCtrl.SpeedLimit);
        Rte_Write_PPort_EngineTorqueLimit(torque_limit);
    }
    
    // 2. 如果超速严重，使用制动干预
    if (current_speed > LimpHomeCtrl.SpeedLimit * 1.2) {
        // 超速20%，施加轻微制动
        float brake_torque = (current_speed - LimpHomeCtrl.SpeedLimit) * 10.0;
        ApplyGentleBraking(brake_torque);
    }
}

// 计算扭矩限制
float CalculateTorqueLimitForSpeed(float target_speed)
{
    // 简化的扭矩-速度关系
    // 假设车辆阻力与速度相关
    
    const float drag_coeff = 0.5;    // 阻力系数
    float drag_force = drag_coeff * target_speed * target_speed;
    
    // 转换为扭矩
    const float wheel_radius = 0.3;  // m
    float torque = drag_force * wheel_radius;
    
    return torque;
}
```

---

## 5. 故障恢复与退出

### 5.1 故障恢复监控

```c
//=============================================================================
// 跛行模式故障恢复
//=============================================================================

void MonitorLimpHomeRecovery(void)
{
    if (!LimpHomeCtrl.Active) return;
    
    // 检查所有触发跛行的故障是否已恢复
    FaultBitmapType active_faults = GetActiveFaultBitmap();
    LimpHomeLevelType new_level = DetermineLimpHomeLevel(active_faults);
    
    if (new_level < LimpHomeCtrl.Level) {
        // 故障恢复，可以降级
        
        // 持续监控一段时间确认稳定
        static uint32 recovery_timer = 0;
        recovery_timer += 10;  // 10ms周期
        
        if (recovery_timer >= 5000) {  // 持续5秒无故障
            ExitLimpHomeLevel(new_level);
            recovery_timer = 0;
        }
    } else {
        // 故障未恢复，重置计时器
        // recovery_timer = 0;  // 不完全重置，允许部分累积
    }
}

// 退出跛行模式
void ExitLimpHomeLevel(LimpHomeLevelType new_level)
{
    LimpHomeLevelType old_level = LimpHomeCtrl.Level;
    
    // 更新等级
    LimpHomeCtrl.Level = new_level;
    LimpHomeCtrl.Active = (new_level > LIMP_HOME_NONE);
    
    // 如果退出到正常
    if (new_level == LIMP_HOME_NONE) {
        // 恢复正常功能
        EnableABS();
        EnableESC();
        EnableEPB();
        EnableAutohold();
        EnableAEB();
        
        // 清除限制
        Rte_Write_PPort_VehicleSpeedLimit(255.0);  // 无限制
        
        // 清除警告
        Rte_Write_PPort_WarningLamp(LAMP_OFF);
        Rte_Write_PPort_HMIWarning("");
        Rte_Write_PPort_HazardLampRequest(FALSE);
        
        // 记录恢复事件
        Dem_SetEventStatus(DTC_LIMP_HOME_EXITED, DEM_EVENT_STATUS_PASSED);
        
        // 执行自检
        if (RunSelfTest() != SELFTEST_PASSED) {
            // 自检失败，回到Level 1
            EnterLimpHomeLevel(LIMP_HOME_LEVEL_1);
            return;
        }
    } else {
        // 降级到更低等级
        switch (new_level) {
            case LIMP_HOME_LEVEL_1:
                // 从Level 2降级
                EnableABS();  // 重新启用ABS
                LimpHomeCtrl.SpeedLimit = 200.0;
                break;
            case LIMP_HOME_LEVEL_2:
                // 从Level 3降级
                EnableESC();
                LimpHomeCtrl.SpeedLimit = 100.0;
                break;
        }
    }
    
    // 通知相关模块
    NotifyLimpHomeExit(old_level, new_level);
}
```

---

## 6. 诊断与记录

### 6.1 跛行模式诊断

```c
//=============================================================================
// 跛行模式诊断
//=============================================================================

typedef struct {
    uint32 EntryCount;             // 进入次数
    uint32 TotalDuration;          // 总持续时间
    uint32 MaxSpeedInLimpHome;     // 跛行中最高车速
    float MaxDecelInLimpHome;      // 跛行中最大减速度
    uint32 DistanceTravelled;      // 跛行中行驶距离
} LimpHomeStatisticsType;

// 记录跛行模式统计
void RecordLimpHomeStatistics(void)
{
    static LimpHomeStatisticsType stats = {0};
    
    if (LimpHomeCtrl.Active) {
        // 更新统计
        float current_speed = GetVehicleSpeed();
        if (current_speed > stats.MaxSpeedInLimpHome) {
            stats.MaxSpeedInLimpHome = current_speed;
        }
        
        float current_decel = GetVehicleDeceleration();
        if (current_decel > stats.MaxDecelInLimpHome) {
            stats.MaxDecelInLimpHome = current_decel;
        }
        
        // 计算行驶距离
        stats.DistanceTravelled += current_speed * 0.002;  // 2ms周期
    }
    
    // 退出时保存统计
    if (!LimpHomeCtrl.Active && stats.EntryCount > 0) {
        // 存储到NVM
        NvM_WriteBlock(NVM_BLOCK_LIMP_HOME_STATS, &stats);
    }
}

// 跛行模式性能监控
void MonitorLimpHomePerformance(void)
{
    if (!LimpHomeCtrl.Active) return;
    
    // 监控跛行模式下的制动性能
    float brake_response_time = MeasureBrakeResponseTime();
    
    if (brake_response_time > 300) {  // > 300ms
        // 跛行模式下制动响应过慢
        Dem_SetEventStatus(DTC_LIMP_HOME_SLOW_RESPONSE, DEM_EVENT_STATUS_FAILED);
    }
    
    // 监控压力建立能力
    float pressure_buildup_rate = MeasurePressureBuildupRate();
    
    if (pressure_buildup_rate < 50) {  // < 50 bar/s
        // 跛行模式下建压能力不足
        Dem_SetEventStatus(DTC_LIMP_HOME_LOW_PRESSURE, DEM_EVENT_STATUS_FAILED);
        
        // 可能需要进一步降级
        if (LimpHomeCtrl.Level < LIMP_HOME_LEVEL_3) {
            EnterLimpHomeLevel(LimpHomeCtrl.Level + 1);
        }
    }
}
```

---

*跛行回家模式设计*  
*系统故障时允许安全驶离，四级渐进降级策略*