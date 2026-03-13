# 智能底盘与高阶智驾系统架构设计

> 文档版本：v1.0  
> 设计阶段：系统架构设计  
> 基于：知识图谱 v1.0

---

## 一、整体架构概览

### 1.1 域集中式架构

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    subgraph Vehicle["🚗 整车电子电气架构"]
        direction TB
        
        subgraph AD_Domain["🤖 智能驾驶域 ADCU"]
            AD_SoC["SoC (Orin/J5/MDC)"]
            AD_MCU["Safety MCU (ASIL-D)"]
            AD_Perception["感知算法"]
            AD_Planning["规划算法"]
            AD_Control["控制算法"]
        end
        
        subgraph Chassis_Domain["🔧 底盘域 DCU"]
            Chassis_MCU["Main MCU (ASIL-D)"]
            Chassis_Pwr["电源管理"]
            Chassis_Driver["驱动电路"]
        end
        
        subgraph Power_Domain["⚡ 动力域"]
            VCU["整车控制器 VCU"]
            BMS["电池管理系统"]
            MCU["电机控制器"]
        end
        
        subgraph Body_Domain["🚪 车身域"]
            BCM["车身控制器"]
            Gateway["中央网关"]
        end
        
        subgraph Cockpit["🖥️ 智能座舱"]
            IVI["信息娱乐系统"]
            Cluster["仪表"]
        end
    end
    
    AD_Domain --"以太网 (1000BASE-T1)"--> Gateway
    Chassis_Domain --"CAN-FD / FlexRay"--> Gateway
    Power_Domain --"CAN-FD"--> Gateway
    Body_Domain --"CAN/LIN"--> Gateway
    Cockpit --"以太网"--> Gateway
    
    AD_Domain --"直接控制总线"--> Chassis_Domain
    Chassis_Domain --"动力请求"--> Power_Domain
    
    style AD_Domain fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style Chassis_Domain fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style Power_Domain fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Body_Domain fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Cockpit fill:#ffebee,stroke:#c62828,stroke-width:2px
