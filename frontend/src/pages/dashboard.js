/** Дашборд: статистика и последние звонки. */
async function loadDashboard() {
  try {
    const [calls, analyses] = await Promise.all([api.getCalls(), api.getAnalyses()]);

    document.getElementById('stat-total-calls').textContent = calls.length;
    document.getElementById('stat-analyzed').textContent = analyses.length;

    const positiveCount = analyses.filter(a => a.sentiment === 'positive').length;
    document.getElementById('stat-positive').textContent = positiveCount;

    const avgQuality = analyses.length
      ? (analyses.reduce((s, a) => s + a.quality_score, 0) / analyses.length).toFixed(1)
      : '—';
    document.getElementById('stat-avg-quality').textContent = avgQuality;

    const container = document.getElementById('recent-calls-list');
    container.innerHTML = '';
    if (calls.length === 0) {
      container.innerHTML = '<div class="empty-state">Звонков пока нет</div>';
    } else {
      calls.slice(-5).reverse().forEach(c => container.appendChild(renderCallCard(c)));
    }
  } catch (e) {
    console.warn('Dashboard load error (API может быть недоступно):', e.message);
  }
}
