"""
新闻采集模块
功能：抓取国内 AI 新闻网站（机器之心、量子位）的最新文章

数据来源：
  - 机器之心: https://www.jiqizhixin.com/（AI 科技媒体）
  - 量子位: https://www.qbitai.com/（AI 科技媒体）
  如页面结构变化导致抓取失败，请检查并更新 CSS 选择器
"""

import datetime
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser


# 创建宽松的 SSL 上下文（解决 Windows 证书问题）
try:
    _ssl_context = ssl._create_unverified_context()
except Exception:
    _ssl_context = None


class SimpleHTMLParser(HTMLParser):
    """
    简易 HTML 解析器，用于提取关键信息
    比 BeautifulSoup 轻量，但这里我们仍然使用 BeautifulSoup 进行更稳健的解析
    """
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_parts.append(text)

    def get_text(self):
        return ' '.join(self.text_parts)


def parse_relative_time(time_str):
    """
    将相对时间字符串转换为绝对时间字符串
    例如："45分钟前" → "2026-06-18 13:30:00"
    参数：
        time_str: 相对时间字符串
    返回：
        ISO 格式时间字符串，解析失败返回空字符串
    """
    if not time_str:
        return ""
    time_str = time_str.strip()
    now = datetime.datetime.now()

    try:
        if '分钟' in time_str:
            minutes = int(re.search(r'(\d+)', time_str).group(1))
            pub_time = now - datetime.timedelta(minutes=minutes)
        elif '小时' in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            pub_time = now - datetime.timedelta(hours=hours)
        elif '天' in time_str:
            days = int(re.search(r'(\d+)', time_str).group(1))
            pub_time = now - datetime.timedelta(days=days)
        elif '昨天' in time_str:
            pub_time = now - datetime.timedelta(days=1)
            # 尝试解析具体时间，如 "昨天 10:30"
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                pub_time = pub_time.replace(hour=int(time_match.group(1)), minute=int(time_match.group(2)), second=0)
        elif '前天' in time_str:
            pub_time = now - datetime.timedelta(days=2)
        else:
            # 尝试直接解析标准日期格式
            try:
                pub_time = datetime.datetime.strptime(time_str, '%Y-%m-%d')
            except:
                return time_str  # 保持原文

        return pub_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return time_str


def fetch_url(url, timeout=15):
    """
    通用 URL 获取函数
    参数：
        url: 目标 URL
        timeout: 超时秒数
    返回：
        HTML 文本，失败返回 None
    """
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.URLError as ssl_err:
            if 'certificate' in str(ssl_err).lower() and _ssl_context:
                print(f"SSL 证书验证失败，尝试不验证模式...")
                resp = urllib.request.urlopen(req, context=_ssl_context, timeout=timeout)
            else:
                raise
        html = resp.read().decode('utf-8', errors='replace')
        return html
    except Exception as e:
        print(f"获取 {url} 失败: {e}")
        return None


