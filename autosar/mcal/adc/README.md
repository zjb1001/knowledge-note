# ADC 模块 - 模数转换

> **学习日期**: 2026-03-03  
> **模块类型**: MCAL模拟输入  
> **难度**: ⭐⭐⭐

---

## 模块定位

ADC Driver是MCAL层的模数转换驱动，负责将模拟电压信号转换为数字量（8/10/12/16 bit）。

---

## 核心概念: Group（通道组）

- 一个Group包含1-N个ADC通道
- 一次触发会按顺序扫描Group内所有通道
- 结果按通道顺序存入缓冲区
- 一个ADC单元同一时刻只能运行一个Group

---

## 关键API

```c
void Adc_Init(const Adc_ConfigType* ConfigPtr);
void Adc_StartGroupConversion(Adc_GroupType Group);      // 启动转换
void Adc_StopGroupConversion(Adc_GroupType Group);       // 停止转换
Std_ReturnType Adc_ReadGroup(Adc_GroupType Group, Adc_ValueGroupType* DataBufferPtr);
Adc_StatusType Adc_GetGroupStatus(Adc_GroupType Group);  // 获取状态
void Adc_EnableHardwareTrigger(Adc_GroupType Group);     // 硬件触发
```

---

## 配置要点

| 参数 | 说明 |
|------|------|
| ADC Unit | ADC0/ADC1... |
| ADC Group | 逻辑分组，需指定所属Unit |
| ADC Channel | 物理通道号 |
| Resolution | 8/10/12/16 bit |
| Conversion Mode | One-Shot / Continuous |
| Trigger Source | SW（软件）/ HW（硬件，如PWM/GPT）|
| Sample Time | 采样保持时间 |

---

## 常见陷阱

1. **Group状态机误用**: BUSY时启动转换会返回E_NOT_OK
2. **缓冲区溢出**: Streaming模式下读取速度跟不上转换速度
3. **硬件触发丢失**: 触发频率>转换时间时部分触发被忽略
4. **通道顺序错位**: 修改配置后需同步更新应用层解析代码
5. **参考电压噪声**: VREF引脚未充分去耦导致转换结果抖动

---

## 模块关系

- **PORT**: ADC通道引脚需配置为`PORT_PIN_MODE_ADC`
- **PWM/GPT**: 可作为ADC的硬件触发源
- **DMA**: 高吞吐场景下DMA搬运ADC结果

---

*整理日期: 2026-03-05*  
*来源: AUTOSAR CP MCAL学习第3期*
