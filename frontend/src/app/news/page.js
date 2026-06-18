"use client";

/**
 * 新闻聚合页面
 * 功能：
 *   1. 以时间线样式展示 AI 新闻
 *   2. 支持按来源筛选
 *   3. 支持按标签筛选和搜索
 */

import { useState, useEffect } from 'react';
import NewsItem from '@/components/NewsItem';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import LoadingSkeleton from '@/components/LoadingSkeleton';

export default function NewsPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [tagFilter, setTagFilter] = useState('');

  // 加载新闻数据
  useEffect(() => {
    async function loadNews() {
      try {
        setLoading(true);

        let newsData;
        try {
          const res = await fetch('/data/news.json');
          if (res.ok) {
            const data = await res.json();
            newsData = data.items || [];
          } else {
            throw new Error('news.json not available');
          }
        } catch {
          // 从 all_data.json 提取
          try {
            const res = await fetch('/data/all_data.json');
            if (res.ok) {
              const data = await res.json();
              newsData = data.news || data.hot_ranking?.filter(p => p.type === 'news') || [];
            } else {
              throw new Error('all_data.json not available');
            }
          } catch {
            newsData = [];
          }
        }

        setNews(newsData);
      } catch (err) {
        console.error('新闻数据加载失败:', err);
      } finally {
        setLoading(false);
      }
    }
    loadNews();
  }, []);

  // 获取所有来源和标签
  const sources = [...new Set(news.map(item => item.source).filter(Boolean))];
  const allTags = [...new Set(news.flatMap(item => item.tags || []))];

  // 筛选新闻
  const filteredNews = news.filter((item) => {
    if (sourceFilter && item.source !== sourceFilter) return false;
    if (tagFilter && !(item.tags || []).includes(tagFilter)) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const title = (item.title || item.title_cn || '').toLowerCase();
      const summary = (item.summary_cn || item.summary || '').toLowerCase();
      if (!title.includes(q) && !summary.includes(q)) return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <div className="h-8 skeleton w-48 mb-2" />
          <div className="h-4 skeleton w-80" />
        </div>
        <LoadingSkeleton count={5} type="list" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="text-center py-6">
        <h1 className="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-blue-500 to-teal-500 bg-clip-text text-transparent">
          📰 新闻聚合
        </h1>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          机器之心 · 量子位 最新 AI 资讯
        </p>
        {news.length > 0 && (
          <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            共收录 {news.length} 篇新闻
          </p>
        )}
      </div>

      {/* 搜索和筛选 */}
      <div className="card p-4 space-y-4">
        <SearchBar onSearch={setSearchQuery} placeholder="搜索新闻标题或摘要..." />

        {sources.length > 0 && (
          <FilterBar
            label="来源"
            options={sources.map(s => ({ label: s, value: s }))}
            selected={sourceFilter}
            onChange={setSourceFilter}
          />
        )}

        {allTags.length > 0 && (
          <FilterBar
            label="标签"
            options={allTags.map(t => ({ label: t, value: t }))}
            selected={tagFilter}
            onChange={setTagFilter}
          />
        )}
      </div>

      {/* 新闻时间线 */}
      {filteredNews.length > 0 ? (
        <div className="card p-6">
          <div className="relative">
            {filteredNews.map((item, index) => (
              <NewsItem key={item.id || item.title || index} news={item} index={index} />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-16 card">
          <div className="text-5xl mb-4">📡</div>
          <h3 className="text-xl font-medium mb-2">暂无符合条件的新闻</h3>
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            {news.length === 0
              ? '新闻数据尚未采集，请先运行采集脚本'
              : '尝试调整筛选条件或搜索关键词'}
          </p>
          {(searchQuery || sourceFilter || tagFilter) && (
            <button
              onClick={() => { setSearchQuery(''); setSourceFilter(''); setTagFilter(''); }}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white text-sm hover:bg-blue-600 transition-colors"
            >
              清除所有筛选
            </button>
          )}
        </div>
      )}

      {/* 统计 */}
      {filteredNews.length > 0 && (
        <div className="text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          显示 {filteredNews.length} / {news.length} 条新闻
        </div>
      )}
    </div>
  );
}
