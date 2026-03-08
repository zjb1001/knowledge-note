# 整车时间同步方案设计

> **文档版本**: v1.0  
> **编制日期**: 2026-03-08  
> **方案类型**: 车载以太网时间同步  
> **技术领域**: TSN/gPTP/AUTOSAR

---

## 1. 背景与需求

### 1.1 为什么需要时间同步

现代智能汽车需要高精度时间同步的场景：

| 应用场景 | 精度要求 | 说明 |
|----------|----------|------|
| 传感器数据融合 | < 1ms | 摄像头/雷达/激光雷达数据时间戳对齐 |
| 运动控制 | < 100μs | 底盘域多ECU协同控制 |
| 数据记录 | < 10ms | 故障日志全局时间戳 |
| 诊断刷写 | < 100ms | DoIP诊断会话时间 |
| ADAS功能 | < 50μs | AEB/LKA等实时功能 |

### 1.2 传统方案的局限

**CAN 时间同步**:
- 精度：~1ms（已无法满足ADAS需求）
- 带宽：1Mbps（无法支持传感器数据洪流）

**GPS 时间同步**:
- 精度：~10ns（授时精度高）
- 问题：隧道/地下车库无信号
- 问题：无法支持内部网络节点间同步

**NTP 网络时间协议**:
- 精度：~1-10ms
- 问题：精度不足，无硬件时间戳支持

---

## 2. 方案总体设计

### 2.1 技术选型：gPTP (IEEE 802.1AS)

**选择理由**:
- 精度：亚微秒级（< 1μs）
- 标准：IEEE 802.1AS-2020（TSN核心标准）
- 支持：AUTOSAR Time Sync over Ethernet
- 兼容：支持CAN的时间同步桥接

### 2.2 系统架构图

```mermaid
graph TB
    subgraph 外部授时["🛰️ 外部授时"]
        GPS["GPS/GNSS模块"]
        PPS["PPS + ToD信号"]
    end

    subgraph 骨干网络["🌐 车载以太网骨干"]
        GM["🎯 Grand Master<br/>主域控制器<br/>(TC397TP)"]
        SW1["🔄 TSN交换机 #1<br/>(SJA1110)"]
        SW2["🔄 TSN交换机 #2<br/>(SJA1110)"]
    end

    subgraph 域控制器["🚗 各域控制器 (gPTP从节点)"]
        ADAS["智驾域<br/>摄像头/雷达融合"]
        CHASSIS["底盘域<br/>ESC/EPS/EHB"]
        POWER["动力域<br/>电机/BMS/VCU"]
        COCKPIT["座舱域<br/>IVI/仪表"]
    end

    subgraph 传感器["📡 传感器/执行器"]
        CAM["摄像头"]
        RADAR["毫米波雷达"]
        LIDAR["激光雷达"]
        ESC["ESC控制器"]
    end

    GPS --> PPS
    PPS --> GM
    GM --> SW1
    SW1 --> SW2
    SW1 --> ADAS
    SW1 --> CHASSIS
    SW2 --> POWER
    SW2 --> COCKPIT
    ADAS --> CAM
    ADAS --> RADAR
    ADAS --> LIDAR
    CHASSIS --> ESC

    style GM fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style SW1 fill:#4dabf7,stroke:#1971c2,color:#fff
    style SW2 fill:#4dabf7,stroke:#1971c2,color:#fff
```

