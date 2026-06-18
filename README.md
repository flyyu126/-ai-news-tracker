# 🤖 AI 热点追踪

> 自动追踪国内外 AI 前沿研究与热点，翻译成中文，用网页展示。

## 📋 项目简介

本项目通过定时采集以下数据源，自动生成 AI 热点追踪网站：

| 数据源 | 类型 | 获取方式 |
|--------|------|----------|
| [arXiv](https://arxiv.org) (cs.AI, cs.CL, cs.LG, cs.CV 等) | 学术论文 | arXiv API |
| [GitHub](https://github.com) | 热门项目 | GitHub Search API |
| [机器之心](https://www.jiqizhixin.com/) | AI 新闻 | 网页抓取 |
| [量子位](https://www.qbitai.com/) | AI 新闻 | 网页抓取 |

### 功能特性

- ✅ 自动采集多源数据，每日更新
- ✅ 英文标题/摘要自动翻译为中文（百度翻译 API）
- ✅ 智能去重、关键词提取、领域标签分类
- ✅ 热度评分算法，自动生成热点排行
- ✅ 关键词标签云可视化
- ✅ 四大分类页面：热点总览、论文前沿、新闻聚合、GitHub 趋势
- ✅ 全站中文界面，支持暗色/亮色主题
- ✅ 响应式设计，移动端友好
- ✅ 支持关键词搜索和多维度筛选

## 🏗️ 项目结构

```
ai-news-tracker/
├── frontend/                    # Next.js 前端应用
│   ├── src/
│   │   ├── app/                 # App Router 页面
│   │   │   ├── layout.js        # 根布局（导航栏 + 页脚）
│   │   │   ├── page.js          # 首页 - 热点总览
│   │   │   ├── globals.css      # 全局样式
│   │   │   ├── papers/page.js   # 论文前沿
│   │   │   ├── news/page.js     # 新闻聚合
│   │   │   └── github/page.js   # GitHub 趋势
│   │   └── components/          # 通用组件
│   │       ├── Header.js        # 顶部导航
│   │       ├── ThemeToggle.js   # 主题切换
│   │       ├── SearchBar.js     # 搜索栏
│   │       ├── TagCloud.js      # 标签云
│   │       ├── EventCard.js     # 热点卡片
│   │       ├── PaperCard.js     # 论文卡片
│   │       ├── NewsItem.js      # 新闻时间条
│   │       ├── GithubCard.js    # GitHub 卡片
│   │       ├── FilterBar.js     # 筛选栏
│   │       └── LoadingSkeleton.js # 加载骨架屏
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/                     # Python 采集与处理脚本
│   ├── run_all.py               # 主流程调度
│   ├── fetch_arxiv.py           # arXiv 论文采集
│   ├── fetch_github.py          # GitHub 项目采集
│   ├── fetch_news.py            # 新闻采集
│   ├── translate.py             # 百度翻译 API
│   └── process.py               # 数据处理（去重/标签/热度）
├── data/                        # JSON 数据输出目录
├── .github/workflows/
│   └── daily-update.yml         # GitHub Actions 定时更新
├── requirements.txt             # Python 依赖
├── README.md                    # 本文件
└── DEPLOY.md                    # 部署说明
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 18+
- （可选）百度翻译 API 密钥

### 1. 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖
cd frontend && npm install
```

### 2. 运行数据采集

```bash
# 基本运行（无翻译）
cd scripts && python run_all.py --no-translate

# 带翻译功能（需配置百度翻译 API）
export BAIDU_APPID="你的AppID"
export BAIDU_SECRET_KEY="你的SecretKey"
cd scripts && python run_all.py
```

### 3. 启动前端

```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 查看效果。

### 4. 构建生产版本

```bash
cd frontend
npm run build
```

## ⚙️ 自定义配置

### 采集配置

通过 `run_all.py` 的命令行参数配置：

```bash
python run_all.py \
  --output-dir ../frontend/public/data \  # 输出目录
  --max-papers 50 \                        # 最大论文数
  --max-github 20 \                        # 最大 GitHub 项目数
  --days-back 7 \                          # 回溯天数
  --no-translate                           # 跳过翻译
```

### 领域标签自定义

编辑 `scripts/process.py` 中的 `CATEGORY_KEYWORDS` 字典，可以添加或修改领域标签及其匹配关键词。

### 数据源新增

如要新增新闻源，在 `scripts/fetch_news.py` 中添加新的抓取函数，并在 `fetch_all_news()` 中调用。

## 📄 技术栈

| 技术 | 用途 |
|------|------|
| Next.js 13 (App Router) | 前端框架 |
| Tailwind CSS | 样式框架 |
| Python 3 | 数据采集与处理 |
| arXiv API | 论文数据源 |
| GitHub REST API | 项目数据源 |
| Baidu Translate API | 翻译引擎 |
| GitHub Actions | 定时任务 |
| Vercel | 前端部署 |

## 📝 License

MIT
