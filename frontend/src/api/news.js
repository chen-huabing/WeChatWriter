export async function fetchHotNews(keywords, days = 7) {
  const params = new URLSearchParams({
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
