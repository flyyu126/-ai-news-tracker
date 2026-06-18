"use client";

/**
 * 论文卡片组件
 * 功能：在论文页面展示 arXiv 论文信息
 * 参数：
 *   paper: 论文数据对象
 */
export default function PaperCard({ paper }) {
  if (!paper) return null;

  // 格式化日期
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr.includes('T') ? dateStr : dateStr);
      return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr.slice(0, 10);
    }
  };

  // arXiv ID 提取
  const arxivId = paper.id || (paper.link?.split('/').pop()?.split('v')[0] || '');
  const arxivUrl = paper.link || `https://arxiv.org/abs/${arxivId}`;
  const pdfUrl = paper.pdf_link || `https://arxiv.org/pdf/${arxivId}`;

  // 主分类缩写转可读名称
  const categoryLabels = {
    'cs.AI': '人工智能', 'cs.CL': '计算语言学', 'cs.LG': '机器学习',
    'cs.CV': '计算机视觉', 'cs.NE': '神经进化', 'cs.RO': '机器人学',
    'cs.IR': '信息检索', 'cs.MM': '多媒体', 'stat.ML': '机器学习(统计)',
  };

  const displayTitle = paper.title_cn || paper.title;

  return (
    <div className="card p-5 animate-fade-in">
      {/* 标题区域 */}
      <h3 className="text-base sm:text-lg font-semibold mb-2 leading-relaxed"
          style={{ color: 'var(--text-primary)' }}>
        {displayTitle}
      </h3>

      {/* 原标题（有翻译时显示） */}
      {paper.title_cn && paper.title && paper.title_cn !== paper.title && (
        <p className="text-xs mb-2 italic" style={{ color: 'var(--text-secondary)' }}>
          {paper.title}
        </p>
      )}

      {/* 作者 */}
      {paper.authors && paper.authors.length > 0 && (
        <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
          <span className="font-medium">作者：</span>
          {paper.authors.join(', ')}
        </p>
      )}

      {/* 摘要 */}
      {(paper.summary_cn || paper.summary) && (
        <div className="mb-3">
          <p className="text-sm leading-relaxed line-clamp-4" style={{ color: 'var(--text-secondary)' }}>
            {paper.summary_cn || paper.summary}
          </p>
        </div>
      )}

      {/* 元信息行 */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {/* 论文分类 */}
        {paper.categories?.slice(0, 4).map((cat, i) => (
          <span key={i}
                className="tag bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 text-xs">
            {categoryLabels[cat] || cat}
          </span>
        ))}

        {/* 发布时间 */}
        {paper.published && (
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            📅 {formatDate(paper.published)}
          </span>
        )}

        {/* 热度 */}
        {paper.hot_score && (
          <span className={`text-xs font-medium ${
            paper.hot_score >= 70 ? 'text-red-500' : paper.hot_score >= 50 ? 'text-orange-500' : 'text-green-500'
          }`}>
            🔥 {paper.hot_score.toFixed(0)} 热度
          </span>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="flex items-center gap-2 mt-auto">
        <a
          href={arxivUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg
                     bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400
                     hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          📖 摘要
        </a>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg
                     bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400
                     hover:bg-red-100 dark:hover:bg-red-900/50 transition-colors"
        >
          📥 PDF
        </a>
        {/* 自定义标签 */}
        {paper.tags?.map((tag, i) => (
          <span key={i} className="tag bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
