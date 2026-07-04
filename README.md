# 云途 - 旅行纪念册

一个记录旅行足迹的个人 Web 应用。上传照片、记录文字，按旅程时间轴整理你的旅行记忆。

## 技术栈

| 前端 | 后端 |
|------|------|
| Vue 3 (Composition API) | Python FastAPI |
| Vite | SQLite + aiosqlite |
| Element Plus | SQLAlchemy (async) |
| vue-router + Pinia | JWT 认证 |
| vue-viewer (图片灯箱) | EXIF 自动读取 |

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

服务运行在 http://localhost:8001

### 前端

```bash
cd frontend
npm install
npm run dev
```

开发服务器运行在 http://localhost:5173

### 构建前端

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/`

## 项目结构

```
travel-app/
├── backend/
│   ├── app/
│   │   ├── routers/       # API 路由
│   │   │   ├── auth.py    # 登录注册
│   │   │   ├── trips.py   # 旅程 CRUD
│   │   │   ├── moments.py # 记录 CRUD
│   │   │   ├── upload.py  # 文件上传
│   │   │   └── stats.py   # 统计
│   │   ├── models.py      # 数据模型
│   │   ├── schemas.py     # Pydantic 校验
│   │   ├── database.py    # 数据库连接
│   │   └── main.py        # 入口
│   ├── uploads/           # 上传文件
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── api/           # API 请求
│   │   ├── stores/        # Pinia 状态
│   │   ├── router/        # 路由配置
│   │   └── style.css      # 全局样式
│   └── vite.config.js
└── README.md
```

## 功能

- 创建/编辑/删除旅程
- 发布文字记录 + 上传照片
- 照片灯箱预览（vue-viewer）
- EXIF 信息自动提取
- 旅程封面上传
- 按时间轴浏览
- 仪表盘统计

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/trips` | 旅程列表 |
| POST | `/api/trips` | 创建旅程 |
| GET | `/api/trips/:id` | 旅程详情 |
| PUT | `/api/trips/:id` | 更新旅程 |
| DELETE | `/api/trips/:id` | 删除旅程 |
| GET | `/api/trips/:id/moments` | 记录列表 |
| POST | `/api/moments` | 创建记录 |
| GET | `/api/moments/:id` | 记录详情 |
| PUT | `/api/moments/:id` | 更新记录 |
| DELETE | `/api/moments/:id` | 删除记录 |
| POST | `/api/upload` | 上传图片 |
| POST | `/api/upload/cover` | 上传封面 |
| GET | `/api/stats/summary` | 统计概览 |
