/**
 * 根布局组件
 * 功能：全局布局，包含导航栏、页脚和基础 SEO 元数据
 */
import Header from '@/components/Header';
import './globals.css';

// 站点元数据
export const metadata = {
  title: 'AI 热点追踪 - 国内外 AI 前沿研究每日速览',
  description: '自动追踪 arXiv、GitHub、机器之心、量子位等来源的 AI 前沿研究与热点，提供中文摘要与热度分析',
  keywords: 'AI, 人工智能, 热点追踪, arXiv, 机器学习, 深度学习, 大语言模型',
  authors: [{ name: 'AI News Tracker' }],
  viewport: 'width=device-width, initial-scale=1',
  openGraph: {
    title: 'AI 热点追踪',
    description: '自动追踪国内外 AI 前沿研究与热点',
    type: 'website',
    locale: 'zh_CN',
  },
};

/**
 * 根布局
 */
export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        {/* 防止暗色模式闪烁：在页面加载前读取 localStorage */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                    document.documentElement.classList.add('dark');
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col">
        {/* 顶部导航 */}
        <Header />

        {/* 主要内容区域 */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>

        {/* 页脚 */}
        <footer className="py-8 mt-auto border-t" style={{
          backgroundColor: 'var(--bg-primary)',
          borderColor: 'var(--border-color)',
        }}>
          <div className="max-w-7xl mx-auto px-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-3">
              <span className="text-2xl">🤖</span>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                AI 热点追踪
              </span>
            </div>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              数据来源：arXiv、GitHub、机器之心、量子位
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              每日自动更新 | 翻译由百度翻译 API 提供 | 基于 Next.js + Tailwind CSS 构建
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              © {new Date().getFullYear()} AI News Tracker · 仅供学习参考
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