### 2.3 网络拓扑架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      整车时间同步架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐     Grand Master (gPTP主时钟)                │
│   │   GPS/GNSS   │     - 主域控制器 (如智驾域)                    │
│   │   授时模块    │     - 以太网交换机（带gPTP支持）               │
│   └──────┬───────┘     - 提供整个网络的基准时间                   │
│          │                                                      │
│          │ PPS + ToD                                            │
│          ▼                                                      │
│   ┌────────────────────────────────────────────────────┐        │
│   │              车载以太网骨干网 (1Gbps)                 │        │
│   │         ┌─────────┐    ┌─────────┐                 │        │
│   │         │ TSN交换 │────│ TSN交换 │                 │        │
│   │         │ 机  #1  │    │ 机  #2  │                 │        │
│   │         └────┬────┘    └────┬────┘                 │        │
│   └──────────────┼──────────────┼──────────────────────┘        │
│                  │              │                               │
│    ┌─────────────┼──────────────┼─────────────┐                  │
│    │             │              │             │                  │
│    ▼             ▼              ▼             ▼                  │
│ ┌──────┐    ┌──────┐      ┌──────┐    ┌──────┐                │
│ │智驾域 │    │座舱域 │      │底盘域 │    │动力域 │                │
│ │控制器 │    │控制器 │      │控制器 │    │控制器 │                │
│ │(gPTP)│    │(gPTP)│      │(gPTP)│    │(gPTP)│                │
│ └──┬───┘    └──┬───┘      └──┬───┘    └──┬───┘                │
│    │           │             │           │                      │
│    ▼           ▼             ▼           ▼                      │
│ ┌──────┐   ┌──────┐     ┌──────┐   ┌──────┐                   │
│ │摄像头│   │激光雷│     │EPS/ESC│   │电机/VCU│                  │
│ │雷达  │   │达    │     │制动   │   │BMS   │                   │
│ └──────┘   └──────┘     └──────┘   └──────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 硬件设计方案

### 3.1 主时钟 (Grand Master) 硬件

**推荐方案**:
- **主控**: TC397TP (Aurix)
- **以太网**: 千兆MAC + TJA1103 PHY (1000BASE-T1)
- **授时**: u-blox ZED-F9T (GPS/GNSS + PPS输出)
- **时钟源**: OCXO/TCXO 恒温晶振 (±1ppm)

**时钟树设计**:
```
OCXO (25MHz)
    │
    ├──► TC397 (MCU时钟)
    │
    └──► TJA1103 (PHY时钟)
            │
            └──► 车载以太网
```

### 3.2 TSN 交换机

**关键特性**:
- 支持 IEEE 802.1AS (gPTP)
- 支持 IEEE 802.1Qbv (时间感知整形)
- 端口：6-8 路 1000BASE-T1
- 时间戳精度：< 10ns

**推荐芯片**:
- NXP SJA1110
- Marvell 88Q5152
- Microchip LAN9690

### 3.3 从节点硬件 (Domain Controller)

**各域控制器通用配置**:
- **MCU**: TC377/TC387 (带ETH)
- **MAC**: 内置千兆MAC
- **PHY**: TJA1101/TJA1103 (100/1000BASE-T1)
- **时间戳**: 硬件时间戳 (PTP Hardware Clock)

**硬件时间戳要求**:
| 组件 | 时间戳精度 | 说明 |
|------|-----------|------|
| MAC | < 25ns | 发送/接收时刻捕获 |
| PHY | < 10ns | 更精确，推荐支持 |

---

## 4. 软件设计方案

### 4.1 AUTOSAR 协议栈

**软件架构**:
```
应用层 (ASW)
├── 传感器融合算法
├── ADAS功能逻辑
└── 数据记录模块
        │
运行时环境 (RTE)
        │
服务层 (BSW)
├── StbM (同步时基管理)
│       ├── 提供同步时间戳API
│       └── 管理时间域 (Time Domain)
│
├── TimeSyncOverEth (gPTP协议)
│       ├── gPTP协议栈 (802.1AS)
│       ├── BMCA算法 (最佳主时钟)
│       └── 时间同步状态机
│
├── EthTSyn (时间同步驱动)
│       ├── 硬件时间戳接口
│       └── 时钟校正算法
│
└── Eth Driver
        ├── MAC驱动 (硬件时间戳)
        └── PHY驱动 (Link状态)
```

### 4.2 gPTP 协议实现

