const tg = window.Telegram?.WebApp;
const initData = tg?.initData || '';
const topics = {brasil:'Brasil',guerras:'Guerras',politica:'Política',ciencia:'Ciência',mulheres:'Mulheres',civilizacoes:'Civilizações',geral:'Geral'};
const missionLabels = {explore:'Explorar um fato',save:'Salvar no Meu Museu',quiz:'Responder um quiz'};
let profile = null;
let currentFacts = new Map();

tg?.ready();
tg?.expand();
document.querySelector('#closeButton').addEventListener('click', () => tg?.close());

async function api(action, options={}) {
  const headers = {'Content-Type':'application/json', ...(options.headers||{})};
  if(initData) headers['X-Telegram-Init-Data'] = initData;
  const response = await fetch(`/api?action=${action}`, {...options, headers});
  const data = await response.json();
  if(!response.ok) throw new Error(data.error || 'Não foi possível carregar');
  return data;
}

function escapeHtml(value='') {
  const element = document.createElement('div');
  element.textContent = String(value);
  return element.innerHTML;
}

function notify(message, type='success') {
  tg?.HapticFeedback?.notificationOccurred(type);
  if(tg?.showAlert) tg.showAlert(message); else window.alert(message);
}

document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', async () => {
  document.querySelectorAll('.tab,.view').forEach(element => element.classList.remove('active'));
  tab.classList.add('active');
  document.querySelector(`#${tab.dataset.view}`).classList.add('active');
  if(tab.dataset.view === 'ranking') await loadRanking();
  if(tab.dataset.view === 'favorites') await loadFavorites();
  if(tab.dataset.view === 'mission') await loadMission();
  if(tab.dataset.view === 'admin') await loadAdmin();
}));

function factCard(item, saved=false) {
  const favoriteButton = saved
    ? `<button class="remove-favorite" data-id="${item.fact_id||item.id}">Remover</button>`
    : `<button class="save-fact" data-id="${item.id}">⭐ Salvar</button>`;
  return `<article class="fact"><small>${escapeHtml(item.date)} · Fonte: ${escapeHtml(item.source||'base curada')}</small><p>${escapeHtml(item.text)}</p><div class="fact-actions">${favoriteButton}<button class="share" data-id="${item.fact_id||item.id}">Compartilhar ↗</button></div></article>`;
}

function bindFactActions(container) {
  container.querySelectorAll('.save-fact').forEach(button => button.addEventListener('click', () => saveFact(button.dataset.id)));
  container.querySelectorAll('.remove-favorite').forEach(button => button.addEventListener('click', () => removeFavorite(button.dataset.id)));
  container.querySelectorAll('.share').forEach(button => button.addEventListener('click', () => shareFact(button.dataset.id)));
}

function showFacts(items) {
  const results = document.querySelector('#results');
  items.forEach(item => currentFacts.set(item.id, item));
  results.innerHTML = items.length
    ? items.map(item => factCard(item)).join('')
    : '<p class="empty">Nenhum fato encontrado. Tente outro termo ou data.</p>';
  bindFactActions(results);
  if(initData && items.length) loadMission();
}

async function saveFact(factId) {
  if(!initData) { notify('Abra pelo Telegram para salvar.', 'error'); return; }
  const collection = window.prompt('Em qual coleção deseja salvar?', 'Meu Museu');
  if(collection === null) return;
  try {
    const result = await api('favorite', {method:'POST', body:JSON.stringify({fact_id:factId, collection})});
    notify(result.mission?.completed ? 'Fato salvo e missão diária concluída: +25 XP!' : 'Fato salvo no seu Museu.');
    await loadMission();
  } catch(error) { notify(error.message, 'error'); }
}

async function removeFavorite(factId) {
  try {
    await api('favorite', {method:'POST', body:JSON.stringify({fact_id:factId, operation:'remove'})});
    await loadFavorites();
  } catch(error) { notify(error.message, 'error'); }
}

