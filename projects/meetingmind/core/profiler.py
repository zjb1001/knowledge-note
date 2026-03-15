#!/usr/bin/env python3
"""
MeetingMind Performance Profiler - 性能分析 Agent
═══════════════════════════════════════════════════════════════
版本: 1.0.0
功能: 精准定位性能瓶颈，提供优化建议

优化阶梯 (Optimization Ladder):
  1. 算法优化 (Big-O)
  2. 数据结构优化
  3. JIT编译器 (PyPy/GraalPy)
  4. 向量化 (NumPy/Numba)
  5. C扩展 (Cython/C)
  6. 异步/并行
  7. 架构重构

作者: MeetingMind Team
═══════════════════════════════════════════════════════════════
"""

import time
import functools
import tracemalloc
import gc
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class PerformanceMetrics:
    """性能指标数据"""
    component: str
    execution_time_ms: float
    memory_peak_mb: float
    call_count: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'component': self.component,
            'execution_time_ms': round(self.execution_time_ms, 3),
            'memory_peak_mb': round(self.memory_peak_mb, 3),
            'call_count': self.call_count,
            'timestamp': self.timestamp
        }


@dataclass
class Bottleneck:
    """瓶颈分析结果"""
    component: str
    severity: str  # critical/high/medium/low
    time_percentage: float
    current_time_ms: float
    potential_optimization: str
    estimated_speedup: str
    recommendation: str


