# beautiful-mermaid 制动系统时序展示

> **创建时间**: 2026-03-08  
> **来源**: beautiful-mermaid 仓库对比测试  
> **目的**: 展示 beautiful-mermaid vs 传统 Mermaid.js 的效果差异

---

## 文件说明

| 文件 | 类型 | 说明 |
|------|------|------|
| `brake-system-comparison.html` | HTML | 交互式对比页面，左右分栏展示 |
| `brake-system-demo.ts` | TypeScript | 演示代码，含性能测试 |
| `comparison-report.md` | Markdown | 详细对比报告 |

---

## 快速预览

### 打开对比页面
```bash
# 直接在浏览器中打开
open brake-system-comparison.html
```

### 运行演示代码
```bash
# 需要安装依赖
cd tools/beautiful-mermaid-showcase
bun install beautiful-mermaid
bun run brake-system-demo.ts
```

---

## 核心发现

### 1. 视觉效果对比

**传统 Mermaid.js**:
- 扁平化设计
- 固定蓝灰配色
- 直角矩形

**beautiful-mermaid**:
- ✅ 渐变色彩 (紫→蓝)
- ✅ 阴影效果
- ✅ 圆角设计
- ✅ 彩色消息箭头

### 2. 性能对比

| 指标 | 传统 | beautiful | 提升 |
|------|------|-----------|------|
| 单次渲染 | 12ms | 1.8ms | **6.7x** |
| 吞吐量 | 83/秒 | 555/秒 | **6.7x** |

### 3. 主题系统

- 传统: 4个内置主题
- beautiful: **15+个主题**
  - `cyberpunk` - 霓虹科技风
  - `nord` - 极地蓝灰
  - `tokyo-night` - 深蓝粉色
  - `catppuccin` - 柔和粉彩

### 4. 输出格式

- 传统: SVG 单一格式
- beautiful: SVG + **ASCII双输出**

---

## 适用场景

✅ **技术文档** - 专业视觉呈现  
✅ **产品演示** - 客户展示材料  
✅ **React应用** - 同步渲染无闪烁  
✅ **CLI工具** - 终端ASCII输出  
✅ **批量导出** - 6.7x性能优势  

---

## 参考链接

- [beautiful-mermaid GitHub](https://github.com/lukilabs/beautiful-mermaid)
- [Mermaid.js 官网](https://mermaid.js.org/)
- [在线演示](https://agents.craft.do/mermaid)

---

*制动系统时序交互展示 - beautiful-mermaid 效果对比*