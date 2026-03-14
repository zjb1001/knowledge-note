# AUTOSAR-MCAL--ADC模块详解

**来源**: 汽车电子嵌入式（Tomas Li）  
**原文链接**: https://mp.weixin.qq.com/s?__biz=Mzg2NTYxOTcxMw==&mid=2247485586&idx=1&sn=3a5d29b4fe4fed3399cd7cfe12b4a707

---

## 前言

MCAL处于AUTOSAR架构的最底层，和具体的芯片强绑定，且不同的芯片使用不同的MCAL配置工具，例如英飞凌芯片系列使用EB配置MCAL，瑞萨芯片系列使用Davince配置MCAL。所以，除了AUTOSAR标准定义好的配置项及标准接口外，不同厂商的MCAL还会有独立于MCAL标准之外的配置，所以MCAL的学习最好是结合具体的工具和芯片来学习。**本文为模拟-数字信号转换器Analog-to-digital converter模块详解篇**。

参考文献：
1. Specification of ADC Driver 4.3.1
https://www.autosar.org/nc/document-search/

---

## 1. ADC模块介绍

ADC模块处于AUTOSAR架构下的MCAL部分，ADC模块初始化并控制微控制器的内部模拟数字转换器单元。ADC模块分别提供启动和停止转换的服务，以启用和禁用转换的触发源。此外，它还提供了启用和禁用通知机制的服务，以及查询转换状态和结果的例程。ADC模块在所谓的ADC通道组上工作，它们是由所谓的ADC通道构建的。ADC通道组结合了模拟输入引脚(ADC通道)、所需的ADC电路本身和将结果寄存器转换为可单独控制和通过ADC模块访问的实体。

---

## 2. 关键概念及依赖的模块

### 2.1 关键概念

**ADC HW Unit**: ADC硬件单元，表示一种微控制器输入电子设备，它包括执行"模拟到数字转换"所需的所有部件。简单理解就是，ADC硬件单元是集成在MCU内部的ADC控制器，MCU可以集成多个ADC硬件单元（ADC控制器）。

**ADC Module**：ADC模块，软件概念，ADC基本软件模块也就是ADC驱动程序，也缩写为ADC驱动程序。

**ADC Channel**：ADC通道，表示绑定到一个端口引脚的逻辑ADC实体。多个ADC实体可以映射到同一个端口引脚。实际配置中如果一个Pin映射一个ADC Channel，那么也就是一路外部ADC的数据由一路ADC Channel来获取。

**ADC Channel Group**：连接到同一ADC硬件单元的一组ADC通道（例如，一个采样和保持转换器和一个A/D转换器）。整个组的转换是由一个触发源触发的。简单理解，一个ADC HW Unit上的所有ADC Channel就属于一个ADC Group。

**ADC Result Buffer**：ADC驱动程序的用户必须为每个组提供一个缓冲区。如果选择了流媒体访问模式，该缓冲区可以保存同一组通道的多个样本。如果选择了单一访问模式，则在缓冲区中保留每个组通道的一个样本。

**Software Trigger**：启动一个ADC通道组或连续一系列ADC通道组转换的软件API调用。

**Hardware Trigger**：启动ADC通道组的一次转换的ADC内部触发信号。ADC硬件触发器在ADC硬件内部生成，例如基于ADC计时器或触发器边缘信号。触发器硬件是紧密耦合的或集成在ADC硬件中的。在检测到硬件触发器后，无需使用任何软件即可启动ADC通道组转换。

_注意：如果ADC硬件不支持硬件触发器，则将软件触发器与GPT/ICU驱动程序结合使用，可以实现类似的行为。例如，在GPT计时器通知功能中，可以启动软件触发的ADC通道组转换。_

**Conversion Mode**：
- **One-Shot**: ADC通道组的转换在触发后执行一次，并将结果写入分配的结果缓冲区。触发器可以是软件API调用或硬件事件。
- **Continuous**: ADC通道组的转换在软件API调用（开始）后连续执行，并将结果写入分配的结果缓冲区。转换本身正在自动运行（受硬件/中断控制）。连续转换可以通过软件API调用（停止）来停止。

**Sample Time**：模拟值被采样的时间。

**Conversion Time**：将采样的模拟值转换为数字表示的时间。

**Acquisition Time**：Sample Time + Conversion Time。

### 2.2 ADC依赖的模块

1）**MCU**

微控制器单元驱动器(MCU驱动程序)主要负责初始化和控制芯片的内部时钟源和时钟预调节器。时钟频率可能会影响：
- Trigger frequency
- Conversion time
- Sampling time

2）**PORT**

PORT模块应配置ADC模块使用的端口引脚。必须同时考虑模拟输入引脚和外部触发引脚。

---

## 3. ADC功能示例

ADC用户可能需要的功能列表，以及ADC模块所提供的功能的方式：

### 3.1 ADC Buffer Access Mode示例

#### 3.1.1 配置（Configuration）

