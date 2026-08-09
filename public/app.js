const tg = window.Telegram?.WebApp;
const initData = tg?.initData || '';
const topics = {brasil:'Brasil',guerras:'Guerras',politica:'Política',ciencia:'Ciência',mulheres:'Mulheres',civilizacoes:'Civilizações',geral:'Geral'};
let profile = null;

tg?.ready(); tg?.expand();
document.querySelector('#closeButton').addEventListener('click', () => tg?.close());
document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', async () => {
  document.querySelectorAll('.tab,.view').forEach(el => el.classList.remove('active'));
  tab.classList.add('active'); document.querySelector(`#${tab.dataset.view}`).classList.add('active');
  if(tab.dataset.view === 'ranking') await loadRanking();
}));

async function api(action, options={}) {
  const headers = {'Content-Type':'application/json', ...(options.headers||{})};
  if(initData) headers['X-Telegram-Init-Data'] = initData;
  const response = await fetch(`/api?action=${action}`, {...options, headers});
  const data = await response.json();
  if(!response.ok) throw new Error(data.error || 'Não foi possível carregar');
  return data;
}

function escapeHtml(value='') { const el=document.createElement('div'); el.textContent=value; return el.innerHTML; }
function showFacts(items) {
  const results=document.querySelector('#results');
  results.innerHTML = items.length ? items.map(item => `<article class="fact"><small>${escapeHtml(item.date)} · Fonte: ${escapeHtml(item.source||'base curada')}</small><p>${escapeHtml(item.text)}</p><button class="share" data-text="${encodeURIComponent(item.text)}">Compartilhar ↗</button></article>`).join('') : '<p class="empty">Nenhum fato encontrado. Tente outro termo ou data.</p>';
  results.querySelectorAll('.share').forEach(button => button.addEventListener('click', () => {
    const text=decodeURIComponent(button.dataset.text); const url=`https://t.me/share/url?url=${encodeURIComponent(location.origin)}&text=${encodeURIComponent(text+' — @fatoshistbot')}`;
    if(tg) tg.openTelegramLink(url); else window.open(url,'_blank');
  }));
}

document.querySelector('#searchForm').addEventListener('submit', async event => { event.preventDefault(); showFacts((await api(`search&q=${encodeURIComponent(document.querySelector('#searchInput').value)}`)).items); });
document.querySelector('#dateForm').addEventListener('submit', async event => { event.preventDefault(); showFacts((await api(`date&date=${encodeURIComponent(document.querySelector('#dateInput').value)}`)).items); });

function renderProfile(data) {
  const accuracy=data.questions ? Math.round(data.hits/data.questions*100) : 0;
  document.querySelector('#greeting').textContent=`Olá, ${data.first_name}. Viaje por séculos de história.`;
  document.querySelector('#passportCard').innerHTML=`<span class="eyebrow">PASSAPORTE HISTÓRICO</span><h3>${escapeHtml(data.first_name)} ${data.premium?'⭐':''}</h3><div class="stats"><div class="stat"><strong>${data.level}</strong>Nível</div><div class="stat"><strong>${data.xp}</strong>XP</div><div class="stat"><strong>${data.streak}</strong>Sequência</div></div><p>Precisão no quiz: <b>${accuracy}%</b></p><div class="badges">${(data.badges.length?data.badges:['Primeiro passo pendente']).map(x=>`<span class="badge">${escapeHtml(x.replaceAll('_',' '))}</span>`).join('')}</div>`;
  document.querySelector('#frequency').value=data.preferences.frequency;
  document.querySelector('#deliveryHour').value=String(data.preferences.delivery_hour);
  document.querySelectorAll('[name="topic"]').forEach(input => input.checked=data.preferences.topics.includes(input.value));
}

async function loadRanking(){ const box=document.querySelector('#rankingList'); if(!initData){box.innerHTML='<p class="empty">Abra pelo Telegram para ver o ranking.</p>';return} try{const data=await api('ranking');box.innerHTML=data.items.map((u,i)=>`<div class="rank"><b>${i+1}</b><span>${escapeHtml(u.first_name||'Historiador')}</span><strong>${u.xp} XP</strong></div>`).join('')||'<p class="empty">Ranking ainda vazio.</p>'}catch(e){box.textContent=e.message} }

const topicBox=document.querySelector('#topicOptions');
topicBox.innerHTML=Object.entries(topics).map(([key,label])=>`<label class="chip"><input type="checkbox" name="topic" value="${key}"> ${label}</label>`).join('');
document.querySelector('#preferencesForm').addEventListener('submit', async event => { event.preventDefault(); const status=document.querySelector('#saveStatus'); if(!initData){status.textContent='Abra a Mini App pelo Telegram para salvar.';return} try{const payload={topics:[...document.querySelectorAll('[name="topic"]:checked')].map(x=>x.value),frequency:document.querySelector('#frequency').value,delivery_hour:Number(document.querySelector('#deliveryHour').value)};await api('preferences',{method:'POST',body:JSON.stringify(payload)});status.textContent='Preferências salvas.';tg?.HapticFeedback?.notificationOccurred('success')}catch(e){status.textContent=e.message} });

(async function init(){ if(!initData) return; try{profile=await api('profile');renderProfile(profile)}catch(e){document.querySelector('#passportCard').textContent=e.message} })();
