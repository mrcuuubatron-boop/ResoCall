/** Карточка агента. */
function renderAgentCard(agent) {
  const el = document.createElement('div');
  el.className = 'agent-card';
  el.innerHTML = `
    <div class="agent-card__info">
      <div class="agent-card__name">👤 ${agent.name}</div>
      <div class="agent-card__sub">${agent.department || 'Отдел не указан'} · ${agent.email || '—'}</div>
    </div>
  `;
  return el;
}
