# 制动系统控制器（BCU）开发设计方案

> **文档版本**: v1.0  
> **编制日期**: 2026-03-08  
> **项目类型**: 汽车电子制动控制单元  
> **安全等级**: ASIL-D  
> **技术栈**: AUTOSAR + MCAL + ISO 26262

---

## 1. 项目概述

### 1.1 项目目标

开发一款符合 ASIL-D 功能安全等级的电子制动控制单元（Brake Control Unit, BCU），实现以下核心功能：
- **防抱死制动系统 (ABS)**
- **电子制动力分配 (EBD)**
- **电子稳定控制 (ESC)**
- **电子驻车制动 (EPB)**
- **自动驻车 (Autohold)**

### 1.2 系统指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 响应时间 | < 200ms | 踏板输入到轮缸压力建立 |
| 控制周期 | 2ms | 主控制循环 |
| 压力精度 | ±0.1bar | 轮缸压力控制精度 |
| 功能安全 | ASIL-D | ISO 26262 最高等级 |
| 工作电压 | 9-16V | 12V车载电源 |
| 工作温度 | -40°C ~ 85°C | 环境温度 |

---

## 2. 系统架构设计

### 2.1 整体架构图

```mermaid
graph TB
    subgraph 外部接口["🚗 车辆接口"]
        PEDAL["制动踏板<br/>位移传感器"]
        WHEEL["4路轮速<br/>传感器"]
        STEER["方向盘<br/>转角"]
        IMU["惯性测量单元<br/>横摆/侧倾"]
    end

    subgraph BCU控制器["⚙️ BCU主控制器"]
        MCU["主控芯片<br/>TC397TP<br/>ASIL-D"]
        
        subgraph 信号采集["📊 信号采集"]
            ADC1["踏板位置<br/>ADC"]
            ADC2["主缸压力<br/>ADC"]
            ICU1["轮速<br/>ICU捕获"]
        end
        
        subgraph 控制执行["🎛️ 控制执行"]
            PWM1["电机控制<br/>PWM"]
            PWM2["阀体驱动<br/>PWM"]
            DIO1["电磁阀<br/>DIO"]
        end
    end

    subgraph 执行机构["🔧 执行机构"]
        MOTOR["无刷电机<br/>+ 泵"]
        VALVE["液压阀体<br/>12路电磁阀"]
        EPB_MOTOR["EPB电机<br/>2路"]
    end

    subgraph 车辆网络["🌐 车辆网络"]
        CAN1["CAN-FD<br/>动力域"]
        CAN2["CAN-FD<br/>底盘域"]
        ETH["以太网<br/>ADAS"]
    end

    subgraph 其他系统["🔗 关联系统"]
        ESP["ESP传感器"]
        EPS["转向系统"]
        VCU["整车控制器"]
        ADAS_ADU["ADAS<br/>AEB请求"]
    end

    PEDAL --> ADC1
    WHEEL --> ICU1
    STEER --> CAN1
    IMU --> CAN1
    
    ADC1 --> MCU
    ADC2 --> MCU
    ICU1 --> MCU
    
    MCU --> PWM1
    MCU --> PWM2
    MCU --> DIO1
    
    PWM1 --> MOTOR
    PWM2 --> VALVE
    DIO1 --> VALVE
    MCU --> EPB_MOTOR
    
    MCU --> CAN1
    MCU --> CAN2
    MCU --> ETH
    
    CAN1 --> ESP
    CAN1 --> EPS
    CAN1 --> VCU
    ETH --> ADAS_ADU

    style MCU fill:#ff6b6b,color:#fff
    style BCU控制器 fill:#f8f9fa
```

### 2.2 硬件架构框图

