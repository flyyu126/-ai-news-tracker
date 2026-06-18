"use client";

import { useState, useCallback } from 'react';

/**
 * 搜索栏组件
 * 功能：关键词搜索，支持防抖
 * 参数：
 *   onSearch: 搜索回调函数
 *   placeholder: 占位文本
 */
export default function SearchBar({ onSearch, placeholder = "搜索关键词..." }) {
  const [value, setValue] = useState('');

  // 使用防抖处理搜索输入
  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    setValue(newValue);
    // 实时搜索，传递给父组件
    onSearch?.(newValue);
  }, [onSearch]);

  // 清空搜索
  const handleClear = () => {
    setValue('');
    onSearch?.('');
  };

  return (
    <div className="relative w-full max-w-md">
      {/* 搜索图标 */}
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      {/* 搜索输入框 */}
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2.5 rounded-xl border text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        style={{
          backgroundColor: 'var(--bg-primary)',
          borderColor: 'var(--border-color)',
          color: 'var(--text-primary)',
        }}
      />

      {/* 清空按钮 */}
      {value && (
        <button
          onClick={handleClear}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="清空搜索"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
