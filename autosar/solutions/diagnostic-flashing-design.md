# 车载诊断刷写（Flashing）系统设计方案

> **文档版本**: v1.0  
> **编制日期**: 2026-03-08  
> **方案类型**: 诊断刷写与程序更新  
> **技术领域**: UDS / DoIP / Bootloader / AUTOSAR

---

## 1. 项目概述

### 1.1 设计目标

设计一套完整的车载ECU诊断刷写系统，支持：
- **UDS on CAN**: 传统CAN总线诊断刷写
- **DoIP (Diagnostic over IP)**: 以太网高速诊断刷写
- **Bootloader**: 安全可靠的引导程序
- **安全刷写**: 加密、签名、防回滚机制

### 1.2 性能指标

| 指标 | CAN刷写 | DoIP刷写 | 说明 |
|------|---------|----------|------|
| 传输速率 | 500kbps | 100Mbps | 物理层速率 |
| 实际吞吐 | ~40KB/s | ~5MB/s | 有效数据速率 |
| 1MB固件刷写 | ~25s | ~0.2s | 理论最短时间 |
| 支持文件大小 | 最大32MB | 最大1GB | 单文件限制 |
| 安全等级 | CMAC/HMAC |  TLS + CMAC | 安全认证 |

---

## 2. 系统架构设计

### 2.1 整体系统架构

```mermaid
graph TB
    subgraph 外部工具["🔧 诊断工具链"]
        DIAG_TOOL["诊断仪<br/>(Vector CANoe/)<br/>DoIP Tester)"]
        ODX["ODX数据库<br/>(诊断描述文件)"]
        HEX["HEX/S19文件<br/>(待刷写固件)"]
        SEC_KEY["安全密钥<br/>(HSM/Token)"]
    end

    subgraph 车辆接口["🚗 车辆接口"]
        OBD["OBD-II接口<br/>16针连接器"]
        ETHERNET["以太网接口<br/>1000BASE-T1"]
        WIRELESS["无线接口<br/>WiFi/4G/5G"]
    end

    subgraph 网关["🌐 车载网关"]
        GW["中央网关<br/>DoIP路由<br/>UDS转发"]
    end

    subgraph 目标ECU["🎯 目标ECU"]
        BL["Bootloader<br/>启动管理"]
        
        subgraph 应用区["应用固件区"]
            APP1["Bank A<br/>当前运行"]
            APP2["Bank B<br/>备份/更新"]
        end
        
        subgraph 安全模块["安全模块"]
            HSM["HSM安全芯片<br/>密钥存储"]
            SEC_BOOT["安全启动<br/>签名验证"]
        end
    end

    DIAG_TOOL --> HEX
    DIAG_TOOL --> ODX
    DIAG_TOOL --> SEC_KEY
    
    DIAG_TOOL --> OBD
    DIAG_TOOL --> ETHERNET
    DIAG_TOOL --> WIRELESS
    
    OBD --> GW
    ETHERNET --> GW
    WIRELESS --> GW
    
    GW --> BL
    BL --> APP1
    BL --> APP2
    BL --> HSM
    HSM --> SEC_BOOT
    SEC_BOOT --> APP1

    style DIAG_TOOL fill:#4dabf7,color:#fff
    style GW fill:#ff6b6b,color:#fff
    style BL fill:#69db7c
```

### 2.2 Bootloader软件架构

