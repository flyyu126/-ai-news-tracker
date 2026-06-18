"use client";

/**
 * 热点事件卡片组件
 * 功能：在热点总览页面展示单个热点事件
 * 参数：
 *   item: 事件数据对象
 */
export default function EventCard({ item }) {
  if (!item) return null;

  // 格式化日期
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T'));
      return d.toLocaleDateString('zh-CN', {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch {
      return dateStr.slice(0, 10);
    }
  };

  // 来源标签颜色
  const sourceColors = {
    'arXiv': 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    '机器之心': 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
    '量子位': 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    'GitHub': 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  };

  // 类型图标
  const typeIcons = {
    'paper': '📄',
    'news': '📰',
    'project': '💻',
  };

  const sourceColor = sourceColors[item.source] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';

  // 热度条颜色
  const heatColor = item.hot_score >= 80 ? 'bg-red-500' :
                     item.hot_score >= 60 ? 'bg-orange-500' :
                     item.hot_score >= 40 ? 'bg-yellow-500' :
                     'bg-green-500';

  // 判断是中文标题还是需要合并显示
  const displayTitle = item.title_cn || item.title;
  const showOriginal = item.title_cn && item.title_cn !== item.title && item.title;

  return (
    <div className="card p-5 animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        {/* 类型和来源标签 */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-lg">{typeIcons[item.type] || '📌'}</span>
          <span className={`tag ${sourceColor}`}>{item.source}</span>
          {item.primary_category && (
            <span className="tag bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300">
              {item.primary_category}
            </span>
          )}
        </div>

        {/* 热度分数 */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
            热度
          </span>
          <span className={`text-lg font-bold ${item.hot_score >= 70 ? 'text-red-500' : item.hot_score >= 50 ? 'text-orange-500' : 'text-green-500'}`}>
            {item.hot_score?.toFixed(0)}
          </span>
        </div>
      </div>

      {/* 标题 */}
      <h3 className="text-base sm:text-lg font-semibold mb-2 leading-relaxed"
          style={{ color: 'var(--text-primary)' }}>
        {displayTitle}
      </h3>

      {/* 原标题（中英对照时显示） */}
      {showOriginal && (
        <p className="text-xs mb-2 italic" style={{ color: 'var(--text-secondary)' }}>
          {item.title}
        </p>
      )}

      {/* 摘要/描述 */}
      {(item.summary_cn || item.summary || item.description_cn || item.description) && (
        <p className="text-sm leading-relaxed mb-3 line-clamp-3"
           style={{ color: 'var(--text-secondary)' }}>
          {item.summary_cn || item.summary || item.description_cn || item.description}
        </p>
      )}

      {/* 热度条 */}
      <div className="w-full h-1.5 rounded-full bg-gray-200 dark:bg-gray-700 mb-3 overflow-hidden">
        <div className={`h-full rounded-full ${heatColor} transition-all duration-500`}
             style={{ width: `${Math.min(item.hot_score || 0, 100)}%` }} />
      </div>

      {/* 底部信息：日期、标签、链接 */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          {/* 日期 */}
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            🕐 {formatDate(item.published || item.created_at)}
          </span>
          {/* 标签 */}
          {item.tags?.slice(0, 3).map((tag, i) => (
            <span key={i} className="tag bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs">
              {tag}
            </span>
          ))}
        </div>

        {/* 查看链接 */}
        {item.link || item.url ? (
          <a
            href={item.link || item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors hover:underline"
          >
            查看原文 →
          </a>
        ) : null}
      </div>
    </div>
  );
}
