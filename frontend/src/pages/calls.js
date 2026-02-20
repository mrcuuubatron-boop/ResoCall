/** Страница звонков. */
async function loadCalls() {
  const container = document.getElementById('calls-list');
  try {
    const calls = await api.getCalls();
    container.innerHTML = '';
    if (calls.length === 0) {
      container.innerHTML = '<div class="empty-state">Звонков нет. Добавьте первый!</div>';
    } else {
      calls.reverse().forEach(c => container.appendChild(renderCallCard(c)));
    }
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Не удалось загрузить звонки: ${e.message}</div>`;
  }
}

function initCallsPage() {
  document.getElementById('btn-add-call').addEventListener('click', () => {
    document.getElementById('modal-add-call').classList.remove('hidden');
  });
  document.getElementById('btn-cancel-call').addEventListener('click', () => {
    document.getElementById('modal-add-call').classList.add('hidden');
  });
  document.getElementById('form-add-call').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      await api.createCall({ agent_id: data.agent_id, customer_phone: data.customer_phone });
      document.getElementById('modal-add-call').classList.add('hidden');
      e.target.reset();
      await loadCalls();
    } catch (err) {
      alert('Ошибка: ' + err.message);
    }
  });
}