```mermaid
graph TB
    subgraph Bootloader分层["📦 Bootloader 软件架构"]
        
        subgraph 应用层["应用层 (Boot Services)"]
            DIAG["诊断服务<br/>UDS 0x10-0x3E"]
            FLASH["刷写服务<br/>0x34/0x36/0x37"]
            SEC["安全服务<br/>0x27/0x29/0x31"]
            MEM["内存管理<br/>擦除/写入/校验"]
        end

        subgraph 协议层["协议层 (Communication)"]
            TP["传输层<br/>ISO-TP (CAN)<br/>DoIP (以太网)"]
            PDUR["PDU路由<br/>协议分发"]
            COM["通信管理<br/>CAN/ETH驱动"]
        end

        subgraph 硬件抽象层["硬件抽象层 (HAL)"]
            FLASH_DRV["Flash驱动<br/>擦写操作"]
            CAN_DRV["CAN驱动"]
            ETH_DRV["ETH驱动"]
            CRYPTO["加密驱动<br/>HSM接口"]
            WDG_DRV["看门狗驱动"]
        end

        subgraph 启动管理["启动管理 (Startup)"]
            RESET["复位处理"]
            CHECK{"有效App?"}
            JUMP_APP["跳转到应用"]
            STAY_BL["留在Bootloader"]
        end
    end

    DIAG --> TP
    FLASH --> MEM
    SEC --> CRYPTO
    MEM --> FLASH_DRV
    
    TP --> PDUR
    PDUR --> COM
    COM --> CAN_DRV
    COM --> ETH_DRV
    
    RESET --> CHECK
    CHECK -->|是| SEC_BOOT["安全启动验证"]
    CHECK -->|否| STAY_BL
    SEC_BOOT -->|通过| JUMP_APP
    SEC_BOOT -->|失败| STAY_BL
    STAY_BL --> DIAG

    style Bootloader分层 fill:#f8f9fa
    style JUMP_APP fill:#69db7c
    style STAY_BL fill:#ffd43b
```

### 2.3 双Bank刷写机制

```
┌─────────────────────────────────────────────────────────────────┐
│                    Flash内存布局 (双Bank设计)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │      Bank A         │    │      Bank B         │            │
│  │   (当前运行区)       │    │   (备份/更新区)      │            │
│  ├─────────────────────┤    ├─────────────────────┤            │
│  │                     │    │                     │            │
│  │   应用固件 (App)     │    │   应用固件 (App)     │            │
│  │   0xA000_0000       │    │   0xB000_0000       │            │
│  │   大小: 2MB         │    │   大小: 2MB         │            │
│  │   版本: v2.1 (当前)  │    │   版本: v2.2 (新)    │            │
│  │                     │    │                     │            │
│  └─────────────────────┘    └─────────────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Bootloader区域 (固定)                       │   │
│  │              0x8000_0000 - 0x8002_0000                  │   │
│  │              大小: 128KB                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              配置/标定区域 (Data Flash)                  │   │
│  │              0x800F_0000 - 0x8010_0000                  │   │
│  │              大小: 64KB                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  刷写流程:                                                       │
│  1. 新固件写入 Bank B                                           │
│  2. 验证 Bank B 完整性和签名                                     │
│  3. 切换启动标志到 Bank B                                        │
│  4. 复位，从 Bank B 启动                                         │
│  5. 验证成功 → Bank A 作为备份                                   │
│     验证失败 → 回滚到 Bank A                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. UDS诊断服务设计

### 3.1 刷写流程状态机

```mermaid
stateDiagram-v2
    [*] --> IDLE: 默认状态
    
    IDLE: 默认会话
    IDLE --> EXTENDED: 10 03<br/>进入扩展会话
    
    EXTENDED: 扩展会话
    EXTENDED --> UNLOCKED: 27 01/02<br/>解锁安全访问
    EXTENDED --> IDLE: S3超时<br/>或10 01
    
    UNLOCKED: 安全解锁
    UNLOCKED --> DOWNLOADING: 34 00...<br/>请求下载
    UNLOCKED --> EXTENDED: 安全锁定
    
    DOWNLOADING: 下载中
    DOWNLOADING --> DOWNLOADING: 36 ...<br/>传输数据块
    DOWNLOADING --> VERIFYING: 37<br/>退出传输
    DOWNLOADING --> UNLOCKED: 31 01...<br/>擦除内存
    
    VERIFYING: 验证中
    VERIFYING --> COMPLETED: 31 01...<br/>完整性检查通过
    VERIFYING --> ERROR: 校验失败
    
    COMPLETED: 刷写完成
    COMPLETED --> IDLE: 11 01<br/>ECU复位
    COMPLETED --> UNLOCKED: 继续刷写<br/>其他Bank
    
    ERROR: 错误状态
    ERROR --> UNLOCKED: 重试
    ERROR --> IDLE: 31 02...<br/>回滚操作
    ERROR --> [*]: 严重错误<br/>停止刷写

    style UNLOCKED fill:#4dabf7,color:#fff
    style DOWNLOADING fill:#ffd43b
    style COMPLETED fill:#69db7c
    style ERROR fill:#ff6b6b,color:#fff