#### 4.2.1 BMCA (Best Master Clock Algorithm) 流程

```mermaid
flowchart TD
    Start([系统启动]) --> Init[初始化gPTP协议栈]
    Init --> Announce[发送/接收Announce消息]
    Announce --> Compare{比较时钟优先级}
    
    Compare -->|本节点优先级高| BecomeGM[成为Grand Master]
    Compare -->|其他节点优先级高| BecomeSlave[成为Slave节点]
    Compare -->|优先级相同| Compare2{比较时钟质量}
    
    Compare2 -->|本节点质量好| BecomeGM
    Compare2 -->|其他节点质量好| BecomeSlave
    Compare2 -->|质量相同| Compare3{比较MAC地址}
    
    Compare3 -->|MAC地址大| BecomeGM
    Compare3 -->|MAC地址小| BecomeSlave
    
    BecomeGM --> Sync[发送Sync消息同步网络]
    BecomeSlave --> Receive[接收Sync消息同步本地时钟]
    
    Sync --> Monitor[监控时钟源状态]
    Receive --> Monitor
    
    Monitor --> GM_Fail{主时钟故障?}
    GM_Fail -->|是| Reelect[重新选举主时钟]
    GM_Fail -->|否| Sync
    
    Reelect --> Announce
    
    style Start fill:#69db7c
    style BecomeGM fill:#ff6b6b,color:#fff
    style BecomeSlave fill:#4dabf7,color:#fff
    style GM_Fail fill:#ffd43b
```

**BMCA选举规则**（优先级从高到低）：
1. **Priority1**: 用户配置优先级（0-255，越小越高）
2. **ClockClass**: 时钟等级（如6=GPS同步，52=保持模式）
3. **ClockAccuracy**: 时钟精度（如0x20=<1μs）
4. **Priority2**: 次级优先级（0-255）
5. **ClockIdentity**: 64位MAC地址（越大优先级越高）

#### 4.2.2 gPTP 时间同步时序图

```mermaid
sequenceDiagram
    participant GM as Grand Master<br/>主时钟
    participant SW as TSN交换机
    participant S1 as Slave 1<br/>智驾域
    participant S2 as Slave 2<br/>底盘域

    Note over GM,S2: 第一阶段：时间同步消息交换

    rect rgb(255, 235, 238)
        Note over GM,S2: Sync消息传输（测量传输延迟）
        GM->>SW: Sync(t1)
        Note right of GM: t1 = 发送时刻<br/>10:00:00.000000
        
        SW->>S1: 转发Sync
        Note left of S1: t2 = 接收时刻<br/>10:00:00.000050
        
        SW->>S2: 转发Sync
        Note left of S2: t2' = 接收时刻<br/>10:00:00.000060
    end

    rect rgb(227, 242, 253)
        Note over GM,S2: Follow_Up消息（传递精确发送时间）
        GM-->>SW: Follow_Up(t1)
        SW-->>S1: 转发Follow_Up
        Note left of S1: 获取t1用于计算Offset
        SW-->>S2: 转发Follow_Up
    end

    rect rgb(255, 249, 230)
        Note over GM,S2: Delay_Req/Delay_Resp（测量路径延迟）
        S1->>SW: Delay_Req(t3)
        Note left of S1: t3 = 发送时刻<br/>10:00:00.001000
        SW->>GM: 转发Delay_Req
        Note left of GM: t4 = 接收时刻<br/>10:00:00.001020
        
        GM-->>SW: Delay_Resp(t4)
        SW-->>S1: 转发Delay_Resp
        Note left of S1: 获取t4用于计算Delay
    end

    Note over S1: 计算结果：<br/>Offset = 25μs<br/>Delay = 50μs
```

**计算公式**:
```
Offset = ((t2 - t1) - (t4 - t3)) / 2
Delay  = ((t2 - t1) + (t4 - t3)) / 2

其中:
- t1: Sync消息离开Master的时间
- t2: Sync消息到达Slave的时间
- t3: Delay_Req离开Slave的时间
- t4: Delay_Req到达Master的时间
```