def parse_jiqizhixin_articles(html):
    """
    解析机器之心首页文章列表
    参数：
        html: 页面 HTML
    返回：
        文章列表
    """
    articles = []

    if not html or len(html) < 1000:
        print("机器之心首页内容过短，可能触发了反爬机制")
        return articles

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # 方式1：从所有标题标签提取
        # 查找 h2/h3/h4 中的文章标题
        for header_tag in ['h2', 'h3', 'h4']:
            for tag in soup.find_all(header_tag):
                title = tag.get_text().strip()
                if len(title) < 8:
                    continue
                # 找最近的链接
                link_tag = tag.find('a') if tag.name != 'a' else tag
                if not link_tag or not link_tag.get('href'):
                    # 向父级找链接
                    parent = tag.find_parent('a')
                    if parent and parent.get('href'):
                        link_tag = parent

                href = link_tag.get('href', '') if link_tag else ''
                if not href and tag.name == 'a' and tag.get('href'):
                    href = tag.get('href', '')

                if href and not href.startswith('http') and not href.startswith('//'):
                    href = f"https://www.jiqizhixin.com{href}" if href.startswith('/') else f"https://www.jiqizhixin.com/{href}"

                # 跳过非文章链接
                if any(skip in title for skip in ['登录', '注册', '关于', '联系']):
                    continue

                article_id = f"jqz_{hash(href or title) & 0xFFFFFFFF}"
                if not any(a['id'] == article_id for a in articles):
                    articles.append({
                        "id": article_id,
                        "title": title,
                        "title_cn": title,
                        "summary": "",
                        "summary_cn": "",
                        "url": href,
                        "published": "",
                        "source": "机器之心",
                        "source_url": "https://www.jiqizhixin.com",
                        "type": "news",
                    })

        # 方式2：从所有链接查找（补充）
        links = soup.find_all('a', href=True)
        seen_urls = {a['url'] for a in articles}
        for link in links:
            href = link['href']
            if not href.startswith('http') and not href.startswith('/'):
                continue
            # 过滤非文章链接
            if not any(kw in href.lower() for kw in ['article', 'post', '/articles/']):
                continue
            full_url = href if href.startswith('http') else f"https://www.jiqizhixin.com{href}"
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            title = link.get_text().strip()
            if len(title) < 8:
                continue
            articles.append({
                "id": f"jqz_{hash(full_url) & 0xFFFFFFFF}",
                "title": title,
                "title_cn": title,
                "summary": "",
                "summary_cn": "",
                "url": full_url,
                "published": "",
                "source": "机器之心",
                "source_url": "https://www.jiqizhixin.com",
                "type": "news",
            })

    except ImportError:
        print("警告: 未安装 BeautifulSoup，使用正则提取")
        _extract_articles_regex(html, articles, '机器之心', 'https://www.jiqizhixin.com')

    except Exception as e:
        print(f"解析机器之心文章失败: {e}")

    # 去除可能的重复
    seen = set()
    unique_articles = []
    for a in articles:
        title_key = a['title'][:30]
        if title_key not in seen:
            seen.add(title_key)
            unique_articles.append(a)

    print(f"从机器之心获取到 {len(unique_articles)} 篇文章")
    return unique_articles[:20]


