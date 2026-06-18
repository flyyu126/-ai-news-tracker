"use client";

/**
 * 首页 - 热点总览
 * 功能：
 *   1. 展示关键词标签云
 *   2. 按热度排序展示热点事件卡片
 *   3. 支持按标签筛选
 *   4. 显示更新时间
 */

import { useState, useEffect } from 'react';
import TagCloud from '@/components/TagCloud';
import EventCard from '@/components/EventCard';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import LoadingSkeleton from '@/components/LoadingSkeleton';

export default function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTag, setActiveTag] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');

  // 加载数据
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        // 尝试加载合并数据，失败则分别加载
        let allData;
        try {
          const res = await fetch('/data/all_data.json');
          if (res.ok) {
            allData = await res.json();
          } else {
            throw new Error('all_data.json not available');
          }
        } catch {
          // 分别加载各类型数据
          const [hotRes, tagRes, papersRes, newsRes, githubRes] = await Promise.all([
            fetch('/data/hot_ranking.json').catch(() => null),
            fetch('/data/tag_cloud.json').catch(() => null),
            fetch('/data/papers.json').catch(() => null),
            fetch('/data/news.json').catch(() => null),
            fetch('/data/github_projects.json').catch(() => null),
          ]);

          const hotItems = hotRes?.ok ? (await hotRes.json()).items || [] : [];
          const tags = tagRes?.ok ? (await tagRes.json()).tags || [] : [];
          const papers = papersRes?.ok ? (await papersRes.json()).items || [] : [];
          const news = newsRes?.ok ? (await newsRes.json()).items || [] : [];
          const github = githubRes?.ok ? (await githubRes.json()).items || [] : [];

          allData = {
            hot_ranking: hotItems.length > 0 ? hotItems : [...papers, ...news, ...github]
              .sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0)).slice(0, 30),
            tag_cloud: tags,
            update_time: new Date().toISOString(),
            total_items: papers.length + news.length + github.length,
          };
        }
        setData(allData);
      } catch (err) {
        console.error('数据加载失败:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // 过滤热点数据
  const filteredHotRanking = (data?.hot_ranking || []).filter((item) => {
    if (activeTag && !(item.tags || []).includes(activeTag) &&
        !(item.keywords || []).includes(activeTag)) {
      return false;
    }
    if (sourceFilter && item.source !== sourceFilter) {
      return false;
    }
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const title = (item.title || item.title_cn || item.name || '').toLowerCase();
      const summary = (item.summary_cn || item.summary || item.description_cn || item.description || '').toLowerCase();
      if (!title.includes(query) && !summary.includes(query)) {
        return false;
      }
    }
    return true;
  });

  // 获取所有来源
  const sources = [...new Set((data?.hot_ranking || []).map(item => item.source).filter(Boolean))];

  // 获取统计数据
  const stats = [
    { label: '今日热点', value: data?.total_items || 0, icon: '📊', color: 'text-blue-500' },
    { label: '标签总数', value: data?.tag_cloud?.length || 0, icon: '🏷️', color: 'text-purple-500' },
    { label: '数据来源', value: sources.length, icon: '🔗', color: 'text-green-500' },
    { label: '更新状态', value: data?.update_time ? '已更新' : '等待更新', icon: '🔄', color: 'text-orange-500' },
  ];

  // 加载状态
  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <div className="h-8 skeleton w-48 mb-2" />
          <div className="h-4 skeleton w-96" />
        </div>
        <div className="mb-8">
          <div className="h-6 skeleton w-32 mb-4" />
          <div className="flex justify-center gap-3">
            {[1,2,3,4,5,6].map(i => <div key={i} className="h-8 skeleton w-20 rounded-full" />)}
          </div>
        </div>
        <LoadingSkeleton count={6} />
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-6">📡</div>
        <h2 className="text-2xl font-bold mb-4">数据加载中</h2>
        <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
          数据采集脚本尚未运行，或数据文件尚未生成
        </p>
        <div className="max-w-md mx-auto p-6 rounded-xl" style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
          <h3 className="font-semibold mb-3">📖 快速开始</h3>
          <ol className="text-sm text-left space-y-2" style={{ color: 'var(--text-secondary)' }}>
            <li>1. 安装 Python 依赖：<code className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-800">pip install -r requirements.txt</code></li>
            <li>2. 运行采集脚本：<code className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-800">cd scripts && python run_all.py</code></li>
            <li>3. 生成的数据将出现在 <code className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-800">frontend/public/data/</code></li>
            <li>4. 刷新本页面即可查看</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div className="text-center py-6">
        <h1 className="text-3xl sm:text-4xl font-bold mb-4 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
          AI 热点总览
        </h1>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          追踪 arXiv 论文 · GitHub 趋势 · AI 科技媒体 最新动态
        </p>
        {data?.update_time && (
          <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            更新时间：{data.update_time}
          </p>
        )}
      </div>

      {/* 数据概览统计 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <div key={i} className="card p-4 text-center">
            <div className={`text-2xl mb-1 ${stat.color}`}>{stat.icon}</div>
            <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {stat.value}
            </div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* 关键词标签云 */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span>🏷️</span> 关键词云
          </h2>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            点击标签筛选相关事件
          </span>
        </div>
        <div className="card p-4">
          {data?.tag_cloud?.length > 0 ? (
            <TagCloud
              tags={data.tag_cloud}
              activeTag={activeTag}
              onTagClick={(tag) => setActiveTag(activeTag === tag ? '' : tag)}
            />
          ) : (
            <div className="text-center py-6" style={{ color: 'var(--text-secondary)' }}>
              暂无标签数据，请先运行采集脚本
            </div>
          )}
        </div>
      </section>

      {/* 搜索和筛选 */}
      <section>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span>🔥</span> 热点排行
            {activeTag && (
              <span className="text-sm font-normal tag bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300">
                {activeTag}
                <button onClick={() => setActiveTag('')} className="ml-1.5 hover:opacity-70">✕</button>
              </span>
            )}
          </h2>
        </div>

        {/* 筛选栏 */}
        <div className="card p-4 mb-4 space-y-3">
          <SearchBar onSearch={setSearchQuery} placeholder="搜索标题或摘要..." />
          <FilterBar
            label="来源"
            options={sources.map(s => ({ label: s, value: s }))}
            selected={sourceFilter}
            onChange={setSourceFilter}
          />
          {data?.tag_cloud?.length > 0 && (
            <FilterBar
              label="标签"
              options={data.tag_cloud.slice(0, 10).map(t => ({ label: t.name, value: t.name }))}
              selected={activeTag}
              onChange={(val) => setActiveTag(val)}
            />
          )}
        </div>

        {/* 事件卡片列表 */}
        {filteredHotRanking.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredHotRanking.map((item, index) => (
              <EventCard key={item.id || item.title || index} item={item} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 card">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-medium mb-2">没有匹配的结果</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {searchQuery ? '尝试其他搜索关键词' : activeTag ? '试试其他标签' : sourceFilter ? '试试其他来源' : ''}
            </p>
            <button
              onClick={() => { setActiveTag(''); setSearchQuery(''); setSourceFilter(''); }}
              className="mt-4 px-4 py-2 rounded-lg bg-blue-500 text-white text-sm hover:bg-blue-600 transition-colors"
            >
              清除筛选条件
            </button>
          </div>
        )}
      </section>

      {/* 分页信息 */}
      {filteredHotRanking.length > 0 && (
        <div className="text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          共 {filteredHotRanking.length} 条热点事件
        </div>
      )}
    </div>
  );
}