async function shareFact(factId) {
  const fact = currentFacts.get(factId);
  if(!initData || typeof tg?.shareMessage !== 'function') {
    const text = fact?.text || 'Descubra fatos históricos no Museu Histórico.';
    const url = `https://t.me/share/url?url=${encodeURIComponent(location.origin)}&text=${encodeURIComponent(text+' — @fatoshistbot')}`;
    if(tg) tg.openTelegramLink(url); else window.open(url, '_blank');
    return;
  }
  try {
    const prepared = await api('prepare-share', {method:'POST', body:JSON.stringify({fact_id:factId})});
    tg.shareMessage(prepared.id, success => {
      if(success) tg.HapticFeedback?.notificationOccurred('success');
    });
  } catch(error) { notify(error.message, 'error'); }
}

document.querySelector('#searchForm').addEventListener('submit', async event => {
  event.preventDefault();
  try { showFacts((await api(`search&q=${encodeURIComponent(document.querySelector('#searchInput').value)}`)).items); }
  catch(error) { notify(error.message, 'error'); }
});

document.querySelector('#dateForm').addEventListener('submit', async event => {
  event.preventDefault();
  try { showFacts((await api(`date&date=${encodeURIComponent(document.querySelector('#dateInput').value)}`)).items); }
  catch(error) { notify(error.message, 'error'); }
});

function renderProfile(data) {
  const accuracy = data.questions ? Math.round(data.hits/data.questions*100) : 0;
  document.querySelector('#greeting').textContent = `Olá, ${data.first_name}. Viaje por séculos de história.`;
  document.querySelector('#passportCard').innerHTML = `<span class="eyebrow">PASSAPORTE HISTÓRICO</span><h3>${escapeHtml(data.first_name)} ${data.premium?'⭐':''}</h3><div class="stats"><div class="stat"><strong>${data.level}</strong>Nível</div><div class="stat"><strong>${data.xp}</strong>XP</div><div class="stat"><strong>${data.streak}</strong>Sequência</div></div><p>Precisão no quiz: <b>${accuracy}%</b></p><div class="badges">${(data.badges.length?data.badges:['Primeiro passo pendente']).map(item=>`<span class="badge">${escapeHtml(item.replaceAll('_',' '))}</span>`).join('')}</div>`;
  document.querySelector('#frequency').value = data.preferences.frequency;
  document.querySelector('#deliveryHour').value = String(data.preferences.delivery_hour);
  document.querySelectorAll('[name="topic"]').forEach(input => input.checked=data.preferences.topics.includes(input.value));
  document.querySelector('#adminTab').hidden = !data.admin;
  renderMission(data.mission);
}

function renderMission(mission) {
  if(!mission) return;
  const actions = new Set(mission.actions || []);
  document.querySelector('#missionTasks').innerHTML = mission.required.map(action => {
    const done = actions.has(action);
    return `<div class="mission-task ${done?'done':''}"><span class="check">${done?'✓':'○'}</span><span>${escapeHtml(missionLabels[action]||action)}</span></div>`;
  }).join('');
  document.querySelector('#missionReward').textContent = mission.completed
    ? `✅ Missão concluída — ${mission.reward_xp} XP recebidos.`
    : `${actions.size}/${mission.required.length} etapas concluídas · Recompensa: ${mission.reward_xp} XP`;
}

async function loadMission() {
  if(!initData) return;
  try { renderMission(await api('mission')); }
  catch(error) { document.querySelector('#missionReward').textContent = error.message; }
}

async function loadFavorites() {
  const box = document.querySelector('#favoritesList');
  if(!initData) { box.innerHTML='<p class="empty">Abra pelo Telegram para acessar seu Museu.</p>'; return; }
  try {
    const items = (await api('favorites')).items;
    items.forEach(item => currentFacts.set(item.fact_id||item.id, item));
    if(!items.length) { box.innerHTML='<p class="empty">Você ainda não salvou nenhum fato.</p>'; return; }
    const groups = Object.groupBy
      ? Object.groupBy(items, item => item.collection || 'Meu Museu')
      : items.reduce((result,item)=>{(result[item.collection||'Meu Museu']??=[]).push(item);return result},{});
    box.innerHTML = Object.entries(groups).map(([name,facts]) => `<section class="collection"><h4>${escapeHtml(name)} · ${facts.length}</h4>${facts.map(item=>factCard(item,true)).join('')}</section>`).join('');
    bindFactActions(box);
  } catch(error) { box.innerHTML=`<p class="empty">${escapeHtml(error.message)}</p>`; }
}