```

### 3.2 UDS服务流程

```mermaid
flowchart TD
    Start([开始刷写]) --> S1[10 03<br/>进入扩展会话]
    
    S1 --> S2[10 02<br/>进入编程会话]
    S2 --> S3{安全访问<br/>已解锁?}
    
    S3 -->|否| S4[27 01<br/>请求种子]
    S4 --> S5[27 02<br/>发送密钥]
    S5 --> S3
    
    S3 -->|是| S6[31 01...<br/>例行程序控制<br/>擦除内存]
    
    S6 --> S7[34 00...<br/>请求下载<br/>指定地址/大小]
    
    S7 --> S8{数据传输}
    S8 -->|更多数据| S9[36 01...<br/>传输数据块]
    S9 --> S8
    
    S8 -->|传输完成| S10[37<br/>退出传输]
    
    S10 --> S11[31 01...<br/>完整性检查<br/>CRC/签名验证]
    
    S11 --> S12{验证结果}
    S12 -->|通过| S13[31 01...<br/>标记新固件有效]
    S12 -->|失败| S14[31 02...<br/>回滚/标记无效]
    
    S13 --> S15[11 01<br/>ECU硬件复位]
    S14 --> S16[通知错误]
    
    S15 --> S17[从Bank B启动]
    S17 --> S18{启动成功?}
    
    S18 -->|是| S19[刷写成功 ✅]
    S18 -->|否| S20[自动回滚到Bank A]
    
    S19 --> End([结束])
    S20 --> S16
    S16 --> End

    style S1 fill:#e3f2fd
    style S4 fill:#fff3e0
    style S9 fill:#ffd43b
    style S13 fill:#69db7c
    style S14 fill:#ff6b6b,color:#fff
    style S19 fill:#69db7c
```

---

## 4. 交互时序设计

### 4.1 CAN总线刷写时序

```mermaid
sequenceDiagram
    participant Tester as 诊断仪
    participant GW as 网关
    participant ECU as 目标ECU<br/>Bootloader
    participant Flash as Flash内存

    Note over Tester,Flash: UDS on CAN 刷写流程

    rect rgb(255, 235, 238)
        Note over Tester,Flash: 步骤1: 会话控制
        Tester->>GW: CAN ID 0x7E0<br/>10 03 (扩展会话)
        GW->>ECU: 路由转发
        ECU-->>GW: 50 03 (积极响应)
        GW-->>Tester: CAN ID 0x7E8
    end

    rect rgb(227, 242, 253)
        Note over Tester,Flash: 步骤2: 安全解锁
        Tester->>ECU: 27 01 (请求种子)
        ECU-->>Tester: 67 01 01 02 03 04 (种子)
        Tester->>Tester: 计算密钥 (Seed2Key)
        Tester->>ECU: 27 02 AA BB CC DD (发送密钥)
        ECU-->>Tester: 67 02 (解锁成功)
    end

    rect rgb(232, 245, 233)
        Note over Tester,Flash: 步骤3: 擦除内存
        Tester->>ECU: 31 01 FF 00 00<br/>(擦除例程)
        ECU->>Flash: 执行擦除 (2-5s)
        Note over ECU,Flash: 擦除中发送<br/>78 01 (响应挂起)
        ECU-->>Tester: 71 01 FF 00 00<br/>(擦除完成)
    end

    rect rgb(255, 249, 230)
        Note over Tester,Flash: 步骤4: 数据传输
        Tester->>ECU: 34 00 44<br/>A0 00 00 00 00 10 00 00<br/>(请求下载: 地址+大小)
        ECU-->>Tester: 74 00 41 00 00 FF<br/>(最大块大小: 255字节)
        
        loop 数据传输 (每块255字节)
            Tester->>ECU: 36 01 [数据块1]
            ECU->>Flash: 写入Flash
            ECU-->>Tester: 76 01
            
            Tester->>ECU: 36 02 [数据块2]
            ECU-->>Tester: 76 02
            Note over Tester,ECU: ... 重复直到全部数据
        end
        
        Tester->>ECU: 37 (退出传输)
        ECU-->>Tester: 77
    end

    rect rgb(243, 229, 245)
        Note over Tester,Flash: 步骤5: 完整性检查
        Tester->>ECU: 31 01 FF 01 02<br/>(CRC32校验)
        ECU->>Flash: 读取并计算CRC
        ECU-->>Tester: 71 01 FF 01 02<br/>(校验通过)
    end

    rect rgb(255, 235, 238)
        Note over Tester,Flash: 步骤6: ECU复位
        Tester->>ECU: 11 01 (硬件复位)
        ECU-->>Tester: 51 01
        Note over ECU: 复位后从<br/>新固件启动
    end
