import { renderMermaidSVG, renderMermaidASCII } from './src/index';

/**
 * beautiful-mermaid vs 传统Mermaid - 制动系统时序展示
 * 
 * 对比维度:
 * 1. 渲染速度
 * 2. 视觉效果
 * 3. 主题切换
 * 4. 输出格式
 */

// ============================================
// 制动系统时序图定义
// ============================================

const brakeSequenceDiagram = `
sequenceDiagram
    autonumber
    participant Driver as 👤 驾驶员
    participant Pedal as 🎮 踏板传感器
    participant BCU as 🧠 制动控制单元
    participant ABS as ⚡ ABS模块
    participant Valve as 🔧 液压阀组
    participant Wheel as ⚙️ 轮缸

    rect rgb(30, 60, 90)
        Note over Driver,Wheel: 正常制动流程
        Driver->>Pedal: 踩下制动踏板
        Pedal->>BCU: 踏板位置信号 (10ms)
        BCU->>BCU: 计算制动力需求
        BCU->>Valve: 发送阀控制指令 (2ms)
        Valve->>Wheel: 建立轮缸压力 (20ms)
        Wheel-->>BCU: 压力反馈信号
    end

    rect rgb(90, 30, 30)
        Note over BCU,ABS: 检测到车轮抱死 ⚠️
        BCU->>ABS: 请求ABS干预
        
        loop ABS循环控制 (60-120ms/周期)
            ABS->>Valve: 减压指令
            Valve->>Wheel: 轮缸减压
            Wheel-->>ABS: 滑移率反馈
            ABS->>Valve: 保压指令
            ABS->>Valve: 增压指令
        end
        
        Note over ABS: 循环控制直至稳定 ✓
    end
`;

const brakeStateDiagram = `
stateDiagram-v2
    [*] --> Idle: 系统启动
    
    Idle: 空闲状态
    Idle --> PreCharge: 预增压请求
    
    PreCharge: 预增压
    PreCharge --> NormalBraking: 踏板踩下
    PreCharge --> Idle: 超时取消
    
    NormalBraking: 正常制动
    NormalBraking --> ABSTriggered: 滑移率>20%
    NormalBraking --> Idle: 踏板释放
    
    ABSTriggered: ABS激活
    ABSTriggered --> PressureIncrease: 滑移率<12%
    ABSTriggered --> PressureHold: 12%<滑移率<18%
    ABSTriggered --> PressureDecrease: 滑移率>22%
    
    PressureIncrease: 增压阶段
    PressureIncrease --> ABSTriggered: 持续监控
    
    PressureHold: 保压阶段
    PressureHold --> ABSTriggered: 持续监控
    
    PressureDecrease: 减压阶段
    PressureDecrease --> ABSTriggered: 持续监控
    
    ABSTriggered --> NormalBraking: 车速<5km/h
    
    style Idle fill:#2d3748,stroke:#4a5568
    style NormalBraking fill:#276749,stroke:#48bb78
    style ABSTriggered fill:#c53030,stroke:#fc8181
    style PressureDecrease fill:#dd6b20,stroke:#f6ad55
`;

const brakeFlowchart = `
flowchart TD
    A[驾驶员踩踏板] --> B{踏板信号有效?}
    B -->|是| C[计算制动力需求]
    B -->|否| D[使用冗余传感器]
    D --> C
    
    C --> E{ABS需要激活?}
    E -->|是| F[进入ABS循环]
    E -->|否| G[正常压力控制]
    
    F --> H{滑移率 > 18%?}
    H -->|是| I[保压阶段]
    H -->|否| J{滑移率 > 22%?}
    
    J -->|是| K[减压阶段]
    J -->|否| L[增压阶段]
    
    I --> M{轮速恢复?}
    K --> M
    L --> M
    
    M -->|是| G
    M -->|否| F
    
    G --> N[输出到液压阀]
    N --> O[建立轮缸压力]
    O --> P{制动结束?}
    
    P -->|是| Q[释放压力]
    P -->|否| C
    Q --> R[返回空闲]
    
    style A fill:#667eea,stroke:#764ba2,color:#fff
    style F fill:#fc8181,stroke:#c53030,color:#fff
    style K fill:#f6ad55,stroke:#dd6b20,color:#fff
`;

// ============================================
// 性能测试
// ============================================

