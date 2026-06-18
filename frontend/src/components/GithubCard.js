"use client";

/**
 * GitHub 项目卡片组件
 * 功能：展示 GitHub 趋势项目信息
 * 参数：
 *   repo: 仓库数据对象
 */
export default function GithubCard({ repo }) {
  if (!repo) return null;

  // 语言对应的颜色（GitHub 语言颜色规范）
  const langColors = {
    'Python': '#3572A5',
    'JavaScript': '#f1e05a',
    'TypeScript': '#3178c6',
    'Jupyter Notebook': '#DA5B0B',
    'Java': '#b07219',
    'Go': '#00ADD8',
    'Rust': '#dea584',
    'C++': '#f34b7d',
    'C': '#555555',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'Swift': '#F05138',
    'Kotlin': '#A97BFF',
    'Ruby': '#701516',
    'Shell': '#89e051',
    'Unknown': '#8b8b8b',
  };

  const dotColor = langColors[repo.language] || langColors['Unknown'];

  // 格式化 Star 数
  const formatStars = (stars) => {
    if (!stars && stars !== 0) return '0';
    if (stars >= 1000) return `${(stars / 1000).toFixed(1)}k`;
    return stars.toString();
  };

  // 提取仓库简称（去掉 owner）
  const repoShortName = repo.name?.split('/').pop() || repo.name;

  const displayTitle = repo.title_cn || repo.title || repo.name;

  return (
    <div className="card p-5 animate-fade-in">
      {/* 头部：Owner 头像和名称 */}
      <div className="flex items-center gap-3 mb-3">
        {repo.owner_avatar && (
          <img
            src={repo.owner_avatar}
            alt={repo.owner}
            className="w-8 h-8 rounded-full"
          />
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg">📦</span>
            <a
              href={repo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-sm text-blue-600 dark:text-blue-400 hover:underline truncate"
            >
              {repo.name}
            </a>
          </div>
          {displayTitle !== repo.name && (
            <p className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>
              {displayTitle}
            </p>
          )}
        </div>
      </div>

      {/* 描述 */}
      {(repo.description_cn || repo.description) && (
        <p className="text-sm leading-relaxed mb-3 line-clamp-2"
           style={{ color: 'var(--text-secondary)' }}>
          {repo.description_cn || repo.description}
        </p>
      )}

      {/* 统计信息 */}
      <div className="flex items-center gap-4 mb-3">
        {/* 语言 */}
        <div className="flex items-center gap-1.5">
          <span className="lang-dot" style={{ backgroundColor: dotColor }} />
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {repo.language || 'Unknown'}
          </span>
        </div>

        {/* Stars */}
        <div className="flex items-center gap-1">
          <span className="text-xs">⭐</span>
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
            {formatStars(repo.stars)}
          </span>
        </div>

        {/* Forks */}
        {repo.forks > 0 && (
          <div className="flex items-center gap-1">
            <span className="text-xs">🔀</span>
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {formatStars(repo.forks)}
            </span>
          </div>
        )}

        {/* 热度 */}
        {repo.hot_score && (
          <span className={`text-xs font-medium ml-auto ${
            repo.hot_score >= 70 ? 'text-red-500' : repo.hot_score >= 50 ? 'text-orange-500' : 'text-green-500'
          }`}>
            🔥 {repo.hot_score.toFixed(0)}
          </span>
        )}
      </div>

      {/* Topics 标签 */}
      {repo.topics && repo.topics.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {repo.topics.slice(0, 5).map((topic, i) => (
            <span key={i}
                  className="tag bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs">
              {topic}
            </span>
          ))}
        </div>
      )}

      {/* 自动标签 */}
      {repo.tags && repo.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {repo.tags.map((tag, i) => (
            <span key={i}
                  className="tag bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