```

### 4.2 DoIP高速刷写时序

```mermaid
sequenceDiagram
    participant PC as 诊断PC
    participant VCI as VCI接口<br/>(Ethernet)
    participant GW as DoIP网关
    participant ECU as 目标ECU

    Note over PC,ECU: DoIP (Diagnostic over IP) 高速刷写

    rect rgb(255, 235, 238)
        Note over PC,ECU: TCP连接建立
        PC->>VCI: TCP连接请求<br/>端口 13400
        VCI->>GW: DoIP路由激活<br/>激活类型: 0x00 (默认)
        GW-->>VCI: 路由激活响应<br/>0x10 (激活成功)
        VCI-->>PC: TCP已连接
    end

    rect rgb(227, 242, 253)
        Note over PC,ECU: 车辆发现与认证
        PC->>VCI: DoIP Vehicle Identification
        VCI->>GW: UDP广播<br/>端口 13400
        GW-->>VCI: VIN/EID/GID
        VCI-->>PC: 车辆信息
        
        PC->>VCI: TLS握手 (如需要)
        VCI->>GW: 安全通道建立
    end

    rect rgb(232, 245, 233)
        Note over PC,ECU: UDS over DoIP
        PC->>VCI: DoIP Header + UDS<br/>0x8001 (诊断消息)
        VCI->>GW: 以太网帧转发
        GW->>ECU: CAN/ETH转换

        Note over PC,ECU: 10 03 (扩展会话)
        PC->>ECU: DoIP: 10 03
        ECU-->>PC: DoIP: 50 03

        Note over PC,ECU: 27 01/02 (安全解锁)
        PC->>ECU: DoIP: 27 01
        ECU-->>PC: DoIP: 67 01 [种子]
        PC->>ECU: DoIP: 27 02 [密钥]
        ECU-->>PC: DoIP: 67 02
    end

    rect rgb(255, 249, 230)
        Note over PC,ECU: 高速数据传输
        PC->>ECU: DoIP: 34 00 ...<br/>(请求下载 1MB)
        ECU-->>PC: DoIP: 74 00 41 00 10 00<br/>(最大块: 4KB)
        
        loop 批量传输 (4KB/包)
            PC->>ECU: DoIP: 36 01 [4096字节]
            Note over PC,ECU: ~0.4ms/包 @100M
            ECU-->>PC: DoIP: 76 01
        end
        
        PC->>ECU: DoIP: 37
        ECU-->>PC: DoIP: 77
    end

    rect rgb(243, 229, 245)
        Note over PC,ECU: 完成与断开
        PC->>ECU: DoIP: 31 01 ... (校验)
        ECU-->>PC: DoIP: 71 01 ...
        
        PC->>ECU: DoIP: 11 01 (复位)
        ECU-->>PC: DoIP: 51 01
        
        PC->>VCI: TCP断开连接
        VCI->>GW: DoIP 路由释放
    end

    Note over PC,ECU: 总刷写时间: ~2-3s (1MB固件)
