# 🌐 AI 热点追踪 - 部署指南

本文档详细说明如何零成本部署本项目，包括百度翻译 API 配置、Vercel 前端部署、GitHub Actions 定时更新。

---

## 📋 目录

1. [百度翻译 API 配置](#1-百度翻译-api-配置)
2. [GitHub 仓库设置](#2-github-仓库设置)
3. [Vercel 前端部署](#3-vercel-前端部署)
4. [GitHub Actions 定时更新](#4-github-actions-定时更新)
5. [完整部署流程速查](#5-完整部署流程速查)

---

## 1. 百度翻译 API 配置

本项目使用百度翻译 API 将英文标题和摘要翻译为中文。免费版每月有 100 万字符的翻译额度。

### 1.1 注册账号

1. 访问 [百度翻译开放平台](https://fanyi-api.baidu.com/)
2. 点击"立即注册"，使用百度账号或手机号注册
3. 登录后进入控制台

### 1.2 申请通用翻译 API

1. 在控制台点击"产品服务" → "通用翻译"（如有需要也可以同时开通"高级翻译"，不过免费版就够了）
2. 点击"立即购买"（选择免费版，¥0/月）
3. 填写应用名称（如 "AI热点追踪"）
4. 提交后，在"管理控制台" → "开发者信息" 中查看：
   - **AppID**（即 API 调用时的 appid）
   - **密钥**（即 API 调用时的 secret_key，注意不要泄露）

### 1.3 本地开发测试

```bash
# 设置环境变量
export BAIDU_APPID="你的AppID"
export BAIDU_SECRET_KEY="你的密钥"

# 运行采集脚本（包含翻译）
cd scripts
python run_all.py

# 或者单独测试翻译功能
python translate.py
```

> **注意**：如果不配置翻译 API，脚本仍会正常运行，只是翻译字段会保留原文。
> 但 GitHub 项目描述等英文内容将不会自动转为中文。

### 1.4 API 免费额度说明

| 项目 | 说明 |
|------|------|
| 免费额度 | 100 万字符/月（标准版）|
| 超额处理 | 超过额度后 API 会返回错误，脚本会自动保留原文 |
| 适用版本 | 通用翻译 API（标准版）|
| 每月费用 | ¥0（免费）|
| 建议用量 | 本项目每月约消耗 5~10 万字符（取决于采集数量）|

---

## 2. GitHub 仓库设置

### 2.1 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`ai-news-tracker`（或其他名称）
4. 选择 **Public**（公开仓库，Vercel 免费套餐需要）
5. 不要勾选任何初始化选项
6. 点击 "Create repository"

### 2.2 上传代码

```bash
# 在项目根目录初始化 git
cd ai-news-tracker
git init
git add .
git commit -m "🎉 初始提交：AI 热点追踪项目"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/ai-news-tracker.git

# 推送到 GitHub
git push -u origin main
```

### 2.3 配置 Secrets（密钥）

为了在 GitHub Actions 中使用翻译 API，需要将密钥配置为 Secrets：

1. 在 GitHub 仓库页面，点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下两个 Secret：

| Name | Value |
|------|-------|
| `BAIDU_APPID` | 你的百度翻译 AppID |
| `BAIDU_SECRET_KEY` | 你的百度翻译密钥 |

![GitHub Secrets 配置示意](https://docs.github.com/assets/cb-23598/images/help/settings/actions-secrets-tab.png)

---

## 3. Vercel 前端部署

### 3.1 注册 Vercel

1. 访问 [Vercel](https://vercel.com)
2. 点击 "Sign Up" → "Continue with GitHub"（用 GitHub 账号登录）
3. 授权 Vercel 访问你的 GitHub 仓库

### 3.2 导入并部署

1. 登录 Vercel 后，点击 **"Add New..."** → **"Project"**
2. 在 "Import Git Repository" 中找到你的 `ai-news-tracker` 仓库，点击 **"Import"**

3. 配置项目：

| 配置项 | 值 |
|--------|-----|
| Framework Preset | **Next.js** |
| Root Directory | **frontend**（注意：一定要选这个！）|
| Build Command | `npm run build` |
| Output Directory | `out`（Next.js 会自动生成）|

4. 展开 **"Environment Variables"**（环境变量，可选）：
   - 如果需要在构建时提供翻译，可以添加：
     - `BAIDU_APPID` = 你的 AppID（不会在构建时使用，但可留做备用）
   
5. 点击 **"Deploy"**，等待部署完成

6. 部署成功后，Vercel 会分配一个域名（如 `ai-news-tracker.vercel.app`）

> **注意**：由于我们使用了 `output: 'export'` 静态导出，部署是完全静态的，不会有服务器端渲染的开销。

### 3.3 配置自定义域名（可选）

1. 在 Vercel 项目页面 → **Settings** → **Domains**
2. 输入你的域名，按照提示配置 DNS 即可

### 3.4 Vercel 自动部署

当你推送到 GitHub 仓库的 `main` 分支时，Vercel 会自动触发重新部署。
GitHub Actions 提交数据更新后，Vercel 会自动检测到变更并部署新版。

---

## 4. GitHub Actions 定时更新

### 4.1 默认配置

项目自带的 `.github/workflows/daily-update.yml` 已配置好：

- **触发时间**：每天 UTC 2:00 和 10:00（北京时间 10:00 和 18:00）
- **执行内容**：
  1. 安装 Python 依赖
  2. 运行 `run_all.py` 采集数据
  3. 提交数据变更到仓库
  4. Vercel 检测到变更后自动部署

### 4.2 启用 Actions

1. 推送代码后，GitHub 会自动识别 `.github/workflows/` 目录
2. 访问仓库的 **Actions** 标签页
3. 会看到 "每日数据更新" 工作流已经注册
4. 可以手动触发测试：
   - 点击 "每日数据更新" → **"Run workflow"** → 绿色的 **"Run workflow"** 按钮
   
### 4.3 查看运行日志

1. Actions → 点击任意运行记录
2. 可以看到每个步骤的执行日志
3. 如果出错，日志会显示详细错误信息

### 4.4 故障排除

**问题：Actions 运行失败**

解决方案：
1. 检查 Secrets 是否正确配置（`BAIDU_APPID`, `BAIDU_SECRET_KEY`）
2. 查看运行日志，确认错误信息
3. 如果是因为翻译 API 超时，可以添加 `--no-translate` 参数跳过翻译

**问题：采集不到新闻数据**

解决方案：
1. 新闻网站可能改变了页面结构，需要更新 `fetch_news.py` 中的选择器
2. 网站可能有反爬虫机制，可以增加请求间隔

**问题：Vercel 没有自动更新**

解决方案：
1. 确认 GitHub Actions 工作流成功运行并提交了变更
2. 在 Vercel 项目页面手动触发部署：**Deployments** → **"Redeploy"**
3. 或者配置 Vercel Webhook（见工作流末尾的注释代码）

---

## 5. 完整部署流程速查

### 首次部署（约 15 分钟）

```bash
# 第一步：本地准备
cd ai-news-tracker
pip install -r requirements.txt

# 第二步：测试采集（可选，可跳过）
cd scripts && python run_all.py --no-translate && cd ..

# 第三步：推送到 GitHub
git init
git add .
git commit -m "🎉 初始提交"
git remote add origin https://github.com/你的用户名/ai-news-tracker.git
git branch -M main
git push -u origin main

# 第四步：在 GitHub 上配置 Secrets（BAIDU_APPID, BAIDU_SECRET_KEY）
# 第五步：在 Vercel 导入项目并部署（Root Directory 选 frontend）
```

### 日常维护

- 数据会自动更新（每天 2 次）
- 如需手动更新，在 GitHub Actions 页面点击 "Run workflow"
- 翻译 API 额度用完时，API 会返回错误，脚本会保留原文

### 费用统计

| 服务 | 费用 | 说明 |
|------|------|------|
| GitHub | 免费 | 公开仓库 |
| Vercel | 免费 | Hobby 计划 |
| 百度翻译 API | 免费 | 每月 100 万字符 |
| GitHub Actions | 免费 | 公开仓库每月 2000 分钟 |
| **总计** | **¥0/月** | |

---

## 📎 参考链接

- [Next.js 部署文档](https://nextjs.org/docs/pages/building-your-application/deploying/static-exports)
- [Vercel 部署指南](https://vercel.com/docs/deployments/overview)
- [GitHub Actions 文档](https://docs.github.com/zh/actions)
- [百度翻译 API 文档](https://fanyi-api.baidu.com/doc/21)

---

> **提示**：部署过程中遇到问题，请先在 GitHub Issues 中搜索类似问题，或提交新的 Issue。
