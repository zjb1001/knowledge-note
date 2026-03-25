# VMC车辆运动控制系列—EMB电子机械制动

> **来源**: 汽车电子设计（微信公众号）  
> **发布时间**: 2025-08-17  
> **整理时间**: 2026-03-18

---

## 一、VMC核心概念与背景

### 1.1 传统汽车电子架构

传统汽车电子按照功能划分为五域模型：

```mermaid
graph TB
    subgraph "传统五域架构"
        A[动力域] -->|驱动控制| B(电机/发动机)
        C[底盘域] -->|制动/转向/悬架| D(执行器)
        E[车身域] -->|车身控制| F(车门/灯光/空调)
        G[座舱域] -->|人机交互| H(仪表/中控)
        I[智驾域] -->|感知决策| J(传感器/算法)
    end
```

### 1.2 VMC融合控制理念

**VMC（Vehicle Motion Control）** 打破传统域间壁垒，实现一体化融合控制：

```mermaid
graph TB
    subgraph "VMC融合架构"
        VMC[VMC底盘运动域控制器<br/>Vehicle Motion Control]
        
        VMC -->|驱动控制| M1[动力域执行器]
        VMC -->|制动控制| M2[EMB电子机械制动]
        VMC -->|转向控制| M3[线控转向系统]
        VMC -->|悬架控制| M4[主动悬架系统]
        
        style VMC fill:#e1f5ff,stroke:#01579b,stroke-width:3px
        style M2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    end
    
    subgraph "上层输入"
        AD[智驾域<br/>目标轨迹/减速度请求]
        CD[座舱域<br/>驾驶模式选择]
    end
    
    AD --> VMC
    CD --> VMC
```

**核心价值**: 多系统协同实现 **1+1>2** 的效果，拓展车辆动态性能边界

---

## 二、制动系统技术演进

### 2.1 制动系统分类总览

```mermaid
graph TD
    B[汽车制动系统] -->|传统| C[非线控]
    B -->|现代| D[线控制动]
    
    D -->|保留液压| E[EHB<br/>电子液压制动]
    D -->|纯电控| F[EMB<br/>电子机械制动]
    
    E -->|Two-Box| E1[iBooster + ESP]
    E -->|One-Box| E2[IPB集成式]
    
    F -->|分布式| F1[四轮独立控制]
    F -->|集中式| F2[中央统一控制]
    
    style F fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style F1 fill:#a5d6a7,stroke:#1b5e20,stroke-width:2px
```

### 2.2 EHB vs EMB 对比

```mermaid
graph LR
    subgraph "EHB电子液压制动"
        E1[踏板] --> E2[踏板模拟器]
        E2 --> E3[液压建压单元]
        E3 --> E4[液压管路]
        E4 --> E5[轮缸制动]
        
        style E3 fill:#ffecb3,stroke:#ff6f00
        style E4 fill:#ffe0b2,stroke:#e65100
    end
    
    subgraph "EMB电子机械制动"
        M1[踏板] --> M2[踏板感觉模拟器PTS]
        M2 --> M3[中央控制器VMC]
        M3 --> M4[电机驱动]
        M4 --> M5[减速机构]
        M5 --> M6[制动块压紧]
        
        style M3 fill:#c8e6c9,stroke:#2e7d32
        style M4 fill:#a5d6a7,stroke:#388e3c
    end
```

| 特性 | EHB | EMB |
|------|-----|-----|
| **传动介质** | 液压油 | 电机机械传动 |
| **响应时间** | ~120-150ms | ~80-100ms |
| **系统复杂度** | 中（需液压管路） | 低（纯电控） |
| **维护成本** | 需更换制动液 | 几乎免维护 |
| **能量回收** | 优秀 | 更优秀 |
| **功能安全** | 成熟方案 | 需多重冗余 |
| **量产状态** | 已大规模量产 | 逐步导入中 |

---

## 三、EMB系统硬件架构

### 3.1 整体系统架构

