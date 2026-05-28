export async function fetchProviders() {
  const res = await fetch("/api/news/providers");
  const data = await res.json().catch(() => []);
  if (!res.ok) {
    throw new Error(data.detail || `获取数据源失败 (${res.status})`);
  }
  return data;
}

export async function fetchHotNews(keywords, days = 7, provider = "volcano") {
  const params = new URLSearchParams({
    provider,
    keywords: keywords.trim(),
    days: String(days),
  });
  const res = await fetch(`/api/news/hot?${params}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `请求失败 (${res.status})`);
  }
  return data;
}
