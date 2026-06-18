"""
数据质量分析脚本
功能：分析采集到的数据质量，输出详细报告
"""
import json
from collections import Counter

def analyze():
    """分析数据质量并打印报告"""
    print("=" * 70)
    print("📊 AI 热点追踪 - 数据质量分析报告")
    print(f"生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    data_dir = r'G:\AiCreate\AIReport\ai-news-tracker\frontend\public\data'

    # ===== 论文分析 =====
    with open(f'{data_dir}/papers.json', encoding='utf-8') as f:
        papers = json.load(f)['items']

    print(f'\n【📄 论文】共 {len(papers)} 篇')

    # 分类分布
    cats = Counter(p.get('primary_category', '?') for p in papers)
    cat_str = ', '.join(f'{c}({n})' for c, n in cats.most_common())
    print(f'  分类分布: {cat_str}')

    # 非目标分类
    target_cats = {'cs.AI', 'cs.CL', 'cs.LG', 'cs.CV', 'cs.NE', 'cs.RO', 'cs.IR'}
    non_ai = [p for p in papers if p['primary_category'] not in target_cats]
    if non_ai:
        print(f'  非目标分类: {", ".join(p["primary_category"] for p in non_ai)}')
        print(f'    (这些论文来自其他领域，相关性不足)')

    # 完整性检查
    missing = {}
    for field in ['title', 'summary', 'categories', 'tags', 'published', 'link']:
        count = sum(1 for p in papers if not p.get(field))
        if count > 0:
            missing[field] = count
    if missing:
        print(f'  字段缺失: {missing}')
    else:
        print(f'  字段完整性: ✅ 所有必填字段完整')

    # 标签分析
    tag_counts = Counter()
    for p in papers:
        for t in p.get('tags', []):
            tag_counts[t] += 1
    no_tag = sum(1 for p in papers if not p.get('tags'))
    avg_tags = sum(len(p.get('tags', [])) for p in papers) / len(papers)
    print(f'  无标签: {no_tag} 篇')
    print(f'  平均标签数: {avg_tags:.1f}')
    print(f'  标签分布: {", ".join(f"{t}({n})" for t,n in tag_counts.most_common(8))}')

    # cs.CL 论文质量
    cl_papers = [p for p in papers if p['primary_category'] == 'cs.CL']
    if cl_papers:
        print(f'  cs.CL(NLP/大模型): {len(cl_papers)} 篇')
        for p in cl_papers:
            tags = ', '.join(p.get('tags', []))
            print(f'    → [{tags}] {p["title"][:60]}')

    # 大模型论文检查
    llm_papers = [p for p in papers if '大模型/LLM' in p.get('tags', [])]
    print(f'  标记为大模型/LLM: {len(llm_papers)} 篇')

    print()

    # ===== 新闻分析 =====
    with open(f'{data_dir}/news.json', encoding='utf-8') as f:
        news = json.load(f)['items']

    print(f'【📰 新闻】共 {len(news)} 篇')
    srcs = Counter(n.get('source', '?') for n in news)
    for s, n in srcs.most_common():
        print(f'  来源: {s} → {n} 篇')

    # 质量检查
    no_url = [n for n in news if not n.get('url')]
    no_tags_news = [n for n in news if not n.get('tags')]
    no_time = [n for n in news if not n.get('published')]
    print(f'  缺链接: {len(no_url)} 篇')
    print(f'  缺标签: {len(no_tags_news)} 篇')
    print(f'  缺时间: {len(no_time)} 篇')
    print(f'  平均标签数: {sum(len(n.get("tags",[])) for n in news)/len(news):.1f}')

    # 重复检查
    seen = set()
    dups = 0
    for n in news:
        key = n.get('title', '')[:15]
        if key in seen:
            dups += 1
        seen.add(key)
    print(f'  疑似重复: {dups} 篇' if dups else '  疑似重复: ✅ 无')

    # 头条新闻质量
    print(f'  头条新闻:')
    for n in news[:3]:
        tags = ', '.join(n.get('tags', []))
        print(f'    📰 {n["title"][:55]}')
        print(f'       tags: {tags}')

    print()

    # ===== GitHub 项目分析 =====
    with open(f'{data_dir}/github_projects.json', encoding='utf-8') as f:
        github = json.load(f)['items']

    print(f'【💻 GitHub】共 {len(github)} 个项目')

    stars = [p['stars'] for p in github]
    print(f'  Star范围: {min(stars):,} ~ {max(stars):,}')
    print(f'  总Stars: {sum(stars):,}')

    # AI相关性
    def is_ai_related(repo):
        text = (repo.get('description', '') + ' ' + repo.get('name', '') + ' ' +
                ' '.join(repo.get('topics', []))).lower()
        ai_kw = ['llm', 'language model', 'ai', 'machine learning', 'deep learning',
                 'agent', 'gpt', 'rag', 'transformer', 'neural', 'artificial intelligence']
        return any(kw in text for kw in ai_kw)

    ai_projects = [p for p in github if is_ai_related(p)]
    non_ai_projects = [p for p in github if not is_ai_related(p)]
    print(f'  AI相关项目: {len(ai_projects)}/{len(github)}')

    if non_ai_projects:
        print(f'  非AI项目:')
        for p in non_ai_projects:
            print(f'    ⚠️ {p["name"]} — {p.get("description", "?")[:40]}')

    # 语言分布
    langs = Counter(p.get('language', 'Unknown') for p in github)
    print(f'  语言分布: {", ".join(f"{l}({n})" for l,n in langs.most_common(5))}')

    tag_count_g = Counter()
    for p in github:
        for t in p.get('tags', []):
            tag_count_g[t] += 1
    print(f'  标签分布: {", ".join(f"{t}({n})" for t,n in tag_count_g.most_common(5))}')

    print()

    # ===== 标签云质量 =====
    with open(f'{data_dir}/tag_cloud.json', encoding='utf-8') as f:
        tc = json.load(f)

    print(f'【🏷️ 标签云】共 {len(tc["tags"])} 个条目')
    domain_tags = [t for t in tc['tags'] if t.get('type') == 'tag']
    keywords = [t for t in tc['tags'] if t.get('type') == 'keyword']
    print(f'  领域标签: {len(domain_tags)} 个')
    print(f'  词频关键词: {len(keywords)} 个')

    # 噪声关键词
    noise_words = {'刚刚', '工厂', '发布', 'based', 'using', 'data', '美元融资', '北京建了', '一座'}
    noise_found = [t for t in keywords if t['name'] in noise_words]
    if noise_found:
        print(f'  噪声关键词: {", ".join(t["name"] for t in noise_found)}')
        print(f'    (这些词来自新闻正文，无实际分析价值)')

    # 热门标签
    print(f'  热门标签 TOP 5:')
    for t in domain_tags[:5]:
        print(f'    {t["name"]:15s}  ×{t["count"]:2d}  权重{t["weight"]:3d}')

    print()

    # ===== 综合评分 =====
    print("=" * 70)
    print("📋 综合评价")
    print("=" * 70)

    score = 100
    issues = []

    # 1. 数量评分
    if len(papers) < 20:
        issues.append(f'❌ 论文数({len(papers)})偏少，理想值30+')
        score -= 10
    elif len(papers) < 30:
        issues.append(f'⚠️ 论文数({len(papers)})一般')
        score -= 5
    else:
        issues.append(f'✅ 论文数({len(papers)})充足')

    if len(news) < 15:
        issues.append(f'❌ 新闻数量不足({len(news)}篇)')
        score -= 10
    elif len(set(n.get('source') for n in news)) < 2:
        issues.append(f'⚠️ 新闻来源单一（只有{",".join(srcs)}）')
        score -= 5
    else:
        issues.append(f'✅ 新闻多源覆盖（{", ".join(f"{s}{n}篇" for s,n in srcs.most_common())}）')

    if len(github) < 10:
        issues.append(f'❌ GitHub项目数({len(github)})不足')
        score -= 5
    else:
        issues.append(f'✅ GitHub项目数({len(github)})适中')

    # 2. 质量评分
    if len(non_ai) > len(papers) * 0.2:
        issues.append(f'❌ 非AI论文占比较高({len(non_ai)}篇)')
        score -= 10

    if len(non_ai_projects) > 3:
        issues.append(f'⚠️ 有{len(non_ai_projects)}个非AI项目混入')
        score -= 5

    if 'IT之家' not in str(srcs) and '机器之心' not in str(srcs):
        issues.append(f'❌ IT之家和机器之心均无数据，需补充新闻源')
        score -= 10
    elif 'IT之家' not in str(srcs):
        pass  # 已有量子位+IT之家则正常

    # 3. 标签质量
    if any(t['name'] == '大模型/LLM' for t in tc['tags']):
        llm_tag = next(t for t in tc['tags'] if t['name'] == '大模型/LLM')
        rank = sum(1 for t in tc['tags'] if t['weight'] > llm_tag['weight']) + 1
        issues.append(f'✅ 大模型/LLM标签排名第{rank}，出现{llm_tag["count"]}次')
    else:
        issues.append('❌ 大模型/LLM标签缺失')
        score -= 15

    if noise_found:
        issues.append(f'⚠️ 有{len(noise_found)}个噪声词需要过滤')
        score -= 3

    # 4. 关键指标
    llm_paper_pct = len(llm_papers) / max(len(papers), 1) * 100
    issues.append(f'{"✅" if llm_paper_pct > 20 else "⚠️"} 大模型论文占比: {llm_paper_pct:.0f}%({len(llm_papers)}/{len(papers)})')

    avg_stars = sum(stars) / max(len(github), 1)
    issues.append(f'{"✅" if avg_stars > 10000 else "⚠️"} GitHub项目平均Stars: {avg_stars:,.0f}')

    issues.append(f'{"✅" if avg_tags > 1.5 else "⚠️"} 论文平均标签: {avg_tags:.1f}个')

    print()
    for issue in issues:
        print(f'  {issue}')

    print(f'\n  📊 总分: {score}/100')
    if score >= 80:
        print(f'  评级: 🟢 良好')
    elif score >= 60:
        print(f'  评级: 🟡 一般')
    else:
        print(f'  评级: 🔴 较差')

    print()

    # ===== 改进建议 =====
    print("=" * 70)
    print("🔧 改进建议")
    print("=" * 70)
    suggestions = []

    if 'IT之家' in str(srcs) or '机器之心' in str(srcs):
        pass  # 已有新闻源
    else:
        suggestions.append('1. 补充新闻源: 考虑加入36氪、虎嗅、雷锋网等AI频道')

    if len(non_ai) > 0:
        suggestions.append(f'2. arXiv过滤: 有{len(non_ai)}篇非目标分类论文混入，可在process.py中过滤')

    if noise_found:
        suggestions.append(f'3. 关键词清洗: 在extract_keywords()中补充噪声过滤词列表')

    suggestions.append('4. 翻译缺失: 配置百度翻译API后可获得中文标题/摘要，提升可读性')

    if 'cs.CL' in cats and cats['cs.CL'] < 5:
        suggestions.append('5. cs.CL论文量偏少，可增加max_results值')

    if not suggestions:
        suggestions.append('🎉 所有指标正常，暂无改进项')

    for s in suggestions:
        print(f'  {s}')

    print()


if __name__ == '__main__':
    analyze()
