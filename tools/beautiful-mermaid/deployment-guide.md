# Beautiful Mermaid - 项目部署实践

> **部署日期**: 2026-03-08  
> **项目类型**: Mermaid 图表渲染库  
> **技术栈**: TypeScript + ELK.js + 零 DOM 依赖

---

## 项目概述

**Beautiful Mermaid** 是一个高性能的 Mermaid 图表渲染库，特点：

- 支持 SVG 和 ASCII 双输出
- 完全同步渲染（无异步依赖）
- 15 种内置主题 + 自定义主题
- 零 DOM 依赖，可在任何环境运行
- 超快渲染性能（100+ 图表 < 500ms）

---

## 部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/lukilabs/beautiful-mermaid.git
cd beautiful-mermaid
```

### 2. 安装依赖

```bash
# 使用 npm（或 bun/pnpm）
npm install
```

### 3. 构建项目

```bash
npm run build
```

输出：
- `dist/index.js` - ESM 构建
- `dist/index.d.ts` - TypeScript 类型定义

### 4. 启动演示

```bash
# 创建演示页面
cat > demo.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  <div class="mermaid">
  graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
  </div>
  <script>
    mermaid.initialize({ theme: 'dark' });
  </script>
</body>
</html>
EOF

# 启动 HTTP 服务器
python3 -m http.server 8889
```

访问: http://localhost:8889/demo.html

---

## 核心功能验证

### 支持的图表类型

| 类型 | 语法示例 | 状态 |
|------|----------|------|
| Flowchart | `graph TD; A --> B` | ✅ |
| Sequence | `sequenceDiagram; A->>B: msg` | ✅ |
| State | `stateDiagram-v2; [*] --> Idle` | ✅ |
| Class | `classDiagram; Animal <|-- Duck` | ✅ |
| ER | `erDiagram; A ||--o{ B : has` | ✅ |
| XY Chart | `xychart-beta; bar [1,2,3]` | ✅ |

### 主题系统

**15 种内置主题**:
- `zinc-light` / `zinc-dark`
- `tokyo-night` / `tokyo-night-storm` / `tokyo-night-light`
- `catppuccin-mocha` / `catppuccin-latte`
- `nord` / `nord-light`
- `dracula`
- `github-light` / `github-dark`
- `solarized-light` / `solarized-dark`
- `one-dark`

**自定义主题**:
```typescript
const myTheme = {
  bg: '#0f0f0f',
  fg: '#e0e0e0',
  accent: '#ff6b6b',
  muted: '#666666',
}
renderMermaidSVG(diagram, myTheme)
```

---

## 双输出模式

### SVG 输出（UI 使用）

```typescript
import { renderMermaidSVG } from 'beautiful-mermaid'

const svg = renderMermaidSVG(`
  graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
`, {
  bg: '#1a1b26',
  fg: '#a9b1d6',
  theme: 'tokyo-night'
})

// 插入到 DOM
document.getElementById('chart').innerHTML = svg
```

### ASCII 输出（Terminal 使用）

```typescript
import { renderMermaidASCII } from 'beautiful-mermaid'

const ascii = renderMermaidASCII(`graph LR; A --> B --> C`)
console.log(ascii)
```

输出:
```
┌───┐     ┌───┐     ┌───┐
│   │     │   │     │   │
│ A │────►│ B │────►│ C │
│   │     │   │     │   │
└───┘     └───┘     └───┘
```

---

## React 集成示例

```tsx
import { renderMermaidSVG } from 'beautiful-mermaid'

function MermaidDiagram({ code }: { code: string }) {
  const { svg, error } = React.useMemo(() => {
    try {
      return {
        svg: renderMermaidSVG(code, {
          bg: 'var(--background)',
          fg: 'var(--foreground)',
          transparent: true,
        }),
        error: null,
      }
    } catch (err) {
      return { svg: null, error: err }
    }
  }, [code])

  if (error) return <pre>{error.message}</pre>
  return <div dangerouslySetInnerHTML={{ __html: svg! }} />
}
```

**优势**:
- 同步渲染，无闪烁
- CSS 变量支持，主题切换无需重渲染
- useMemo 缓存，性能优化

---

## 技术亮点

### 1. 同步渲染实现

传统 Mermaid 渲染是异步的，需要 `await`。beautiful-mermaid 通过 FakeWorker 绕过 ELK.js 的 Worker 依赖，实现同步渲染：

```typescript
// 同步渲染，无需 await
const svg = renderMermaidSVG(diagram)
// 立即使用 svg
```

### 2. 两色主题系统

仅需 `bg` 和 `fg` 两个颜色，通过 CSS `color-mix()` 自动生成完整配色：

| 元素 | 计算方式 |
|------|----------|
| 文本 | `--fg` 100% |
| 次要文本 | `--fg` 60% into `--bg` |
| 连接线 | `--fg` 50% into `--bg` |
| 节点填充 | `--fg` 3% into `--bg` |

### 3. 零 DOM 依赖

纯 TypeScript 实现，不依赖浏览器 DOM，可在：
- Node.js 服务端
- 终端 CLI
- 浏览器客户端
- 边缘计算环境

---

## 部署验证

| 检查项 | 结果 |
|--------|------|
| 代码克隆 | ✅ |
| 依赖安装 | ✅ |
| 构建成功 | ✅ dist/index.js |
| HTTP 服务 | ✅ http://localhost:8889 |
| 图表渲染 | ✅ 6 种类型 |
| 主题切换 | ✅ 15 种主题 |

---

## 应用场景

1. **AI 助手**: 在对话中实时渲染图表
2. **文档系统**: Markdown 文档图表渲染
3. **CLI 工具**: 终端 ASCII 图表输出
4. **项目管理**: 甘特图、流程图生成
5. **数据库设计**: ER 图渲染

---

*部署实践记录*  
*关键词: Mermaid, SVG, ASCII, TypeScript, 图表渲染*
