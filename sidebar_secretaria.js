let projectSecretariaMap = {};

async function loadSecretariaMapping() {
    try {
        const response = await fetch('Filtro SIEC/project_secretaria.json');
        if (response.ok) {
            projectSecretariaMap = await response.json();
            console.log('Mapeamento carregado:', Object.keys(projectSecretariaMap).length, 'projetos');
        }
    } catch (error) {
        console.error('Erro ao carregar mapeamento:', error);
    }
}

function renderSidebarBySecretaria(projectData, activeSector, meetingMode) {
    const projectsBySecretaria = { 'SIPE': [], 'SIEC': [], 'SISU': [] };
    
    projectData.forEach(project => {
        const guid = project.rawData?.Guid || project.sourceId || project.guid || project.id;
        const secretaria = projectSecretariaMap[guid] || 'SIEC';
        if (projectsBySecretaria[secretaria]) {
            projectsBySecretaria[secretaria].push(project);
        }
    });
    
    let html = `
        <a href="#" data-sector="Todos" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors ${!meetingMode && activeSector === 'Todos' ? 'bg-blue-100 text-blue-700 font-bold' : ''}">
            <i class="fas fa-th mr-3"></i>
            <span>Todos os Projetos</span>
        </a>
        <div class="mt-4 pt-4 border-t border-gray-200">`;
    
    ['SIPE', 'SIEC', 'SISU'].forEach(sec => {
        const projs = projectsBySecretaria[sec];
        if (projs.length === 0) return;
        
        html += `
            <div class="mb-4">
                <div class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    ${sec} (${projs.length})
                </div>
                ${projs.map(p => `
                    <a href="#" data-project-id="${p.id}" class="block px-4 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100 transition-colors truncate" title="${p.name}">
                        <span class="ml-3">${p.name}</span>
                    </a>
                `).join('')}
            </div>`;
    });
    
    html += `</div>
        <div class="mt-4 pt-4 border-t border-gray-200">
            <a href="#" data-action="meeting" class="flex items-center px-4 py-3 rounded-lg transition-colors ${meetingMode ? 'bg-blue-100 text-blue-700 font-bold' : 'text-gray-700 hover:bg-gray-100'}">
                <i class="fas fa-people-arrows mr-2"></i>
                <span>Reunião</span>
            </a>
        </div>`;
    
    return html;
}

window.loadSecretariaMapping = loadSecretariaMapping;
window.renderSidebarBySecretaria = renderSidebarBySecretaria;