```

### 1.2 底盘域内部架构

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    subgraph Chassis_DCU["🔧 底盘域控制器 (DCU)"]
        direction TB
        
        subgraph Core["核心控制层"]
            VDMC_Core["VDMC\n整车动态稳定"]
            Mode_Mgr["模式管理器"]
            Safety_Mon["安全监控"]
        end
        
        subgraph Modules["功能模块层"]
            ICC_Mod["ICC Module\n制动控制"]
            RWS_Mod["RWS Module\n转向控制"]
            ASC_Mod["ASC Module\n悬架控制"]
        end
        
        subgraph Interface["接口适配层"]
            ADAS_If["智驾接口适配"]
            Driver_If["驾驶员接口"]
            Power_If["动力域接口"]
        end
        
        subgraph MCAL["MCAL 硬件抽象层"]
            CAN_Drv["CAN/CAN-FD 驱动"]
            PWM_Drv["PWM 驱动"]
            ADC_Drv["ADC 驱动"]
            DIO_Drv["DIO 驱动"]
        end
        
        subgraph Actuators["执行器接口"]
            EHB_If["EHB 线控制动"]
            EPS_If["EPS 线控转向"]
            RWS_If["RWS 后轮转向"]
            ASC_If["空气悬架"]
        end
    end
    
    Interface --> Core
    Core --> Modules
    Modules --> MCAL
    MCAL --> Actuators
    
    style Chassis_DCU fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style Core fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    style Modules fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Interface fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

---

## 二、模块划分与职责定义

### 2.1 底盘域模块职责表

| 模块 | 英文全称 | ASIL等级 | 核心职责 | 关键功能 |
|------|----------|----------|----------|----------|
| **VDMC** | Vehicle Dynamic Motion Control | D | 整车动态协调控制 | 多系统仲裁、稳定性控制 |
| **ICC** | Integrated Chassis Control | D | 制动系统综合控制 | 能量回收、ESC、AEB执行 |
| **RWS** | Rear Wheel Steering | D | 后轮转向控制 | 转角控制、前后轮协调 |
| **ASC** | Air Suspension Control | B | 空气悬架控制 | 高度调节、阻尼控制 |
| **Mode Manager** | - | D | 系统模式管理 | 状态机、模式切换 |
| **Safety Monitor** | - | D | 安全监控 | 故障诊断、降级策略 |

### 2.2 智能驾驶域模块职责

| 模块 | 功能域 | ASIL等级 | 核心职责 |
|------|--------|----------|----------|
| **感知融合** | 感知 | B | 摄像头/雷达/激光雷达融合 |
| **定位建图** | 感知 | B | 高精定位、SLAM |
| **行为决策** | 决策 | D | 驾驶策略选择（车道/换道/泊车）|
| **运动规划** | 规划 | D | 轨迹规划、速度规划 |
| **车辆控制** | 控制 | D | 横向/纵向控制算法 |
| **预测模块** | 感知 | B | 交通参与者轨迹预测 |

---

## 三、接口定义

### 3.1 智驾域 -> 底盘域（ADCU -> DCU）

#### 横向控制接口

| 信号ID | 信号名称 | 数据类型 | 范围 | 精度 | 周期 | 说明 |
|--------|----------|----------|------|------|------|------|
| 0x100 | AD_LateralControlReq | boolean | 0-1 | - | 100ms | 横向控制使能请求 |
| 0x101 | AD_SteeringAngleReq | float | ±720° | 0.1° | 10ms | 目标方向盘转角 |
| 0x102 | AD_SteeringAngleRateReq | float | ±1000°/s | 1°/s | 10ms | 目标方向盘转角速度 |
| 0x103 | AD_LateralAccReq | float | ±10m/s² | 0.01m/s² | 10ms | 目标横向加速度 |
| 0x104 | AD_YawRateReq | float | ±100°/s | 0.01°/s | 10ms | 目标横摆角速度 |

#### 纵向控制接口

| 信号ID | 信号名称 | 数据类型 | 范围 | 精度 | 周期 | 说明 |
|--------|----------|----------|------|------|------|------|
| 0x200 | AD_LongitudinalControlReq | boolean | 0-1 | - | 100ms | 纵向控制使能请求 |
| 0x201 | AD_AccelerationReq | float | ±10m/s² | 0.01m/s² | 10ms | 目标加速度 |
| 0x202 | AD_VehicleSpeedReq | float | 0-250km/h | 0.1km/h | 20ms | 目标车速 |
| 0x203 | AD_DecelerationReq | float | 0-10m/s² | 0.01m/s² | 10ms | 目标减速度 |
| 0x204 | AD_StandstillReq | boolean | 0-1 | - | 50ms | 驻车请求 |

#### 系统状态接口

| 信号ID | 信号名称 | 数据类型 | 范围 | 周期 | 说明 |
|--------|----------|----------|------|------|------|
| 0x300 | AD_SystemState | uint8 | 0-7 | 50ms | 系统状态机状态 |
| 0x301 | AD_ControlMode | uint8 | 0-3 | 50ms | 控制模式 |
| 0x302 | AD_FaultLevel | uint8 | 0-3 | 100ms | 故障等级 |
| 0x303 | AD_HandsOffWarning | uint8 | 0-3 | 100ms | 脱手警告级别 |

### 3.2 底盘域 -> 智驾域（DCU -> ADCU）

#### 底盘状态反馈

| 信号ID | 信号名称 | 数据类型 | 范围 | 精度 | 周期 | 说明 |
|--------|----------|----------|------|------|------|------|
| 0x400 | Chassis_SteeringAngle | float | ±720° | 0.1° | 10ms | 实际方向盘转角 |
| 0x401 | Chassis_SteeringAngleSpeed | float | ±1000°/s | 1°/s | 10ms | 实际转角速度 |
| 0x402 | Chassis_VehicleSpeed | float | 0-250km/h | 0.1km/h | 10ms | 实际车速 |
| 0x403 | Chassis_LongitudinalAcc | float | ±10m/s² | 0.01m/s² | 10ms | 纵向加速度 |
| 0x404 | Chassis_LateralAcc | float | ±10m/s² | 0.01m/s² | 10ms | 横向加速度 |
| 0x405 | Chassis_YawRate | float | ±100°/s | 0.01°/s | 10ms | 横摆角速度 |
| 0x406 | Chassis_RearWheelAngle | float | ±15° | 0.1° | 20ms | 后轮转角 |

#### 系统就绪状态

| 信号ID | 信号名称 | 数据类型 | 周期 | 说明 |
|--------|----------|----------|------|------|
| 0x500 | Chassis_Ready | boolean | 50ms | 底盘系统就绪 |
| 0x501 | Chassis_LateralReady | boolean | 50ms | 横向控制就绪 |
| 0x502 | Chassis_LongitudinalReady | boolean | 50ms | 纵向控制就绪 |
| 0x503 | Chassis_FaultLevel | uint8 | 100ms | 底盘故障等级 |
| 0x504 | Chassis_ControlActive | boolean | 50ms | 控制激活状态 |

### 3.3 底盘域内部接口

#### VDMC -> 各子系统

| 源模块 | 目标模块 | 信号名称 | 说明 |
|--------|----------|----------|------|
| VDMC | ICC | VDMC_BrakeForceReq | 制动力请求 |
| VDMC | RWS | VDMC_RearAngleReq | 后轮转角请求 |
| VDMC | ASC | VDMC_DampingReq | 阻尼系数请求 |
| VDMC | ASC | VDMC_HeightReq | 车身高度请求 |
| ICC | VDMC | ICC_BrakeForceAvail | 可用制动力 |
| RWS | VDMC | RWS_RearAngleActual | 实际后轮转角 |
| ASC | VDMC | ASC_HeightActual | 实际车身高度 |

---

## 四、数据流图

### 4.1 横向控制数据流

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    subgraph AD["🤖 智驾域"]
        A1["感知融合\n车道线/障碍物"]
        A2["横向规划\n轨迹生成"]
        A3["横向控制\nLKA/LCC算法"]
    end
    
    subgraph Chassis["🔧 底盘域"]
        C1["VDMC\n请求仲裁"]
        C2["RWS\n后轮转向控制"]
        C3["EPS\n前轮转向控制"]
        C4["底盘状态\n反馈"]
    end
    
    subgraph Vehicle["🚗 车辆"]
        V["车辆运动\nYaw/β"]
    end
    
    A1 --"车道线信息"--> A2
    A2 --"目标轨迹"--> A3
    A3 --"方向盘转角请求"--> C1
    C1 --"前轮转角请求"--> C3
    C1 --"后轮转角请求"--> C2
    C2 --"后轮转角"--> V
    C3 --"前轮转角"--> V
    V --"车辆状态"--> C4
    C4 --"状态反馈"--> A1
    
    style AD fill:#e3f2fd,stroke:#1565c0
    style Chassis fill:#e8f5e9,stroke:#2e7d32
    style Vehicle fill:#fff3e0,stroke:#ef6c00
```