class PerformanceProfiler:
    """
    性能分析 Agent
    
    功能:
    1. 自动测量各组件执行时间和内存占用
    2. 识别性能瓶颈 (按时间占比排序)
    3. 提供针对性的优化建议
    4. 生成性能分析报告
    
    使用方式:
        profiler = PerformanceProfiler()
        
        # 方式1: 装饰器
        @profiler.profile("ASR模块")
        def asr_process():
            pass
        
        # 方式2: 上下文管理器
        with profiler.measure("Summarizer"):
            generate_minutes()
        
        # 生成报告
        report = profiler.generate_report()
    """
    
    def __init__(self, enable_memory_profiling: bool = True):
        self.metrics: List[PerformanceMetrics] = []
        self.component_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_time': 0.0,
            'total_memory': 0.0,
            'call_count': 0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
        self.enable_memory = enable_memory_profiling
        self._current_measurements: Dict[str, Dict] = {}
    
    def profile(self, component_name: str):
        """装饰器: 自动测量函数性能"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.measure(component_name):
                    result = func(*args, **kwargs)
                return result
            return wrapper
        return decorator
    
    def measure(self, component_name: str):
        """上下文管理器: 测量代码块性能"""
        return self._MeasurementContext(self, component_name)
    
    class _MeasurementContext:
        def __init__(self, profiler: 'PerformanceProfiler', component: str):
            self.profiler = profiler
            self.component = component
            self.start_time = 0
            self.start_memory = 0
        
        def __enter__(self):
            self.start_time = time.perf_counter()
            if self.profiler.enable_memory:
                tracemalloc.start()
            gc.collect()  # 清理垃圾，减少干扰
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = time.perf_counter()
            execution_time = (end_time - self.start_time) * 1000  # ms
            
            memory_peak = 0
            if self.profiler.enable_memory:
                current, peak = tracemalloc.get_traced_memory()
                memory_peak = peak / 1024 / 1024  # MB
                tracemalloc.stop()
            
            metric = PerformanceMetrics(
                component=self.component,
                execution_time_ms=execution_time,
                memory_peak_mb=memory_peak
            )
            self.profiler.metrics.append(metric)
            
            # 更新统计
            stats = self.profiler.component_stats[self.component]
            stats['total_time'] += execution_time
            stats['total_memory'] = max(stats['total_memory'], memory_peak)
            stats['call_count'] += 1
            stats['min_time'] = min(stats['min_time'], execution_time)
            stats['max_time'] = max(stats['max_time'], execution_time)
    
    def identify_bottlenecks(self) -> List[Bottleneck]:
        """识别性能瓶颈"""
        if not self.component_stats:
            return []
        
        # 计算总时间
        total_time = sum(s['total_time'] for s in self.component_stats.values())
        if total_time == 0:
            return []
        
        bottlenecks = []
        
        for component, stats in sorted(
            self.component_stats.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        ):
            time_percentage = (stats['total_time'] / total_time) * 100
            
            # 确定严重级别
            if time_percentage >= 50:
                severity = 'critical'
            elif time_percentage >= 30:
                severity = 'high'
            elif time_percentage >= 10:
                severity = 'medium'
            else:
                severity = 'low'
            
            # 生成优化建议
            optimization, speedup, recommendation = self._generate_optimization_advice(
                component, stats, time_percentage
            )
            
            bottlenecks.append(Bottleneck(
                component=component,
                severity=severity,
                time_percentage=round(time_percentage, 1),
                current_time_ms=round(stats['total_time'], 2),
                potential_optimization=optimization,
                estimated_speedup=speedup,
                recommendation=recommendation
            ))
        
        return bottlenecks
    
    def _generate_optimization_advice(
        self, component: str, stats: Dict, percentage: float
    ) -> tuple:
        """根据组件类型生成优化建议"""
        
        # 根据组件名称推断优化策略
        component_lower = component.lower()
        
        if 'asr' in component_lower or 'recognition' in component_lower:
            return (
                "批量API调用/本地模型",
                "2-10x",
                "考虑使用更快的ASR服务或本地Whisper模型"
            )
        
        if 'summarizer' in component_lower or 'llm' in component_lower:
            return (
                "流式响应/模型缓存",
                "1.5-3x",
                "启用流式输出，实现首字快响；缓存相似请求的响应"
            )
        
        if 'recorder' in component_lower or 'audio' in component_lower:
            return (
                "异步IO/ring buffer",
                "2-5x",
                "使用异步录音，避免阻塞主线程"
            )
        
        if 'json' in component_lower or 'parse' in component_lower:
            return (
                "orjson/ujson替代",
                "2-10x",
                "使用orjson或ujson替代标准库json模块"
            )
        
        if 'loop' in component_lower or 'iterate' in component_lower:
            return (
                "NumPy向量化/Cython",
                "10-100x",
                "将Python循环改写为NumPy向量化操作"
            )
        
        if percentage > 30:
            return (
                "算法优化/并行处理",
                "2-5x",
                "检查算法复杂度，考虑使用多线程/多进程"
            )
        
        return (
            "代码审查/微优化",
            "1.2-2x",
            "检查是否有不必要的计算或内存分配"
        )
    
    def generate_report(self, output_format: str = 'markdown') -> str:
        """生成性能分析报告"""
        bottlenecks = self.identify_bottlenecks()
        
        if output_format == 'json':
            return json.dumps({
                'timestamp': datetime.now().isoformat(),
                'total_components': len(self.component_stats),
                'bottlenecks': [self._bottleneck_to_dict(b) for b in bottlenecks],
                'metrics': [m.to_dict() for m in self.metrics]
            }, ensure_ascii=False, indent=2)
        
        return self._generate_markdown_report(bottlenecks)
    
    def _bottleneck_to_dict(self, b: Bottleneck) -> Dict:
        return {
            'component': b.component,
            'severity': b.severity,
            'time_percentage': b.time_percentage,
            'current_time_ms': b.current_time_ms,
            'potential_optimization': b.potential_optimization,
            'estimated_speedup': b.estimated_speedup,
            'recommendation': b.recommendation
        }
    
    def _generate_markdown_report(self, bottlenecks: List[Bottleneck]) -> str:
        """生成Markdown格式报告"""
        total_time = sum(s['total_time'] for s in self.component_stats.values())
        
        report = f"""# 🚀 Performance Profiler 性能分析报告

## 执行摘要

| 指标 | 数值 |
|------|------|
| **总执行时间** | {total_time:.2f} ms ({total_time/1000:.2f}s) |
| **分析组件数** | {len(self.component_stats)} |
| **瓶颈数量** | {len([b for b in bottlenecks if b.severity in ['critical', 'high']])} (关键/高) |
| **分析时间** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

---

## 性能瓶颈分析

"""
        
        if not bottlenecks:
            report += "✅ 未发现明显性能瓶颈\n\n"
        else:
            # 严重级别颜色
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            for i, b in enumerate(bottlenecks, 1):
                emoji = severity_emoji.get(b.severity, '⚪')
                report += f"### {emoji} #{i} {b.component} ({b.severity.upper()})\n\n"
                report += f"- **时间占比**: {b.time_percentage}%\n"
                report += f"- **当前耗时**: {b.current_time_ms} ms\n"
                report += f"- **潜在优化**: {b.potential_optimization}\n"
                report += f"- **预期加速**: {b.estimated_speedup}\n"
                report += f"- **建议**: {b.recommendation}\n\n"
        
        # 详细统计
        report += """---

