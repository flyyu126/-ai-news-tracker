/** @type {import('next').NextConfig} */
const repoName = '-ai-news-tracker'
const isGithubPages = process.env.GITHUB_PAGES === 'true'
const basePath = isGithubPages ? `/${repoName}` : ''

const nextConfig = {
  // 静态导出配置，适合 Vercel / GitHub Pages 部署
  output: 'export',
  basePath,
  assetPrefix: basePath || undefined,
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
}

module.exports = nextConfig