```
┌─────────────────────────────────────────────────────────────────┐
│                      BCU 硬件架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │   电源管理    │    │         TC397TP (ASIL-D)              │  │
│  │   9-16V输入   │───>│  ┌─────────┐  ┌─────────┐  ┌──────┐  │  │
│  │   多级保护    │    │  │  Core0  │  │  Core1  │  │  PPU │  │  │
│  └──────────────┘    │  │  主控制  │  │  安全监控│  │  外设│  │  │
│                      │  │         │  │         │  │      │  │  │
│  ┌──────────────┐    │  │ 2MB Flash│  │ 安全核  │  │ 640KB│  │  │
│  │   传感器接口  │    │  │ 512KB RAM│  │ 校验    │  │ SRAM │  │  │
│  │  ├─ 踏板位置  │───>│  └─────────┘  └─────────┘  └──────┘  │  │
│  │  ├─ 主缸压力  │    │                                      │  │
│  │  ├─ 轮速×4   │    │  外设:                               │  │
│  │  └─ 温度×2   │    │  • CAN-FD ×4                         │  │
│  └──────────────┘    │  • 100M以太网                          │  │
│                      │  • ADC 12bit ×16                       │  │
│  ┌──────────────┐    │  • PWM ×24                            │  │
│  │   执行器驱动  │    │  • ICU ×8                             │  │
│  │  ├─ 电机驱动  │<──│  • SPI/QSCI ×4                        │  │
│  │  ├─ 阀驱动×12│<──│  • DIO ×100+                          │  │
│  │  └─ EPB驱动×2│<──│                                      │  │
│  └──────────────┘    └──────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   通信接口    │    │   调试接口    │    │   诊断接口    │     │
│  │  CAN-FD ×2   │    │  JTAG/DAP     │    │  UDS on CAN   │     │
│  │  以太网 100M │    │  Trace        │    │  DoIP         │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 软件架构 (AUTOSAR)

```mermaid
graph TB
    subgraph ASW["应用层 (ASW)"]
        direction TB
        ABS["ABS算法<br/>滑移率控制"]
        EBD["EBD分配<br/>前后轴力"]
        ESC["ESC稳定<br/>横摆控制"]
        EPB["EPB控制<br/>驻车管理"]
        HOLD["Autohold<br/>坡道辅助"]
        SAFE["安全监控<br/>ASIL-D"]
    end

    subgraph RTE["运行时环境 (RTE)"]
        PORT["端口接口<br/>Sender/Receiver"]
    end

    subgraph BSW["基础软件 (BSW)"]
        direction TB
        
        subgraph 服务层["服务层"]
            COM["COM<br/>信号路由"]
            DCM["DCM<br/>诊断通信"]
            DEM["DEM<br/>故障管理"]
            NVM["NVM<br/>非易失存储"]
        end
        
        subgraph ECU抽象层["ECU抽象层"]
            IO["IO驱动<br/>ADC/PWM/DIO"]
            COM_DRV["通信驱动<br/>CAN/ETH"]
            MEM_DRV["存储驱动<br/>Flash/EEPROM"]
        end
        
        subgraph 微控制器驱动["微控制器驱动 (MCAL)"]
            ADC_MCAL["ADC Driver"]
            PWM_MCAL["PWM Driver"]
            ICU_MCAL["ICU Driver"]
            CAN_MCAL["CAN Driver"]
            ETH_MCAL["ETH Driver"]
            DIO_MCAL["DIO Driver"]
            GPT_MCAL["GPT Driver"]
            WDG_MCAL["WDG Driver"]
        end
    end

    subgraph 微控制器["微控制器硬件"]
        HW["TC397TP<br/>硬件外设"]
    end

    ABS --> PORT
    EBD --> PORT
    ESC --> PORT
    EPB --> PORT
    HOLD --> PORT
    SAFE --> PORT
    
    PORT --> COM
    PORT --> DCM
    PORT --> DEM
    PORT --> NVM
    PORT --> IO
    
    COM --> COM_DRV
    IO --> ADC_MCAL
    IO --> PWM_MCAL
    IO --> ICU_MCAL
    IO --> DIO_MCAL
    COM_DRV --> CAN_MCAL
    COM_DRV --> ETH_MCAL
    MEM_DRV --> WDG_MCAL
    
    ADC_MCAL --> HW
    PWM_MCAL --> HW
    ICU_MCAL --> HW
    CAN_MCAL --> HW
    ETH_MCAL --> HW
    DIO_MCAL --> HW
    GPT_MCAL --> HW
    WDG_MCAL --> HW

    style ASW fill:#e3f2fd
    style BSW fill:#fff3e0
    style 微控制器 fill:#f3e5f5
