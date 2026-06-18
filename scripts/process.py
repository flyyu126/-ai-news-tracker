"""
数据处理模块
功能：合并去重、提取关键词、自动打标签、热度计算、生成标签云和榜单
"""

import datetime
import json
import os
import re
from collections import Counter


# 领域关键词映射表
CATEGORY_KEYWORDS = {
    "大模型/LLM": [
        "large language model", "llm", "llms", "gpt", "gpt-4", "gpt-5", "chatgpt", "claude",
        "gemini", "llama", "alpaca", "vicuna", "mistral", "qwen", "baichuan", "glm", "chatglm",
        "yi-", "deepseek", "moonshot", "kimi", "ernie", "tongyi", "spark",
        "token", "prompt", "chain-of-thought", "cot", "instruction tuning", "rlhf",
        "reinforcement learning from human feedback", "supervised fine-tuning", "sft",
        "few-shot", "zero-shot", "in-context learning", "context window",
        "大模型", "大语言模型", "大模型", "语言模型", "对话模型", "预训练模型",
        "提示工程", "上下文学习", "指令微调", "模型对齐",
    ],
    "NLP": [
        "natural language processing", "nlp", "transformer", "bert", "text generation",
        "machine translation", "sentiment analysis", "named entity", "ner", "sequence",
        "attention mechanism", "self-attention", "word embedding",
        "自然语言", "语义理解", "文本生成", "机器翻译", "情感分析", "命名实体",
    ],
    "CV/计算机视觉": [
        "computer vision", "image recognition", "object detection", "segmentation",
        "visual", "cnn", "convolutional", "face recognition", "video understanding",
        "diffusion model", "vae", "3d reconstruction", "image generation",
        "resnet", "yolo", "vit", "vision transformer", "stable diffusion", "dall-e",
        "计算机视觉", "图像", "检测", "识别", "视频", "目标检测", "图像生成",
    ],
    "强化学习": [
        "reinforcement learning", "rl", "reward", "policy gradient", "q-learning",
        "deep reinforcement", "multi-agent", "game", "control",
        "强化学习", "奖励", "策略", "智能体",
    ],
    "语音技术": [
        "speech recognition", "text-to-speech", "tts", "voice", "audio",
        "speaker", "waveform", "whisper", "语音", "声学", "语音识别",
    ],
    "多模态": [
        "multimodal", "vision-language", "image-text", "video-text", "clip",
        "multi-modal", "vlm", "vision-language model", "多模态", "图文理解",
    ],
    "模型压缩/部署": [
        "quantization", "pruning", "distillation", "compression", "efficient",
        "lightweight", "onnx", "tensorrt", "边缘计算", "量化", "剪枝", "蒸馏", "边缘部署",
    ],
    "AI安全/对齐": [
        "alignment", "ai safety", "bias", "fairness", "robustness",
        "adversarial", "privacy", "jailbreak", "red team",
        "安全", "对齐", "偏见", "隐私", "红队",
    ],
    "机器人": [
        "robot", "robotics", "manipulation", "navigation", "slam",
        "grasp", "dexterous", "embodied", "具身智能", "机器人",
        "机械臂", "自主导航", "人形机器人",
    ],
    "知识图谱": [
        "knowledge graph", "knowledge base", "triple", "entity",
        "relation extraction", "知识图谱", "知识库", "知识增强",
    ],
    "AI应用": [
        "healthcare", "medical", "drug", "biology", "finance", "legal",
        "code generation", "coding", "program synthesis", "autonomous driving",
        "自动驾驶", "医疗", "金融", "教育", "代码生成", "法律",
    ],
    "数据集/评估": [
        "data augmentation", "dataset", "benchmark", "evaluation",
        "synthetic data", "数据增强", "数据集", "评测", "基准",
    ],
    "模型训练/优化": [
        "training", "fine-tuning", "transfer learning", "meta-learning",
        "self-supervised", "pre-training", "optimization", "convergence",
        "训练", "微调", "预训练", "迁移学习", "优化器",
    ],
    # 新增：具体 AI 模型动态（GPT/Claude/DeepSeek 等）
    "模型动态/AI编程": [
        # 闭源模型
        "gpt-4o", "gpt-4", "gpt-5", "chatgpt", "openai o1", "openai o3",
        "claude", "claude sonnet", "claude opus", "claude haiku",
        "gemini", "gemini ultra", "gemini pro", "gemini flash",
        "grok", "grok-3",
        # 国产模型
        "deepseek", "deepseek-r1", "deepseek-v2", "deepseek-v3",
        "qwen", "qwen2", "qwen2.5", "通义千问",
        "glm", "glm-4", "glm-5", "chatglm", "智谱",
        "kimi", "moonshot", "月之暗面",
        "yi", "零一万物",
        "ernie", "文心一言", "百度文心",
        "tongyi", "通义",
        "spark", "讯飞星火",
        "doubao", "豆包", "字节跳动",
        "baichuan", "百川",
        "minimax",
        "step", "阶跃星辰",
        # 开源模型
        "llama", "llama-3", "llama-4", "meta llama",
        "mistral", "mixtral",
        "fable", "claude fable",
        # AI 编程工具
        "github copilot", "copilot",
        "cursor", "cursor ai",
        "windsurf", "codeium",
        "claude code", "codex",
        "devinci", "replit",
        "通义灵码", "codeqwen",
        "ai编程", "编程助手", "代码生成",
        # AI 公司
        "openai", "anthropic", "google deepmind", "meta ai",
        "智谱ai", "深度求索", "deepseek", "百川智能", "月之暗面",
    ],
}


