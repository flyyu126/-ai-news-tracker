"use client";

/**
 * 筛选栏组件
 * 功能：按标签、来源等维度筛选数据
 * 参数：
 *   options: 筛选选项 {label, value}[]
 *   selected: 当前选中的值
 *   onChange: 筛选变更回调
 *   label: 筛选器标签
 */
export default function FilterBar({ options = [], selected, onChange, label = "筛选" }) {
  if (!options || options.length === 0) return null;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {label && (
        <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
          {label}：
        </span>
      )}

      {/* 全部选项 */}
      <button
        onClick={() => onChange?.('')}
        className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
          !selected
            ? 'bg-blue-500 text-white shadow-sm'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
        }`}
      >
        全部
      </button>

      {/* 筛选选项 */}
      {options.map((opt, i) => (
        <button
          key={opt.value || i}
          onClick={() => onChange?.(opt.value)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
            selected === opt.value
              ? 'bg-blue-500 text-white shadow-sm'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
