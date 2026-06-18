"""
主流程控制脚本
功能：依次执行采集 → 翻译 → 处理，生成最终数据文件
用法：python run_all.py [--output-dir ../frontend/public/data] [--no-translate]
"""

import argparse
import json
import os
import sys
import time


def run_script(module_name, func_name, *args, **kwargs):
    """
    动态运行指定模块的函数
    参数：
        module_name: 模块名
        func_name: 函数名
    返回：
        函数执行结果
    """
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        print(f"\n{'='*50}")
        print(f"执行: {module_name}.{func_name}")
        print(f"{'='*50}")
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        print(f"错误 [{module_name}.{func_name}]: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数 - 协调整个数据流程"""
    parser = argparse.ArgumentParser(description="AI 热点追踪 - 数据采集与处理")
    parser.add_argument('--output-dir', default='../frontend/public/data',
                       help='数据输出目录（默认: ../frontend/public/data）')
    parser.add_argument('--no-translate', action='store_true',
                       help='跳过翻译步骤')
    parser.add_argument('--max-papers', type=int, default=30,
                       help='最大论文数（默认: 30）')
    parser.add_argument('--max-github', type=int, default=15,
                       help='最大 GitHub 项目数（默认: 15）')
    parser.add_argument('--days-back', type=int, default=7,
                       help='回溯天数（默认: 7）')

    args = parser.parse_args()

    # 确保输出目录存在
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 50)
    print("  AI 热点追踪 - 数据采集与处理")
    print("=" * 50)
    print(f"输出目录: {output_dir}")
    print(f"翻译: {'跳过' if args.no_translate else '开启'}")
    print()

    # 步骤 1: 获取 arXiv 论文
    print("\n【步骤 1/4】采集 arXiv 论文...")
    papers = run_script('fetch_arxiv', 'fetch_arxiv_papers',
                        max_results=args.max_papers,
                        days_back=args.days_back) or []
    time.sleep(1)

    # 步骤 2: 获取 GitHub 趋势项目
    print("\n【步骤 2/4】采集 GitHub 趋势项目...")
    github_projects = run_script('fetch_github', 'fetch_github_trending',
                                  top_n=args.max_github) or []
    # 如果主方法获取不到，尝试备用方法
    if len(github_projects) < 5:
        print("主方法获取不足，尝试备用 Trending API...")
        backup = run_script('fetch_github', 'fetch_trending_repositories') or []
        # 去重合并
        existing_names = {p['name'] for p in github_projects}
        for p in backup:
            if p['name'] not in existing_names:
                github_projects.append(p)
                existing_names.add(p['name'])
    time.sleep(1)

    # 步骤 3: 获取新闻
    print("\n【步骤 3/4】采集国内 AI 新闻...")
    news = run_script('fetch_news', 'fetch_all_news') or []
    time.sleep(1)

    # 步骤 4: 翻译（如果启用）
    if not args.no_translate:
        baidu_appid = os.environ.get('BAIDU_APPID', '')
        baidu_secret = os.environ.get('BAIDU_SECRET_KEY', '')

        if baidu_appid and baidu_secret:
            print("\n【步骤 4/4】翻译英文内容为中文...")
            from translate import batch_translate

            # 翻译论文标题和摘要
            if papers:
                batch_translate(papers, 'title', baidu_appid, baidu_secret)
                batch_translate(papers, 'summary', baidu_appid, baidu_secret)
                print(f"已翻译 {len(papers)} 篇论文")

            # 翻译 GitHub 项目描述
            if github_projects:
                batch_translate(github_projects, 'title', baidu_appid, baidu_secret)
                batch_translate(github_projects, 'description', baidu_appid, baidu_secret)
                print(f"已翻译 {len(github_projects)} 个项目描述")
        else:
            print("\n【步骤 4/4】跳过翻译（未设置 BAIDU_APPID/BAIDU_SECRET_KEY 环境变量）")
            print("提示：如需翻译功能，请在运行前设置环境变量")
            # 即使不翻译，也复制原标题到翻译字段
            for item in papers + github_projects:
                item['title_cn'] = item.get('title', '')
                if 'summary' in item:
                    item['summary_cn'] = item.get('summary', '')
                if 'description' in item:
                    item['description_cn'] = item.get('description', '')
    else:
        print("\n【步骤 4/4】跳过翻译（--no-translate 参数）")
        for item in papers + github_projects:
            item['title_cn'] = item.get('title', '')
            if 'summary' in item:
                item['summary_cn'] = item.get('summary', '')
            if 'description' in item:
                item['description_cn'] = item.get('description', '')

    # 步骤 5: 处理数据（去重、打标签、热度计算）
    print("\n【步骤 5/5】处理数据（去重、打标签、热度计算）...")
    from process import process_all_data
    result = process_all_data(papers, news, github_projects, output_dir)

    # 也输出一份到 /data 目录（用户要求的结构）
    root_data_dir = os.path.join(os.path.dirname(os.path.dirname(output_dir)), 'data')
    root_data_dir = os.path.abspath(root_data_dir)
    if root_data_dir != output_dir:
        print(f"\n同步数据到: {root_data_dir}")
        os.makedirs(root_data_dir, exist_ok=True)
        import shutil
        for f in os.listdir(output_dir):
            if f.endswith('.json'):
                shutil.copy2(os.path.join(output_dir, f), os.path.join(root_data_dir, f))

    print("\n" + "=" * 50)
    print("  所有步骤完成！")
    print("=" * 50)
    print(f"\n生成的数据文件:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.json'):
            fpath = os.path.join(output_dir, f)
            size = os.path.getsize(fpath)
            print(f"  📄 {f} ({size/1024:.1f} KB)")

    return result


if __name__ == "__main__":
    main()
