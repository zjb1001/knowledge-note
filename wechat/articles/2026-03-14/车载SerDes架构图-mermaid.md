# 车载 SerDes 技术架构图

## 1. 技术架构对比

```mermaid
flowchart TB
    subgraph Camera["摄像头端"]
        C1[8MP Camera Sensor]
        C2[12MP Camera Sensor]
        C3[16MP Camera Sensor]
    end
    
    subgraph SerDes["SerDes传输层"]
        direction TB
        S1[GMSL2/3<br/>ADI]
        S2[FPD-Link IV<br/>TI]
        S3[A-PHY<br/>MIPI标准]
    end
    
    subgraph SoC["域控制器端"]
        D1[Deserializer]
        D2[Image Signal Processor]
        D3[AI Compute<br/>Orin/Thor]
    end
    
    C1 -->|6Gbps| S1
    C2 -->|12Gbps| S1
    C3 -->|16Gbps| S3
    
    S1 -->|同轴线缆| D1
    S2 -->|同轴线缆| D1
    S3 -->|同轴线缆| D1
    
    D1 --> D2 --> D3
```

## 2. 技术演进时间线

```mermaid
timeline
    title 车载视频传输技术演进
    
    section 过去
        2015-2018 : MIPI CSI-2
                  : 传输距离<30cm
                  : 仅用于后视摄像头
    
    section 现在
        2019-2024 : SerDes时代
                  : GMSL2 (6Gbps)
                  : FPD-Link III (4Gbps)
                  : 支持8MP摄像头
                  : 8-12摄像头系统
    
    section 未来
        2025+ : A-PHY标准
              : 16Gbps带宽
              : 开放生态
              : 多厂商支持
        2026+ : Ethernet架构
              : 中央计算
              : 传感器融合
```

## 3. 技术选型决策树

```mermaid
flowchart TD
    Start([开始选型]) --> Q1{项目时间?}
    
    Q1 -->|2024-2025量产| Q2{带宽需求?}
    Q1 -->|2026+项目| Q3{是否需要开放标准?}
    
    Q2 -->|<=6Gbps| A1[GMSL2]
    Q2 -->|6-8Gbps| A2[GMSL3/<br/>FPD-Link IV]
    Q2 -->|>8Gbps| A3[GMSL3/<br/>A-PHY]
    
    Q3 -->|是| A4[A-PHY]
    Q3 -->|否| Q4{成本敏感?}
    
    Q4 -->|是| A5[FPD-Link]
    Q4 -->|否| A1
    
    A1 --> Result1[ADI生态<br/>带宽高<br/>成本较高]
    A2 --> Result2[平衡选择<br/>根据供应链定]
    A3 --> Result3[高带宽场景<br/>未来兼容]
    A4 --> Result4[开放标准<br/>多供应商<br/>长期最优]
    A5 --> Result5[成本控制<br/>TI生态]
```

## 4. 自动驾驶摄像头系统架构

```mermaid
flowchart LR
    subgraph Front["前视系统"]
        F1[前视主摄<br/>8MP]
        F2[前视广角<br/>3MP]
    end
    
    subgraph Side["侧视系统"]
        S1[左前<br/>2MP]
        S2[右前<br/>2MP]
        S3[左后<br/>2MP]
        S4[右后<br/>2MP]
    end
    
    subgraph Rear["后视系统"]
        R1[后视主摄<br/>3MP]
        R2[后视广角<br/>2MP]
    end
    
    subgraph Interior["舱内系统"]
        I1[DMS<br/>1MP]
        I2[OMS<br/>2MP]
    end
    
    subgraph DCU["域控制器"]
        DES[GMSL Deserializer<br/>MAX96712]
        ISP[ISP处理]
        AI[NPU计算]
    end
    
    F1 -->|GMSL2| DES
    F2 -->|GMSL2| DES
    S1 -->|GMSL2| DES
    S2 -->|GMSL2| DES
    S3 -->|GMSL2| DES
    S4 -->|GMSL2| DES
    R1 -->|GMSL2| DES
    R2 -->|GMSL2| DES
    I1 -->|GMSL2| DES
    I2 -->|GMSL2| DES
    
    DES --> ISP --> AI
```

## 5. SerDes vs A-PHY 生态对比

```mermaid
flowchart TB
    subgraph Private["私有协议生态"]
        direction TB
        P1[GMSL] --> P1_S[Serializer<br/>MAX9295]
        P1 --> P1_D[Deserializer<br/>MAX96712]
        P1 --> P1_C[Camera]
        P1 --> P1_SOC[SoC]
        
        P2[FPD-Link] --> P2_S[Serializer<br/>DS90UB953]
        P2 --> P2_D[Deserializer<br/>DS90UB960]
        P2 --> P2_C[Camera]
        P2 --> P2_SOC[SoC]
        
        P1 -.->|不兼容| P2
    end
    
    subgraph Open["开放标准生态 A-PHY"]
        direction TB
        A1[A-PHY标准] --> A1_S[Serializer<br/>多厂商]
        A1 --> A1_D[Deserializer<br/>多厂商]
        A1 --> A1_C[Camera<br/>标准化]
        A1 --> A1_SOC[SoC<br/>标准化]
        
        A1_S -.->|兼容| A1_D
    end
    
    Private -.->|演进| Open
```

## 6. 带宽需求与SerDes匹配

```mermaid
xychart-beta
    title "摄像头分辨率 vs 带宽需求"
    x-axis [1MP, 2MP, 3MP, 5MP, 8MP, 12MP, 16MP]
    y-axis "带宽(Gbps)" 0 --> 20
    
    line "Raw Data Rate" [1.5, 3, 4.5, 7.5, 12, 18, 24]
    line "GMSL2 Limit" [6, 6, 6, 6, 6, 6, 6]
    line "GMSL3 Limit" [12, 12, 12, 12, 12, 12, 12]
    line "A-PHY Limit" [16, 16, 16, 16, 16, 16, 16]
    
    annotation "GMSL2适合8MP" [4, 6]
    annotation "GMSL3适合12MP" [5, 12]
    annotation "A-PHY适合16MP+" [6, 16]
```

## 7. 技术特点雷达图对比

```mermaid
radar
    title 三大SerDes技术能力对比
    
    axis Bandwidth [0, 4, 8, 12, 16, 20]
    axis Distance [0, 5, 10, 15, 20]
    axis Maturity [0, 2, 4, 6, 8, 10]
    axis Cost [0, 2, 4, 6, 8, 10]
    axis Openness [0, 2, 4, 6, 8, 10]
    
    GMSL: 12, 15, 9, 5, 2
    FPD-Link: 8, 15, 8, 7, 2
    A-PHY: 16, 15, 4, 6, 10
```

## 8. 供应商生态系统

```mermaid
mindmap
  root((车载SerDes<br/>供应商))
    ADI
      GMSL1
      GMSL2
      GMSL3
      优势: 带宽高<br/>生态成熟
      劣势: 私有协议<br/>成本高
    TI
      FPD-Link II
      FPD-Link III
      FPD-Link IV
      优势: 稳定成熟<br/>成本可控
      劣势: 带宽略低<br/>生态封闭
    MIPI联盟
      A-PHY
      优势: 开放标准<br/>16Gbps<br/>多厂商
      劣势: 生态初期<br/>量产经验少
    其他
      Inova APIX
      索尼GVIF
      小众方案
```