```

---

## 3. 控制逻辑设计

### 3.1 主控制流程图

```mermaid
flowchart TD
    Start([系统启动]) --> Init[初始化]
    
    subgraph 初始化阶段["🔧 初始化阶段"]
        Init --> MCAL_Init[MCAL初始化]
        MCAL_Init --> BSW_Init[BSW初始化]
        BSW_Init --> APP_Init[应用层初始化]
        APP_Init --> SelfTest[上电自检]
        SelfTest --> Check{自检通过?}
        Check -->|否| ErrorMode[故障模式]
        Check -->|是| Ready[系统就绪]
    end

    subgraph 主循环["🔄 主控制循环 2ms"]
        Ready --> ReadInput[读取传感器<br/>ADC/ICU/CAN]
        ReadInput --> Estimation[状态估计<br/>滑移率/减速度]
        
        Estimation --> ModeSel{工作模式}
        
        ModeSel -->|正常制动| Normal[常规制动控制]
        ModeSel -->|ABS触发| ABS_CTRL[ABS控制逻辑]
        ModeSel -->|ESC触发| ESC_CTRL[ESC控制逻辑]
        ModeSel -->|EPB触发| EPB_CTRL[EPB控制逻辑]
        
        Normal --> OutputCalc[输出计算]
        ABS_CTRL --> OutputCalc
        ESC_CTRL --> OutputCalc
        EPB_CTRL --> OutputCalc
        
        OutputCalc --> SafetyCheck[安全校验]
        SafetyCheck --> Check2{校验通过?}
        
        Check2 -->|是| Output[输出到执行器]
        Check2 -->|否| SafeMode[安全降级模式]
        
        Output --> Diag[诊断记录]
        SafeMode --> Diag
        
        Diag --> Wait[等待下一周期]
        Wait --> ReadInput
    end

    ErrorMode --> Limphome[跛行回家模式]
    
    style Start fill:#69db7c
    style Ready fill:#4dabf7,color:#fff
    style ErrorMode fill:#ff6b6b,color:#fff
    style SafeMode fill:#ffd43b
```

### 3.2 ABS控制算法流程

```mermaid
flowchart LR
    subgraph 输入["📥 输入信号"]
        VREF["参考车速<br/>Vref"]
        VWHEEL["轮速<br/>Vwheel"]
        SLIP["滑移率<br/>λ"]
    end

    subgraph 判断逻辑["🧮 判断逻辑"]
        CMP1{"λ > 15%?"}
        CMP2{"减速度<br/>阈值?"}
        CMP3{"增压次数<br/>上限?"}
    end

    subgraph 控制策略["🎛️ 控制策略"]
        INC["增压<br/>Increase"]
        HOLD["保压<br/>Hold"]
        DEC["减压<br/>Decrease"]
    end

    subgraph 输出["📤 阀控制"]
        IN_VALVE["进油阀<br/>PWM控制"]
        OUT_VALVE["出油阀<br/>PWM控制"]
        PUMP["回油泵<br/>电机控制"]
    end

    VREF --> SLIP
    VWHEEL --> SLIP
    SLIP --> CMP1
    
    CMP1 -->|是| CMP2
    CMP1 -->|否| INC
    
    CMP2 -->|是| CMP3
    CMP2 -->|否| HOLD
    
    CMP3 -->|是| HOLD
    CMP3 -->|否| DEC
    
    INC --> IN_VALVE
    HOLD --> IN_VALVE
    DEC --> IN_VALVE
    DEC --> OUT_VALVE
    DEC --> PUMP

    style INC fill:#69db7c
    style HOLD fill:#ffd43b
    style DEC fill:#ff6b6b,color:#fff
