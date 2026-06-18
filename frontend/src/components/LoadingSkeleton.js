"use client";

/**
 * 加载骨架屏组件
 * 功能：数据加载时的占位动画
 * 参数：
 *   count: 骨架屏数量
 *   type: 类型（card / list）
 */
export default function LoadingSkeleton({ count = 3, type = 'card' }) {
  const items = Array.from({ length: count }, (_, i) => i);

  if (type === 'list') {
    return (
      <div className="space-y-4">
        {items.map((i) => (
          <div key={i} className="flex items-start gap-4 p-4 card">
            <div className="w-3 h-3 rounded-full skeleton flex-shrink-0 mt-1" />
            <div className="flex-1 space-y-2">
              <div className="h-4 skeleton w-3/4" />
              <div className="h-3 skeleton w-1/2" />
              <div className="h-3 skeleton w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((i) => (
        <div key={i} className="card p-5 space-y-3">
          <div className="flex justify-between">
            <div className="h-5 w-20 skeleton" />
            <div className="h-5 w-16 skeleton" />
          </div>
          <div className="h-5 skeleton w-full" />
          <div className="h-5 skeleton w-3/4" />
          <div className="h-4 skeleton w-full" />
          <div className="h-4 skeleton w-2/3" />
          <div className="h-2 skeleton w-full" />
          <div className="flex justify-between">
            <div className="h-4 w-24 skeleton" />
            <div className="h-4 w-16 skeleton" />
          </div>
        </div>
      ))}
    </div>
  );
}