async function loadRanking() {
  const box = document.querySelector('#rankingList');
  if(!initData) { box.innerHTML='<p class="empty">Abra pelo Telegram para ver o ranking.</p>'; return; }
  try {
    const data = await api('ranking');
    box.innerHTML = data.items.map((user,index)=>`<div class="rank"><b>${index+1}</b><span>${escapeHtml(user.first_name||'Historiador')}</span><strong>${user.xp} XP</strong></div>`).join('') || '<p class="empty">Ranking ainda vazio.</p>';
  } catch(error) { box.textContent=error.message; }
}

function formatDate(value) {
  if(!value) return 'Sem horário';
  return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short'}).format(new Date(value));
}

async function loadAdmin() {
  if(!profile?.admin) return;
  try {
    const data = await api('admin');
    document.querySelector('#adminStats').innerHTML = Object.entries(data.stats).map(([key,value])=>`<div class="admin-stat"><strong>${value}</strong>${escapeHtml(key.replaceAll('_',' '))}</div>`).join('');
    document.querySelector('#adminSuggestions').innerHTML = data.suggestions.map(item=>`<article class="admin-row"><small>${escapeHtml(item.first_name)}</small><p>${escapeHtml(item.text)}</p><small>${escapeHtml(item.source)}</small><div class="admin-actions"><button class="approve" data-suggestion="${item.id}" data-decision="approve">Aprovar</button><button class="danger" data-suggestion="${item.id}" data-decision="reject">Recusar</button></div></article>`).join('') || '<p class="empty">Nenhuma sugestão pendente.</p>';
    document.querySelector('#adminQueue').innerHTML = data.queue.map(item=>`<article class="admin-row"><b>${escapeHtml(item.type)}</b><p>${formatDate(item.scheduled_at)} · ${escapeHtml(item.status)}</p>${item.status==='pending'?`<div class="admin-actions"><button data-queue="${item.id}" data-operation="delay">Próximo horário</button><button class="danger" data-queue="${item.id}" data-operation="cancel">Cancelar</button></div>`:''}</article>`).join('') || '<p class="empty">Fila vazia.</p>';
    bindAdminActions();
  } catch(error) { notify(error.message, 'error'); }
}

function bindAdminActions() {
  document.querySelectorAll('[data-suggestion]').forEach(button => button.addEventListener('click', async () => {
    if(!window.confirm('Confirmar esta decisão?')) return;
    try { await api('admin-suggestion',{method:'POST',body:JSON.stringify({id:button.dataset.suggestion,decision:button.dataset.decision})}); await loadAdmin(); }
    catch(error) { notify(error.message,'error'); }
  }));
  document.querySelectorAll('[data-queue]').forEach(button => button.addEventListener('click', async () => {
    if(!window.confirm('Confirmar alteração na fila?')) return;
    try { await api('admin-queue',{method:'POST',body:JSON.stringify({id:button.dataset.queue,operation:button.dataset.operation,minutes:60})}); await loadAdmin(); }
    catch(error) { notify(error.message,'error'); }
  }));
}

document.querySelector('#refreshFavorites').addEventListener('click', loadFavorites);
document.querySelector('#refreshAdmin').addEventListener('click', loadAdmin);

const topicBox = document.querySelector('#topicOptions');
topicBox.innerHTML = Object.entries(topics).map(([key,label])=>`<label class="chip"><input type="checkbox" name="topic" value="${key}"> ${label}</label>`).join('');
document.querySelector('#preferencesForm').addEventListener('submit', async event => {
  event.preventDefault();
  const status=document.querySelector('#saveStatus');
  if(!initData) { status.textContent='Abra a Mini App pelo Telegram para salvar.'; return; }
  try {
    const payload={topics:[...document.querySelectorAll('[name="topic"]:checked')].map(input=>input.value),frequency:document.querySelector('#frequency').value,delivery_hour:Number(document.querySelector('#deliveryHour').value)};
    await api('preferences',{method:'POST',body:JSON.stringify(payload)});
    status.textContent='Preferências salvas.';
    tg?.HapticFeedback?.notificationOccurred('success');
  } catch(error) { status.textContent=error.message; }
});

(async function init(){
  if(!initData) return;
  try { profile=await api('profile'); renderProfile(profile); }
  catch(error) { document.querySelector('#passportCard').textContent=error.message; }
})();
