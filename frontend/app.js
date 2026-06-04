const statusPill = document.getElementById("statusPill");
const ollamaStatus = document.getElementById("ollamaStatus");
const llmModel = document.getElementById("llmModel");
const embedModel = document.getElementById("embedModel");
const documentCount = document.getElementById("documentCount");
const chunkCount = document.getElementById("chunkCount");
const vectorStore = document.getElementById("vectorStore");
const statusMessage = document.getElementById("statusMessage");
const rebuildIndexBtn = document.getElementById("rebuildIndexBtn");
const refreshStatusBtn = document.getElementById("refreshStatusBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const chatForm = document.getElementById("chatForm");
const chatLog = document.getElementById("chatLog");
const questionInput = document.getElementById("questionInput");
const topKInput = document.getElementById("topKInput");
const sendBtn = document.getElementById("sendBtn");
const sampleQuestions = document.getElementById("sampleQuestions");
const processList = document.getElementById("processList");
const sourcesList = document.getElementById("sourcesList");
const sourceCountBadge = document.getElementById("sourceCountBadge");
const latencyBadge = document.getElementById("latencyBadge");

const defaultProcess = [
  "接收用户问题",
  "问题向量化",
  "知识库检索",
  "Prompt 构造",
  "本地模型生成",
  "返回答案与来源",
].map((name, index) => ({
  step: index + 1,
  name,
  status: "waiting",
  detail: "等待执行。",
}));

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusLabel(status) {
  const labels = {
    waiting: "等待",
    running: "执行中",
    done: "完成",
    failed: "失败",
  };
  return labels[status] || status;
}

async function readJson(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    const message = text.length > 200 ? `${text.slice(0, 200)}...` : text;
    throw new Error(message || `HTTP ${response.status}`);
  }
}

function renderProcess(steps = defaultProcess) {
  processList.innerHTML = steps
    .map(
      (step) => `
        <li class="process-step ${escapeHtml(step.status)}">
          <div class="step-number">${step.step}</div>
          <div>
            <div class="step-title">
              <span>${escapeHtml(step.name)}</span>
              <span class="step-status">${statusLabel(step.status)}</span>
            </div>
            <p class="step-detail">${escapeHtml(step.detail)}</p>
          </div>
        </li>
      `,
    )
    .join("");
}

function renderSources(sources = []) {
  sourceCountBadge.textContent = `${sources.length} 来源`;
  if (!sources.length) {
    sourcesList.innerHTML = '<p class="empty-state">没有检索来源。</p>';
    return;
  }
  sourcesList.innerHTML = sources
    .map(
      (source, index) => `
        <details class="source-card" ${index === 0 ? "open" : ""}>
          <summary>
            <span class="rank">Top ${source.rank}</span>
            <span class="source-title">${escapeHtml(source.title)}</span>
            <span class="score">${Math.round(source.score * 100)}%</span>
          </summary>
          <p class="source-meta">类别：${escapeHtml(source.category)} | 来源：${escapeHtml(source.source)}</p>
          <p class="source-content">${escapeHtml(source.content)}</p>
        </details>
      `,
    )
    .join("");
}

function addMessage(role, content, extraClass = "") {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.innerHTML =
    role === "user"
      ? `<div class="bubble ${extraClass}">${escapeHtml(content)}</div><div class="avatar">我</div>`
      : `<div class="avatar">AI</div><div class="bubble ${extraClass}">${escapeHtml(content)}</div>`;
  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;
  return message.querySelector(".bubble");
}

function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  rebuildIndexBtn.disabled = isLoading;
  sendBtn.textContent = isLoading ? "处理中" : "发送";
}

