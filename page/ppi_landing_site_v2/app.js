
(function(){
  const $ = (s,root=document)=>root.querySelector(s);
  const $$ = (s,root=document)=>Array.from(root.querySelectorAll(s));
  const phaseCols = [
    ['Estudos','status_dos_estudos'],['Consulta Pública','status_consulta_publica'],['TCU','status_do_tcu'],['Edital','status_do_edital'],['Leilão','status_do_leilao'],['Contrato','status_do_contrato']
  ];
  function lastCompletedIdx(rec){ let last=-1; for(let i=0;i<phaseCols.length;i++){ const v=(rec[phaseCols[i][1]]||'').toString().toLowerCase(); if(v.includes('conclu')||v.includes('completed')||v.includes('assinado')||v.includes('assinatura')) last=i;} return last; }
  function timelineHTML(rec){ 
    const states = phaseCols.map(_=>false); 
    const last = lastCompletedIdx(rec); 
    if(last >= 0){ 
        for(let i = 0; i <= last; i++) states[i] = true; 
    } 
    const completed = states.filter(Boolean).length; 
    const width = (completed/phaseCols.length*100).toFixed(2) + '%'; 
    
    const items = phaseCols.map((p, i) => {
        const isCompleted = states[i];
        const isCurrent = i === last + 1 && last >= 0;
        
        let statusClass = '';
        let statusIcon = '';
        let statusText = '';
        
        if (isCompleted) {
            statusClass = 'completed';
            statusIcon = '✓';
            statusText = 'Concluído';
        } else if (isCurrent) {
            statusClass = 'current';
            statusIcon = '';
            statusText = rec[phaseCols[i][1]] || 'Em andamento';
        } else {
            statusText = 'Pendente';
        }
        
        return `<div class="phase-item group" data-phase="${p[0].toLowerCase().replace(/\s+/g, '-')}">
            <div class="phase-dot ${statusClass}" title="${p[0]}: ${statusText}">
                ${statusIcon}
            </div>
            <div class="phase-label ${statusClass}">
                <span class="font-medium">${p[0]}</span>
                <div class="text-xs opacity-80 mt-0.5">${statusText}</div>
            </div>
        </div>`;
    }).join('');
    
    return `<div class="phase-timeline">
        <div class="phase-line"></div>
        <div class="phase-line-completed" style="width: ${width}"></div>
        <div class="phase-items">${items}</div>
    </div>`;
}

  function makeBars(container, obj, valueFormatter){ const entries=Object.entries(obj||{}); const total=entries.reduce((a,[_k,v])=>a+(typeof v==='number'?v:0),0); container.innerHTML = entries.sort((a,b)=>b[1]-a[1]).map(([k,v])=>{ const pct = total? (v/total*100).toFixed(1):0; const label=valueFormatter? valueFormatter(k): k; return `<div class="bar"><div class="lbl">${label}</div><div class="track"><div class="fill" style="width:${pct}%"></div></div><div style="width:60px;text-align:right; font-size:12px;">${(typeof v==='number')? v.toLocaleString('pt-BR'): v}</div></div>`; }).join(''); }

  function createPieChart(canvasId, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const entries = Object.entries(data);
    if (entries.length === 0) return;
    
    const colors = [
      '#1E40AF', '#0891B2', '#059669', '#10B981', '#3B82F6', 
      '#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#EF4444'
    ];
    
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: entries.map(([k]) => k),
        datasets: [{
          data: entries.map(([,v]) => v),
          backgroundColor: colors.slice(0, entries.length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 12,
              font: { size: 11 },
              boxWidth: 12
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((context.parsed / total) * 100).toFixed(1);
                return `${context.label}: ${context.parsed} (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }

  // ----- INDEX (landing) -----
  async function initIndex(){
    if(!$('#kpi-total')) return; // not on index
    const METRICS = await (await fetch('data/metrics.json')).json();
    $('#kpi-total').textContent = METRICS.total_projetos.toLocaleString('pt-BR');
    $('#kpi-coords').textContent = METRICS.projetos_com_coordenadas.toLocaleString('pt-BR');

    // custos por moeda (KPIs em chips + tabela detalhada)
    const costs = METRICS.custos_por_moeda||{};
    const chips = Object.entries(costs).map(([cur, s])=>`<span class="chip"><strong>${cur}</strong> • soma ${fmt(cur,s.soma)} • ${s.projetos_com_custo} proj.</span>`).join('');
    $('#cost-chips').innerHTML = chips || '<span class="chip">Sem dados de custo</span>';
    $('#cost-table').innerHTML = tableFromCosts(costs);

    // barras por setor (contagem)
    makeBars($('#bars-setor'), METRICS.por_setor||{});
    
    // gráfico de pizza por setor
    createPieChart('pie-setor', METRICS.por_setor||{}, 'Projetos por Setor');

    // barras por última etapa concluída (contagem)
    makeBars($('#bars-etapa'), METRICS.por_ultima_etapa_concluida||{});
    
    // gráfico de pizza por etapa
    createPieChart('pie-etapa', METRICS.por_ultima_etapa_concluida||{}, 'Projetos por Etapa');

    // barras de custo por setor (BRL se existir)
    const byCur = METRICS.custos_por_setor_por_moeda||{}; const brlObj = byCur['BRL']||{}; const formatted = {}; Object.keys(brlObj).forEach(k=> formatted[k]=brlObj[k]); makeBars($('#bars-custo-setor-brl'), formatted, k=>k);

    // por UF (top 10)
    const porUF = METRICS.por_uf||{}; const topUF = Object.fromEntries(Object.entries(porUF).slice(0,10)); makeBars($('#bars-uf'), topUF);

    // Top 10 BRL
    $('#top10').innerHTML = (METRICS.top10_custo_brl||[]).map((x,i)=>`<div class="bar"><div class="lbl">${i+1}. ${esc(x.nome)}</div><div class="track"><div class="fill" style="width:100%"></div></div><div style="width:120px;text-align:right; font-size:12px;">${fmt('BRL',x.valor)}</div></div>`).join('');

    // mapa com clustering
    const DATA = await (await fetch('data/projects_full.json')).json();
    initMapCluster(DATA);

    // quick form -> projects
    $('#go').addEventListener('click', ()=>{ const q=enc($('#q').value), s=enc($('#sector').value), e=enc($('#etapa').value); location.href=`projects.html?q=${q}&sector=${s}&etapa=${e}`; });
  }

  function esc(s){ return (s||'').toString().replace(/[&<>]/g, m=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[m])); }
  function enc(s){ return encodeURIComponent(s||''); }
  function fmt(cur, val){ try{ return new Intl.NumberFormat('pt-BR',{style:'currency',currency:cur}).format(val);}catch(e){ return `${cur} ${Number(val).toLocaleString('pt-BR')}`; } }
  function tableFromCosts(obj){ const rows = Object.entries(obj).map(([cur,v])=>`<tr><td>${cur}</td><td style="text-align:right">${fmt(cur,v.soma)}</td><td style="text-align:right">${fmt(cur,v.min)}</td><td style="text-align:right">${fmt(cur,v.max)}</td><td style="text-align:right">${fmt(cur,v.media)}</td><td style="text-align:right">${fmt(cur,v.mediana)}</td><td style="text-align:right">${v.projetos_com_custo}</td></tr>`).join(''); return `<div class="table"><table><thead><tr><th>Moeda</th><th>Soma</th><th>Mín</th><th>Máx</th><th>Média</th><th>Mediana</th><th>Projetos</th></tr></thead><tbody>${rows||'<tr><td colspan="7">—</td></tr>'}</tbody></table></div>`; }

  function initMapCluster(DATA){
    if(typeof L==='undefined'){ $('#map').textContent='(Mapa requer conexão para carregar a biblioteca Leaflet)'; return; }
    const map = L.map('map').setView([-14.2,-51.9], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map);
    let group;
    if(window.L && L.markerClusterGroup){ group = L.markerClusterGroup(); map.addLayer(group);} else { group = L.layerGroup().addTo(map); }
    DATA.forEach(p=>{ const lat=parseFloat(p.latitude), lon=parseFloat(p.longitude); if(!isNaN(lat)&&!isNaN(lon)){ const t=(p.nome_completo||p.nome_projeto||'Projeto'); const s=(p.setor||''); const pop = `<strong>${esc(t)}</strong><br/><small>${esc(s)}</small>`; const m = L.marker([lat,lon]).bindPopup(pop); group.addLayer(m);} });
    try{ if(group.getLayers && group.getLayers().length){ map.fitBounds(group.getBounds(), {padding:[20,20]}); } }catch(e){}
  }

  // ----- PROJECTS (filters & cards) -----
  async function initProjects(){
    if(!$('#grid')) return; // not on projects
    const DATA = await (await fetch('data/projects_full.json')).json();
    const sectorSel = $('#sector');
    const sectors = [...new Set(DATA.map(p=>p.setor).filter(Boolean))].sort(); sectors.forEach(v=>{ const o=document.createElement('option'); o.value=o.textContent=v; sectorSel.appendChild(o); });

    const params = new URLSearchParams(location.search); $('#q').value=params.get('q')||''; $('#sector').value=params.get('sector')||''; $('#etapa').value=params.get('etapa')||'';

    function cardTemplate(p){ 
    const nome = p.nome_completo || p.nome_projeto || 'Projeto';
    const setor = p.setor || '';
    const desc = p.descricao_do_projeto || p.descricao_curta || '';
    const situ = p.status_atual_do_projeto || '—';
    const deliberacao = p.deliberacao || '—';
    const riscos = p.questoes_chaves || '';
    const lat = parseFloat(p.latitude), lon = parseFloat(p.longitude);
    
    const mapa = (!isNaN(lat) && !isNaN(lon)) ? 
        `<div class="space-y-4">
            <div class="h-64 w-full rounded-lg overflow-hidden border border-gray-200">
                <iframe 
                    width="100%" 
                    height="100%" 
                    frameborder="0" 
                    scrolling="no" 
                    marginheight="0" 
                    marginwidth="0" 
                    src="https://maps.google.com/maps?q=${lat},${lon}&z=15&output=embed">
                </iframe>
            </div>
            <p class="text-sm text-gray-500 mt-2">Coordenadas: ${lat.toFixed(4)}, ${lon.toFixed(4)}</p>
        </div>` : 
        `<div class="space-y-4">
            <div class="bg-gray-100 rounded-lg h-64 flex items-center justify-center text-gray-500">
                <div class="text-center p-6">
                    <i class="fas fa-map-marked-alt text-4xl mb-2 text-gray-300"></i>
                    <p>Localização não disponível</p>
                </div>
            </div>
        </div>`;
    
    const riscosList = riscos ? 
        riscos.split(/\n|;|•/).filter(x => x.trim()).map(x => `<li>${esc(x.trim())}</li>`).join('') : 
        '<li>Nenhum ponto de atenção identificado</li>';
    
    return `<article class="card">
      <div class="card-header">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div>
            <p style="color: #6b7280; font-size: 14px; margin: 0 0 8px 0;">${esc(setor)}</p>
            <h3 style="color: #1f2937; font-size: 20px; margin: 0; font-weight: 700;">${esc(nome)}</h3>
          </div>
        </div>
      </div>

      <div class="project-info-grid">
        <div class="left-col">
          <div class="info-large description">
            <h4>Descrição</h4>
            <p>${esc(desc)}</p>
          </div>

          <div class="row-2cols">
            <div class="info-small">
              <h5>Situação Atual</h5>
              <p>${esc(situ)}</p>
            </div>

            <div class="info-small">
              <h5>Próximos Passos</h5>
              <p>${esc(deliberacao)}</p>
            </div>
          </div>

          <div class="info-large">
            <h4>Pontos de Atenção</h4>
            <ul class="list-disc list-inside space-y-1 text-gray-700">
              ${riscosList}
            </ul>
          </div>
        </div>

        <div class="right-col">
          ${mapa}
        </div>

        <div class="timeline-col">
          <h4>ETAPA</h4>
          ${timelineHTML(p)}
        </div>
      </div>
    </article>`;
}

    const etapaSel = $('#etapa'); const etapaLabels=['Nenhuma', ...phaseCols.map(p=>p[0])]; etapaLabels.forEach(l=>{ const o=document.createElement('option'); o.value=o.textContent=l; etapaSel.appendChild(o); });

    function apply(){ const q=($('#q').value||'').toLowerCase().trim(); const sector=$('#sector').value||''; const etapa=$('#etapa').value||''; const filtered = DATA.filter(p=>{ const okQ=!q || ((p.nome_completo||'').toLowerCase().includes(q) || (p.descricao_do_projeto||'').toLowerCase().includes(q) || (p.localizacoes||'').toLowerCase().includes(q)); const okS=!sector||(p.setor===sector); let okE=true; if(etapa){ const idx=lastCompletedIdx(p); const lab=idx<0?'Nenhuma':phaseCols[idx][0]; okE=(lab===etapa);} return okQ&&okS&&okE; }); $('#grid').innerHTML = filtered.map(cardTemplate).join(''); $('#count').textContent = String(filtered.length); }

    ['q','sector','etapa'].forEach(id=> $('#'+id).addEventListener('input', apply)); $('#clear').addEventListener('click', ()=>{ ['q','sector','etapa'].forEach(id=> $('#'+id).value=''); apply(); }); apply();
  }

  document.addEventListener('DOMContentLoaded', ()=>{ initIndex(); initProjects();
    const exportBtn = document.getElementById('export-pdf');
    if(exportBtn){
      exportBtn.addEventListener('click', ()=>{
        const grid = document.getElementById('grid');
        if(!grid) return alert('Nenhum card disponível para exportar.');
        const opt = {
          margin:       [10, 10, 10, 10],
          filename:     'projetos.pdf',
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 2, useCORS: true },
          jsPDF:        { unit: 'pt', format: 'a4', orientation: 'portrait' },
          pagebreak:    { mode: ['css', 'legacy'] }
        };
        // ensure each card doesn't get split in PDF
        document.querySelectorAll('.card').forEach(c=> c.style.breakInside='avoid');
        // run export
        try{ html2pdf().set(opt).from(grid).save(); }catch(e){ console.error(e); alert('Erro ao gerar PDF — veja console.'); }
      });
    }
  });
})();