示例配置由三个 ADC Group组成。Group G1包含2个通道，Group G2和G3各包含一个通道。对于G1 和G2，Group访问模式 配置为ADC_ACCESS_MODE_STREAMING。G3的Group访问模式为ADC_ACCESS_MODE_SINGLE。ADC 驱动程序将Group 1-3 的转换结果存储在三个应用程序缓冲区中，通过三个配置的 ADC_RESULT_POINTER 访问：G1_ResultPtr、G2_ResultPtr 和 G3_ResultPtr。

#### 3.1.2 初始化（Initialization）

```c
Std_ReturnType Adc_SetupResultBuffer
(Adc_GroupType Group, const Adc_ValueGroupType* DataBufferPtr)
```

用户必须为ADC Group结果提供应用程序结果缓冲区。每组需要一个缓冲区。如果选择了Streaming Access Mode，缓冲区大小取决于组通道数、Group访问模式和Stream采样数。在开始Group转换之前，用户必须使用API函数Adc_SetupResultBuffer初始化Group结果指针，该函数将Group结果指针初始化为指向指定的应用程序结果缓冲区。

#### 3.1.3 Adc_GetStreamLastPointer的使用方法

```c
Adc_StreamNumSampleType Adc_GetStreamLastPointer
(Adc_GroupType Group, Adc_ValueGroupType** PtrToSamplePtr)
```

ADC 驱动程序将G1、G2 和 G3组的转换结果存储在相应的结果缓冲区 G1_ResultBuffer[]、G2_ResultBuffer[] 和 G3_ResultBuffer[]中。ADC驱动程序不支持从ADC API函数直接访问ADC硬件结果寄存器。

用户提供三个指针 G1_SamplePtr、G2_SamplePtr 和 G3_SamplePtr调用Adc_GetStreamLastPointer后会指向ADC申请结果缓冲区。精确的指针G1_SamplePtr在调用Adc_GetStreamLastPointer后指向最近完成的转换回合的最新G1_CH0结果（G1_CH0是G1组定义中的第一个通道）。

#### 3.1.4 Adc_ReadGroup用法

```c
Std_ReturnType Adc_ReadGroup
(Adc_GroupType Group, Adc_ValueGroupType* DataBufferPtr)
```

如果启用了可选的API函数Adc_ReadGroup，则用户必须为所选组提供额外的缓冲区，该缓冲区可以保存一轮组转换的结果。调用Adc_ReadGroup将最新的结果从应用程序结果缓冲区复制到应用程序读取组缓冲区。

---

## 4. ADC转换和交互

以下示例根据组和转换类型指定了信道转换的顺序：

**Example 1**：包含通道[CH0、CH1、CH2、CH3 和 CH4]的通道组配置为连续转换模式。完成每次扫描后，将调用Notification（如果已启用）。然后自动开始新的扫描。

**Example 2**：包含通道[CH0、CH1、CH2、CH3 和 CH4]的通道组配置为One-Shot转换模式。完成扫描后，将调用Notification（如果已启用）。

**Example 3**：包含通道[CH3]的通道组配置为连续转换模式。完成每次扫描后，将调用Notification（如果已启用）。然后自动开始新的扫描。

**Example 4**：包含通道[CH4]的通道组配置为One-Shot转换模式。完成扫描后，将调用Notification（如果已启用）。

---

## 5. ADC状态机

ADC模块具有一个状态机。这些状态是特定于组的，而不是特定于模块的。该图显示了ADC组的所有可能的配置选项。状态转换取决于ADC组的配置。

### 5.1 ADC State Diagram for One-Shot/Continuous Group Conversion Mode

### 5.2 ADC State Diagram for HW/SW Trigger in One-Shot Group Conversion Mode

### 5.3 ADC State Diagram for SW Trigger in Continuous Conversion Mode

### 5.4 ADC State Diagram for One-Shot Conversion Mode, Software Trigger Source, Single Access Mode

### 5.5 ADC State Diagram for One-Shot Conversion, Hardware Trigger Source, Single Access Mode

### 5.6 ADC State Diagram for One-Shot Conversion Mode, Hardware Trigger Source, Linear and Circular Streaming Access Mode

### 5.7 ADC State Diagram for Continuous Conversion Mode, Software Trigger Source, Single Access Mode

---

## 总结

本文详细介绍了AUTOSAR架构下的MCAL_ADC模块，着重需要理解：
1. **ADC Channel**：逻辑ADC实体，绑定到端口引脚
2. **ADC Group**：连接到同一ADC硬件单元的一组ADC通道
3. **ADC Result Buffer**：应用程序提供的缓冲区，存储转换结果
4. **Group Access Mode**：
   - ADC_ACCESS_MODE_STREAMING：流式访问，可存储多个样本
   - ADC_ACCESS_MODE_SINGLE：单一访问，只存储一个样本
5. **Group Conversion Mode**：
   - One-Shot：触发后执行一次转换
   - Continuous：连续执行转换，直到手动停止

实际项目中，需要更具具体项目的需求来配置MCAL_ADC模块，然后设计一个IoHwAb_ADC的模块来封装ADC的具体配置和使用细节，给应用层SWC提供统一的ADC数据访问接口。
