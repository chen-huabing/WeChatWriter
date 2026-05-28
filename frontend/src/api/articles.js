export async function composeArticle(sourceNews) {
  const res = await fetch("/api/articles/compose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_news: sourceNews }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `撰写失败 (${res.status})`);
  }
  return data;
}
