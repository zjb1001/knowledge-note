# VinFast 制动系统技术框架预研

基于公开技术资料整理，供项目参考

---

## 1. 电子液压制动系统 (EHB) 架构

### 核心组件
```
┌─────────────────────────────────────────────────────┐
│                    VCU (整车控制器)                  │
│              制动意图识别 + 制动力分配                │
└──────────────┬────────────────────────┬─────────────┘
               │                        │
    ┌──────────▼──────────┐    ┌───────▼────────┐
    │   EHB主控制器        │    │   EHB备份控制器 │
    │   (主缸压力控制)      │    │   (冗余备份)    │
    └──────────┬──────────┘    └────────────────┘
               │
    ┌──────────▼──────────┐
    │   液压调节单元 (HCU)  │
    │   - 增压阀/减压阀     │
    │   - 回油泵           │
    │   - 蓄能器           │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   轮缸制动器         │
    │   (前盘/后盘或鼓式)   │
    └─────────────────────┘
```

---

## 2. 三电机制动回收策略 (VF9专用)

### 制动力分配逻辑

| 制动踏板深度 | 制动力分配策略 |
|-------------|--------------|
| 0-30% (轻踩) | 三电机联合回收 (优先后轴) |
| 30-70% (中踩) | 三电机满功率 + 前轴EHB补充 |
| 70-100% (重踩) | 三电机退出 + EHB全液压 |

### 后轴双电机协调
```c
// 后轮双电机制动力分配 (考虑轮速差)
float rear_left_torque = base_torque * (1 + wheel_speed_diff * Kp);
float rear_right_torque = base_torque * (1 - wheel_speed_diff * Kp);

// 限制总制动力不超过后轴附着力
float max_rear_force = vehicle_mass * rear_axle_load_ratio * road_friction;
if (rear_left_torque + rear_right_torque > max_rear_force) {
    scale_factor = max_rear_force / (rear_left_torque + rear_right_torque);
    rear_left_torque *= scale_factor;
    rear_right_torque *= scale_factor;
}
```

---

## 3. 后轮EPS与制动协调 (关键技术)

### 问题
后轮转向时制动产生**横摆力矩**，可能导致车辆失稳。

### 解决方案
```c
// 制动-转向协调控制
void Coordination_Brake_Steering(void) {
    float rear_steering_angle = Get_Rear_EPS_Angle();  // ±3°范围
    float vehicle_speed = Get_Vehicle_Speed();
    
    // 高速时限制后轮转向角度
    if (vehicle_speed > 80 && abs(rear_steering_angle) > 1.5) {
        rear_steering_angle = sign(rear_steering_angle) * 1.5;
    }
    
    // 制动时后轮转向补偿
    if (Brake_Pedal_Pressed) {
        // 内侧轮增加制动力，外侧轮减少
        float compensation = rear_steering_angle * BRAKE_COMPENSATION_GAIN;
        Brake_FL += compensation;
        Brake_FR -= compensation;
        Brake_RL += compensation * 0.6;  // 后轴权重较低
        Brake_RR -= compensation * 0.6;
        
        // ESC介入判断
        if (Yaw_Rate_Error > YAW_RATE_THRESHOLD) {
            ESC_Enable_Correction();
        }
    }
}
```

---

## 4. MCAL配置要点 (AUTOSAR)

### 关键模块配置

| 模块 | 功能 | VinFast VF9配置 |
|------|------|----------------|
| **ADC** | 踏板/压力采样 | 16路，含3路电机温度 |
| **GPT** | 轮速采集 | 8路IC，3电机+4轮速 |
| **PWM** | 阀控制 | 12路，电磁阀+电机 |
| **CAN** | 总线通信 | 3路FD，三电机独立通道 |
| **DIO** | 信号输入 | 32路，踏板开关+冗余互锁 |
| **WDG** | 安全监控 | 独立看门狗，EHB/EPS分离 |

### 功能安全要求
- ASIL-D等级：制动系统必须达到
- 冗余设计：双ECU + 双传感器
- 故障响应时间：<100ms

---

## 5. 越南环境适应性设计

### 高温高湿 (全年80%+湿度)
```c
// 温度补偿策略
void Temperature_Compensation(void) {
    if (Brake_Disc_Temp > 400) {
        // 高温时增加电机回收，减少机械制动
        Regen_Max = 0.9;
        EHB_Limit = 0.5;
        Cooling_Fan_Enable();
    }
    
    if (Motor_Temp > 150) {
        // 电机过热转移制动力
        Shift_Braking_to_Front_Axle();
    }
}
```

### 涉水工况
```c
// 涉水检测与处理
void Water_Wading_Handler(void) {
    if (Wheel_Speed_Anomaly_Detected() && 
        Brake_Disc_Temp_Drop_Rate > 50) {
        // 检测到涉水
        ABS_Increase_Release_Pulse();  // 防止水膜打滑
        Regen_Disable();                // 退出电机回收
        Brake_Disc_Dry_Mode();          // 自动除水
    }
}
```

---

## 6. 测试验证建议

### 台架测试
- HIL仿真：三电机协调控制逻辑验证
- 硬件在环：EHB阀体响应测试

### 实车测试 (越南本地)
1. **高温测试**: 胡志明市夏季40°C连续制动
2. **涉水测试**: 雨季积水路面通过性
3. **山路测试**: 大叻-芽庄长下坡制动衰退
4. **高湿测试**: 海滨城市盐雾腐蚀验证

---

*框架基于公开技术资料整理*  
*适用于VinFast VF9三电机+后轮EPS项目*
