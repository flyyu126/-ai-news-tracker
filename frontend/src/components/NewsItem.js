"use client";

/**
 * 新闻时间线条目组件
 * 功能：在新闻页面以时间线样式展示新闻
 * 参数：
 *   news: 新闻数据对象
 *   index: 在列表中的位置
 */
export default function NewsItem({ news, index = 0 }) {
  if (!news) return null;

  // 格式化时间
  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T'));
      const now = new Date();
      const diff = now - d;
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (hours < 1) return '刚刚';
      if (hours < 24) return `${hours} 小时前`;
      if (days < 7) return `${days} 天前`;
      return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    } catch {
      return dateStr.slice(0, 10);
    }
  };

  // 来源对应的颜色
  const sourceConfig = {
    '机器之心': { color: 'bg-red-500', label: '机器之心' },
    '量子位': { color: 'bg-blue-500', label: '量子位' },
    'arXiv': { color: 'bg-purple-500', label: 'arXiv' },
    'GitHub': { color: 'bg-gray-500', label: 'GitHub' },
  };

  const config = sourceConfig[news.source] || { color: 'bg-green-500', label: news.source };

  return (
    <div className="relative pl-10 pb-6 animate-slide-up"
         style={{ animationDelay: `${(index % 10) * 50}ms` }}>
      {/* 时间线竖线 */}
      <div className="timeline-line" />

      {/* 时间线圆点 */}
      <div className={`timeline-dot ${config.color} ring-4`}
           style={{ borderColor: 'var(--bg-card)', '--tw-ring-color': 'var(--bg-card)' }}/>

      {/* 内容卡片 */}
      <div className="card p-4 ml-4">
        {/* 头部信息 */}
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          {/* 来源徽章 */}
          <span className={`tag text-white text-xs ${config.color}`}>
            {config.label}
          </span>
          {/* 发布时间 */}
          {news.published && (
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {formatTime(news.published)}
            </span>
          )}
          {/* 热度 */}
          {news.hot_score && (
            <span className="text-xs ml-auto" style={{ color: 'var(--text-secondary)' }}>
              🔥 {news.hot_score.toFixed(0)}
            </span>
          )}
        </div>

        {/* 标题 */}
        <h3 className="text-base font-medium mb-1.5 leading-relaxed"
            style={{ color: 'var(--text-primary)' }}>
          {news.title_cn || news.title || '无标题'}
        </h3>

        {/* 摘要 */}
        {(news.summary_cn || news.summary) && (
          <p className="text-sm leading-relaxed line-clamp-2 mb-2"
             style={{ color: 'var(--text-secondary)' }}>
            {news.summary_cn || news.summary}
          </p>
        )}

        {/* 底部标签和链接 */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-1.5 flex-wrap">
            {news.tags?.slice(0, 3).map((tag, i) => (
              <span key={i}
                    className="tag bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs">
                {tag}
              </span>
            ))}
          </div>

          {/* 查看原文链接 */}
          {news.url && (
            <a
              href={news.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-medium text-blue-500 hover:text-blue-600 dark:hover:text-blue-400
                         hover:underline transition-colors"
            >
              查看原文 →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
