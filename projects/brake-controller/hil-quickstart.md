# HIL 快速开始指南

**目标**: 30分钟内搭建可运行的HIL测试环境

---

## 环境要求

| 项目 | 要求 |
|------|------|
| OS | Ubuntu 20.04+ / Windows 10+ |
| Python | 3.8+ |
| 硬件 | PC + (可选) NI USB-6001 |
| 内存 | 8GB+ |

---

## 一键安装

```bash
# 进入项目目录
cd /root/.openclaw/workspace/projects/brake-controller

# 运行自动搭建脚本
./scripts/setup-hil.sh
```

**脚本会自动完成**:
- 创建HIL工作目录
- 安装Python依赖
- 创建车辆模型代码
- 创建DAQ接口代码
- 创建测试框架

---

## 手动步骤（如果脚本失败）

### 1. 创建虚拟环境

```bash
mkdir -p hil
cd hil
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install numpy scipy matplotlib

# 如果有NI硬件
pip install nidaqmx
```

### 3. 下载示例代码

```bash
# 车辆模型、I/O接口、测试框架
# 代码在 docs/design/hil-architecture.md 中有详细说明
```

---

## 运行测试

### 模拟模式（无硬件）

```bash
cd hil
source venv/bin/activate
python hil_runner.py
```

**预期输出**:
```
🚗 初始化HIL测试台架...
🎮 运行模式: 模拟
⏱️  启动测试: 5.0秒
  t=0.0s v=100.0km/h slip=0.00
  t=1.0s v=95.2km/h slip=0.02
  ...
✅ 测试完成
💾 数据已保存: data/hil_test_20260314_103000.json
```

### 真实硬件模式

```bash
# 连接NI USB-6001
python hil_runner.py --real
```

---

## 硬件接线

### MVP版本接线图

```
TC3x7 (DUT)                    工控PC + USB-6001
┌──────────┐                  ┌──────────────┐
│          │                  │              │
│ PWM输出  │──────→ DIO0      │ AI0 读取PWM  │
│ (制动阀) │                  │              │
│          │                  │              │
│ 传感器   │←────── AO0       │ AO0 输出电压 │
│ (轮速)   │                  │ (模拟速度)   │
│          │                  │              │
└──────────┘                  └──────────────┘
```

**接线说明**:
1. TC3x7的PWM输出 → USB-6001的AI0
2. USB-6001的AO0 → TC3x7的传感器输入
3. 共地连接

---

## 测试场景

### 运行预定义场景

```bash
python tests/test_scenarios.py
```

### 自定义测试

```python
from hil_runner import HILTestbench

# 创建测试台架
hil = HILTestbench(simulation=True)

# 设置初始条件
hil.vehicle.reset(v0=27.78)  # 100km/h

# 运行测试
hil.run_test(duration=10.0)

# 保存数据
hil.save_data('my_test.json')
```

---

## 数据分析

### 查看测试结果

```python
import json
import matplotlib.pyplot as plt

# 加载数据
with open('data/hil_test_20260314_103000.json') as f:
    data = json.load(f)

# 绘制速度曲线
time = [d['time'] for d in data]
velocity = [d['v'] * 3.6 for d in data]  # 转换为km/h

plt.plot(time, velocity)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (km/h)')
plt.title('Braking Test Result')
plt.grid()
plt.show()
```

---

## 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| DAQ未找到 | 驱动未安装 | 安装NI-DAQmx驱动 |
| 权限不足 | udev规则 | sudo usermod -aG ni $USER |
| 数据全为0 | 接线错误 | 检查信号调理板 |
| 模型发散 | 步长过大 | 减小dt至0.001 |

---

## 下一步

- [ ] 运行第一个测试
- [ ] 查看数据文件
- [ ] 修改车辆参数
- [ ] 添加新的测试场景

---

**完整文档**: [HIL架构设计](./hil-architecture.md)  
**任务追踪**: [HIL任务列表](./hil-tasks.json)
