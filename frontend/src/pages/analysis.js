/** Страница анализа звонков. */
async function loadAnalysis() {
  const container = document.getElementById('analysis-list');
  try {
    const results = await api.getAnalyses();
    container.innerHTML = '';
    if (results.length === 0) {
      container.innerHTML = '<div class="empty-state">Результатов анализа нет</div>';
    } else {
      results.forEach(r => container.appendChild(renderAnalysisCard(r)));
    }
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Не удалось загрузить анализ: ${e.message}</div>`;
  }
}