```mermaid
graph TB
    subgraph "驾驶员输入"
        PEDAL[制动踏板]
        PTS[踏板感觉模拟器<br/>Pedal Travel Sensor]
    end
    
    subgraph "中央决策层"
        VMC[VMC底盘域控制器<br/>Vehicle Motion Control]
        ABS[ABS算法]
        TCS[TCS牵引力控制]
        VDC[VDC车辆动态控制]
        EBD[EBD制动力分配]
    end
    
    subgraph "四轮执行层"
        direction LR
        EMB_FL[左前EMB控制器]
        EMB_FR[右前EMB控制器]
        EMB_RL[左后EMB控制器]
        EMB_RR[右后EMB控制器]
    end
    
    subgraph "传感器网络"
        WSS[轮速传感器WSS]
        BFS[夹紧力传感器BFS]
        MPS[电机位置传感器MPS]
        IMU[惯性测量单元]
    end
    
    PEDAL --> PTS
    PTS -->|踏板位移信号| VMC
    
    VMC --> ABS
    VMC --> TCS
    VMC --> VDC
    VMC --> EBD
    
    VMC -->|目标制动扭矩| EMB_FL
    VMC -->|目标制动扭矩| EMB_FR
    VMC -->|目标制动扭矩| EMB_RL
    VMC -->|目标制动扭矩| EMB_RR
    
    WSS -->|轮速反馈| VMC
    BFS -->|夹紧力反馈| VMC
    MPS -->|电机位置| VMC
    IMU -->|车辆姿态| VMC
    
    style VMC fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style EMB_FL fill:#c8e6c9,stroke:#2e7d32
    style EMB_FR fill:#c8e6c9,stroke:#2e7d32
    style EMB_RL fill:#c8e6c9,stroke:#2e7d32
    style EMB_RR fill:#c8e6c9,stroke:#2e7d32
```

### 3.2 EMB轮边执行器内部结构

```mermaid
graph TB
    subgraph "EMB电子机械制动卡钳"
        direction TB
        
        MCU[微控制器<br/>MCU]
        
        subgraph "电机驱动"
            DRV[三相电机驱动器]
            MOTOR[永磁同步电机<br/>PMSM]
        end
        
        subgraph "传动机构"
            GEAR[减速齿轮组]
            SCREW[滚珠丝杠]
            PISTON[活塞推杆]
        end
        
        subgraph "制动执行"
            PAD[制动块]
            DISC[制动盘]
        end
        
        subgraph "传感器"
            MPS[电机位置传感器]
            BFS[夹紧力传感器]
            TEMP[温度传感器]
        end
        
        MCU -->|PWM信号| DRV
        DRV -->|三相电流| MOTOR
        MOTOR -->|旋转运动| GEAR
        GEAR -->|减速增扭| SCREW
        SCREW -->|直线运动| PISTON
        PISTON --> PAD
        PAD --> DISC
        
        MPS -->|位置反馈| MCU
        BFS -->|力反馈| MCU
        TEMP -->|温度监测| MCU
    end
    
    style MCU fill:#fff3e0,stroke:#e65100
    style MOTOR fill:#e8f5e9,stroke:#2e7d32
    style PAD fill:#ffebee,stroke:#c62828
```

---

## 四、EMB控制工作流程

### 4.1 制动请求处理流程

```mermaid
sequenceDiagram
    participant Driver as 驾驶员
    participant PTS as 踏板感觉模拟器
    participant VMC as VMC域控制器
    participant Algo as 控制算法
    participant EMB as EMB轮边控制器
    participant Motor as 电机驱动
    participant Caliper as 制动卡钳
    participant Sensor as 传感器组

    Driver->>PTS: 踩下制动踏板
    PTS->>VMC: 踏板位移信号 + 踏板力信号
    
    VMC->>Algo: 请求计算目标制动扭矩
    
    Note over Algo: 综合计算考虑：<br/>1. 踏板行程→驾驶员意图<br/>2. 车速→动能<br/>3. 载荷→质量<br/>4. 路面附着系数
    
    Algo->>VMC: 返回目标制动扭矩
    
    VMC->>EMB: 下发目标扭矩(四轮独立)
    
    EMB->>EMB: 扭矩→电流换算
    EMB->>Motor: 输出三相电流
    
    Motor->>Caliper: 电机旋转→减速→直线运动
    Caliper->>Caliper: 制动块压紧制动盘
    
    Sensor->>EMB: 实时反馈(夹紧力/电机位置/轮速)
    EMB->>EMB: 闭环控制(PID/FOC)
    EMB->>VMC: 状态上报
    
    Note over VMC: 监测功能：<br/>ABS防抱死<br/>TCS牵引力<br/>VDC动态稳定<br/>EBD制动力分配
```

### 4.2 制动力分配策略