### 4.2 纵向控制数据流

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    subgraph AD["🤖 智驾域"]
        A1["目标识别\n前车/障碍物"]
        A2["纵向规划\n速度曲线"]
        A3["纵向控制\nACC/AEB算法"]
    end
    
    subgraph Chassis["🔧 底盘域"]
        C1["VDMC\n请求仲裁"]
        C2["ICC\n一体化制动"]
        C3["动力域\n驱动控制"]
        C4["底盘状态\n反馈"]
    end
    
    subgraph Vehicle["🚗 车辆"]
        V["车辆运动\nVx/Ax"]
    end
    
    A1 --"目标信息"--> A2
    A2 --"目标加速度"--> A3
    A3 --"加速度请求"--> C1
    C1 --"制动请求"--> C2
    C1 --"驱动请求"--> C3
    C2 --"制动力矩"--> V
    C3 --"驱动力矩"--> V
    V --"车辆状态"--> C4
    C4 --"状态反馈"--> A1
    
    style AD fill:#e3f2fd,stroke:#1565c0
    style Chassis fill:#e8f5e9,stroke:#2e7d32
    style Vehicle fill:#fff3e0,stroke:#ef6c00
```

### 4.3 能量回收数据流

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    subgraph Driver["👤 驾驶员"]
        D1["制动踏板"]
        D2["能量回收\n强度选择"]
    end
    
    subgraph Chassis["🔧 底盘域"]
        C1["VDMC\n协调控制"]
        C2["ICC\n制动力分配"]
    end
    
    subgraph Power["⚡ 动力域"]
        P1["MCU\n电机控制"]
        P2["BMS\n电池管理"]
    end
    
    D1 --"踏板行程"--> C1
    D2 --"回收等级"--> C1
    C1 --"总制动需求"--> C2
    C2 --"电机制动请求"--> P1
    C2 --"机械制动请求"--> C2_Mech["液压制动"]
    P1 --"可回收功率"--> C2
    P2 --"电池状态"--> P1
    P1 --"实际回收功率"--> C1
    
    style Driver fill:#f3e5f5,stroke:#7b1fa2
    style Chassis fill:#e8f5e9,stroke:#2e7d32
    style Power fill:#fff3e0,stroke:#ef6c00
```