async function refreshHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await readJson(response);
    statusPill.textContent = data.status === "ok" ? "正常" : "降级";
    statusPill.className = `status-pill ${data.status === "ok" ? "ok" : "degraded"}`;
    ollamaStatus.textContent = data.ollama_connected ? "已连接" : "未连接";
    llmModel.textContent = data.llm_model || "-";
    embedModel.textContent = data.embed_model || "-";
    documentCount.textContent = data.document_count ?? 0;
    chunkCount.textContent = data.chunk_count ?? 0;
    vectorStore.textContent = data.vector_store || "-";
    statusMessage.textContent = data.message || "系统已就绪。";
  } catch (error) {
    statusPill.textContent = "异常";
    statusPill.className = "status-pill degraded";
    statusMessage.textContent = `状态检查失败：${error.message}`;
  }
}

async function loadSampleQuestions() {
  try {
    const response = await fetch("/api/sample-questions");
    const questions = await readJson(response);
    sampleQuestions.innerHTML = questions
      .map((question) => `<button class="sample-chip" type="button" title="${escapeHtml(question)}">${escapeHtml(question)}</button>`)
      .join("");
    sampleQuestions.querySelectorAll(".sample-chip").forEach((button, index) => {
      button.addEventListener("click", () => {
        questionInput.value = questions[index];
        questionInput.focus();
      });
    });
  } catch (error) {
    sampleQuestions.innerHTML = `<span class="empty-state">示例问题加载失败：${escapeHtml(error.message)}</span>`;
  }
}

async function rebuildIndex() {
  rebuildIndexBtn.disabled = true;
  statusMessage.textContent = "正在重建知识库索引...";
  try {
    const response = await fetch("/api/rebuild-index", { method: "POST" });
    const data = await readJson(response);
    if (!response.ok) {
      throw new Error(data.detail || "索引重建失败");
    }
    statusMessage.textContent = `${data.message} 文档 ${data.document_count}，Chunk ${data.chunk_count}，Embedding：${data.embedding_provider}`;
    await refreshHealth();
  } catch (error) {
    statusMessage.textContent = `索引重建失败：${error.message}`;
  } finally {
    rebuildIndexBtn.disabled = false;
  }
}

async function sendQuestion(event) {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    questionInput.focus();
    return;
  }

  addMessage("user", question);
  const placeholder = addMessage("assistant", "正在检索知识库，并调用本地模型生成回答...", "loading");
  renderProcess(defaultProcess.map((step) => (step.step === 1 ? { ...step, status: "running", detail: "正在接收问题。" } : step)));
  renderSources([]);
  latencyBadge.textContent = "处理中";
  setLoading(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        top_k: Number(topKInput.value || 3),
      }),
    });
    const data = await readJson(response);
    if (!response.ok) {
      throw new Error(data.detail || "请求失败");
    }
    placeholder.classList.remove("loading");
    placeholder.textContent = data.answer;
    renderProcess(data.process);
    renderSources(data.sources);
    latencyBadge.textContent = `${data.metrics.latency_ms} ms`;
    questionInput.value = "";
    await refreshHealth();
  } catch (error) {
    placeholder.classList.remove("loading");
    placeholder.textContent = `请求失败：${error.message}`;
    renderProcess(defaultProcess.map((step) => (step.step === 1 ? { ...step, status: "failed", detail: error.message } : step)));
  } finally {
    setLoading(false);
  }
}

function clearChat() {
  chatLog.innerHTML = `
    <div class="message assistant">
      <div class="avatar">AI</div>
      <div class="bubble">你好，我是基于本地 Ollama 与 RAG 知识库的 NXP AIoT Cloud 智能客服。请选择示例问题或直接输入问题。</div>
    </div>
  `;
  renderProcess(defaultProcess);
  renderSources([]);
  latencyBadge.textContent = "待提问";
}

chatForm.addEventListener("submit", sendQuestion);
rebuildIndexBtn.addEventListener("click", rebuildIndex);
refreshStatusBtn.addEventListener("click", refreshHealth);
clearChatBtn.addEventListener("click", clearChat);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

renderProcess(defaultProcess);
renderSources([]);
refreshHealth();
loadSampleQuestions();