## 详细性能统计

| 组件 | 调用次数 | 总时间(ms) | 平均(ms) | 最小(ms) | 最大(ms) |
|------|---------|-----------|---------|---------|---------|
"""
        
        for component, stats in sorted(
            self.component_stats.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        ):
            avg = stats['total_time'] / stats['call_count'] if stats['call_count'] > 0 else 0
            report += f"| {component} | {stats['call_count']} | "
            report += f"{stats['total_time']:.2f} | {avg:.2f} | "
            report += f"{stats['min_time']:.2f} | {stats['max_time']:.2f} |\n"
        
        # 优化建议总结
        report += """

---

## 💡 优化建议优先级

"""
        
        if bottlenecks:
            report += "### 立即处理 (ROI最高)\n\n"
            critical_high = [b for b in bottlenecks if b.severity in ['critical', 'high']]
            if critical_high:
                for b in critical_high[:3]:
                    report += f"1. **{b.component}**: {b.potential_optimization} → 预期{b.estimated_speedup}加速\n"
            else:
                report += "- 无关键瓶颈，系统运行良好\n"
            
            report += "\n### 后续优化\n\n"
            medium_low = [b for b in bottlenecks if b.severity in ['medium', 'low']]
            for b in medium_low[:3]:
                report += f"- **{b.component}**: {b.recommendation}\n"
        
        # 优化阶梯参考
        report += """

---

## 📚 优化阶梯参考 (Optimization Ladder)

根据本文作者的经验，性能优化应遵循以下阶梯：

| 层级 | 方法 | 预期加速 | 成本 | 适用场景 |
|------|------|---------|------|---------|
| 1 | **算法优化** | 10-1000x | 低 | 算法复杂度问题 |
| 2 | **数据结构** | 2-10x | 低 | 不当的数据结构选择 |
| 3 | **JIT编译器** (PyPy/GraalPy) | 6-66x | 极低 | 纯Python计算密集型 |
| 4 | **向量化** (NumPy/Numba/JAX) | 10-1600x | 中 | 数值计算/矩阵运算 |
| 5 | **C扩展** (Cython/C/Rust) | 10-100x | 高 | 核心算法瓶颈 |
| 6 | **异步/并行** | 2-8x | 中 | IO密集型/可并行任务 |
| 7 | **架构重构** | - | 极高 | 系统性问题 |

**核心原则**: 先定位瓶颈，再选择优化策略，避免盲目重写。

---

*报告生成工具: MeetingMind Performance Profiler*
*参考文章: cemrehancavdar.com/optimization-ladder*
"""
        
        return report
    
    def print_summary(self):
        """打印性能摘要到控制台"""
        bottlenecks = self.identify_bottlenecks()
        
        print("\n" + "=" * 70)
        print("🚀 Performance Profiler 摘要")
        print("=" * 70)
        
        if bottlenecks:
            print(f"\n发现 {len(bottlenecks)} 个性能瓶颈:\n")
            for i, b in enumerate(bottlenecks[:5], 1):
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(b.severity, '⚪')
                
                print(f"{severity_color} #{i} {b.component}")
                print(f"   占比: {b.time_percentage}% | 耗时: {b.current_time_ms}ms")
                print(f"   建议: {b.potential_optimization} ({b.estimated_speedup})")
                print()
        else:
            print("\n✅ 未发现明显性能瓶颈")
        
        print("=" * 70)


# 便捷函数
def profile_performance(func: Callable, *args, **kwargs) -> tuple:
    """
    便捷函数：一键分析函数性能
    
    Returns:
        (result, report): 函数返回值和性能报告
    """
    profiler = PerformanceProfiler()
    
    with profiler.measure(func.__name__):
        result = func(*args, **kwargs)
    
    report = profiler.generate_report('markdown')
    return result, report


# 示例用法
if __name__ == '__main__':
    print("🚀 Performance Profiler Agent 测试\n")
    
    profiler = PerformanceProfiler()
    
    # 模拟各组件
    @profiler.profile("ASR模块")
    def mock_asr():
        time.sleep(0.5)  # 模拟API调用
    
    @profiler.profile("Summarizer")
    def mock_summarizer():
        time.sleep(1.2)  # 模拟LLM调用
    
    @profiler.profile("JSON解析")
    def mock_json_parse():
        time.sleep(0.1)
    
    # 执行
    mock_asr()
    mock_summarizer()
    mock_json_parse()
    
    # 生成报告
    print("\n" + profiler.generate_report('markdown'))
