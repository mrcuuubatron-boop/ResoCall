/**
 * app.js — точка входа веб-приложения ResoCall.
 * Управляет навигацией между страницами и инициализирует каждую из них.
 */
(function () {
  const pages = {
    dashboard: { load: loadDashboard },
    calls:     { load: loadCalls,    init: initCallsPage },
    agents:    { load: loadAgents,   init: initAgentsPage },
    analysis:  { load: loadAnalysis },
  };

  let initialized = {};

  function showPage(name) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(a => a.classList.remove('active'));

    const page = document.getElementById(`page-${name}`);
    const link = document.querySelector(`.nav-link[data-page="${name}"]`);
    if (page) page.classList.add('active');
    if (link) link.classList.add('active');

    const handler = pages[name];
    if (!handler) return;

    if (handler.init && !initialized[name]) {
      handler.init();
      initialized[name] = true;
    }
    if (handler.load) handler.load();
  }

  // Navigation
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      showPage(link.dataset.page);
    });
  });

  // Initial page
  showPage('dashboard');
})();