---

## 五、安全架构设计

### 5.1 功能安全 ASIL 分配

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    subgraph Safety["🛡️ 功能安全架构"]
        direction TB
        
        subgraph ASIL_D["ASIL-D 级"]
            D1["VDMC 核心控制"]
            D2["ICC 制动控制"]
            D3["RWS 转向控制"]
            D4["安全监控"]
        end
        
        subgraph ASIL_B["ASIL-B 级"]
            B1["ASC 悬架控制"]
            B2["智驾感知"]
        end
        
        subgraph QM["QM 级"]
            Q1["HMI 显示"]
            Q2["数据记录"]
        end
    end
    
    style ASIL_D fill:#ffebee,stroke:#c62828,stroke-width:2px
    style ASIL_B fill:#fff3e0,stroke:#f57f17,stroke-width:2px
    style QM fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### 5.2 冗余架构设计

#### 线控制动冗余（ICC）

| 组件 | 主通道 | 冗余通道 | 说明 |
|------|--------|----------|------|
| ECU | Main MCU | Safety MCU | 双核锁步 |
| 传感器 | 主压力传感器 | 冗余压力传感器 | 双路采集 |
| 执行器 | 主电机 | 冗余电机 | 双电机方案 |
| 通信 | CAN-FD A | CAN-FD B | 双路通信 |

#### 线控转向冗余（RWS）

| 组件 | 主通道 | 冗余通道 | 说明 |
|------|--------|----------|------|
| ECU | Main MCU | Safety MCU | 双核锁步 |
| 传感器 | 主转角传感器 | 冗余转角传感器 | 双路采集 |
| 执行器 | 主电机 | 冗余电机 | 双绕组电机 |
| 通信 | CAN-FD A | CAN-FD B | 双路通信 |

### 5.3 故障降级策略

| 故障等级 | 触发条件 | 系统响应 | 驾驶员提示 |
|----------|----------|----------|------------|
| **Level 0** | 无故障 | 正常功能 | - |
| **Level 1** | 轻微故障 | 功能受限，降级运行 | 黄色警告 |
| **Level 2** | 中等故障 | 功能关闭，请求接管 | 红色警告+声音 |
| **Level 3** | 严重故障 | 紧急停车，进入安全状态 | 紧急警告 |

### 5.4 预期功能安全 (SOTIF)

| 危害场景 | 触发条件 | 安全措施 |
|----------|----------|----------|
| 误制动 | 传感器误识别 | 多传感器融合确认 |
| 误转向 | 车道线误识别 | 驾驶员监控+力矩检测 |
| 低速追尾 | AEB误触发 | 低速场景抑制策略 |
| 弯道超速 | 曲率估计误差 | 地图数据校验 |

---

## 六、通信架构

