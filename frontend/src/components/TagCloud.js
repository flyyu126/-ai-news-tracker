"use client";

/**
 * 关键词标签云组件
 * 功能：展示热门关键词和领域标签，点击可跳转筛选
 * 参数：
 *   tags: 标签数组 [{name, count, weight}]
 *   onTagClick: 标签点击回调
 *   activeTag: 当前选中标签
 */
export default function TagCloud({ tags = [], onTagClick, activeTag }) {
  if (!tags || tags.length === 0) {
    return (
      <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
        <p className="text-lg mb-2">暂无标签数据</p>
        <p className="text-sm">等待数据采集完成后将在这里展示关键词云</p>
      </div>
    );
  }

  // 按权重分为 6 个等级
  const getWeightLevel = (weight) => {
    if (weight >= 80) return 6;
    if (weight >= 60) return 5;
    if (weight >= 40) return 4;
    if (weight >= 20) return 3;
    if (weight >= 10) return 2;
    return 1;
  };

  // 根据权重生成颜色
  const getTagColor = (weight) => {
    const colors = [
      'text-gray-500 dark:text-gray-400',
      'text-blue-500 dark:text-blue-400',
      'text-green-500 dark:text-green-400',
      'text-yellow-600 dark:text-yellow-400',
      'text-orange-600 dark:text-orange-400',
      'text-red-600 dark:text-red-400',
    ];
    return colors[Math.min(getWeightLevel(weight) - 1, colors.length - 1)];
  };

  // 根据权重生成背景色
  const getTagBg = (weight, isActive = false) => {
    if (isActive) {
      return 'bg-blue-100 dark:bg-blue-900/50 border-blue-300 dark:border-blue-700';
    }
    const bgs = [
      'bg-gray-100 dark:bg-gray-800',
      'bg-blue-50 dark:bg-blue-900/20',
      'bg-green-50 dark:bg-green-900/20',
      'bg-yellow-50 dark:bg-yellow-900/20',
      'bg-orange-50 dark:bg-orange-900/20',
      'bg-red-50 dark:bg-red-900/20',
    ];
    return bgs[Math.min(getWeightLevel(weight) - 1, bgs.length - 1)];
  };

  return (
    <div className="w-full">
      <div className="flex flex-wrap justify-center gap-2 sm:gap-3 p-4">
        {tags.map((tag, index) => {
          const weightLevel = getWeightLevel(tag.weight);
          const isActive = activeTag === tag.name;

          return (
            <button
              key={`${tag.name}-${index}`}
              onClick={() => onTagClick?.(tag.name)}
              className={`
                tag px-3 py-1.5 rounded-full border transition-all duration-200
                hover:scale-110 hover:shadow-md cursor-pointer
                tag-weight-${weightLevel}
                ${getTagBg(tag.weight, isActive)}
                ${getTagColor(tag.weight)}
                ${isActive ? 'ring-2 ring-blue-400 shadow-lg scale-110' : ''}
              `}
              title={`${tag.name} (出现 ${tag.count} 次)`}
            >
              {tag.name}
              <span className="ml-1 text-xs opacity-60">×{tag.count}</span>
            </button>
          );
        })}
      </div>

      {/* 统计信息 */}
      <div className="text-center text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
        共 {tags.length} 个热门标签/关键词
      </div>
    </div>
  );
}
