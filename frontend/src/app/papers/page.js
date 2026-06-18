"use client";

/**
 * 论文前沿页面
 * 功能：
 *   1. 展示 arXiv 最新论文列表
 *   2. 支持按领域标签筛选
 *   3. 支持关键词搜索
 *   4. 按时间排序
 */

import { useState, useEffect } from 'react';
import PaperCard from '@/components/PaperCard';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import LoadingSkeleton from '@/components/LoadingSkeleton';

// 领域标签定义
const DOMAIN_LABELS = [
  { label: '人工智能 (AI)', value: 'AI' },
  { label: '自然语言处理 (NLP)', value: 'NLP' },
  { label: '计算机视觉 (CV)', value: 'CV' },
  { label: '机器学习 (ML)', value: '机器学习' },
  { label: '多模态', value: '多模态' },
  { label: '强化学习', value: '强化学习' },
  { label: '机器人', value: '机器人' },
  { label: '语音技术', value: '语音技术' },
  { label: '模型压缩', value: '模型压缩' },
  { label: 'AI 安全', value: 'AI安全' },
  { label: '知识图谱', value: '知识图谱' },
];

// arXiv 原始分类筛选
const ARXIV_CATEGORIES = [
  { label: '全部', value: '' },
  { label: 'cs.AI', value: 'cs.AI' },
  { label: 'cs.CL', value: 'cs.CL' },
  { label: 'cs.LG', value: 'cs.LG' },
  { label: 'cs.CV', value: 'cs.CV' },
  { label: 'cs.NE', value: 'cs.NE' },
  { label: 'cs.RO', value: 'cs.RO' },
];

export default function PapersPage() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [sortBy, setSortBy] = useState('newest'); // newest | hottest

  // 加载论文数据
  useEffect(() => {
    async function loadPapers() {
      try {
        setLoading(true);

        // 先尝试从单独的文件加载
        let papersData;
        try {
          const res = await fetch('/data/papers.json');
          if (res.ok) {
            const data = await res.json();
            papersData = data.items || [];
          } else {
            throw new Error('papers.json not available');
          }
        } catch {
          // 从 all_data.json 中提取
          try {
            const res = await fetch('/data/all_data.json');
            if (res.ok) {
              const data = await res.json();
              papersData = data.papers || data.hot_ranking?.filter(p => p.type === 'paper' || p.source === 'arXiv') || [];
            } else {
              throw new Error('all_data.json not available');
            }
          } catch {
            papersData = [];
          }
        }

        // 确保每篇论文都有 type 字段
        papersData = papersData.filter(p => p.source === 'arXiv' || p.type === 'paper' || p.categories);
        setPapers(papersData);
      } catch (err) {
        console.error('论文数据加载失败:', err);
      } finally {
        setLoading(false);
      }
    }
    loadPapers();
  }, []);

  // 筛选和排序
  const filteredPapers = papers
    .filter((paper) => {
      // 文本搜索
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const title = (paper.title || paper.title_cn || '').toLowerCase();
        const summary = (paper.summary_cn || paper.summary || '').toLowerCase();
        const authors = (paper.authors || []).join(' ').toLowerCase();
        if (!title.includes(q) && !summary.includes(q) && !authors.includes(q)) {
          return false;
        }
      }
      // 领域筛选
      if (domainFilter) {
        const tags = paper.tags || [];
        const cats = paper.categories || [];
        const combined = [...tags, ...cats].map(t => t.toLowerCase());
        if (!combined.some(t => t.includes(domainFilter.toLowerCase()))) {
          return false;
        }
      }
      // arXiv 分类筛选
      if (categoryFilter) {
        const cats = paper.categories || [];
        if (!cats.includes(categoryFilter)) {
          return false;
        }
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'hottest') {
        return (b.hot_score || 0) - (a.hot_score || 0);
      }
      // 按时间从新到旧
      const dateA = a.published || a.updated || '';
      const dateB = b.published || b.updated || '';
      return dateB.localeCompare(dateA);
    });

  if (loading) {
    return (
      <div>
        <div className="mb-8">
          <div className="h-8 skeleton w-48 mb-2" />
          <div className="h-4 skeleton w-80" />
        </div>
        <LoadingSkeleton count={6} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="text-center py-6">
        <h1 className="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
          📄 论文前沿
        </h1>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          arXiv 人工智能 · 计算语言学 · 机器学习 最新论文（中文摘要）
        </p>
        {papers.length > 0 && (
          <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            共收录 {papers.length} 篇论文
          </p>
        )}
      </div>

      {/* 搜索和筛选 */}
      <div className="card p-4 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <SearchBar onSearch={setSearchQuery} placeholder="搜索论文标题、摘要或作者..." />
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">排序：</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm px-3 py-1.5 rounded-lg border bg-white dark:bg-gray-800"
              style={{ borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
            >
              <option value="newest">最新发布</option>
              <option value="hottest">热度最高</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <FilterBar
            label="领域"
            options={DOMAIN_LABELS}
            selected={domainFilter}
            onChange={setDomainFilter}
          />
          <FilterBar
            label="分类"
            options={ARXIV_CATEGORIES}
            selected={categoryFilter}
            onChange={setCategoryFilter}
          />
        </div>
      </div>

      {/* 论文列表 */}
      {filteredPapers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredPapers.map((paper, index) => (
            <PaperCard key={paper.id || paper.title || index} paper={paper} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 card">
          <div className="text-5xl mb-4">🔬</div>
          <h3 className="text-xl font-medium mb-2">暂无符合条件的论文</h3>
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            {papers.length === 0
              ? '数据采集脚本尚未运行，请先执行 python scripts/run_all.py'
              : '尝试调整筛选条件或搜索关键词'}
          </p>
          {(searchQuery || domainFilter || categoryFilter) && (
            <button
              onClick={() => { setSearchQuery(''); setDomainFilter(''); setCategoryFilter(''); }}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white text-sm hover:bg-blue-600 transition-colors"
            >
              清除筛选
            </button>
          )}
        </div>
      )}

      {/* 统计信息 */}
      {filteredPapers.length > 0 && (
        <div className="text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          显示 {filteredPapers.length} / {papers.length} 篇论文
        </div>
      )}
    </div>
  );
}
