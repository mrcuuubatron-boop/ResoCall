/** Карточка результата анализа. */
function renderAnalysisCard(result) {
  const sentimentMap = { positive: 'badge--positive', neutral: 'badge--neutral', negative: 'badge--negative' };
  const sentimentLabel = { positive: '😊 Позитив', neutral: '😐 Нейтраль', negative: '😠 Негатив' };
  const badgeClass = sentimentMap[result.sentiment] || 'badge--neutral';
  const quality = Math.round(result.quality_score);
  const keywords = result.keywords.slice(0, 5).join(', ') || '—';

  const el = document.createElement('div');
  el.className = 'analysis-card';
  el.innerHTML = `
    <div class="analysis-card__info">
      <div class="analysis-card__title">🔍 Звонок: ${result.call_id.slice(0, 8)}…</div>
      <div class="quality-bar">
        <div class="quality-bar__track">
          <div class="quality-bar__fill" style="width:${quality}%"></div>
        </div>
        <span class="quality-bar__label">${quality}/100</span>
      </div>
      <div class="analysis-card__sub">Ключевые слова: ${keywords}</div>
    </div>
    <span class="badge ${badgeClass}">${sentimentLabel[result.sentiment] || result.sentiment}</span>
  `;
  return el;
}
