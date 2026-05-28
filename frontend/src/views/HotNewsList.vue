<script setup>
import { ref } from "vue";
import { fetchHotNews } from "../api/news.js";

const keywords = ref("高考,强基");
const days = ref(7);
const loading = ref(false);
const error = ref("");
const result = ref(null);

async function loadNews() {
  error.value = "";
  loading.value = true;
  result.value = null;
  try {
    result.value = await fetchHotNews(keywords.value, days.value);
  } catch (e) {
    error.value = e.message || "加载失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <header class="header">
      <h1>热点新闻列表</h1>
      <p class="subtitle">通过火山引擎 Doubao 获取指定关键词近期热点</p>
    </header>

    <section class="toolbar card">
      <label class="field">
        <span>关键词</span>
        <input
          v-model="keywords"
          type="text"
          placeholder="多个关键词用逗号分隔，如：高考,强基"
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
          <a
            v-if="item.url"
            :href="item.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            阅读原文
          </a>
        </footer>
      </li>
    </ul>

    <p v-else-if="!loading && !error" class="empty">输入关键词后点击「获取热点」</p>
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

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}

.field-narrow {
  flex: 0 0 120px;
}

.field span {
  font-size: 0.85rem;
  color: #64748b;
}

.field input {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
}

.btn-primary {
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

.source {
  color: #64748b;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 48px 0;
}
</style>