#### 4.2.3 时钟同步状态机

```mermaid
stateDiagram-v2
    [*] --> INIT: 系统启动
    
    INIT --> DISCOVERING: 启动gPTP
    
    DISCOVERING --> MASTER: BMCA选举<br/>成为主时钟
    DISCOVERING --> SLAVE: BMCA选举<br/>成为从时钟
    
    MASTER --> SYNCING: 发送Sync消息
    
    SLAVE --> SYNCING: 接收Sync消息
    SLAVE --> SYNCING: 校准本地时钟
    
    SYNCING --> SYNCHRONIZED: 达到精度目标<br/>(Offset < 1μs)
    
    SYNCHRONIZED --> SYNCING: 定期同步
    SYNCHRONIZED --> HOLDOVER: 失去主时钟信号
    
    HOLDOVER --> DISCOVERING: Holdover超时
    HOLDOVER --> SYNCING: 重新发现主时钟
    
    SYNCING --> DISCOVERING: 主时钟故障
    
    MASTER --> DISCOVERING: 检测到更高优先级时钟
    SLAVE --> DISCOVERING: BMCA重新选举
```

**状态说明**:
- **INIT**: 初始化状态
- **DISCOVERING**: 发现网络中的时钟节点
- **MASTER**: 作为Grand Master运行
- **SLAVE**: 作为Slave节点运行
- **SYNCING**: 正在进行时间同步
- **SYNCHRONIZED**: 已达到同步精度目标
- **HOLDOVER**: 失去主时钟，保持模式运行

#### 4.2.4 时钟校正流程

```mermaid
flowchart LR
    subgraph 输入["📥 时间戳输入"]
        t1["t1: Master发送Sync"]
        t2["t2: Slave接收Sync"]
        t3["t3: Slave发送Delay_Req"]
        t4["t4: Master接收Delay_Req"]
    end

    subgraph 计算["🧮 计算过程"]
        direction TB
        calc1["计算路径延迟:<br/>Delay = ((t2-t1) + (t4-t3)) / 2"]
        calc2["计算时钟偏差:<br/>Offset = ((t2-t1) - (t4-t3)) / 2"]
        calc3["频率比计算:<br/>RateRatio = (t2'-t2) / (t1'-t1)"]
    end

    subgraph 输出["📤 时钟校正"]
        adj1["相位校正:<br/>调整本地时钟Offset"]
        adj2["频率校正:<br/>调整时钟RateRatio"]
        result["同步精度 < 1μs ✅"]
    end

    t1 --> calc1
    t2 --> calc1
    t3 --> calc1
    t4 --> calc1
    calc1 --> calc2
    calc2 --> calc3
    calc3 --> adj1
    calc3 --> adj2
    adj1 --> result
    adj2 --> result

    style result fill:#69db7c
```

### 4.3 MCAL 配置要点

**ETH Driver 配置**:
```c
// EthGeneral
typedef struct {
    boolean EthDevErrorDetect = TRUE;
    boolean EthEnableTimeSync = TRUE;        // 启用时间同步
    uint8 EthTimeSyncClockSource = ETH_TSC_INTERNAL;  // 内部PTP时钟
} EthGeneralType;

// EthControllerConfig
typedef struct {
    uint16 EthCtrlIdx = 0;
    boolean EthEnableHwTimestamp = TRUE;     // 硬件时间戳
    uint32 EthTimestampClockFreq = 100000000; // 100MHz
} EthControllerConfigType;
```

**GPT 配置 (提供PTP时钟基准)**:
```c
// 用于生成gPTP所需的本地时钟 (如80MHz)
GptChannelConfigSet_GptChannelConfig_0:
    GptChannelId = 0
    GptHwChannel = FTM0
    GptChannelMode = CONTINUOUS
    GptPrescaler = 0              // 不分频
    GptChannelTickFrequency = 80000000  // 80MHz
```

