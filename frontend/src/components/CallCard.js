/** Карточка звонка. */
function renderCallCard(call) {
  const badgeClass = call.status === 'completed' ? 'badge--completed' : 'badge--pending';
  const el = document.createElement('div');
  el.className = 'call-card';
  el.innerHTML = `
    <div class="call-card__info">
      <div class="call-card__title">📞 ${call.customer_phone}</div>
      <div class="call-card__sub">Агент: ${call.agent_id} · ${new Date(call.started_at).toLocaleString('ru')}</div>
    </div>
    <span class="badge ${badgeClass}">${call.status}</span>
  `;
  return el;
}