### 6.1 车载网络拓扑

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    subgraph Gateway["🌐 中央网关"]
        G_Eth["以太网交换机"]
        G_CAN["CAN 网关"]
    end
    
    subgraph ADAS_Bus["🤖 ADAS 域总线"]
        AD1["ADCU"]
        AD2["摄像头"]
        AD3["雷达"]
        AD4["激光雷达"]
    end
    
    subgraph Chassis_Bus["🔧 底盘域总线"]
        C1["DCU"]
        C2["EHB"]
        C3["EPS"]
        C4["RWS"]
        C5["ASC"]
    end
    
    subgraph Power_Bus["⚡ 动力域总线"]
        P1["VCU"]
        P2["MCU"]
        P3["BMS"]
    end
    
    AD1 --"1000BASE-T1"--> G_Eth
    C1 --"CAN-FD 2M"--> G_CAN
    P1 --"CAN-FD 2M"--> G_CAN
    
    AD1 -."直接控制\nCAN-FD".- C1
    C1 -."私有 CAN".- C2
    C1 -."私有 CAN".- C3
    C1 -."私有 CAN".- C4
    C1 -."私有 CAN".- C5
    
    style Gateway fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style ADAS_Bus fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Chassis_Bus fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Power_Bus fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

### 6.2 通信矩阵

| 信号流 | 总线类型 | 波特率 | 周期 | 延迟要求 |
|--------|----------|--------|------|----------|
| ADCU -> DCU | CAN-FD | 2Mbps | 10ms | <5ms |
| DCU -> EHB | CAN-FD | 2Mbps | 10ms | <3ms |
| DCU -> EPS | CAN-FD | 2Mbps | 10ms | <3ms |
| DCU -> RWS | CAN-FD | 1Mbps | 20ms | <10ms |
| DCU -> ASC | CAN | 500kbps | 50ms | <20ms |
| ADCU -> 感知 | 以太网 | 1000Mbps | - | <1ms |

---

## 七、状态机设计

### 7.1 底盘域状态机

```mermaid
%%{init: {'theme': 'base'}}%%
stateDiagram-v2
    [*] --> Init: 上电
    Init --> Standby: 初始化完成
    Standby --> Ready: 自检通过
    Ready --> Active: 控制请求
    Active --> Ready: 控制结束
    Ready --> Standby: 故障/休眠请求
    Standby --> Init: 唤醒
    Ready --> Degraded: 故障发生
    Degraded --> Ready: 故障恢复
    Degraded --> Emergency: 严重故障
    Emergency --> Standby: 故障清除+重启
    
    note right of Init
        系统初始化
        硬件自检
    end note
    
    note right of Ready
        等待控制请求
        可进入主动控制
    end note
    
    note right of Active
        执行智驾/驾驶员请求
        实时控制运行中
    end note
```

---

## 八、设计原则与约束

### 8.1 设计原则

1. **安全第一**：所有设计以满足 ASIL-D 安全目标为首要原则
2. **可扩展性**：架构支持从 L2 到 L4 的功能扩展
3. **标准化**：遵循 AUTOSAR 标准和行业最佳实践
4. **冗余设计**：关键功能采用冗余设计确保可靠性
5. **可测试性**：每个模块都具备独立的测试接口

### 8.2 设计约束

| 约束项 | 要求 |
|--------|------|
| 功能安全 | 满足 ISO 26262 ASIL-D |
| 预期功能安全 | 满足 ISO 21448 |
| 网络安全 | 满足 ISO/SAE 21434 |
| 软件架构 | 符合 AUTOSAR Classic Platform |
| 通信协议 | 符合 CAN/CAN-FD 2.0 和 Ethernet TSN |
| 响应延迟 | 端到端控制延迟 < 100ms |
| 控制精度 | 横向误差 < 0.2m，纵向误差 < 0.5m/s |

---

## 九、参考文档

1. **知识图谱** - `knowledge_graph.md`
2. **ISO 26262** - 道路车辆功能安全
3. **ISO 21448** - 预期功能安全
4. **AUTOSAR Classic Platform** - 软件架构标准
5. **培训大纲** - 智能底盘一体化控制及高阶智能驾驶关键技术

---

> 🏷️ **标签**：`系统架构`, `底盘域`, `智驾域`, `接口定义`, `功能安全`, `ASIL-D`