function benchmarkRendering() {
    console.log('🏁 开始性能测试...\n');
    
    const iterations = 100;
    
    // 测试SVG渲染
    const svgStart = performance.now();
    for (let i = 0; i < iterations; i++) {
        renderMermaidSVG(brakeSequenceDiagram);
    }
    const svgTime = performance.now() - svgStart;
    
    console.log(`📊 SVG渲染 (${iterations}次):`);
    console.log(`   总时间: ${svgTime.toFixed(2)}ms`);
    console.log(`   平均: ${(svgTime/iterations).toFixed(2)}ms/次`);
    console.log(`   吞吐量: ${(1000/(svgTime/iterations)).toFixed(0)} 图表/秒\n`);
    
    // 测试ASCII渲染
    const asciiStart = performance.now();
    for (let i = 0; i < iterations; i++) {
        renderMermaidASCII(brakeSequenceDiagram);
    }
    const asciiTime = performance.now() - asciiStart;
    
    console.log(`📊 ASCII渲染 (${iterations}次):`);
    console.log(`   总时间: ${asciiTime.toFixed(2)}ms`);
    console.log(`   平均: ${(asciiTime/iterations).toFixed(2)}ms/次`);
    console.log(`   吞吐量: ${(1000/(asciiTime/iterations)).toFixed(0)} 图表/秒\n`);
}

// ============================================
// 主题展示
// ============================================

const themes = [
    'default',
    'dark',
    'forest',
    'neutral',
    'base',
    'cyberpunk',
    'dracula',
    'github',
    'monokai',
    'nord',
    'tokyo-night',
    'ayu',
    'catppuccin',
    'gruvbox',
    'rose-pine'
];

function showcaseThemes() {
    console.log('🎨 主题展示:\n');
    
    themes.forEach(theme => {
        console.log(`  ${theme}:`);
        const svg = renderMermaidSVG(brakeSequenceDiagram, { theme });
        console.log(`    SVG长度: ${svg.length} 字符`);
        console.log(`    包含样式: ${svg.includes('style') ? '✓' : '✗'}`);
    });
}

// ============================================
// ASCII输出示例
// ============================================

function showASCIIExample() {
    console.log('\n📺 ASCII终端输出示例:\n');
    
    const ascii = renderMermaidASCII(`
        sequenceDiagram
            Driver->>BCU: 制动请求
            BCU->>Valve: 阀控制
            Valve->>Wheel: 建压
    `);
    
    console.log(ascii);
    console.log('\n✨ 适用于CLI工具和终端界面\n');
}

// ============================================
// 制动系统数据可视化 (XYChart)
// ============================================

const pressureCurveData = `
xychart-beta
    title "制动压力建立曲线"
    x-axis [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    y-axis "压力 (bar)" 0 --> 100
    line [0, 15, 35, 55, 70, 80, 85, 88, 90, 91, 92]
    bar [0, 12, 30, 48, 65, 75, 82, 86, 88, 89, 90]
`;

const slipRatioData = `
xychart-beta
    title "ABS循环 - 滑移率变化"
    x-axis [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    y-axis "滑移率 (%)" 0 --> 40
    line [10, 15, 22, 28, 20, 12, 25, 30, 18, 15, 12]
    area [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
`;

// ============================================
// 运行演示
// ============================================

console.log('╔════════════════════════════════════════════════════════╗');
console.log('║     beautiful-mermaid - 制动系统时序图演示            ║');
console.log('║     传统Mermaid vs beautiful-mermaid 对比             ║');
console.log('╚════════════════════════════════════════════════════════╝\n');

// 1. 渲染示例图表
console.log('📈 渲染制动系统图表...\n');

const svg1 = renderMermaidSVG(brakeSequenceDiagram);
const svg2 = renderMermaidSVG(brakeStateDiagram);
const svg3 = renderMermaidSVG(brakeFlowchart);

console.log('✓ 时序图渲染完成');
console.log('✓ 状态图渲染完成');
console.log('✓ 流程图渲染完成\n');

// 2. 性能测试
benchmarkRendering();

// 3. ASCII展示
showASCIIExample();

// 4. 主题展示
// showcaseThemes();  // 取消注释以查看所有主题

console.log('\n═══════════════════════════════════════════════════════');
console.log('优势总结:');
console.log('• ⚡ 同步渲染 - 无async/await，React useMemo友好');
console.log('• 🎨 15+主题 - 一键切换，无需复杂CSS');
console.log('• 💻 双输出 - SVG用于Web，ASCII用于终端');
console.log('• 🔥 高性能 - 100+图表&lt;500ms');
console.log('• 📦 零依赖 - 无DOM依赖，服务端渲染友好');
console.log('═══════════════════════════════════════════════════════');