def extract_keywords(text, top_n=5):
    """
    从文本中提取关键词
    参数：
        text: 输入文本（中英文混合）
        top_n: 返回的关键词数量
    返回：
        关键词列表
    """
    if not text:
        return []

    text = text.lower()

    # 提取英文单词（至少 3 个字符）
    words = re.findall(r'\b[a-z]{3,}\b', text)

    # 过滤常见英文停用词
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'on', 'and',
                  'or', 'with', 'from', 'by', 'at', 'this', 'that', 'we', 'our', 'their', 'its',
                  'it', 'as', 'be', 'been', 'has', 'have', 'had', 'do', 'does', 'did', 'but',
                  'not', 'what', 'which', 'who', 'how', 'when', 'where', 'than', 'then', 'also',
                  'these', 'those', 'can', 'may', 'will', 'would', 'could', 'should', 'about',
                  'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
                  'such', 'each', 'all', 'both', 'few', 'more', 'most', 'some', 'any',
                  'no', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'because',
                  'out', 'up', 'down', 'off', 'over', 'under', 'again', 'further', 'once'}
    words = [w for w in words if w not in stop_words]

    # 过滤噪声英文词（常见无实际意义的学术/框架词/HTML残留）
    noise_english = {'based', 'using', 'data', 'domain', 'large', 'show', 'method',
                     'model', 'result', 'propose', 'approach', 'different', 'however',
                     'also', 'well', 'way', 'three', 'can', 'given', 'used', 'make',
                     'performance', 'experiment', 'task', 'set', 'paper',
                     'present', 'proposed', 'novel', 'introduce', 'experimental',
                     'state', 'art', 'existing', 'within', 'without', 'including',
                     'img', 'src', 'alt', 'href', 'class', 'width', 'height',
                     'style', 'https', 'http', 'com', 'www', 'html', 'div', 'span',
                     'vmark', 'strong', 'title', 'more', 'utf', 'jpg', 'view',
                     'topic', 'switch', 'app', 'xiaomi', 'ultra', 'report', 'image',
                     'text', 'list', 'item', 'header', 'footer', 'button', 'label'}
    words = [w for w in words if w not in noise_english]

    # 提取中文短语（2-6 个字的组合，包含"大模型""语言模型"等更长词组）
    chinese_words = re.findall(r'[一-鿿]{2,6}', text)

    # 过滤中文噪声词
    noise_chinese = {'一个', '可以', '进行', '用于', '提出', '方法', '问题', '我们',
                     '使用', '通过', '基于', '实现', '结果', '不同', '之间',
                     '利用', '相关', '需要', '具有', '其中', '以及', '其他',
                     '但是', '因为', '所以', '如果', '没有', '还是',
                     '刚刚', '发布', '工厂', '一座', '目标', '通了', '国产',
                     '拿下', '因此', '美元融资', '北京建了'}
    chinese_words = [w for w in chinese_words if w not in noise_chinese]

    # 统计词频
    word_counter = Counter(words + chinese_words)

    # 返回前 top_n 个关键词
    keywords = [w for w, _ in word_counter.most_common(top_n)]
    return keywords


def auto_tag(item):
    """
    根据标题和摘要自动判断领域标签
    参数：
        item: 数据条目（包含 title、summary 等字段）
    返回：
        标签列表
    """
    # 合并标题和摘要用于匹配
    title = (item.get('title', '') + ' ' + item.get('title_cn', '')).lower()
    summary = (item.get('summary', '') + ' ' + item.get('summary_cn', '')).lower()

    tags = []

    # 1. 从 arXiv 分类映射基础标签
    if 'categories' in item and item['categories']:
        arxiv_map = {
            'cs.CL': 'NLP/大模型', 'cs.AI': 'AI', 'cs.LG': '机器学习',
            'cs.CV': 'CV', 'cs.NE': '神经网络', 'cs.RO': '机器人',
            'cs.IR': '信息检索', 'cs.MM': '多模态',
        }
        for cat in item['categories']:
            if cat in arxiv_map and arxiv_map[cat] not in tags:
                tags.append(arxiv_map[cat])

    # 2. 再用关键词匹配补充更具体的标签（如大模型/LLM）
    text = title + ' ' + summary
    matched_tags = []
    for tag, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                matched_tags.append(tag)
                break

    # 3. 合并 arXiv 标签和关键词匹配标签
    for t in matched_tags:
        if t not in tags:
            tags.append(t)

    return tags if tags else ["AI综合"]