---

## 5. 时间同步性能指标

### 5.1 设计目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 同步精度 | < 1μs | 端到端时间偏差 |
| 收敛时间 | < 2s | 上电到稳定同步 |
| 保持能力 | < 100μs/s | 失去主时钟后的漂移 |
| 消息周期 | 125ms | Sync消息发送周期 |
| 故障切换 | < 100ms | 主时钟故障切换时间 |

### 5.2 精度保障措施

**硬件层面**:
- 使用硬件时间戳 (MAC/PHY层)
- 对称的链路延迟 (等长网线)
- 温度补偿晶振 (TCXO)

**软件层面**:
- 高优先级任务处理gPTP消息
- 中断驱动接收 (非轮询)
- 时钟滤波算法 (Kalman/PID)

---

## 6. 测试验证方案

### 6.1 测试环境

**测试设备**:
- Vector VN5640 (以太网分析仪)
- Keysight N5247B (PNA-X网络分析仪)
- 示波器 (≥1GHz带宽)

**测试拓扑**:
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   主时钟      │──────│   TSN交换机   │──────│   从时钟      │
│   (DUT)      │      │   (DUT)      │      │   (DUT)      │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                    ┌────────▼─────┐
                    │ 时间测试设备  │
                    │ (示波器/PNA) │
                    └──────────────┘
```

### 6.2 测试验证流程

```mermaid
flowchart TB
    subgraph 环境搭建["🔧 测试环境搭建"]
        DUT_GM["Grand Master<br/>(DUT)"]
        DUT_SW["TSN交换机<br/>(DUT)"]
        DUT_SLAVE["Slave节点<br/>(DUT)"]
        REF["参考时钟<br/>(铷原子钟)"]
        ANALYZER["时间分析仪<br/>(Vector VN5640)"]
    end

    subgraph 功能测试["✅ 功能测试"]
        TC1["TC-001:<br/>gPTP协议握手"]
        TC2["TC-002:<br/>BMCA选举"]
        TC3["TC-003:<br/>时间同步精度"]
        TC4["TC-004:<br/>故障切换"]
    end

    subgraph 性能测试["⚡ 性能测试"]
        TC5["TC-005:<br/>收敛时间"]
        TC6["TC-006:<br/>保持能力"]
        TC7["TC-007:<br/>温度影响"]
        TC8["TC-008:<br/>EMC干扰"]
    end

    subgraph 结果分析["📊 结果分析"]
        REPORT["测试报告生成"]
        PASS{"全部通过?"}
        FIX["问题修复"]
        CERT["认证通过 ✅"]
    end

    DUT_GM --> TC1
    DUT_SW --> TC1
    DUT_SLAVE --> TC1
    REF --> TC3
    ANALYZER --> TC3

    TC1 --> TC2 --> TC3 --> TC4
    TC4 --> TC5 --> TC6 --> TC7 --> TC8
    TC8 --> REPORT
    REPORT --> PASS
    PASS -->|否| FIX
    FIX --> TC1
    PASS -->|是| CERT

    style CERT fill:#69db7c
    style FIX fill:#ff6b6b,color:#fff
```

### 6.3 测试用例详情

| 测试项 | 方法 | 通过标准 |
|--------|------|----------|
| 同步精度 | 测量PPS信号偏差 | < 1μs |
| 收敛时间 | 上电后计时 | < 2s |
| 保持能力 | 断开后计时漂移 | < 100μs/s |
| 主时钟切换 | 强制主时钟故障 | < 100ms |
| 温度影响 | -40°C ~ 85°C循环 | 精度满足 |
| EMC干扰 | 传导/辐射抗扰 | 功能正常 |

---

## 7. 典型应用场景

### 7.1 传感器数据融合

**多传感器时间对齐**:
```
时间戳对齐前:
摄像头: t=100.000ms
雷达:   t=100.100ms  ← 100μs偏差
激光雷达: t=99.900ms  ← 100μs偏差