```mermaid
graph TD
    subgraph "制动力分配决策"
        INPUT[输入参数] --> LOAD[车辆载荷]
        INPUT --> SPEED[车速]
        INPUT --> YAW[横摆角速度]
        INPUT --> SLIP[滑移率]
        INPUT --> STEER[方向盘转角]
        
        LOAD --> CALC[制动力计算模块]
        SPEED --> CALC
        YAW --> CALC
        SLIP --> CALC
        STEER --> CALC
        
        CALC -->|理想制动力分配| BBD[基础制动分配]
        CALC -->|防抱死控制| ABS[ABS模块]
        CALC -->|稳定性控制| VDC[VDC模块]
        
        BBD --> FL[左前轮<br/>目标扭矩]
        BBD --> FR[右前轮<br/>目标扭矩]
        BBD --> RL[左后轮<br/>目标扭矩]
        BBD --> RR[右后轮<br/>目标扭矩]
        
        ABS -.->|调节| FL
        ABS -.->|调节| FR
        ABS -.->|调节| RL
        ABS -.->|调节| RR
        
        VDC -.->|修正| FL
        VDC -.->|修正| FR
        VDC -.->|修正| RL
        VDC -.->|修正| RR
    end
```

---

## 五、EMB软件架构方案

### 5.1 方案一：EMB作为独立域控系统

```mermaid
graph TB
    subgraph "方案一：独立域控架构"
        direction TB
        
        subgraph "EMB Domain Controller"
            APP[应用层软件]
            RTE[RTE运行时环境]
            BSW[基础软件层]
            MCAL[微控制器驱动层]
        end
        
        subgraph "应用层功能"
            APP --> ABS[ABS算法]
            APP --> TCS[TCS算法]
            APP --> VDC[VDC算法]
            APP --> EBD[EBD算法]
            APP --> MOTOR[电机控制算法<br/>FOC矢量控制]
        end
        
        subgraph "底层驱动"
            MCAL --> PWM[PWM生成]
            MCAL --> ADC[ADC采样]
            MCAL --> CAN[CAN通信]
            MCAL --> GPIO[GPIO控制]
        end
        
        subgraph "执行层"
            PWM --> DRV[电机驱动器]
            ADC --> SENS[传感器采集]
        end
        
        DRV --> MOTOR_H[四个轮毂电机]
    end
    
    style APP fill:#e3f2fd,stroke:#1565c0
    style MOTOR fill:#c8e6c9,stroke:#2e7d32
```

### 5.2 方案二：EMB作为轮边控制器

```mermaid
graph TB
    subgraph "方案二：分层协同架构"
        direction TB
        
        subgraph "中央域控制器"
            VMC_C[VMC Controller]
            VMC_C --> UPPER[上层算法]
            UPPER --> TCS_C[TCS]
            UPPER --> VDC_C[VDC/VAF]
            UPPER --> VAF_C[车辆姿态控制]
        end
        
        subgraph "通信总线"
            CAN1[CAN-FD总线<br/>1Mbps+]
            ETH[车载以太网<br/>100Mbps+]
        end
        
        subgraph "四轮轮边控制器"
            direction LR
            
            EMB_FL[左前EMB<br/>轮边控制器] --> FL_M[ABS算法<br/>电机控制]
            EMB_FR[右前EMB<br/>轮边控制器] --> FR_M[ABS算法<br/>电机控制]
            EMB_RL[左后EMB<br/>轮边控制器] --> RL_M[ABS算法<br/>电机控制]
            EMB_RR[右后EMB<br/>轮边控制器] --> RR_M[ABS算法<br/>电机控制]
        end
        
        VMC_C -->|目标扭矩| CAN1
        CAN1 --> EMB_FL
        CAN1 --> EMB_FR
        CAN1 --> EMB_RL
        CAN1 --> EMB_RR
        
        FL_M -->|状态反馈| CAN1
        FR_M -->|状态反馈| CAN1
        RL_M -->|状态反馈| CAN1
        RR_M -->|状态反馈| CAN1
        
        style VMC_C fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
        style EMB_FL fill:#c8e6c9,stroke:#2e7d32
        style EMB_FR fill:#c8e6c9,stroke:#2e7d32
        style EMB_RL fill:#c8e6c9,stroke:#2e7d32
        style EMB_RR fill:#c8e6c9,stroke:#2e7d32
    end
```

### 5.3 两种方案对比

| 对比维度 | 方案一：独立域控 | 方案二：轮边控制器 |
|---------|-----------------|-------------------|
| **控制延迟** | 低（单芯片内部） | 中（需总线通信） |
| **系统复杂度** | 高（集中处理） | 低（分布式处理） |
| **扩展性** | 较差 | 好（可灵活增加节点） |
| **功能安全** | ASIL-D需复杂设计 | 更易实现ASIL-D |
| **成本** | 较低（单控制器） | 较高（多个控制器） |
| **适用场景** | 高性能需求 | 高安全等级需求 |

---

## 六、EMB冗余安全设计

### 6.1 冗余架构设计