def _extract_articles_regex(html, articles, source_name, base_url):
    """使用正则表达式从 HTML 中提取文章信息的通用方法"""
    # 提取所有 h2/h3/h4 内容
    for pattern in [r'<h2[^>]*>(.*?)</h2>', r'<h3[^>]*>(.*?)</h3>', r'<h4[^>]*>(.*?)</h4>']:
        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            content = match.group(1)
            # 提取其中的链接和标题
            link_match = re.search(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', content, re.DOTALL)
            if link_match:
                url, title = link_match.groups()
                title = re.sub(r'<[^>]+>', '', title).strip()
                if len(title) >= 8:
                    full_url = url if url.startswith('http') else f"{base_url}{url}"
                    article_id = f"rss_{hash(full_url) & 0xFFFFFFFF}"
                    if not any(a.get('url') == full_url for a in articles):
                        articles.append({
                            "id": article_id,
                            "title": title,
                            "title_cn": title,
                            "url": full_url,
                            "source": source_name,
                            "source_url": base_url,
                            "type": "news",
                        })


def parse_qbitai_articles(html):
    """
    解析量子位首页文章列表
    参数：
        html: 页面 HTML
    返回：
        文章列表
    """
    articles = []

    if not html or len(html) < 1000:
        return articles

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # 从页面中提取所有文章卡片: 容器 div.text_box > h4(标题) + div.info > span.time(时间)
        for header_tag in ['h2', 'h3', 'h4']:
            for tag in soup.find_all(header_tag):
                title = tag.get_text().strip()
                if len(title) < 8:
                    continue

                # 跳过非文章链接
                if tag.find('a') is None:
                    continue

                # 提取链接
                link_tag = tag.find('a') if tag.name != 'a' else tag
                href = ""
                if link_tag and link_tag.get('href'):
                    href = link_tag['href']
                elif tag.get('href'):
                    href = tag['href']

                if href and not href.startswith('http'):
                    href = f"https://www.qbitai.com{href}" if href.startswith('/') else f"https://www.qbitai.com/{href}"

                # 获取发布时间：从父容器 text_box 中查找 span.time
                published = ""
                for parent_cls in ['text_box', 'col', 'item', 'post']:
                    parent = tag.find_parent('div', class_=lambda c: c and parent_cls in c.lower())
                    if parent:
                        time_el = parent.find('span', class_='time')
                        if time_el:
                            published = parse_relative_time(time_el.get_text(strip=True))
                            break

                article_id = f"qbt_{hash(href or title) & 0xFFFFFFFF}"
                if not any(a['id'] == article_id for a in articles):
                    articles.append({
                        "id": article_id,
                        "title": title,
                        "title_cn": title,
                        "summary": "",
                        "summary_cn": "",
                        "url": href,
                        "published": published,
                        "source": "量子位",
                        "source_url": "https://www.qbitai.com",
                        "type": "news",
                    })

        # 也从所有链接中补充
        all_links = soup.find_all('a', href=True)
        seen_urls = {a['url'] for a in articles if a['url']}
        for link in all_links:
            href = link['href']
            title = link.get_text().strip()
            if len(title) < 8:
                continue
            if not href.startswith('http') and not href.startswith('/'):
                continue
            full_url = href if href.startswith('http') else f"https://www.qbitai.com{href}"
            if full_url in seen_urls:
                continue
            # 只看确实像文章页面的链接
            if not any(kw in full_url for kw in ['qbitai', 'archives', 'article', 'post']):
                continue
            seen_urls.add(full_url)
            articles.append({
                "id": f"qbt_{hash(full_url) & 0xFFFFFFFF}",
                "title": title,
                "title_cn": title,
                "summary": "",
                "summary_cn": "",
                "url": full_url,
                "source": "量子位",
                "source_url": "https://www.qbitai.com",
                "type": "news",
            })

    except ImportError:
        print("警告: 未安装 BeautifulSoup，使用正则提取")
        _extract_articles_regex(html, articles, '量子位', 'https://www.qbitai.com')

    except Exception as e:
        print(f"解析量子位文章失败: {e}")

    # 去重
    seen = set()
    unique = []
    for a in articles:
        key = a['title'][:30]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    print(f"从量子位获取到 {len(unique)} 篇文章")
    return unique[:20]


def parse_ithome_articles(html):
    """
    解析 IT之家 AI 标签页文章列表
    IT之家结构：<li> > <h2> > <a>标题 + <div.c data-ot="时间">
    参数：
        html: 页面 HTML
    返回：
        文章列表
    """
    articles = []

    if not html or len(html) < 5000:
        print("IT之家页面内容过短")
        return articles

    try:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html, 'lxml')

        # IT之家文章在 <li> 中，每个 <li> 包含 <h2> > <a> 标题 和 <div.c data-ot=""> 时间
        for li in soup.find_all('li'):
            h2 = li.find('h2')
            if not h2:
                continue
            a_tag = h2.find('a') if h2.find('a') else h2
            title = a_tag.get_text().strip() if a_tag.get_text() else ""
            href = a_tag.get('href', '') if a_tag else ""

            if len(title) < 8 or not href:
                continue

            if not href.startswith('http'):
                href = f"https://www.ithome.com{href}" if href.startswith('/') else f"https://www.ithome.com/{href}"

            # 提取发布时间
            published = ""
            c_div = li.find('div', class_='c')
            if c_div and c_div.has_attr('data-ot'):
                time_str = c_div['data-ot']
                try:
                    # data-ot 格式: "2026-06-18T11:25:20.6370000+08:00"
                    from datetime import datetime
                    dt = datetime.fromisoformat(time_str.replace('+08:00', '+08:00'))
                    published = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    published = time_str[:19]

            # 提取摘要（如果有 p 标签）
            summary = ""
            p_tag = li.find('p')
            if p_tag:
                summary = p_tag.get_text().strip()

            articles.append({
                "id": f"ith_{hash(href) & 0xFFFFFFFF}",
                "title": title,
                "title_cn": title,
                "summary": summary,
                "summary_cn": summary,
                "url": href,
                "published": published,
                "source": "IT之家",
                "source_url": "https://www.ithome.com",
                "type": "news",
            })

    except ImportError:
        print("警告: 未安装 BeautifulSoup")
        # 正则备用
        import re
        # 提取 h2 > a 标题
        for match in re.finditer(r'<h2[^>]*>.*?<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>.*?</h2>', html, re.DOTALL):
            href, title = match.groups()
            title = re.sub(r'<[^>]+>', '', title).strip()
            if len(title) >= 8:
                full_url = href if href.startswith('http') else f"https://www.ithome.com{href}"
                articles.append({
                    "id": f"ith_{hash(full_url) & 0xFFFFFFFF}",
                    "title": title,
                    "title_cn": title,
                    "summary": "",
                    "summary_cn": "",
                    "url": full_url,
                    "source": "IT之家",
                    "source_url": "https://www.ithome.com",
                    "type": "news",
                })

    except Exception as e:
        print(f"解析 IT之家文章失败: {e}")

    # 去重
    seen = set()
    unique = []
    for a in articles:
        key = a['title'][:20]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    print(f"从 IT之家获取到 {len(unique)} 篇文章")
    return unique[:20]