def calculate_hot_score(item, base_score=50):
    """
    计算热度分数
    综合多个因素：来源权重、时效性、互动数据
    参数：
        item: 数据条目
        base_score: 基础分数
    返回：
        热度分数（0-100）
    """
    score = base_score

    # 来源权重
    source_weights = {
        'arXiv': 60,      # 学术论文
        '机器之心': 70,    # 专业 AI 媒体
        '量子位': 70,      # 专业 AI 媒体
        'GitHub': 50,     # 开源项目
    }
    score += source_weights.get(item.get('source', ''), 50)

    # GitHub 项目根据 Star 数加分
    if item.get('source') == 'GitHub':
        stars = item.get('stars', 0)
        if stars > 10000:
            score += 40
        elif stars > 5000:
            score += 30
        elif stars > 1000:
            score += 20
        elif stars > 100:
            score += 10

    # 时间衰减因子：越新的文章分数越高
    published = item.get('published', '')
    if published:
        try:
            if 'T' in published:
                pub_date = datetime.datetime.fromisoformat(published.split('T')[0])
            elif ' ' in published:
                pub_date = datetime.datetime.strptime(published.split(' ')[0], '%Y-%m-%d')
            else:
                pub_date = datetime.datetime.strptime(published[:10], '%Y-%m-%d')

            days_ago = (datetime.datetime.now() - pub_date).days
            time_factor = max(0, 1 - days_ago * 0.1)  # 每天衰减 10%
            score = score * (0.5 + 0.5 * time_factor)
        except:
            pass

    return round(min(max(score, 0), 100), 1)  # 限制在 0-100 之间


def deduplicate(items, title_key='title', threshold=0.7):
    """
    简单的标题去重
    参数：
        items: 数据条目列表
        title_key: 用于比较的标题字段
        threshold: 相似度阈值
    返回：
        去重后的列表
    """
    if not items:
        return []

    def text_similarity(t1, t2):
        """简单的基于字符集合的相似度计算"""
        if not t1 or not t2:
            return 0
        t1, t2 = t1.lower(), t2.lower()
        # 提取英文单词和中文短语
        set1 = set(re.findall(r'\b\w+\b', t1)) | set(re.findall(r'[一-鿿]+', t1))
        set2 = set(re.findall(r'\b\w+\b', t2)) | set(re.findall(r'[一-鿿]+', t2))
        if not set1 or not set2:
            return 0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0

    unique = []
    for item in items:
        title = item.get(title_key, '')
        is_dup = False
        for existing in unique:
            if text_similarity(title, existing.get(title_key, '')) > threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(item)

    return unique


def generate_tag_cloud(all_items):
    """
    生成关键词云数据
    参数：
        all_items: 所有数据条目
    返回：
        标签云列表 [{name, count, weight}]
    """
    all_tags = []
    all_keywords = []

    for item in all_items:
        tags = item.get('tags', [])
        all_tags.extend(tags)
        keywords = item.get('keywords', [])
        all_keywords.extend(keywords)

    # 统计标签频次
    tag_counts = Counter(all_tags)

    # 统计关键词频次
    keyword_counts = Counter(all_keywords)

    # 合并标签云
    tag_cloud = []

    for tag, count in tag_counts.most_common(20):
        tag_cloud.append({
            "name": tag,
            "count": count,
            "weight": min(count * 10, 100),
            "type": "tag",
        })

    for keyword, count in keyword_counts.most_common(30):
        # 避免与标签重复
        if not any(t['name'] == keyword for t in tag_cloud):
            tag_cloud.append({
                "name": keyword,
                "count": count,
                "weight": min(count * 5, 80),
                "type": "keyword",
            })

    # 按权重排序
    tag_cloud.sort(key=lambda x: x['weight'], reverse=True)
    return tag_cloud[:40]  # 最多 40 个


