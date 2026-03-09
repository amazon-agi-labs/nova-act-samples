let tasks = [
  {
    id: 1,
    text: "Review pull request for auth module",
    priority: "high",
    completed: false,
  },
  {
    id: 2,
    text: "Update API documentation",
    priority: "medium",
    completed: false,
  },
  {
    id: 3,
    text: "Fix CSS alignment on dashboard",
    priority: "low",
    completed: true,
  },
  {
    id: 4,
    text: "Write unit tests for payment flow",
    priority: "high",
    completed: false,
  },
];
let currentFilter = "all";
let nextId = 5;

function render() {
  const list = document.getElementById("task-list");
  const filtered = tasks.filter((t) => {
    if (currentFilter === "active") return !t.completed;
    if (currentFilter === "completed") return t.completed;
    return true;
  });

  if (filtered.length === 0) {
    list.innerHTML = '<li class="empty-state">No tasks to show</li>';
  } else {
    list.innerHTML = filtered
      .map(
        (t) => `
      <li class="task-item ${t.completed ? "completed" : ""}" data-id="${t.id}">
        <input type="checkbox" ${t.completed ? "checked" : ""} aria-label="Mark ${t.text} as ${t.completed ? "incomplete" : "complete"}">
        <span class="task-text">${t.text}</span>
        <span class="task-priority priority-${t.priority}">${t.priority}</span>
        <button class="delete-btn" aria-label="Delete ${t.text}">&times;</button>
      </li>`,
      )
      .join("");
  }

  const total = tasks.length;
  const done = tasks.filter((t) => t.completed).length;
  const active = total - done;
  document.getElementById("stats").innerHTML =
    `Total: <span>${total}</span> &nbsp;|&nbsp; Active: <span>${active}</span> &nbsp;|&nbsp; Completed: <span>${done}</span>`;
}

document.getElementById("add-btn").addEventListener("click", () => {
  const input = document.getElementById("task-input");
  const text = input.value.trim();
  if (!text) return;
  const priority = document.getElementById("priority-select").value;
  tasks.push({ id: nextId++, text, priority, completed: false });
  input.value = "";
  render();
});

document.getElementById("task-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("add-btn").click();
});

document.getElementById("task-list").addEventListener("click", (e) => {
  const item = e.target.closest(".task-item");
  if (!item) return;
  const id = Number(item.dataset.id);

  if (e.target.type === "checkbox") {
    const task = tasks.find((t) => t.id === id);
    if (task) task.completed = e.target.checked;
    render();
  } else if (e.target.classList.contains("delete-btn")) {
    tasks = tasks.filter((t) => t.id !== id);
    render();
  }
});

document.querySelectorAll(".filters button").forEach((btn) => {
  btn.addEventListener("click", () => {
    currentFilter = btn.dataset.filter;
    document
      .querySelectorAll(".filters button")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    render();
  });
});

render();
