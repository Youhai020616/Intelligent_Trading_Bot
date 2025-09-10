# 🤖 智能交易机器人前端

基于 React + TypeScript + Material-UI + Redux Toolkit 构建的现代化交易界面。

## ✨ 特性

- **现代化UI**: 基于 Material-UI 的精美设计
- **实时数据**: WebSocket 支持实时数据更新
- **智能体监控**: 可视化智能体协作状态
- **响应式设计**: 支持桌面端和移动端
- **状态管理**: Redux Toolkit 全局状态管理
- **类型安全**: 完整的 TypeScript 支持

## 🚀 快速开始

### 环境要求

- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── layout/         # 布局组件
│   │   ├── dashboard/      # 仪表板组件
│   │   ├── analysis/       # 分析组件
│   │   ├── agents/         # 智能体组件
│   │   └── common/         # 通用组件
│   ├── pages/              # 页面组件
│   ├── store/              # Redux 状态管理
│   │   ├── slices/         # Redux slices
│   │   └── index.ts        # Store 配置
│   ├── utils/              # 工具函数
│   ├── types/              # TypeScript 类型定义
│   ├── App.tsx             # 主应用组件
│   ├── main.tsx            # 应用入口
│   └── index.css           # 全局样式
├── public/                 # 静态资源
├── vercel.json            # Vercel 部署配置
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🎨 设计系统

### 颜色主题

```typescript
const theme = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  background: '#f5f5f5',
  surface: '#ffffff'
}
```

### 组件样式

- **卡片**: 圆角 12px，阴影效果
- **按钮**: 圆角 8px，无大写转换
- **表格**: 现代化数据展示
- **图表**: 专业金融图表样式

## 🔧 主要功能

### 1. 📊 仪表板 (Dashboard)
- 实时交易信号展示
- 系统状态指标
- 智能体活动时间线
- 快速操作面板

### 2. 📈 交易分析 (Analysis)
- 股票搜索和选择
- 技术指标图表
- 智能体分析结果
- 决策建议生成

### 3. 🤖 智能体监控 (Agents)
- 智能体状态列表
- 协作流程可视化
- 性能指标统计
- 实时活动日志

### 4. 📋 决策历史 (History)
- 交易信号历史
- 智能体活动记录
- 性能统计分析

## 🔌 API 集成

### 后端连接配置

```typescript
// src/config/api.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  timeout: 10000,
}
```

### WebSocket 连接

```typescript
// 实时数据更新
const socket = io(API_CONFIG.wsURL)

socket.on('signal_update', (data) => {
  dispatch(addSignal(data))
})

socket.on('agent_status', (data) => {
  dispatch(updateAgentStatus(data))
})
```

## 📱 响应式设计

### 断点系统

```scss
$breakpoints: (
  xs: 0px,      // 手机
  sm: 600px,    // 平板竖屏
  md: 960px,    // 平板横屏
  lg: 1280px,   // 桌面小屏
  xl: 1920px    // 桌面大屏
);
```

### 移动端适配

- 自适应布局组件
- 触摸友好的交互
- 优化的移动端导航

## 🚀 Vercel 部署

### 自动部署

1. 连接 GitHub 仓库到 Vercel
2. 配置环境变量
3. 自动构建和部署

### 环境变量

```bash
VITE_API_BASE_URL=https://your-backend-api.com
VITE_WS_URL=wss://your-backend-api.com
```

## 🧪 测试

```bash
# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 启动测试UI
npm run test:ui
```

## 📚 开发指南

### 组件开发规范

```typescript
// 组件命名使用 PascalCase
interface ComponentProps {
  // 属性定义
}

const ComponentName: React.FC<ComponentProps> = ({ prop }) => {
  return (
    <div>
      {/* JSX 内容 */}
    </div>
  )
}

export default ComponentName
```

### 状态管理模式

```typescript
// 使用 Redux Toolkit
const slice = createSlice({
  name: 'feature',
  initialState,
  reducers: {
    actionName: (state, action) => {
      // 状态更新逻辑
    }
  }
})
```

## 🔧 可用脚本

```json
{
  "dev": "vite",           // 开发服务器
  "build": "tsc && vite build",  // 生产构建
  "lint": "eslint src",    // 代码检查
  "preview": "vite preview",     // 预览构建
  "test": "vitest",        // 运行测试
  "test:ui": "vitest --ui" // 测试UI
}
```

## 🌟 最佳实践

1. **组件设计**: 保持组件单一职责
2. **状态管理**: 合理使用本地和全局状态
3. **性能优化**: 使用 React.memo 和 useMemo
4. **代码规范**: 遵循 ESLint 和 Prettier 配置
5. **测试覆盖**: 核心功能保持 80%+ 测试覆盖率

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。