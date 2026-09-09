# 🏔️ 四川旅游指南系统（Sichuan Travel）

> 一个集**景点展示、用户收藏、后台管理**与 **AI 旅游智能助手**于一体的四川旅游 Web 应用。
> 后端 Flask + MySQL，前端原生 HTML/JS，AI 助手接入 DeepSeek 等 OpenAI 兼容大模型。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange)
![AI](https://img.shields.io/badge/AI-DeepSeek%20%2F%20OpenAI%20兼容-9b59b6)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 📖 目录

- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [需要自己准备的本地文件](#-需要自己准备的本地文件)
- [AI 智能助手配置](#-ai-智能助手配置)
- [默认账号](#-默认账号)
- [主要页面与接口](#-主要页面与接口)
- [注意事项](#-注意事项)
- [常见问题 FAQ](#-常见问题-faq)

---

## ✨ 功能特性

- 🏞 **景点展示**：首页轮播大图（自动播放 + 左右箭头切换）、景点卡片、去重渲染、搜索、分类筛选。
- 📄 **景点详情**：图文介绍、交通指南、游玩贴士、门票价格、开放时间。
- ❤️ **用户收藏**：注册/登录（JWT）、收藏/取消收藏、个人中心查看收藏列表。
- 🛠 **后台管理**：景点增删改、图片上传管理。
- 🤖 **AI 旅游智能助手**：右下角悬浮聊天窗，**全站页面可用**，支持多轮对话、回车发送、加载状态、防重复提交；接入 DeepSeek / OpenAI / Qwen 等 OpenAI 兼容大模型；未配置时自动降级为本地旅游知识库。
- 🔔 **交互优化**：Toast 滑动消息条（替代 alert 弹窗）、登录进度条、按钮动画、XSS 转义。

---

## 🧰 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python、Flask、Flask-CORS |
| 数据库 | MySQL 5.7+（`mysql-connector-python`） |
| 认证 | PyJWT（Token 鉴权） |
| AI | `openai` SDK（OpenAI 兼容协议）、`python-dotenv` |
| 前端 | 原生 HTML5 + CSS3 + JavaScript（**无框架**，非 Vue/React） |

> 说明：前端是经典的多页应用（MPA），每个 `.html` 页面由 Flask 直接托管，公共逻辑在 `frontend/js/common.js`。

---

## 📁 项目结构

```
Sichuan-Travel/
├── backend/
│   ├── app.py                # Flask 入口：路由注册、静态托管、启动（端口 3000）
│   ├── sjk.py                # 数据库连接配置 + 建表 + 初始数据
│   ├── .env                  # 【需自建】AI Key 等敏感配置（已被 .gitignore 忽略）
│   ├── .env.example          # .env 模板（可提交）
│   ├── routes/
│   │   ├── users.py          # 用户注册/登录/鉴权
│   │   ├── spots.py          # 景点 CRUD
│   │   ├── favorites.py      # 收藏
│   │   └── ai.py             # AI 聊天接口 + 本地知识库兜底
│   └── services/
│       └── ai_service.py     # 大模型服务封装（.env 热加载、多轮对话、异常处理）
├── frontend/
│   ├── index.html            # 首页（轮播 + 推荐景点）
│   ├── all-spots.html        # 全部景点
│   ├── spot-detail.html      # 景点详情
│   ├── login.html / register.html
│   ├── user-profile.html     # 个人中心
│   ├── admin-panel.html      # 后台管理
│   ├── image-upload.html     # 图片上传
│   ├── travel-tips.html / about-sichuan.html
│   ├── css/style.css         # 全部样式（含 AI 聊天组件）
│   ├── js/common.js          # 公共逻辑 + 全站 AI 聊天组件
│   └── images/               # 景点图片
├── database/
│   └── database.sql          # 建库建表 SQL（可选，app.py 也会自动建表）
├── requirements.txt          # Python 依赖
├── start.bat                 # Windows 一键启动脚本
└── .gitignore
```

---

## 🚀 快速开始

### 1. 环境准备

- **Python 3.8+**
- **MySQL 5.7 或 8.x**（本地安装并启动服务）

### 2. 克隆并安装依赖

```bash
git clone <你的仓库地址>
cd Sichuan-Travel
pip install -r requirements.txt
```

### 3. 准备数据库

连接 MySQL，执行建库（也可用图形工具 Navicat / DBeaver）：

```sql
CREATE DATABASE IF NOT EXISTS sichuan_tourism
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;
```

> 数据表和初始数据**无需手动建**——Flask 启动时 `init_db()` 会自动创建表、写入默认管理员和景点数据。
> 若你的 MySQL 账号密码不是默认值，请改 [backend/sjk.py](file:///d:/GitHub/Sichuan-Travel/backend/sjk.py) 顶部的 `config`：
>
> ```python
> config = {
>     'host': 'localhost',
>     'user': 'root',
>     'password': '你的MySQL密码',   # 默认 123456
>     'database': 'sichuan_tourism',
>     'charset': 'utf8mb4'
> }
> ```

### 4. 配置 AI（可选，不配也能跑本地知识库）

```bash
# Windows
copy backend\.env.example backend\.env
```

然后编辑 `backend/.env` 填入你的 API Key（详见下一节）。

### 5. 启动项目

**Windows 一键启动**：双击根目录 `start.bat`

**或命令行**：

```bash
cd backend
python app.py
```

启动成功后访问 👉 **http://localhost:3000/index.html**

---

## 📄 需要自己准备的本地文件

以下文件**包含敏感信息、不进 Git**，需要你在本地手动创建：

| 文件 | 是否必须 | 说明 |
|------|:---:|------|
| `backend/.env` | AI 功能需要 | 复制 `.env.example` 得到，填 API Key。**不填则 AI 走本地知识库兜底，不影响其他功能** |
| MySQL 数据库 `sichuan_tourism` | ✅ 必须 | 见上一节建库语句 |
| `backend/sjk.py` 里的数据库密码 | ✅ 必须 | 若你 MySQL 密码不是 `123456`，改成你自己的 |

**`.env` 文件格式**（UTF-8 纯文本，无引号、无多余空格）：

```env
AI_API_KEY=sk-你的真实key
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
AI_TIMEOUT=30
```

> ⚠️ `backend/.env` 已被 `.gitignore` 忽略，不会提交到仓库。请勿将真实 Key 写进任何 `.py` / `.html` 文件，也不要贴进截图或聊天记录。

---

## 🤖 AI 智能助手配置

本项目通过 **OpenAI 兼容协议**接入大模型，可自由切换服务商：

| 服务商 | `AI_BASE_URL` | `AI_MODEL` |
|--------|---------------|------------|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 通义千问 Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |

**获取 DeepSeek Key**：登录 [DeepSeek 开放平台](https://platform.deepseek.com/) → API Keys → 创建 Key（形如 `sk-xxxx`）。

**特性说明**：

- 修改 `backend/.env`（换 Key / 换模型）后 **无需重启**，系统检测到文件变化会自动热加载，下一条消息即生效。
- 修改后端 `.py` 代码也会自动重载（`debug=True`）。
- 若 Key 失效 / 未配置 / 网络异常，接口返回友好提示且**不泄露 Key 与堆栈**，并自动降级为内置本地知识库回答常见旅游问题。

---

## 👤 默认账号

首次启动时自动写入（仅本地测试用，**上线前请修改**）：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 普通用户 | `user1` | `user123` |

后台管理入口：登录管理员账号后访问 `/admin-panel.html`。

---

## 🔌 主要页面与接口

**页面**（均由 Flask 托管，`http://localhost:3000/`）：

| 页面 | 路径 |
|------|------|
| 首页 | `/index.html` |
| 全部景点 | `/all-spots.html` |
| 景点详情 | `/spot-detail.html?id=景点ID` |
| 登录/注册 | `/login.html`、`/register.html` |
| 个人中心 | `/user-profile.html` |
| 后台管理 | `/admin-panel.html` |
| 旅游指南 | `/travel-tips.html` |

**API 前缀**：

| 模块 | 前缀 |
|------|------|
| 用户 | `/api/users` |
| 景点 | `/api/spots` |
| 收藏 | `/api/favorites` |
| AI 助手 | `/api/ai` |

AI 聊天接口示例：

```http
POST /api/ai/chat
Content-Type: application/json

{
  "question": "成都三天怎么安排？",
  "history": [
    {"role": "user", "content": "我准备去成都"},
    {"role": "assistant", "content": "成都可以这样安排……"}
  ]
}
```

返回：

```json
{
  "success": true,
  "answer": "……模型回答……",
  "source": "llm",
  "model": "deepseek-chat"
}
```

> `source` 为 `llm` 表示真实调用了大模型；为 `local` 表示走本地知识库兜底。

---

## ⚠️ 注意事项

1. **数据库必须先建库**：库名 `sichuan_tourism`，否则 Flask 连接数据库会失败（表会自动建，但库要先存在）。
2. **API Key 安全**：只放在后端 `backend/.env`；前端绝不接触 Key；该文件已被 Git 忽略。**Key 一旦泄露（如贴到公开场合）请立即到服务商后台吊销并重新生成。**
3. **`debug=True` 仅供本地开发**：[app.py](file:///d:/GitHub/Sichuan-Travel/backend/app.py) 中部署到公网时务必改回 `debug=False`，否则错误页会暴露代码。
4. **默认密码**：`sjk.py` 的数据库密码和内置账号密码仅用于本地，生产环境务必修改。
5. **实时信息免责**：AI 回答中的门票价格、营业时间、天气等可能变动，请以官方最新信息为准。
6. **Python 依赖**：`openai`、`python-dotenv` 为 AI 功能所需，未安装时 AI 会降级为本地知识库，不影响其余功能。

---

## ❓ 常见问题 FAQ

**Q：机器人回复"AI 服务暂时不可用"？**
A：多为 Key 失效 / 未配置 / 网络问题。访问 `/api/ai/status` 看 `configured`；刚换 Key 后保存 `.env` 即可自动生效；若 Key 被吊销需换新 Key。

**Q：访问页面报数据库错误？**
A：确认 MySQL 已启动、已建库 `sichuan_tourism`、`sjk.py` 里的账号密码正确。

**Q：端口 3000 被占用？**
A：关掉占用进程，或修改 [app.py](file:///d:/GitHub/Sichuan-Travel/backend/app.py) 末尾 `app.run(port=3000)` 的端口号。

**Q：改了代码/Key 要重启吗？**
A：改前端 → 刷新浏览器；改后端 `.py` → 自动重载；改 `.env` 换 Key → 自动热加载，均无需手动重启。

**Q：没有 API Key 能用吗？**
A：能。景点、收藏、后台等功能完全不受影响；AI 助手会用内置本地旅游知识库回答常见问题。

---

## 📜 License

MIT License —— 可自由用于学习与二次开发。

---

> 🌶️ 天府之国，欢迎来四川！
