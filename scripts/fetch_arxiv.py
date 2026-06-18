"""
arXiv 论文采集模块
功能：通过 arXiv API 获取人工智能（cs.AI）和计算语言学（cs.CL）领域的最新论文
API 文档：https://info.arxiv.org/help/api/index.html
"""

import datetime
import json
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


# 创建可选的 SSL 上下文（解决 Windows 环境证书问题）
try:
    _ssl_context = ssl._create_unverified_context()
except Exception:
    try:
        _ssl_context = ssl.create_default_context()
        _ssl_context.check_hostname = False
        _ssl_context.verify_mode = ssl.CERT_NONE
    except Exception:
        _ssl_context = None


# arXiv API 地址
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# 关注的分类列表
CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV", "cs.NE", "cs.RO", "cs.IR"]

# XML 命名空间
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
}


def fetch_arxiv_papers(max_results=50, days_back=7):
    """
    获取 arXiv 最新论文
    参数：
        max_results: 最大获取数量
        days_back: 回溯天数
    返回：
        论文列表，每篇包含标题、摘要、作者、分类、发布时间、链接
    """
    all_papers = []

    # 按分类逐个获取，每个分类取少量，避免单次查询过大
    # 优先获取大模型相关的 cs.CL（计算语言学）
    category_groups = [
        ["cs.CL"],      # NLP / 大模型 主阵地 — 要最多
        ["cs.AI"],      # 通用 AI
        ["cs.LG"],      # 机器学习
        ["cs.CV"],      # 计算机视觉
    ]

    # 按分类重要性分配数量
    per_group = [min(max_results, 15), min(max_results, 12), 12, 12]
    # 确保总获取量不超过 max_results * 2
    total_fetch = sum(per_group)
    if total_fetch > max_results * 2:
        scale = (max_results * 2) / total_fetch
        per_group = [int(n * scale) for n in per_group]

    for idx, (group_cats, fetch_cnt) in enumerate(zip(category_groups, per_group)):
        if fetch_cnt <= 0:
            continue
        if idx > 0:
            time.sleep(2)

        cat_query = '+OR+'.join(f'cat:{cat}' for cat in group_cats)
        query = f'({cat_query})'
        url = f"{ARXIV_API_URL}?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={fetch_cnt}"

        print(f"正在获取 arXiv 论文（分类: {', '.join(group_cats)}）...")

        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; AI-News-Tracker/1.0; +https://github.com)'
            })
            # 使用不验证 SSL 证书的上下文（解决 Windows 证书问题）
            resp = urllib.request.urlopen(req, context=_ssl_context, timeout=60)
            with resp:
                xml_data = resp.read().decode('utf-8')

            root = ET.fromstring(xml_data)

            for entry in root.findall('atom:entry', NS):
                paper = parse_arxiv_entry(entry)
                if paper:
                    # 去重
                    if not any(p['id'] == paper['id'] for p in all_papers):
                        all_papers.append(paper)

        except urllib.error.HTTPError as http_err:
            if http_err.code == 429:
                print(f"  触发了限流，等待 5 秒后重试...")
                time.sleep(5)
                try:
                    resp = urllib.request.urlopen(req, context=_ssl_context, timeout=60)
                    with resp:
                        xml_data = resp.read().decode('utf-8')
                    root = ET.fromstring(xml_data)
                    for entry in root.findall('atom:entry', NS):
                        paper = parse_arxiv_entry(entry)
                        if paper and not any(p['id'] == paper['id'] for p in all_papers):
                            all_papers.append(paper)
                    print(f"  重试成功，获取到论文")
                except Exception as retry_err:
                    print(f"  重试也失败: {retry_err}")
            else:
                print(f"  HTTP 错误 {http_err.code}: {http_err.reason}")
        except Exception as e:
            print(f"  失败: {e}")

    # 按日期过滤
    if days_back > 0 and all_papers:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days_back)
        filtered = []
        for p in all_papers:
            try:
                pub_date = datetime.datetime.fromisoformat(p['published'].replace('Z', '+00:00'))
                if pub_date >= cutoff.replace(tzinfo=pub_date.tzinfo):
                    filtered.append(p)
            except:
                filtered.append(p)
        all_papers = filtered

    # 如果当前论文中具体模型（GPT/Claude等）不够多，补充搜索
    model_mentions = sum(1 for p in all_papers if any(kw in (p['title']+' '+p['summary']).lower()
        for kw in ['gpt', 'claude', 'deepseek', 'gemini', 'llama', 'mistral', 'copilot', 'code generation']))
    if model_mentions < max_results * 0.3 and max_results > 5 and len(all_papers) < max_results:
        need_more = min(max_results - len(all_papers), 8)
        print(f"  具体模型论文偏少({model_mentions}篇)，再补充 {need_more} 篇...")
        time.sleep(3)
        model_queries = [
            'ti:"large language model"', 'ti:gpt', 'ti:claude',
            'ti:gemini', 'ti:llama', 'ti:mistral',
            'code generation',
        ]
        for mq in model_queries:
            if len(all_papers) >= max_results:
                break
            url = f"{ARXIV_API_URL}?search_query=({mq})+AND+cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=3"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                resp = urllib.request.urlopen(req, context=_ssl_context, timeout=60)
                with resp:
                    root = ET.fromstring(resp.read().decode('utf-8'))
                for entry in root.findall('atom:entry', NS):
                    paper = parse_arxiv_entry(entry)
                    if paper and not any(p['id'] == paper['id'] for p in all_papers):
                        all_papers.append(paper)
                time.sleep(2)
            except Exception as e:
                print(f"  补充 '{mq}' 失败: {e}")

    # 按提交时间排序
    all_papers.sort(key=lambda p: p.get('published', ''), reverse=True)

    print(f"获取到 {len(all_papers)} 篇 arXiv 论文（{days_back} 天内）")
    return all_papers[:max_results]


