<script setup>
import { computed, onMounted, ref } from "vue";
import { composeArticle } from "../api/articles.js";
import { fetchHotNews, fetchProviders } from "../api/news.js";

const providers = ref([
  { id: "volcano", label: "火山引擎", description: "Doubao 模型 + 联网搜索" },
  { id: "tianapi", label: "天行数据", description: "社会新闻热点 API" },
  { id: "justoneapi", label: "JustOneAPI", description: "跨平台社交媒体搜索" },
]);
const provider = ref("volcano");
const keywords = ref("强基");
const days = ref(7);
const loading = ref(false);
const error = ref("");
const result = ref(null);
const composingIndex = ref(null);
const composedArticles = ref({});

const currentProvider = computed(
  () => providers.value.find((p) => p.id === provider.value) || providers.value[0]
);

const subtitle = computed(() => {
  const label = currentProvider.value?.label || "数据源";
  return `通过 ${label} 获取指定关键词近期热点`;
});

onMounted(async () => {
  try {
    const list = await fetchProviders();
    if (list?.length) providers.value = list;
  } catch {
    /* 使用默认列表 */
  }
});

async function loadNews() {
  error.value = "";
  loading.value = true;
  result.value = null;
  composedArticles.value = {};
  try {
    result.value = await fetchHotNews(keywords.value, days.value, provider.value);
  } catch (e) {
    error.value = e.message || "加载失败";
  } finally {
    loading.value = false;
  }
}

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleString("zh-CN", { hour12: false });
}

function articleParagraphs(content) {
  return (content || "").split(/\n\n+/).filter(Boolean);
}

async function handleCompose(item, index) {
  error.value = "";
  composingIndex.value = index;
  try {
    const article = await composeArticle(item);
    composedArticles.value = { ...composedArticles.value, [index]: article };
  } catch (e) {
    error.value = e.message || "改编失败";
  } finally {
    composingIndex.value = null;
  }
}
</script>

<template>
  <div class="page">
    <header class="header">
      <h1>热点新闻列表</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </header>

    <section class="toolbar card">
      <label class="field field-provider">
        <span>数据源</span>
        <select v-model="provider">
          <option
            v-for="p in providers"
            :key="p.id"
            :value="p.id"
          >
            {{ p.label }}
          </option>
        </select>
        <small v-if="currentProvider?.description" class="hint">
          {{ currentProvider.description }}
        </small>
      </label>
      <label class="field">
        <span>关键词</span>
        <input
          v-model="keywords"
          type="text"
          placeholder="多个关键词用逗号分隔，如：高考,强基,大学"
        />
      </label>
      <label class="field field-narrow">
        <span>回溯天数</span>
        <input v-model.number="days" type="number" min="1" max="30" />
      </label>
      <button class="btn-primary" :disabled="loading" @click="loadNews">
        {{ loading ? "获取中…" : "获取热点" }}
      </button>
    </section>

    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="result" class="meta card">
      <span>数据源：{{ result.provider_label || result.provider }}</span>
      <span>关键词：{{ result.keywords.join("、") }}</span>
      <span>近 {{ result.days }} 天</span>
      <span>共 {{ result.total }} 条</span>
    </section>

    <ul v-if="result?.items?.length" class="news-list">
      <li v-for="(item, index) in result.items" :key="index" class="card news-item">
        <time class="date">{{ item.date }}</time>
        <h2 class="title">{{ item.title }}</h2>
        <p class="summary">{{ item.summary }}</p>
        <footer class="footer">
          <span class="source">{{ item.source }}</span>
          <div class="footer-actions">
            <a
              v-if="item.url"
              :href="item.url"
              target="_blank"
              rel="noopener noreferrer"
            >
              阅读原文
            </a>
            <button
              class="btn-compose"
              :disabled="composingIndex !== null"
              @click="handleCompose(item, index)"
            >
              {{ composingIndex === index ? "改编中…" : "改编" }}
            </button>
          </div>
        </footer>
        <section v-if="composedArticles[index]" class="composed-article">
          <header class="composed-header">
            <h3 class="composed-title">{{ composedArticles[index].title }}</h3>
            <span class="composed-meta">
              已保存 · {{ formatTime(composedArticles[index].created_at) }}
            </span>
          </header>
          <p
            v-for="(para, pIdx) in articleParagraphs(composedArticles[index].content)"
            :key="pIdx"
            class="composed-para"
          >
            {{ para }}
          </p>
        </section>
      </li>
    </ul>

    <p v-else-if="!loading && !error" class="empty">选择数据源并输入关键词后点击「获取热点」</p>
  </div>
</template>

<style scoped>
.page {
  max-width: 880px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}

.header {
  margin-bottom: 24px;
}

.header h1 {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  padding: 16px 20px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  margin-bottom: 20px;
}

.toolbar .field {
  position: relative;
  padding-bottom: calc(0.75rem * 1.3 + 4px);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}

.field-provider {
  flex: 0 0 200px;
  min-width: 180px;
}

.field-narrow {
  flex: 0 0 120px;
}

.field span {
  font-size: 0.85rem;
  color: #64748b;
}

.field input,
.field select {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: #fff;
}

.hint {
  position: absolute;
  left: 0;
  bottom: 0;
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.btn-primary {
  margin-bottom: calc(0.75rem * 1.3 + 4px);
  padding: 10px 24px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #dc2626;
  margin-bottom: 16px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: #475569;
}

.news-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-item {
  list-style: none;
}

.date {
  display: inline-block;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 6px;
}

.title {
  margin: 0 0 8px;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.4;
}

.summary {
  margin: 0 0 12px;
  color: #334155;
  font-size: 0.95rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-compose {
  padding: 6px 14px;
  background: #0f766e;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
}

.btn-compose:hover:not(:disabled) {
  background: #0d9488;
}

.btn-compose:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.source {
  color: #64748b;
}

.composed-article {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.composed-header {
  margin-bottom: 12px;
}

.composed-title {
  margin: 0 0 6px;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.4;
  color: #0f172a;
}

.composed-meta {
  font-size: 0.75rem;
  color: #94a3b8;
}

.composed-para {
  margin: 0 0 12px;
  color: #334155;
  font-size: 0.95rem;
  line-height: 1.75;
  white-space: pre-wrap;
}

.composed-para:last-child {
  margin-bottom: 0;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 48px 0;
}
</style>
