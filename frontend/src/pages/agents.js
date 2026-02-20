/** Страница агентов. */
async function loadAgents() {
  const container = document.getElementById('agents-list');
  try {
    const agents = await api.getAgents();
    container.innerHTML = '';
    if (agents.length === 0) {
      container.innerHTML = '<div class="empty-state">Агентов нет. Добавьте первого!</div>';
    } else {
      agents.forEach(a => container.appendChild(renderAgentCard(a)));
    }
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Не удалось загрузить агентов: ${e.message}</div>`;
  }
}

function initAgentsPage() {
  document.getElementById('btn-add-agent').addEventListener('click', () => {
    document.getElementById('modal-add-agent').classList.remove('hidden');
  });
  document.getElementById('btn-cancel-agent').addEventListener('click', () => {
    document.getElementById('modal-add-agent').classList.add('hidden');
  });
  document.getElementById('form-add-agent').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      await api.createAgent({ name: data.name, department: data.department, email: data.email });
      document.getElementById('modal-add-agent').classList.add('hidden');
      e.target.reset();
      await loadAgents();
    } catch (err) {
      alert('Ошибка: ' + err.message);
    }
  });
}
