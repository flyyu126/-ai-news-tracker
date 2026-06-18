/** @type {import('next').NextConfig} */
const nextConfig = {
  // 静态导出配置，适合 Vercel 部署
  output: 'export',
  images: {
    unoptimized: true, // Vercel 静态部署无需图片优化
  },
  // 确保 trailing slash 一致
  trailingSlash: true,
}

module.exports = nextConfig