时间戳对齐后 (gPTP同步后):
摄像头: t=100.000ms ± 500ns
雷达:   t=100.000ms ± 500ns
激光雷达: t=100.000ms ± 500ns
```

### 7.2 底盘域协同控制时序

**ESC + EPS + EHB 协同制动**:

```mermaid
sequenceDiagram
    participant VCU as VCU<br/>整车控制
    participant EHB as EHB<br/>电子液压制动
    participant ESC as ESC<br/>电子稳定控制
    participant EPS as EPS<br/>电动助力转向

    Note over VCU,EPS: 控制周期: 2ms<br/>同步精度: < 100μs

    rect rgb(255, 235, 238)
        Note over VCU,EPS: T=0ms: 制动请求
        VCU->>EHB: 制动请求 (减速度 0.6g)<br/>t=0.000
        Note right of VCU: 发送时间戳<br/>同步误差 < 50μs
    end

    rect rgb(227, 242, 253)
        Note over VCU,EPS: T=0.5ms: 协调控制
        EHB->>ESC: 制动压力状态<br/>t=0.500
        VCU->>EPS: 后轮转角 3°<br/>t=0.550
        Note right of VCU: 横摆力矩补偿
    end

    rect rgb(232, 245, 233)
        Note over VCU,EPS: T=1.0ms: 执行动作
        ESC->>EHB: 轮缸压力调节<br/>t=1.000
        EPS-->>VCU: 转向扭矩反馈<br/>t=1.050
        EHB-->>VCU: 制动执行确认<br/>t=1.080
    end

    rect rgb(255, 249, 230)
        Note over VCU,EPS: T=2.0ms: 下一周期
        Note over VCU,EPS: 循环执行<br/>周期抖动 < 100μs
    end
```

### 7.3 传感器数据融合流程

**多传感器时间对齐**:

```mermaid
flowchart TB
    subgraph 采集["📡 传感器数据采集"]
        CAM["摄像头<br/>30fps"]
        RADAR["毫米波雷达<br/>20fps"]
        LIDAR["激光雷达<br/>10fps"]
        IMU["IMU<br/>100Hz"]
    end

    subgraph 时间戳["⏱️ gPTP时间戳标记"]
        TS_CAM["t=100.000000s"]
        TS_RADAR["t=100.000020s"]
        TS_LIDAR["t=100.000050s"]
        TS_IMU["t=100.000010s"]
    end

    subgraph 同步["🔄 时间同步处理"]
        BUFFER["同步缓冲区<br/>最大等待 50ms"]
        ALIGN["时间对齐<br/>插值/外推"]
    end

    subgraph 融合["🧠 数据融合"]
        FUSION["多传感器融合算法"]
        OUTPUT["感知结果输出"]
    end

    CAM --> TS_CAM
    RADAR --> TS_RADAR
    LIDAR --> TS_LIDAR
    IMU --> TS_IMU

    TS_CAM --> BUFFER
    TS_RADAR --> BUFFER
    TS_LIDAR --> BUFFER
    TS_IMU --> BUFFER

    BUFFER --> ALIGN
    ALIGN --> FUSION
    FUSION --> OUTPUT

    style TS_CAM fill:#ff6b6b,color:#fff
    style TS_RADAR fill:#4dabf7,color:#fff
    style TS_LIDAR fill:#69db7c,color:#000
    style TS_IMU fill:#ffd43b,color:#000