def parse_arxiv_entry(entry):
    """
    解析单篇 arXiv 论文的 XML 条目
    参数：
        entry: XML 条目元素
    返回：
        论文信息字典
    """
    try:
        # 标题（移除换行符）
        title_el = entry.find('atom:title', NS)
        title = title_el.text.strip().replace('\n', ' ') if title_el is not None and title_el.text else ""

        # 摘要
        summary_el = entry.find('atom:summary', NS)
        summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None and summary_el.text else ""

        # 发布时间
        published_el = entry.find('atom:published', NS)
        published = published_el.text.strip() if published_el is not None and published_el.text else ""

        # 更新时间
        updated_el = entry.find('atom:updated', NS)
        updated = updated_el.text.strip() if updated_el is not None and updated_el.text else ""

        # arXiv 编号和链接
        id_el = entry.find('atom:id', NS)
        paper_id = ""
        link = ""
        if id_el is not None and id_el.text:
            link = id_el.text.strip()
            paper_id = link.split('/')[-1].split('v')[0]  # 提取 ID

        # 分类
        categories = []
        for cat in entry.findall('atom:category', NS):
            term = cat.get('term', '')
            if term:
                categories.append(term)

        # 作者
        authors = []
        for author in entry.findall('atom:author', NS):
            name_el = author.find('atom:name', NS)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        # 主要分类（第一个）
        primary_category = categories[0] if categories else ""

        # PDF 链接
        pdf_link = ""
        for link_el in entry.findall('atom:link', NS):
            if link_el.get('title') == 'pdf':
                pdf_link = link_el.get('href', '')
                break

        return {
            "id": paper_id,
            "title": title,
            "title_cn": "",  # 翻译后填充
            "summary": summary[:500],  # 截断过长的摘要
            "summary_cn": "",
            "authors": authors[:5],  # 只保留前 5 位作者
            "categories": categories,
            "primary_category": primary_category,
            "published": published,
            "updated": updated,
            "link": link,
            "pdf_link": pdf_link,
            "source": "arXiv",
            "type": "paper",
        }

    except Exception as e:
        print(f"解析论文条目失败: {e}")
        return None


if __name__ == "__main__":
    # 测试采集功能
    papers = fetch_arxiv_papers(max_results=5, days_back=30)
    for p in papers[:3]:
        print(f"\n标题: {p['title'][:80]}...")
        print(f"分类: {', '.join(p['categories'][:3])}")
        print(f"日期: {p['published']}")