```

### 3.3 控制状态机

```mermaid
stateDiagram-v2
    [*] --> INIT: 系统启动
    
    INIT --> STANDBY: 初始化完成
    
    STANDBY: 待机状态
    STANDBY --> NORMAL: 踏板踩下<br/>制动请求
    
    NORMAL: 常规制动
    NORMAL --> ABS: 滑移率超标
    NORMAL --> EBD: 前后轴<br/>分配需求
    NORMAL --> STANDBY: 踏板释放
    
    ABS: ABS激活
    ABS --> NORMAL: 工况恢复
    ABS --> ESC: 横摆失控
    
    EBD: EBD分配
    EBD --> NORMAL: 分配完成
    
    ESC: ESC稳定控制
    ESC --> ABS: 仅轮控
    ESC --> NORMAL: 稳定恢复
    
    STANDBY --> EPB: EPB开关<br/>拉取请求
    STANDBY --> AUTOHOLD: 自动驻车<br/>激活
    
    EPB: 电子驻车
    EPB --> STANDBY: 释放完成
    
    AUTOHOLD: 自动驻车
    AUTOHOLD --> NORMAL: 油门踩下
    AUTOHOLD --> STANDBY: 关闭
    
    NORMAL --> FAULT: 检测到故障
    ABS --> FAULT: 检测到故障
    ESC --> FAULT: 检测到故障
    
    FAULT: 故障模式
    FAULT --> LIMPHOME: 跛行回家
    FAULT --> [*]: 严重故障<br/>系统关闭
    
    LIMPHOME: 跛行模式
    LIMPHOME --> STANDBY: 故障恢复
```

---

## 4. 系统交互设计

### 4.1 制动请求处理时序

```mermaid
sequenceDiagram
    participant Driver as 驾驶员
    participant Pedal as 踏板传感器
    participant BCU as BCU控制器
    participant ESC as ESC阀体
    participant Wheel as 制动轮缸

    Note over Driver,Wheel: 正常制动场景

    rect rgb(255, 235, 238)
        Note over Driver,Wheel: T=0ms: 制动请求
        Driver->>Pedal: 踩下踏板
        Pedal-->>BCU: 踏板位移信号<br/>ADC采样 t=2ms
    end

    rect rgb(227, 242, 253)
        Note over Driver,Wheel: T=2-10ms: 控制计算
        BCU->>BCU: 目标减速度计算
        BCU->>BCU: 轮缸目标压力
        BCU->>BCU: 滑移率预估
    end

    rect rgb(232, 245, 233)
        Note over Driver,Wheel: T=10-50ms: 压力建立
        BCU->>ESC: 电机启动指令<br/>PWM控制
        ESC->>ESC: 泵建立压力
        ESC->>Wheel: 轮缸压力上升
        Wheel-->>BCU: 压力反馈<br/>t=50ms
    end

    rect rgb(255, 249, 230)
        Note over Driver,Wheel: T=50-200ms: 闭环控制
        loop 每2ms周期
            BCU->>BCU: 实际vs目标比较
            BCU->>ESC: 阀调节
            ESC->>Wheel: 压力微调
        end
    end

    Note over Driver,Wheel: 总响应时间: 200ms
```

### 4.2 ABS触发交互时序

```mermaid
sequenceDiagram
    participant Wheel as 轮速传感器
    participant BCU as BCU主核
    participant Safe as 安全监控核
    participant Valve as 液压阀体

    Note over Wheel,Valve: ABS紧急制动场景

    rect rgb(255, 235, 238)
        Note over Wheel,Valve: T=0ms: 滑移率检测
        Wheel-->>BCU: 轮速脉冲<br/>ICU捕获
        BCU->>BCU: 计算滑移率 λ=18%
        Note right of BCU: 超过阈值15%
    end

    rect rgb(227, 242, 253)
        Note over Wheel,Valve: T=2ms: ABS决策
        BCU->>Safe: 请求ABS激活
        Safe->>Safe: 安全校验
        Safe-->>BCU: 允许激活
    end

    rect rgb(232, 245, 233)
        Note over Wheel,Valve: T=4ms: 减压阶段
        BCU->>Valve: 进油阀关闭<br/>出油阀打开
        Valve->>Valve: 轮缸减压
        Note over Wheel,Valve: 滑移率下降
    end

    rect rgb(255, 249, 230)
        Note over Wheel,Valve: T=20ms: 保压阶段
        BCU->>Valve: 进出油阀关闭
        Wheel-->>BCU: 轮速恢复
    end

    rect rgb(243, 229, 245)
        Note over Wheel,Valve: T=40ms: 增压阶段
        BCU->>Valve: 进油阀打开
        Valve->>Valve: 轮缸增压
    end

    Note over Wheel,Valve: ABS周期: 60-120ms