```

### 7.3 数据记录与回放

**全局时间戳日志**:
```
[2024-03-08 10:30:00.000000123] [智驾域] AEB触发
[2024-03-08 10:30:00.000000345] [底盘域] ESC启动
[2024-03-08 10:30:00.000000567] [动力域] 扭矩限制
```

---

## 8. 实施建议

### 8.1 开发阶段甘特图

```mermaid
gantt
    title 整车时间同步项目开发计划
    dateFormat  YYYY-MM-DD
    section 阶段1: 需求分析
    需求收集           :a1, 2024-03-01, 7d
    方案设计           :a2, after a1, 7d
    需求评审           :milestone, after a2, 0d
    
    section 阶段2: 硬件设计
    芯片选型           :b1, after a2, 7d
    原理图设计         :b2, after b1, 14d
    PCB Layout         :b3, after b2, 14d
    硬件评审           :milestone, after b3, 0d
    
    section 阶段3: 软件开发
    gPTP协议栈移植     :c1, after b1, 21d
    MCAL配置           :c2, after b1, 14d
    StbM集成           :c3, after c1, 14d
    应用层开发         :c4, after c3, 21d
    软件评审           :milestone, after c4, 0d
    
    section 阶段4: 集成测试
    硬件调试           :d1, after b3, 14d
    软件调试           :d2, after c4, 14d
    系统联调           :d3, after d1, 14d
    性能测试           :d4, after d3, 14d
    
    section 阶段5: 量产准备
    产线测试方案       :e1, after d4, 7d
    文档整理           :e2, after d4, 7d
    量产评审           :milestone, after e2, 0d
```

**开发阶段详情**:

| 阶段 | 周期 | 关键交付物 | 依赖 |
|------|------|------------|------|
| 需求分析 | 2周 | 需求规格书、系统架构图 | - |
| 硬件设计 | 4周 | 原理图、PCB、BOM | 需求冻结 |
| 软件开发 | 8周 | gPTP协议栈、MCAL配置、StbM | 芯片选型 |
| 集成测试 | 4周 | 测试报告、性能数据 | 软硬件完成 |
| 量产准备 | 2周 | 产线测试方案、用户手册 | 测试通过 |

### 8.2 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| PHY不支持gPTP | 高 | 选型时确认802.1AS支持 |
| 布线不对称 | 中 | 严格等长布线 |
| 温度漂移 | 中 | 使用TCXO温度补偿 |
| EMI干扰 | 中 | 双绞线屏蔽层接地 |

### 8.3 成本估算

| 组件 | 单价(USD) | 数量 | 小计 |
|------|-----------|------|------|
| TSN交换机芯片 | $15 | 1 | $15 |
| 千兆PHY (TJA1103) | $8 | 6 | $48 |
| GPS模块 | $25 | 1 | $25 |
| OCXO晶振 | $10 | 1 | $10 |
| **总计** | | | **~$98** |

---

## 9. 参考标准

- IEEE 802.1AS-2020: Timing and Synchronization for Time-Sensitive Applications
- IEEE 802.1Qbv-2015: Enhancements for Scheduled Traffic
- AUTOSAR: Specification of Time Synchronization over Ethernet
- AUTOSAR: Specification of Synchronized Time-Base Manager

---

## 10. 附录

### 10.1 术语表

| 术语 | 说明 |
|------|------|
| gPTP | generalized Precision Time Protocol，通用精确时间协议 |
| TSN | Time-Sensitive Networking，时间敏感网络 |
| PTP | Precision Time Protocol，IEEE 1588精确时间协议 |
| BMCA | Best Master Clock Algorithm，最佳主时钟算法 |
| Grand Master | gPTP网络的主时钟节点 |
| TCXO | Temperature Compensated Xtal Oscillator，温度补偿晶振 |

### 10.2 供应商清单

| 组件 | 供应商 | 型号 |
|------|--------|------|
| TSN交换机 | NXP | SJA1110 |
| PHY | NXP | TJA1103 |
| GPS模块 | u-blox | ZED-F9T |
| MCU | Infineon | TC397TP |

---

*整车时间同步方案设计*  
*关键词: gPTP, 802.1AS, TSN, AUTOSAR, 时间同步, 车载以太网*