def fetch_all_news():
    """
    抓取所有新闻源的文章
    返回：
        合并后的文章列表
    """
    all_articles = []

    # 抓取 IT之家 AI 频道
    print("\n=== 正在抓取 IT之家 AI 频道 ===")
    ith_html = fetch_url("https://ithome.com/tag/ai")
    ith_articles = parse_ithome_articles(ith_html)
    all_articles.extend(ith_articles)
    time.sleep(1)

    # 抓取量子位
    print("\n=== 正在抓取量子位 ===")
    qbt_html = fetch_url("https://www.qbitai.com/")
    qbt_articles = parse_qbitai_articles(qbt_html)
    all_articles.extend(qbt_articles)
    time.sleep(1)

    # 尝试从 RSS 补充
    print("\n=== 尝试从 RSS 获取 ===")
    rss_sources = [
        ("IT之家", "https://ithome.com/rss"),
    ]

    for source_name, rss_url in rss_sources:
        try:
            rss_html = fetch_url(rss_url)
            if rss_html:
                from bs4 import BeautifulSoup
                rss_soup = BeautifulSoup(rss_html, 'xml')
                for item_tag in rss_soup.find_all('item'):
                    title_tag = item_tag.find('title')
                    link_tag = item_tag.find('link')
                    desc_tag = item_tag.find('description')
                    pub_date_tag = item_tag.find('pubDate')

                    title = title_tag.get_text().strip() if title_tag else ""
                    url = link_tag.get_text().strip() if link_tag else ""

                    if title and url and len(title) >= 5:
                        # 检查是否已存在
                        if not any(a['url'] == url for a in all_articles):
                            all_articles.append({
                                "id": f"rss_{hash(url) & 0xFFFFFFFF}",
                                "title": title,
                                "title_cn": title,
                                "summary": desc_tag.get_text().strip()[:200] if desc_tag else "",
                                "summary_cn": "",
                                "url": url,
                                "published": pub_date_tag.get_text().strip() if pub_date_tag else "",
                                "source": source_name,
                                "source_url": rss_url,
                                "type": "news",
                            })
        except Exception as e:
            print(f"RSS {rss_url} 解析失败: {e}")

    print(f"\n总共获取到 {len(all_articles)} 篇新闻文章")
    return all_articles


if __name__ == "__main__":
    articles = fetch_all_news()
    for a in articles[:5]:
        print(f"\n标题: {a['title'][:60]}")
        print(f"来源: {a['source']}")
        print(f"链接: {a['url'][:80]}")