```mermaid
graph TB
    subgraph "EMB冗余安全架构"
        direction TB
        
        subgraph "主控制通道"
            MAIN_CPU[主CPU<br/>Core 0]
            MAIN_DRV[主电机驱动]
            MAIN_PWR[主电源]
        end
        
        subgraph "冗余监控通道"
            MON_CPU[监控CPU<br/>Core 1]
            MON_DRV[冗余电机驱动]
            MON_PWR[冗余电源]
        end
        
        subgraph "安全机制"
            WD[独立看门狗]
            LVC[低压监控]
            OVC[过流保护]
            OTC[过温保护]
        end
        
        MAIN_CPU -->|主控制信号| ACTUATOR[执行机构]
        MON_CPU -.->|监控/接管| ACTUATOR
        
        MAIN_CPU <->|交叉监控| MON_CPU
        
        WD --> MAIN_CPU
        WD --> MON_CPU
        
        LVC -.-> MAIN_PWR
        OVC -.-> MAIN_DRV
        OTC -.-> ACTUATOR
    end
    
    style MAIN_CPU fill:#c8e6c9,stroke:#2e7d32
    style MON_CPU fill:#fff3e0,stroke:#e65100
```

### 6.2 故障降级策略

```mermaid
graph TD
    A[系统正常运行] -->|故障检测| B{故障类型判断}
    
    B -->|单轮EMB故障| C[单轮失效模式]
    B -->|同轴两轮故障| D[同轴失效模式]
    B -->|对角轮故障| E[对角失效模式]
    B -->|三轮以上故障| F[紧急制动模式]
    
    C --> C1[其他三轮正常制动]
    C --> C2[报警提示驾驶员]
    C --> C3[限制最高车速]
    
    D --> D1[启用同轴另一轮]
    D --> D2[EBD重新分配制动力]
    D --> D3[限制转向角速度]
    
    E --> E1[启用全部剩余制动力]
    E --> E2[强制双闪警示]
    E --> E3[请求驾驶员接管]
    
    F --> F1[紧急制动激活]
    F --> F2[拉紧手刹EPB]
    F --> F3[请求靠边停车]
    
    style A fill:#c8e6c9,stroke:#2e7d32
    style F fill:#ffebee,stroke:#c62828
```

---

## 七、EMB关键技术参数

### 7.1 性能指标

| 参数 | 典型值 | 说明 |
|------|--------|------|
| **响应时间** | 80-100ms | 踏板触发到制动建立 |
| **夹紧力范围** | 0-30kN | 单轮最大夹紧力 |
| **电机功率** | 200-350W | 单轮电机额定功率 |
| **控制精度** | ±2% | 夹紧力控制精度 |
| **工作电压** | 12V/24V/48V | 根据系统配置 |
| **防护等级** | IP6K9K | 防尘防水最高等级 |
| **工作温度** | -40°C~150°C | 全温度范围工作 |

### 7.2 功能安全等级

```mermaid
graph LR
    subgraph "ASIL等级分解"
        A[整车制动系统<br/>ASIL-D] --> B[EMB控制器<br/>ASIL-D]
        B --> C[电机驱动<br/>ASIL-C]
        B --> D[传感器采集<br/>ASIL-B]
        B --> E[通信接口<br/>ASIL-B]
        
        style A fill:#ffcdd2,stroke:#c62828,stroke-width:3px
        style B fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    end
```

---

## 八、总结与展望

### 8.1 EMB技术优势

```mermaid
graph LR
    subgraph "EMB核心价值"
        A[EMB电子机械制动] --> B[响应更快<br/>80ms vs 120ms]
        A --> C[效率更高<br/>能量回收提升10%+]
        A --> D[维护更少<br/>免更换制动液]
        A --> E[集成更好<br/>易于自动驾驶集成]
        A --> F[控制更精<br/>轮缸压力闭环控制]
    end
    
    style A fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
```

### 8.2 发展趋势

1. **短期（2025-2027）**: EHB仍是主流，EMB在高端车型试量产
2. **中期（2027-2030）**: EMB逐步放量，成本下降推动普及
3. **长期（2030+）**: EMB成为线控制动主流方案，与自动驾驶深度融合

### 8.3 挑战与对策

| 挑战 | 对策 |
|------|------|
| 功能安全认证难度大 | 采用双冗余架构，通过ASIL-D认证 |
| 成本高于EHB | 规模化生产，供应链本土化 |
| 驾驶员接受度 | 踏板感觉模拟器优化，保持熟悉感 |
| 极端工况可靠性 | 严格环境测试，故障降级策略 |

---

**参考资料**:
- 汽车电子设计微信公众号
- 博世/大陆EMB技术白皮书
- ISO 26262功能安全标准
- ECE R13-H制动法规

**文档版本**: v1.0  
**更新时间**: 2026-03-18