```

### 4.3 ADAS AEB请求交互

```mermaid
sequenceDiagram
    participant ADAS as ADAS控制器
    participant ETH as 以太网
    participant BCU as BCU主核
    participant SAFE as 安全核
    participant ESC as ESC执行

    Note over ADAS,ESC: AEB自动紧急制动

    rect rgb(255, 235, 238)
        Note over ADAS,ESC: T=0ms: AEB触发
        ADAS->>ETH: AEB请求<br/>减速度 0.8g<br/>时间戳 t0
        ETH-->>BCU: 以太网接收
    end

    rect rgb(227, 242, 253)
        Note over ADAS,ESC: T=5ms: 请求验证
        BCU->>BCU: 解析AEB报文
        BCU->>SAFE: 安全校验<br/>时间戳有效性
        BCU->>BCU: 驾驶员意图仲裁
    end

    rect rgb(232, 245, 233)
        Note over ADAS,ESC: T=10ms: 执行制动
        BCU->>ESC: 全制动指令<br/>目标压力 180bar
        ESC->>ESC: 电机全速<br/>阀体调节
    end

    rect rgb(255, 249, 230)
        Note over ADAS,ESC: T=10-200ms: 压力建立
        loop 每2ms反馈
            ESC-->>BCU: 实际压力
            BCU->>ESC: 调节指令
        end
    end

    BCU-->>ETH: 执行确认<br/>时间戳 t1
    ETH-->>ADAS: 状态反馈

    Note over ADAS,ESC: 端到端延迟: < 10ms
```

---

## 5. 功能安全设计

### 5.1 安全监控架构

```mermaid
graph TB
    subgraph 主控制核["主控制核 (Core0)"]
        APP["应用算法<br/>ASIL-B"]
        CTRL["控制逻辑<br/>ASIL-B"]
    end

    subgraph 安全监控核["安全监控核 (Core1)"]
        SAFE["安全监控<br/>ASIL-D"]
        CHECK["合理性检查"]
        VOTER["多数表决器"]
    end

    subgraph 冗余通道["冗余设计"]
        ADC_R["ADC冗余通道"]
        PWM_R["PWM回读检查"]
        CAN_R["CAN冗余总线"]
    end

    APP --> CTRL
    CTRL --> SAFE
    
    SAFE --> CHECK
    CHECK --> VOTER
    
    ADC_R --> VOTER
    PWM_R --> CHECK
    CAN_R --> SAFE
    
    SAFE -->|故障| SAFE_ACT[安全动作]
    SAFE_ACT --> WDG[看门狗复位]
    SAFE_ACT --> LIMP[跛行模式]
    SAFE_ACT --> WARN[故障警告]

    style 安全监控核 fill:#ff6b6b,color:#fff
    style SAFE_ACT fill:#ffd43b
```

### 5.2 E2E保护流程

```mermaid
flowchart LR
    subgraph 发送端["📤 发送端"]
        Data1["原始数据"]
        CRC["计算CRC"]
        Seq["序列计数器"]
        E2E_Pack["E2E打包"]
    end

    subgraph 传输["🌐 传输"]
        CAN["CAN-FD总线"]
    end

    subgraph 接收端["📥 接收端"]
        E2E_Unpack["E2E解包"]
        CRC_Check["CRC校验"]
        Seq_Check["序列检查"]
        Alive_Check["存活计数"]
        Data2["有效数据"]
    end

    Data1 --> CRC
    CRC --> Seq
    Seq --> E2E_Pack
    E2E_Pack --> CAN
    CAN --> E2E_Unpack
    E2E_Unpack --> CRC_Check
    CRC_Check --> Seq_Check
    Seq_Check --> Alive_Check
    Alive_Check -->|通过| Data2
    Alive_Check -->|失败| Error["错误处理"]

    style Data2 fill:#69db7c
    style Error fill:#ff6b6b,color:#fff
