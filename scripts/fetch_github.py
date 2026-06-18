"""
GitHub 趋势项目采集模块
功能：通过 GitHub API 获取 AI 相关热门仓库信息
"""

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request


# SSL 上下文（Windows 证书问题解决）
try:
    _ssl_ctx = ssl._create_unverified_context()
except Exception:
    _ssl_ctx = None


def _urlopen(url, timeout=15, headers=None):
    """带 SSL 降级的 URL 打开函数"""
    req_headers = {
        'User-Agent': 'AI-News-Tracker/1.0',
    }
    if headers:
        req_headers.update(headers)
    # 如果是 GitHub API 请求，添加 API 版本头
    if 'api.github.com' in url:
        req_headers['Accept'] = 'application/vnd.github.v3+json'

    req = urllib.request.Request(url, headers=req_headers)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if 'certificate' in str(e).lower() and _ssl_ctx:
            print(f"  SSL 证书问题，尝试不验证模式...")
            return urllib.request.urlopen(req, context=_ssl_ctx, timeout=timeout)
        raise


def fetch_github_trending(top_n=20):
    """
    获取 GitHub 上 AI 相关热门项目
    使用 GitHub Search API 按 Stars 增速排序（最近发布的）

    参数：
        top_n: 返回项目数量
    返回：
        项目列表
    """
    projects = []
    days_back = 7

    # AI 相关搜索关键词 - 按 stars 排序获取最热门项目
    # GitHub Search API: q 参数搜索，sort=stars 按星标数排序
    queries = [
        "topic:llm",
        "topic:large-language-model",
        "topic:artificial-intelligence",
        "topic:machine-learning",
        "topic:deep-learning",
        "topic:nlp",
        "topic:computer-vision",
        "topic:rag",
        "topic:agentic",
        "topic:code-generation",
        "topic:ai-coding",
        "topic:gpt",
        "topic:claude",
        "topic:deepseek",
    ]

    seen_ids = set()

    for query in queries:
        if len(projects) >= top_n:
            break

        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=15"

        try:
            with _urlopen(url) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            for item in data.get('items', []):
                repo_id = item['id']
                if repo_id in seen_ids:
                    continue
                seen_ids.add(repo_id)

                # 提取第一主题作为分类
                topics = item.get('topics', [])
                primary_topic = topics[0] if topics else "AI"

                # 判断编程语言
                language = item.get('language', 'Unknown') or 'Unknown'

                project = {
                    "id": repo_id,
                    "name": item['full_name'],
                    "title": item['full_name'],
                    "title_cn": "",
                    "description": item.get('description') or "暂无描述",
                    "description_cn": "",
                    "url": item['html_url'],
                    "stars": item.get('stargazers_count', 0),
                    "forks": item.get('forks_count', 0),
                    "language": language,
                    "topics": topics[:5],
                    "primary_category": primary_topic,
                    "owner": item['owner']['login'],
                    "owner_avatar": item['owner']['avatar_url'],
                    "created_at": item.get('created_at', ''),
                    "updated_at": item.get('updated_at', ''),
                    "source": "GitHub",
                    "type": "project",
                }
                projects.append(project)

        except Exception as e:
            print(f"查询 '{query}' 失败: {e}")

        # 控制请求频率
        time.sleep(0.5)

    # 如果获取的项目太多，按 Stars 排序截取
    projects.sort(key=lambda x: x['stars'], reverse=True)

    print(f"获取到 {len(projects)} 个 GitHub 热门项目")
    return projects[:top_n]


def fetch_trending_repositories(language="", since="weekly"):
    """
    从 GitHub Trending 页面获取趋势项目（备用方案）
    参数：
        language: 编程语言过滤
        since: 时间范围 (daily/weekly/monthly)
    返回：
        项目列表
    """
    # 使用 github-trending-api 非官方 API
    url = "https://github-trending-api.com/repositories"
    params = {}
    if language:
        params['language'] = language
    if since:
        params['since'] = since

    try:
        if params:
            url += "?" + urllib.parse.urlencode(params)

        with _urlopen(url) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        projects = []
        for item in data[:30]:
            project = {
                "id": item.get('repoName', ''),
                "name": item.get('fullname', ''),
                "title": item.get('fullname', ''),
                "title_cn": "",
                "description": item.get('description') or "暂无描述",
                "description_cn": "",
                "url": item.get('url', ''),
                "stars": item.get('stars', 0),
                "forks": item.get('forks', 0),
                "language": item.get('language', 'Unknown') or 'Unknown',
                "topics": item.get('topics', []),
                "primary_category": item.get('language', 'AI') or 'AI',
                "owner": item.get('author', ''),
                "owner_avatar": item.get('avatar', ''),
                "created_at": "",
                "updated_at": "",
                "source": "GitHub",
                "type": "project",
            }
            projects.append(project)

        print(f"从 Trending API 获取到 {len(projects)} 个项目")
        return projects

    except Exception as e:
        print(f"获取 Trending 页面失败: {e}")
        return []


if __name__ == "__main__":
    # 测试采集
    projects = fetch_github_trending(top_n=5)
    for p in projects[:3]:
        print(f"\n项目: {p['name']}")
        print(f"描述: {p['description'][:60]}...")
        print(f"Stars: {p['stars']}")
        print(f"语言: {p['language']}")
