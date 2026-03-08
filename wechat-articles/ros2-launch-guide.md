# ROS 2 Launch File 工程实践指南

> 来源: 微信公众号「机器人技术笔记」
> 原文链接: https://mp.weixin.qq.com/s/EXcnir2MEKpxxskIpHrk1g
> 收录时间: 2026-03-06
> 标签: #ROS2 #Launch #机器人 #工程实践

---

## 1. 为什么必须要 Launch Files？

### 现实问题
当你有10个节点、几十个参数时，手动启动会变得非常复杂：
- 开很多终端，一个个 `ros2 run`
- 手动 `-p`、手动 `--params-file`、手动 remap
- 节点越多，犯错概率越高（名字错了、参数没加载、remap漏了一条）

### Launch File 的意义
> 把"启动系统"这件事，从一堆终端命令，变成一个**可版本管理、可复用、可一键启动**的配置入口。

---

## 2. Launch File 是什么？

> **Launch file = 启动描述文件**：在一个文件里声明要启动哪些节点，并给它们配置参数、重命名、remap、namespace 等。

启动命令：
```bash
ros2 launch <package_name> <launch_file>
```

支持的格式：
- **XML** - 简洁直观（推荐）
- **Python** - 支持逻辑（条件、循环等）
- **YAML** - 较少使用

---

## 3. 工程最佳实践：单独建一个 bringup 包

### 推荐做法
**专门建一个"启动入口包"，名字以 `_bringup` 结尾。**

例如：
```
my_robot/
├── my_robot_bringup/      # 启动包
│   ├── launch/            # 启动文件
│   └── config/            # YAML参数文件
├── my_robot_hardware/     # 硬件驱动
├── my_robot_description/  # 机器人描述
└── ...
```

### 好处
- 启动配置与业务代码解耦
- 依赖清晰：bringup 负责"拉起全系统"
- 迁移、复用、交付都更干净

---

## 4. 最小可用示例

### 4.1 XML 版本（最简洁）

```xml
<launch>
    <node pkg="my_py_pkg" exec="number_publisher"/>
    <node pkg="my_cpp_pkg" exec="number_counter"/>
</launch>
```

### 4.2 Python 版本（支持逻辑）

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='my_py_pkg', executable='number_publisher'),
        Node(package='my_cpp_pkg', executable='number_counter'),
    ])
```

---

## 5. 实战策略：XML 做主，Python 补充

### 推荐做法
- **默认用 XML 写主 launch**（简单、短、结构清晰）
- **需要高级功能时用 Python**
- **把 Python launch include 进 XML**

### XML include Python

```xml
<launch>
  <include file="$(find-pkg-share my_robot_bringup)/launch/number_app.launch.py" />
</launch>
```

---

## 6. Launch File 核心三件套

### 6.1 重命名节点（避免冲突）

```xml
<node pkg="my_py_pkg" exec="number_publisher" name="num_pub1"/>
```

### 6.2 Remap 通信名（topic重映射）

```xml
<node pkg="my_cpp_pkg" exec="number_counter">
  <remap from="/number" to="/my_number"/>
</node>
```

> 💡 调试建议：用 `rqt_graph` 看图，最容易发现"发布订阅不在同一个 topic"的低级错误。

### 6.3 加载参数

**方式一：直接写参数（少量）**
```xml
<node pkg="my_py_pkg" exec="number_publisher" name="num_pub1">
  <param name="number" value="3"/>
  <param name="publish_period" value="1.5"/>
</node>
```

**方式二：YAML参数文件（推荐）**
```xml
<param from="$(find-pkg-share my_robot_bringup)/config/number_params.yaml"/>
```

---

## 7. Namespace：系统隔离神器

### 使用场景
- 启动两台同类型机器人
- 启动两份同构节点（如两套 turtlesim）

### 关键细节
**topic 名前导 `/` 的影响：**

| 代码写法 | 效果 |
|---------|------|
| `number`（无前导`/`）| 随 namespace 变成 `/abc/number` ✅ |
| `/number`（有前导`/`）| 全局名字，namespace 不会影响 ❌ |

> ⚠️ **工程陷阱**：你以为加了 namespace 就隔离了，结果 topic 仍然撞在一起！

---

## 8. 工程目录结构模板

```
my_robot_bringup/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── robot.launch.xml          # 主启动文件
│   ├── sensors.launch.xml        # 传感器启动
│   ├── navigation.launch.py      # 导航（Python逻辑）
│   └── simulation.launch.xml     # 仿真启动
└── config/
    ├── robot_params.yaml         # 机器人参数
    ├── sensors_params.yaml       # 传感器参数
    └── navigation_params.yaml    # 导航参数
```

---

## 9. 完整 XML Launch 示例

```xml
<?xml version="1.0"?>
<launch>
  <!-- 设置全局参数 -->
  <arg name="use_sim_time" default="false"/>
  <param name="/use_sim_time" value="$(var use_sim_time)"/>
  
  <!-- 加载参数文件 -->
  <param from="$(find-pkg-share my_robot_bringup)/config/robot_params.yaml"/>
  
  <!-- 启动硬件节点（带namespace） -->
  <group>
    <push_ros_namespace namespace="robot1"/>
    
    <node pkg="my_hardware" exec="motor_driver" name="left_motor">
      <param name="device_id" value="/dev/ttyUSB0"/>
      <remap from="/cmd_vel" to="/robot1/cmd_vel"/>
    </node>
    
    <node pkg="my_hardware" exec="sensor_node" name="lidar">
      <param from="$(find-pkg-share my_robot_bringup)/config/sensors_params.yaml"/>
    </node>
  </group>
  
  <!-- 启动导航节点 -->
  <include file="$(find-pkg-share my_robot_bringup)/launch/navigation.launch.py"/>
  
</launch>
```

---

## 10. 关键工程结论

### 你需要形成的固定套路：

1. ✅ **建一个 `_bringup` 包** - 专门负责启动
2. ✅ **`launch/` 放启动文件** - XML/Python
3. ✅ **`config/` 放 YAML 参数** - 与代码解耦
4. ✅ **XML 作为主力** - 简洁直观
5. ✅ **Python 只在需要逻辑时出现** - 条件、循环等
6. ✅ **namespace 用于隔离多实例系统**
7. ✅ **全局 topic 用 remap 修补** - 第三方包的坑

### 从"会写节点"到"会搭系统"

掌握 Launch File 后，你就从：
> ❌ "会写 ROS 节点"

升级为：
> ✅ "会搭 ROS 系统"

---

## 参考资源

- ROS 2 Launch 官方文档: https://docs.ros.org/en/rolling/Tutorials/Intermediate/Launch/Creating-Launch-Files.html
- Launch XML 语法: https://design.ros2.org/articles/roslaunch_xml.html