```

---

## 6. 项目开发计划

### 6.1 开发甘特图

```mermaid
gantt
    title BCU制动控制器开发项目计划
    dateFormat  YYYY-MM-DD
    
    section 阶段1: 需求与设计
    需求分析              :a1, 2024-01-01, 14d
    系统架构设计          :a2, after a1, 14d
    硬件方案设计          :a3, after a2, 14d
    软件架构设计          :a4, after a2, 14d
    安全概念设计          :a5, after a3, 14d
    设计评审              :milestone, after a5, 0d
    
    section 阶段2: 硬件开发
    原理图设计            :b1, after a5, 21d
    PCB Layout            :b2, after b1, 21d
    PCB制板               :b3, after b2, 14d
    样板焊接              :b4, after b3, 7d
    硬件测试              :b5, after b4, 21d
    硬件评审              :milestone, after b5, 0d
    
    section 阶段3: 基础软件开发
    MCAL配置              :c1, after a5, 21d
    BSW集成               :c2, after c1, 28d
    诊断功能              :c3, after c2, 14d
    通信栈                :c4, after c2, 14d
    存储管理              :c5, after c2, 14d
    BSW测试               :c6, after c5, 14d
    
    section 阶段4: 应用算法开发
    踏板解析              :d1, after c6, 14d
    轮速处理              :d2, after c6, 14d
    ABS算法               :d3, after d2, 28d
    EBD算法               :d4, after d3, 14d
    ESC算法               :d5, after d4, 28d
    EPB算法               :d6, after d4, 21d
    Autohold算法          :d7, after d6, 14d
    
    section 阶段5: 功能安全
    安全监控              :e1, after c6, 28d
    E2E保护               :e2, after c6, 21d
    FTA分析               :e3, after d7, 14d
    FMEA分析              :e4, after e3, 14d
    安全测试              :e5, after e4, 21d
    
    section 阶段6: 集成测试
    HIL测试               :f1, after e5, 28d
    台架测试              :f2, after f1, 21d
    实车测试              :f3, after f2, 42d
    冬季测试              :f4, after f3, 14d
    夏季测试              :f5, after f4, 14d
    
    section 阶段7: 量产准备
    产线导入              :g1, after f5, 21d
    PPAP提交              :g2, after g1, 14d
    量产评审              :milestone, after g2, 0d
```

### 6.2 开发阶段详情

| 阶段 | 周期 | 关键交付物 | 里程碑 |
|------|------|------------|--------|
| **需求与设计** | 10周 | 需求规格书、系统架构设计、安全概念 | 设计冻结 |
| **硬件开发** | 12周 | 原理图、PCB、BOM、测试报告 | 硬件冻结 |
| **基础软件** | 12周 | MCAL配置、BSW集成、通信栈 | BSW就绪 |
| **应用算法** | 14周 | ABS/EBD/ESC/EPB算法、仿真报告 | 算法冻结 |
| **功能安全** | 12周 | FTA/FMEA报告、安全测试用例 | 安全认可 |
| **集成测试** | 16周 | HIL报告、台架报告、实车报告 | 测试通过 |
| **量产准备** | 6周 | 产线测试方案、PPAP文档 | 量产就绪 |

**总计**: 约 **18个月** 开发周期

### 6.3 资源分配

```
团队配置 (20人):
├── 系统工程师    ×2
├── 硬件工程师    ×3
├── 底层软件工程师 ×3
├── 应用算法工程师 ×4
├── 功能安全工程师 ×2
├── 测试工程师    ×4
└── 项目经理     ×1

工具链:
├── IDE: EB tresos / DaVinci
├── HIL: dSPACE / Vector
├── 仿真: CarMaker / MATLAB
├── 诊断: CANoe / CANape
└── 版本: Git / Jenkins
```

---

## 7. 风险评估与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| ASIL-D认证不通过 | 中 | 高 | 早期介入TÜV评审，严格遵循ISO 26262 |
| 液压阀体噪声 | 中 | 中 | PWM频率优化，阻尼设计 |
| 电磁干扰 | 中 | 高 | EMC预测试，屏蔽设计 |
| 响应时间不达标 | 低 | 高 | 算法优化，硬件加速 |
| 供应商芯片短缺 | 高 | 中 | 双源策略，备选方案 |

---

## 8. 参考文档

- ISO 26262: 道路车辆功能安全
- ISO 6469: 电动汽车安全要求
- ECE R13-H: 制动系统法规
- AUTOSAR: 经典平台规范
- Infineon TC3xx 用户手册

---

*BCU制动控制器开发设计方案*  
*关键词: BCU, ABS, ESC, EPB, AUTOSAR, ASIL-D, 制动系统*