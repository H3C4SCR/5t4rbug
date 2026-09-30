const STORAGE_KEY = "5t4rbug.tasks.v2";
const VALID_PRIORITIES = new Set(["low", "medium", "high"]);
const VALID_STATUSES = new Set(["pending", "in_progress", "done"]);
const priorityLabels = { high: "ALTA", medium: "MÉDIA", low: "BAIXA" };
const statusLabels = { pending: "Pendente", in_progress: "Em andamento", done: "Concluída" };

const state = { tasks: [], filter: "all" };
const elements = {};

function byId(id) {
  return document.getElementById(id);
}

function makeId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function validTask(task) {
  return task && typeof task.id === "string" && typeof task.title === "string"
    && task.title.trim().length > 0 && task.title.length <= 120
    && typeof task.description === "string" && task.description.length <= 2000
    && VALID_PRIORITIES.has(task.priority) && VALID_STATUSES.has(task.status)
    && (!task.dueDate || /^\d{4}-\d{2}-\d{2}$/.test(task.dueDate))
    && (!task.reminderAt || !Number.isNaN(new Date(task.reminderAt).getTime()));
}

function loadTasks() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]");
    state.tasks = Array.isArray(stored) ? stored.filter(validTask) : [];
  } catch (_error) {
    state.tasks = [];
    setNotice("Não foi possível ler o armazenamento deste navegador.", "error");
  }
}

function saveTasks() {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state.tasks));
    return true;
  } catch (_error) {
    setNotice("Não foi possível salvar. O armazenamento do navegador pode estar cheio ou bloqueado.", "error");
    return false;
  }
}

function setNotice(message, type = "info") {
  elements.notificationStatus.textContent = message;
  elements.notificationStatus.className = `notice notice-${type}`;
}

function textElement(tag, className, text) {
  const element = document.createElement(tag);
  element.className = className;
  element.textContent = text;
  return element;
}

function formatDueDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(new Date(`${value}T12:00:00`));
}

function formatReminder(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function sortTasks(tasks) {
  const priorityOrder = { high: 1, medium: 2, low: 3 };
  return [...tasks].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]
    || (a.dueDate ? 0 : 1) - (b.dueDate ? 0 : 1)
    || (a.dueDate || "9999-99-99").localeCompare(b.dueDate || "9999-99-99")
    || b.createdAt.localeCompare(a.createdAt));
}

function renderTasks() {
  elements.taskList.replaceChildren();
  const visible = sortTasks(state.tasks.filter((task) => state.filter === "all" || task.status === state.filter));
  elements.emptyState.hidden = visible.length > 0;

  visible.forEach((task) => {
    const card = document.createElement("article");
    card.className = `task-card ${task.status === "done" ? "is-done" : ""}`;

    const top = document.createElement("div");
    top.className = "task-top";
    const heading = document.createElement("div");
    heading.append(textElement("h3", "", task.title), textElement("span", `badge priority-${task.priority}`, priorityLabels[task.priority]));
    top.append(heading, textElement("span", "task-meta", statusLabels[task.status]));
    card.append(top);

    if (task.description) card.append(textElement("p", "", task.description));
    if (task.dueDate) card.append(textElement("div", "task-meta", `Prazo: ${formatDueDate(task.dueDate)}`));
    if (task.notify && task.reminderAt && task.status !== "done") {
      card.append(textElement("div", "task-meta", `Lembrete: ${formatReminder(task.reminderAt)}`));
    }

    const actions = document.createElement("div");
    actions.className = "task-actions";
    const toggle = textElement("button", "link-button", task.status === "done" ? "Reabrir" : "Concluir");
    toggle.type = "button";
    toggle.addEventListener("click", () => toggleTask(task.id));
    const edit = textElement("button", "link-button", "Editar");
    edit.type = "button";
    edit.addEventListener("click", () => editTask(task));
    const remove = textElement("button", "link-button", "Excluir");
    remove.type = "button";
    remove.addEventListener("click", () => deleteTask(task.id));
    actions.append(toggle, edit, remove);
    card.append(actions);
    elements.taskList.append(card);
  });
}

function clearForm() {
  elements.form.reset();
  elements.taskId.value = "";
  elements.status.value = "pending";
  elements.formHeading.textContent = "Nova tarefa";
  elements.saveTask.textContent = "Adicionar tarefa";
  elements.cancelEdit.hidden = true;
  elements.formMessage.textContent = "";
}

function editTask(task) {
  elements.taskId.value = task.id;
  elements.title.value = task.title;
  elements.description.value = task.description;
  elements.priority.value = task.priority;
  elements.status.value = task.status;
  elements.dueDate.value = task.dueDate || "";
  elements.reminderAt.value = task.reminderAt ? task.reminderAt.slice(0, 16) : "";
  elements.notify.checked = Boolean(task.notify);
  elements.formHeading.textContent = "Editar tarefa";
  elements.saveTask.textContent = "Salvar alteração";
  elements.cancelEdit.hidden = false;
  elements.title.focus();
}

