const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

/** GitHub Pages 子路径部署时，为 /data/*.json 补上 basePath 前缀 */
export function dataUrl(path) {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${basePath}${normalized}`;
}