```

### 4.3 Bootloader启动流程（静态时序）

```mermaid
flowchart LR
    subgraph 启动时序["⏱️ Bootloader 启动时序"]
        direction TB
        
        T0["T=0ms<br/>复位向量"]
        T1["T=5ms<br/>初始化<br/>时钟/内存"]
        T2["T=10ms<br/>外设初始化<br/>CAN/ETH"]
        T3["T=15ms<br/>检查<br/>启动标志"]
        
        subgraph 分支判断["启动决策"]
            T4A["T=20ms<br/>App有效?"]
            T4B["T=20ms<br/>刷写请求?"]
        end
        
        T5A["T=25ms<br/>安全验证"]
        T6A["T=35ms<br/>跳转App"]
        T5B["T=25ms<br/>启动诊断服务"]
    end

    T0 --> T1 --> T2 --> T3
    T3 --> T4A
    T3 --> T4B
    
    T4A -->|是| T5A -->|通过| T6A
    T4A -->|否| T5B
    T4B -->|是| T5B
    T4B -->|否| T5A

    style T6A fill:#69db7c
    style T5B fill:#ffd43b
```

**详细时序表**:

| 阶段 | 时间 | 操作 | 说明 |
|------|------|------|------|
| 复位向量 | 0-5ms | 从Reset Vector启动 | 硬件复位后自动执行 |
| 基础初始化 | 5-10ms | 时钟、PLL、内存 | 配置系统时钟到最高频率 |
| 外设初始化 | 10-15ms | CAN/ETH/GPIO | 初始化诊断通信接口 |
| 启动检查 | 15-20ms | 读取启动标志 | 从Data Flash读取配置 |
| 安全验证 | 20-35ms | CRC/签名验证 | 验证应用固件完整性 |
| 跳转App | 35ms+ | 跳转到应用入口 | 0xA000_0000或0xB000_0000 |
| 启动诊断 | 20ms+ | 等待诊断连接 | 留在Bootloader模式 |

---

## 5. 安全刷写机制

### 5.1 安全验证流程

```mermaid
flowchart TB
    subgraph 刷写前["📥 刷写前验证"]
        PKG["固件包"]
        META["元数据<br/>版本/日期/依赖"]
        SIG["数字签名<br/>RSA/ECDSA"]
        CRC["CRC32<br/>完整性"]
    end

    subgraph 验证["🔐 验证过程"]
        V1{版本检查}
        V2{签名验证}
        V3{CRC校验}
        V4{依赖检查}
    end

    subgraph 刷写["💾 刷写过程"]
        WRITE["写入Flash"]
        VERIFY["回读验证"]
    end

    subgraph 刷写后["✅ 刷写后确认"]
        ACTIVATE["激活新固件"]
        ROLLBACK["回滚机制"]
    end

    PKG --> META
    PKG --> SIG
    PKG --> CRC
    
    META --> V1
    SIG --> V2
    CRC --> V3
    META --> V4
    
    V1 -->|通过| V2
    V1 -->|失败| ERR1[错误: 版本过低]
    V2 -->|通过| V3
    V2 -->|失败| ERR2[错误: 签名无效]
    V3 -->|通过| V4
    V3 -->|失败| ERR3[错误: 数据损坏]
    V4 -->|通过| WRITE
    V4 -->|失败| ERR4[错误: 依赖不满足]
    
    WRITE --> VERIFY
    VERIFY -->|通过| ACTIVATE
    VERIFY -->|失败| ROLLBACK

    style ACTIVATE fill:#69db7c
    style ROLLBACK fill:#ff6b6b,color:#fff