function getFormTask() {
  const title = elements.title.value.trim();
  const reminderAt = elements.reminderAt.value ? new Date(elements.reminderAt.value).toISOString() : null;
  if (!title || title.length > 120) return { error: "O título é obrigatório e deve ter até 120 caracteres." };
  if (elements.description.value.length > 2000) return { error: "A descrição deve ter até 2.000 caracteres." };
  if (elements.notify.checked && !reminderAt) return { error: "Escolha data e hora para ativar o lembrete." };
  return {
    title,
    description: elements.description.value.trim(),
    priority: elements.priority.value,
    status: elements.status.value,
    dueDate: elements.dueDate.value || null,
    reminderAt,
    notify: elements.notify.checked,
  };
}

function saveForm(event) {
  event.preventDefault();
  const result = getFormTask();
  elements.formMessage.textContent = result.error || "";
  if (result.error) return;

  const existingId = elements.taskId.value;
  const current = state.tasks.find((task) => task.id === existingId);
  const task = {
    id: existingId || makeId(),
    ...result,
    createdAt: current ? current.createdAt : new Date().toISOString(),
    notifiedAt: current && current.reminderAt === result.reminderAt && current.notify === result.notify ? current.notifiedAt : null,
  };
  state.tasks = existingId ? state.tasks.map((item) => item.id === existingId ? task : item) : [...state.tasks, task];
  if (saveTasks()) {
    clearForm();
    renderTasks();
  }
}

function toggleTask(id) {
  state.tasks = state.tasks.map((task) => task.id === id ? { ...task, status: task.status === "done" ? "pending" : "done" } : task);
  saveTasks();
  renderTasks();
}

function deleteTask(id) {
  if (!window.confirm("Excluir esta tarefa?")) return;
  state.tasks = state.tasks.filter((task) => task.id !== id);
  saveTasks();
  renderTasks();
}

async function enableNotifications() {
  if (!("Notification" in window)) {
    setNotice("Este navegador não oferece notificações web.", "error");
    return;
  }
  if (!window.isSecureContext) {
    setNotice("Notificações exigem HTTPS ou localhost.", "error");
    return;
  }
  const permission = await Notification.requestPermission();
  setNotice(permission === "granted" ? "Lembretes ativados neste navegador." : "Lembretes não foram autorizados.", permission === "granted" ? "success" : "error");
  checkReminders();
}

function checkReminders() {
  if (!("Notification" in window) || Notification.permission !== "granted") return;
  const now = Date.now();
  let changed = false;
  state.tasks = state.tasks.map((task) => {
    if (task.notify && task.status !== "done" && task.reminderAt && !task.notifiedAt && new Date(task.reminderAt).getTime() <= now) {
      try {
        new Notification("Lembrete 5T4RBUG", { body: task.title, tag: `5t4rbug-${task.id}` });
        changed = true;
        return { ...task, notifiedAt: new Date().toISOString() };
      } catch (_error) {
        return task;
      }
    }
    return task;
  });
  if (changed) {
    saveTasks();
    renderTasks();
  }
}

function setFilter(event) {
  state.filter = event.currentTarget.dataset.filter;
  document.querySelectorAll(".filter").forEach((button) => button.classList.toggle("active", button === event.currentTarget));
  renderTasks();
}

function init() {
  elements.form = byId("task-form");
  elements.taskId = byId("task-id");
  elements.title = byId("title");
  elements.description = byId("description");
  elements.priority = byId("priority");
  elements.status = byId("status");
  elements.dueDate = byId("due-date");
  elements.reminderAt = byId("reminder-at");
  elements.notify = byId("notify");
  elements.formHeading = byId("form-heading");
  elements.saveTask = byId("save-task");
  elements.cancelEdit = byId("cancel-edit");
  elements.formMessage = byId("form-message");
  elements.taskList = byId("task-list");
  elements.emptyState = byId("empty-state");
  elements.notificationStatus = byId("notification-status");
  loadTasks();
  renderTasks();
  elements.form.addEventListener("submit", saveForm);
  elements.cancelEdit.addEventListener("click", clearForm);
  byId("enable-notifications").addEventListener("click", enableNotifications);
  document.querySelectorAll(".filter").forEach((button) => button.addEventListener("click", setFilter));
  window.addEventListener("storage", () => { loadTasks(); renderTasks(); });
  document.addEventListener("visibilitychange", checkReminders);
  window.setInterval(checkReminders, 30000);
  checkReminders();
}

document.addEventListener("DOMContentLoaded", init);