def process_all_data(papers, news, github_projects, output_dir):
    """
    处理所有数据：合并、去重、打标签、计算热度
    参数：
        papers: 论文列表
        news: 新闻列表
        github_projects: GitHub 项目列表
        output_dir: 输出目录
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n=== 开始处理数据 ({timestamp}) ===")

    # 1. 为每类数据打标签、提取关键词
    print("正在打标签和提取关键词...")
    for item in papers + news + github_projects:
        item['tags'] = auto_tag(item)
        combined_text = (item.get('title', '') + ' ' + item.get('title_cn', '') + ' ' +
                        item.get('summary', '') + ' ' + item.get('summary_cn', ''))
        item['keywords'] = extract_keywords(combined_text)
        item['hot_score'] = calculate_hot_score(item)

    # 2. 按类型去重
    print("正在去重...")
    unique_papers = deduplicate(papers)
    unique_news = deduplicate(news)
    unique_github = deduplicate(github_projects)

    # 过滤非目标分类的 arXiv 论文（只保留 AI 相关分类）
    target_cats = {'cs.AI', 'cs.CL', 'cs.LG', 'cs.CV', 'cs.NE', 'cs.RO', 'cs.IR', 'cs.MM', 'stat.ML'}
    before = len(unique_papers)
    unique_papers = [p for p in unique_papers if (
        p.get('source') != 'arXiv' or  # 非 arXiv 来源全部保留
        p.get('primary_category') in target_cats  # arXiv 论文只保留目标分类
    )]
    filtered = before - len(unique_papers)
    if filtered > 0:
        print(f"过滤了 {filtered} 篇非 AI 分类的 arXiv 论文")

    # 3. 合并所有数据
    all_items = unique_papers + unique_news + unique_github

    # 4. 生成标签云
    print("正在生成标签云...")
    tag_cloud = generate_tag_cloud(all_items)

    # 5. 生成热度榜单（按热度排序）
    print("正在生成热度榜单...")
    hot_ranking = sorted(all_items, key=lambda x: x.get('hot_score', 0), reverse=True)
    # 移除过长的内容
    for item in hot_ranking:
        for field in ['summary', 'summary_cn']:
            if field in item and isinstance(item[field], str) and len(item[field]) > 300:
                item[field] = item[field][:300] + '...'

    # 6. 生成每日摘要
    daily_summary = {
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "update_time": timestamp,
        "total_items": len(all_items),
        "papers_count": len(unique_papers),
        "news_count": len(unique_news),
        "github_count": len(unique_github),
        "hot_ranking": hot_ranking[:30],  # 前 30 条
        "tag_cloud": tag_cloud,
        "papers": unique_papers,
        "news": unique_news,
        "github_projects": unique_github,
    }

    # 7. 写入文件
    os.makedirs(output_dir, exist_ok=True)

    # 主数据文件（合并所有）
    main_path = os.path.join(output_dir, 'all_data.json')
    with open(main_path, 'w', encoding='utf-8') as f:
        json.dump(daily_summary, f, ensure_ascii=False, indent=2)

    # 按类型拆分
    for key in ['papers', 'news', 'github_projects']:
        file_path = os.path.join(output_dir, f'{key}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"items": daily_summary[key], "update_time": timestamp}, f, ensure_ascii=False, indent=2)

    # 标签云
    cloud_path = os.path.join(output_dir, 'tag_cloud.json')
    with open(cloud_path, 'w', encoding='utf-8') as f:
        json.dump({"tags": tag_cloud, "update_time": timestamp}, f, ensure_ascii=False, indent=2)

    # 热度榜单
    ranking_path = os.path.join(output_dir, 'hot_ranking.json')
    with open(ranking_path, 'w', encoding='utf-8') as f:
        json.dump({"items": hot_ranking[:30], "update_time": timestamp}, f, ensure_ascii=False, indent=2)

    print(f"\n处理完成！共 {len(all_items)} 条数据")
    print(f"  论文: {len(unique_papers)} 篇")
    print(f"  新闻: {len(unique_news)} 篇")
    print(f"  GitHub: {len(unique_github)} 个项目")
    print(f"  标签云: {len(tag_cloud)} 个标签/关键词")
    print(f"数据已写入: {output_dir}")

    return daily_summary


if __name__ == "__main__":
    # 测试处理功能
    sample_papers = [
        {"id": "test1", "title": "Large Language Models are Few-Shot Learners", "summary": "We demonstrate that scaling up language models improves few-shot performance.",
         "source": "arXiv", "type": "paper", "published": "2026-06-10"},
        {"id": "test2", "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition", "summary": "We apply transformers directly to image patches.",
         "source": "arXiv", "type": "paper", "published": "2026-06-12"},
    ]
    sample_news = [
        {"id": "n1", "title": "OpenAI 发布 GPT-5，性能全面超越前代", "source": "机器之心", "type": "news"},
        {"id": "n2", "title": "谷歌 DeepMind 推出新一代蛋白质预测模型", "source": "量子位", "type": "news"},
    ]
    sample_github = [
        {"id": "g1", "name": "langchain-ai/langchain", "title": "langchain-ai/langchain", "description": "Building applications with LLMs",
         "stars": 85000, "source": "GitHub", "type": "project"},
    ]

    process_all_data(sample_papers, sample_news, sample_github, "../data")