```

### 5.2 加密与签名方案

```
┌─────────────────────────────────────────────────────────────────┐
│                    固件安全保护方案                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 固件加密 (Confidentiality)                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  明文固件                                               │   │
│  │     ↓                                                   │   │
│  │  AES-128-CBC 加密                                       │   │
│  │     ↓                                                   │   │
│  │  密文固件 + IV                                          │   │
│  │     ↓                                                   │   │
│  │  存储/传输                                              │   │
│  │     ↓                                                   │   │
│  │  Bootloader解密 (HSM密钥)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  2. 固件签名 (Integrity & Authenticity)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  固件内容                                               │   │
│  │     ↓                                                   │   │
│  │  SHA-256 哈希                                           │   │
│  │     ↓                                                   │   │
│  │  RSA-2048 签名 (私钥签名)                               │   │
│  │     ↓                                                   │   │
│  │  签名值附加到固件尾部                                   │   │
│  │     ↓                                                   │   │
│  │  Bootloader验证 (公钥验证)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  3. 安全启动链 (Secure Boot Chain)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Bootloader (Root of Trust)                             │   │
│  │     ↓ 验证签名                                          │   │
│  │  应用固件 Bank A/B                                      │   │
│  │     ↓ 验证通过                                          │   │
│  │  启动应用                                               │   │
│  │     ↓ 验证失败                                          │   │
│  │  留在Bootloader/回滚                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 错误处理与回滚

### 6.1 错误处理流程

```mermaid
flowchart TD
    Error{检测到错误}
    
    Error -->|通信错误| E1[7F xx 78<br/>响应挂起]
    Error -->|安全错误| E2[7F xx 31<br/>访问被拒绝]
    Error -->|序列错误| E3[7F xx 24<br/>请求序列错误]
    Error -->|内存错误| E4[7F xx 72<br/>擦写失败]
    Error -->|校验错误| E5[7F xx 31<br/>签名验证失败]
    
    E1 --> Retry1{重试?}
    E2 --> Unlock[重新解锁]
    E3 --> Restart[重启刷写流程]
    E4 --> Rollback[回滚到旧版本]
    E5 --> Abort[终止刷写]
    
    Retry1 -->|是| Continue[继续刷写]
    Retry1 -->|否| Abort
    
    Unlock --> E2_Check{解锁成功?}
    E2_Check -->|是| Continue
    E2_Check -->|否| Abort
    
    Rollback --> BankA[从Bank A启动]
    Abort --> Log[记录错误日志]
    
    style E4 fill:#ff6b6b,color:#fff
    style E5 fill:#ff6b6b,color:#fff
    style Rollback fill:#ffd43b
    style Continue fill:#69db7c
```

---

## 7. 工具链与测试

### 7.1 刷写工具链

```
诊断工具链:
├── 上位机软件
│   ├── Vector CANoe (CAN诊断)
│   ├── Vector CANape (标定/刷写)
│   ├── DoIP Tester (以太网诊断)
│   └── 自研刷写工具 (Python/C#)
│
├── 接口硬件
│   ├── VN1610/VN1630 (CAN接口)
│   ├── VN5650 (以太网接口)
│   ├── VCI (车载通信接口)
│   └── J-Link (调试接口)
│
├── 固件生成
│   ├── 编译器 (Green Hills/HighTec)
│   ├── 签名工具 (openssl)
│   └── 打包工具 (生成.s19/.hex)
│
└── 测试验证
    ├── HIL测试台架
    ├── 实车测试环境
    └── 自动化测试脚本
```

### 7.2 测试用例

| 测试项 | 测试内容 | 通过标准 |
|--------|----------|----------|
| 正常刷写 | 完整UDS流程 | 刷写成功，ECU正常启动 |
| 中断恢复 | 传输中断后重连 | 支持断点续传 |
| 安全验证 | 错误密钥/签名 | 拒绝刷写，记录日志 |
| 回滚测试 | 新固件启动失败 | 自动回滚到旧版本 |
| 并发测试 | 多ECU同时刷写 | 各ECU独立刷写成功 |
| 压力测试 | 连续刷写100次 | 无内存泄漏，功能正常 |

---

## 8. 参考标准

- **ISO 14229**: UDS统一诊断服务
- **ISO 13400**: DoIP诊断通信协议
- **ISO 15765**: CAN诊断传输层 (ISO-TP)
- **AUTOSAR**: Classic Platform DCM/DEM/Flash驱动规范
- **HIS**: 汽车OEM刷写规范

---

*车载诊断刷写系统设计方案*  
*关键词: UDS, DoIP, Bootloader, Flashing, OTA, 安全刷写*