"use client";

/**
 * GitHub 趋势页面
 * 功能：
 *   1. 展示 AI 相关 GitHub 热门项目
 *   2. 支持按编程语言筛选
 *   3. 支持关键词搜索
 *   4. 按 Stars 数排序
 */

import { useState, useEffect } from 'react';
import GithubCard from '@/components/GithubCard';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import LoadingSkeleton from '@/components/LoadingSkeleton';
import { dataUrl } from '@/lib/dataPath';

export default function GithubPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [langFilter, setLangFilter] = useState('');
  const [sortBy, setSortBy] = useState('stars'); // stars | hottest | newest

  // 加载 GitHub 项目数据
  useEffect(() => {
    async function loadProjects() {
      try {
        setLoading(true);

        let projectsData;
        try {
          const res = await fetch(dataUrl('/data/github_projects.json'));
          if (res.ok) {
            const data = await res.json();
            projectsData = data.items || [];
          } else {
            throw new Error('github_projects.json not available');
          }
        } catch {
          // 从 all_data.json 提取
          try {
            const res = await fetch(dataUrl('/data/all_data.json'));
            if (res.ok) {
              const data = await res.json();
              projectsData = data.github_projects || data.hot_ranking?.filter(p => p.type === 'project' || p.source === 'GitHub') || [];
            } else {
              throw new Error('all_data.json not available');
            }
          } catch {
            projectsData = [];
          }
        }

        setProjects(projectsData.filter(p => p.source === 'GitHub' || p.type === 'project'));
      } catch (err) {
        console.error('GitHub 数据加载失败:', err);
      } finally {
        setLoading(false);
      }
    }
    loadProjects();
  }, []);

  // 获取所有编程语言
  const languages = [...new Set(projects.map(p => p.language).filter(Boolean))];

  // 筛选和排序
  const filteredProjects = projects
    .filter((repo) => {
      if (langFilter && repo.language !== langFilter) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const name = (repo.name || '').toLowerCase();
        const desc = (repo.description_cn || repo.description || '').toLowerCase();
        const title = (repo.title_cn || repo.title || '').toLowerCase();
        if (!name.includes(q) && !desc.includes(q) && !title.includes(q)) {
          return false;
        }
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'hottest') return (b.hot_score || 0) - (a.hot_score || 0);
      if (sortBy === 'newest') {
        return (b.created_at || '').localeCompare(a.created_at || '');
      }
      return (b.stars || 0) - (a.stars || 0); // 默认按 Stars 排序
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
        <h1 className="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
          💻 GitHub 趋势
        </h1>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          AI / 机器学习 / 深度学习 热门开源项目
        </p>
        {projects.length > 0 && (
          <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            共收录 {projects.length} 个项目
          </p>
        )}
      </div>

      {/* 搜索和筛选 */}
      <div className="card p-4 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <SearchBar onSearch={setSearchQuery} placeholder="搜索项目名称或描述..." />
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">排序：</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm px-3 py-1.5 rounded-lg border bg-white dark:bg-gray-800"
              style={{ borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
            >
              <option value="stars">⭐ Stars 最多</option>
              <option value="hottest">🔥 热度最高</option>
              <option value="newest">🆕 最新发布</option>
            </select>
          </div>
        </div>

        {languages.length > 0 && (
          <FilterBar
            label="编程语言"
            options={languages.map(l => ({ label: l, value: l }))}
            selected={langFilter}
            onChange={setLangFilter}
          />
        )}

        {/* 统计条 */}
        <div className="flex flex-wrap gap-4 text-xs" style={{ color: 'var(--text-secondary)' }}>
          <span>⭐ 总 Stars: {projects.reduce((s, p) => s + (p.stars || 0), 0).toLocaleString()}</span>
          <span>📦 总项目: {projects.length}</span>
          <span>🔤 语言: {languages.length}</span>
        </div>
      </div>

      {/* 项目列表 */}
      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredProjects.map((repo, index) => (
            <GithubCard key={repo.id || repo.name || index} repo={repo} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 card">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="text-xl font-medium mb-2">暂无符合条件的项目</h3>
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            {projects.length === 0
              ? 'GitHub 数据尚未采集，请先运行采集脚本'
              : '尝试调整筛选条件或搜索关键词'}
          </p>
          {(searchQuery || langFilter) && (
            <button
              onClick={() => { setSearchQuery(''); setLangFilter(''); }}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white text-sm hover:bg-blue-600 transition-colors"
            >
              清除筛选
            </button>
          )}
        </div>
      )}

      {/* 分页信息 */}
      {filteredProjects.length > 0 && (
        <div className="text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          显示 {filteredProjects.length} / {projects.length} 个项目
        </div>
      )}
    </div>
  );
}
