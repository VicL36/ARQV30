// Neomorphic Dashboard with Neon Blue & Orange Theme
// Advanced Avatar Archaeology with IA

// Global variables
let currentAnalysis = null;
let loadingInterval = null;
let progressInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 Initializing Neomorphic Avatar Archaeology Dashboard...');
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize scroll effects
    initializeScrollEffects();
    
    // Initialize floating animations
    initializeFloatingAnimations();
    
    console.log('✅ Dashboard initialized successfully');
}

function initializeNavigation() {
    const navLinks = document.querySelectorAll('.neo-nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Get target section
            const target = this.getAttribute('href').substring(1);
            showSection(target);
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('main > section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
        
        // Add entrance animation
        targetSection.style.opacity = '0';
        targetSection.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            targetSection.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            targetSection.style.opacity = '1';
            targetSection.style.transform = 'translateY(0)';
        }, 50);
    }
}

function showAnalyzer() {
    showSection('analyzer');
    
    // Update navigation
    const navLinks = document.querySelectorAll('.neo-nav-link');
    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelector('a[href="#analyzer"]').classList.add('active');
}

function initializeFormHandlers() {
    const form = document.getElementById('analyzerForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Validate required fields
    if (!data.segmento) {
        showNotification('Por favor, informe o segmento de atuação', 'error');
        return;
    }
    
    // Show loading and switch to dashboard
    showSection('dashboard');
    updateNavigation('dashboard');
    startAnalysis(data);
}

function updateNavigation(activeSection) {
    const navLinks = document.querySelectorAll('.neo-nav-link');
    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelector(`a[href="#${activeSection}"]`).classList.add('active');
}

async function startAnalysis(data) {
    try {
        showLoadingState();
        
        console.log('🔍 Starting ultra-detailed analysis with IA...');
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro na análise');
        }
        
        const result = await response.json();
        currentAnalysis = result;
        
        hideLoadingState();
        displayResults(result);
        
        showNotification('Análise ultra-detalhada concluída com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro na análise:', error);
        hideLoadingState();
        showNotification(`Erro na análise: ${error.message}`, 'error');
    }
}

function showLoadingState() {
    const loadingContainer = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    
    loadingContainer.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Start loading animation
    startLoadingAnimation();
}

function hideLoadingState() {
    const loadingContainer = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    
    loadingContainer.style.display = 'none';
    resultsContainer.style.display = 'block';
    
    // Stop loading animation
    stopLoadingAnimation();
}

function startLoadingAnimation() {
    const loadingTexts = [
        'Iniciando análise ultra-detalhada...',
        'Pesquisando dados atualizados na internet...',
        'Analisando segmento com IA...',
        'Mapeando avatar ultra-detalhado...',
        'Identificando dores profundas...',
        'Analisando concorrência em tempo real...',
        'Coletando inteligência de mercado...',
        'Calculando métricas de performance...',
        'Gerando projeções de cenários...',
        'Criando plano de ação detalhado...',
        'Finalizando insights exclusivos...'
    ];
    
    let currentStep = 0;
    let progress = 0;
    
    const loadingText = document.getElementById('loadingText');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    loadingInterval = setInterval(() => {
        if (currentStep < loadingTexts.length) {
            loadingText.textContent = loadingTexts[currentStep];
            currentStep++;
        }
    }, 3000);
    
    progressInterval = setInterval(() => {
        if (progress < 95) {
            progress += Math.random() * 3;
            progressBar.style.width = `${Math.min(progress, 95)}%`;
            progressText.textContent = `${Math.round(Math.min(progress, 95))}%`;
        }
    }, 200);
}

function stopLoadingAnimation() {
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }
    
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Complete progress
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    if (progressBar && progressText) {
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
    }
}

function displayResults(analysis) {
    const container = document.getElementById('resultsContainer');
    
    // Create results HTML
    const resultsHTML = createResultsHTML(analysis);
    container.innerHTML = resultsHTML;
    
    // Initialize charts and interactions
    setTimeout(() => {
        initializeCharts(analysis);
        initializeResultsInteractions();
    }, 100);
}

function createResultsHTML(analysis) {
    return `
        <div class="results-header">
            <h2 class="neo-section-title">Análise Ultra-Detalhada Concluída</h2>
            <div class="results-actions">
                <button class="neo-cta-button" onclick="downloadPDFReport()">
                    <i class="fas fa-file-pdf"></i>
                    <span>Baixar Relatório PDF</span>
                </button>
                <button class="neo-cta-button pdf-export-button" onclick="shareResults()">
                    <i class="fas fa-share-alt"></i>
                    <span>Compartilhar</span>
                </button>
            </div>
        </div>
        
        ${createOverviewSection(analysis)}
        ${createScopeSection(analysis)}
        ${createAvatarSection(analysis)}
        ${createPainMappingSection(analysis)}
        ${createCompetitionSection(analysis)}
        ${createMarketIntelligenceSection(analysis)}
        ${createKeywordsSection(analysis)}
        ${createMetricsSection(analysis)}
        ${createVoiceSection(analysis)}
        ${createProjectionsSection(analysis)}
        ${createActionPlanSection(analysis)}
        ${createInsightsSection(analysis)}
    `;
}

function createOverviewSection(analysis) {
    const escopo = analysis.escopo || {};
    const projecoes = analysis.projecoes_cenarios || {};
    const realista = projecoes.cenario_realista || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    <h3 class="neo-card-title">Overview Executivo</h3>
                </div>
                <div class="neo-card-content">
                    <div class="infographic-container">
                        <div class="infographic-item">
                            <div class="infographic-icon">
                                <i class="fas fa-bullseye"></i>
                            </div>
                            <div class="infographic-value">${escopo.segmento_principal || 'N/A'}</div>
                            <div class="infographic-label">Segmento Principal</div>
                        </div>
                        <div class="infographic-item">
                            <div class="infographic-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="infographic-value">${realista.roi || 'N/A'}</div>
                            <div class="infographic-label">ROI Projetado</div>
                        </div>
                        <div class="infographic-item">
                            <div class="infographic-icon">
                                <i class="fas fa-percentage"></i>
                            </div>
                            <div class="infographic-value">${realista.taxa_conversao || 'N/A'}</div>
                            <div class="infographic-label">Taxa Conversão</div>
                        </div>
                        <div class="infographic-item">
                            <div class="infographic-icon">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                            <div class="infographic-value">${realista.faturamento_mensal || 'N/A'}</div>
                            <div class="infographic-label">Faturamento Mensal</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <h4 class="chart-title">Tamanho do Mercado</h4>
                        <canvas id="marketSizeChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createScopeSection(analysis) {
    const escopo = analysis.escopo || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-crosshairs"></i>
                    </div>
                    <h3 class="neo-card-title">Definição do Escopo</h3>
                </div>
                <div class="neo-card-content">
                    <div class="detail-item">
                        <strong>Segmento Principal:</strong>
                        <p>${escopo.segmento_principal || 'N/A'}</p>
                    </div>
                    
                    ${escopo.subsegmentos ? `
                    <div class="detail-item">
                        <strong>Subsegmentos Identificados:</strong>
                        <ul>
                            ${escopo.subsegmentos.map(sub => `<li>${sub}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    <div class="detail-item">
                        <strong>Produto Ideal:</strong>
                        <p>${escopo.produto_ideal || 'N/A'}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Proposta de Valor:</strong>
                        <blockquote>${escopo.proposta_valor || 'N/A'}</blockquote>
                    </div>
                    
                    ${escopo.tamanho_mercado ? `
                    <div class="market-size-grid">
                        <div class="market-metric">
                            <span class="metric-label">TAM</span>
                            <span class="metric-value">${escopo.tamanho_mercado.tam || 'N/A'}</span>
                        </div>
                        <div class="market-metric">
                            <span class="metric-label">SAM</span>
                            <span class="metric-value">${escopo.tamanho_mercado.sam || 'N/A'}</span>
                        </div>
                        <div class="market-metric">
                            <span class="metric-label">SOM</span>
                            <span class="metric-value">${escopo.tamanho_mercado.som || 'N/A'}</span>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createAvatarSection(analysis) {
    const avatar = analysis.avatar_ultra_detalhado || {};
    const persona = avatar.persona_principal || {};
    const demografia = avatar.demografia_detalhada || {};
    const psicografia = avatar.psicografia_profunda || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-user-circle"></i>
                    </div>
                    <h3 class="neo-card-title">Avatar Ultra-Detalhado</h3>
                </div>
                <div class="neo-card-content">
                    <div class="avatar-profile">
                        <div class="avatar-section">
                            <h4>Persona Principal</h4>
                            <div class="persona-card">
                                <div class="persona-info">
                                    <h5>${persona.nome || 'Avatar Principal'}</h5>
                                    <p><strong>Idade:</strong> ${persona.idade || 'N/A'}</p>
                                    <p><strong>Profissão:</strong> ${persona.profissao || 'N/A'}</p>
                                    <p><strong>Renda:</strong> ${persona.renda_mensal || 'N/A'}</p>
                                    <p><strong>Localização:</strong> ${persona.localizacao || 'N/A'}</p>
                                    <p><strong>Estado Civil:</strong> ${persona.estado_civil || 'N/A'}</p>
                                    <p><strong>Escolaridade:</strong> ${persona.escolaridade || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        
                        ${Object.keys(demografia).length > 0 ? `
                        <div class="avatar-section">
                            <h4>Demografia Detalhada</h4>
                            <div class="detail-grid">
                                ${Object.entries(demografia).map(([key, value]) => `
                                    <div class="detail-item">
                                        <strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                                        <p>${value}</p>
                                    </div>
                                `).join('')}
                            </div>
                            
                            <div class="chart-container">
                                <h4 class="chart-title">Distribuição Demográfica</h4>
                                <canvas id="demographicsChart" width="400" height="200"></canvas>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${Object.keys(psicografia).length > 0 ? `
                        <div class="avatar-section">
                            <h4>Psicografia Profunda</h4>
                            ${psicografia.valores_fundamentais ? `
                            <div class="detail-item">
                                <strong>Valores Fundamentais:</strong>
                                <ul>
                                    ${psicografia.valores_fundamentais.map(valor => `<li>${valor}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            
                            ${psicografia.estilo_vida_detalhado ? `
                            <div class="detail-item">
                                <strong>Estilo de Vida:</strong>
                                <p>${psicografia.estilo_vida_detalhado}</p>
                            </div>
                            ` : ''}
                            
                            ${psicografia.aspiracoes_profissionais ? `
                            <div class="detail-item">
                                <strong>Aspirações Profissionais:</strong>
                                <ul>
                                    ${psicografia.aspiracoes_profissionais.map(asp => `<li>${asp}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            
                            ${psicografia.medos_profundos ? `
                            <div class="detail-item">
                                <strong>Medos Profundos:</strong>
                                <ul>
                                    ${psicografia.medos_profundos.map(medo => `<li>${medo}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createPainMappingSection(analysis) {
    const dores = analysis.mapeamento_dores_ultra_detalhado || {};
    const nivel1 = dores.dores_nivel_1_criticas || [];
    const nivel2 = dores.dores_nivel_2_importantes || [];
    const nivel3 = dores.dores_nivel_3_latentes || [];
    const jornada = dores.jornada_dor || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-heart-broken"></i>
                    </div>
                    <h3 class="neo-card-title">Mapeamento de Dores Ultra-Detalhado</h3>
                </div>
                <div class="neo-card-content">
                    <div class="chart-container">
                        <h4 class="chart-title">Intensidade das Dores por Nível</h4>
                        <canvas id="painLevelsChart" width="400" height="200"></canvas>
                    </div>
                    
                    ${nivel1.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Dores Críticas (Nível 1)</h4>
                        <div class="dores-list">
                            ${nivel1.map((dor, index) => `
                                <div class="dor-item nivel-1">
                                    <h5>Dor Crítica ${index + 1}</h5>
                                    <p><strong>Dor:</strong> ${typeof dor === 'object' ? dor.dor : dor}</p>
                                    ${typeof dor === 'object' ? `
                                        <p><strong>Intensidade:</strong> ${dor.intensidade || 'N/A'} | <strong>Frequência:</strong> ${dor.frequencia || 'N/A'}</p>
                                        <p><strong>Impacto:</strong> ${dor.impacto_vida || 'N/A'}</p>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${nivel2.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Dores Importantes (Nível 2)</h4>
                        <div class="dores-list">
                            ${nivel2.map((dor, index) => `
                                <div class="dor-item nivel-2">
                                    <h5>Dor Importante ${index + 1}</h5>
                                    <p><strong>Dor:</strong> ${typeof dor === 'object' ? dor.dor : dor}</p>
                                    ${typeof dor === 'object' ? `
                                        <p><strong>Intensidade:</strong> ${dor.intensidade || 'N/A'} | <strong>Frequência:</strong> ${dor.frequencia || 'N/A'}</p>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${Object.keys(jornada).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Jornada da Dor</h4>
                        <div class="jornada-dor">
                            ${Object.entries(jornada).map(([key, value]) => `
                                <p><strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value}</p>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createCompetitionSection(analysis) {
    const concorrencia = analysis.analise_concorrencia_detalhada || {};
    const diretos = concorrencia.concorrentes_diretos || [];
    const indiretos = concorrencia.concorrentes_indiretos || [];
    const gaps = concorrencia.gaps_oportunidades || [];
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chess"></i>
                    </div>
                    <h3 class="neo-card-title">Análise da Concorrência</h3>
                </div>
                <div class="neo-card-content">
                    ${diretos.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Concorrentes Diretos</h4>
                        ${diretos.map(concorrente => `
                            <div class="competitor-item">
                                <h5>${concorrente.nome || 'Concorrente'}</h5>
                                <p><strong>Preço:</strong> ${concorrente.preco_range || 'N/A'}</p>
                                <p><strong>Proposta:</strong> ${concorrente.proposta_valor || 'N/A'}</p>
                                <p><strong>Share de Mercado:</strong> ${concorrente.share_mercado_estimado || 'N/A'}</p>
                                
                                ${concorrente.pontos_fortes ? `
                                <div class="detail-item">
                                    <strong>Pontos Fortes:</strong>
                                    <ul>
                                        ${concorrente.pontos_fortes.map(ponto => `<li>${ponto}</li>`).join('')}
                                    </ul>
                                </div>
                                ` : ''}
                                
                                ${concorrente.pontos_fracos ? `
                                <div class="detail-item">
                                    <strong>Pontos Fracos:</strong>
                                    <ul>
                                        ${concorrente.pontos_fracos.map(ponto => `<li>${ponto}</li>`).join('')}
                                    </ul>
                                </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${gaps.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Gaps e Oportunidades</h4>
                        <ul>
                            ${gaps.map(gap => `<li>${gap}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    <div class="chart-container">
                        <h4 class="chart-title">Market Share dos Concorrentes</h4>
                        <canvas id="competitionChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createMarketIntelligenceSection(analysis) {
    const mercado = analysis.inteligencia_mercado || {};
    const tendencias = mercado.tendencias_crescimento || [];
    const sazonalidade = mercado.sazonalidade_detalhada || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    <h3 class="neo-card-title">Inteligência de Mercado</h3>
                </div>
                <div class="neo-card-content">
                    ${tendencias.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Tendências em Crescimento</h4>
                        ${tendencias.map(tendencia => `
                            <div class="tendencia-item crescimento">
                                <h5>${tendencia.tendencia || 'Tendência'}</h5>
                                <p><strong>Impacto:</strong> ${tendencia.impacto || 'N/A'}</p>
                                <p><strong>Timeline:</strong> ${tendencia.timeline || 'N/A'}</p>
                                <p><strong>Oportunidade:</strong> ${tendencia.oportunidade || 'N/A'}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${Object.keys(sazonalidade).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Sazonalidade</h4>
                        <div class="sazonalidade-grid">
                            ${sazonalidade.picos_demanda ? `
                            <div class="sazonalidade-item">
                                <h6>Picos de Demanda</h6>
                                <p>${sazonalidade.picos_demanda.join(', ')}</p>
                            </div>
                            ` : ''}
                            
                            ${sazonalidade.baixas_demanda ? `
                            <div class="sazonalidade-item">
                                <h6>Baixas de Demanda</h6>
                                <p>${sazonalidade.baixas_demanda.join(', ')}</p>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="chart-container">
                            <h4 class="chart-title">Sazonalidade do Mercado</h4>
                            <canvas id="seasonalityChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createKeywordsSection(analysis) {
    const palavras = analysis.estrategia_palavras_chave || {};
    const primarias = palavras.palavras_primarias || [];
    const custos = palavras.custos_aquisicao_canal || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h3 class="neo-card-title">Estratégia de Palavras-Chave</h3>
                </div>
                <div class="neo-card-content">
                    ${primarias.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Palavras-Chave Primárias</h4>
                        <div class="keywords-table">
                            <div class="keyword-row" style="background: var(--brand-gradient-neon); color: white; font-weight: bold;">
                                <div class="keyword">Termo</div>
                                <div>Volume/Mês</div>
                                <div>CPC</div>
                                <div>Dificuldade</div>
                                <div>Intenção</div>
                                <div>Oportunidade</div>
                            </div>
                            ${primarias.slice(0, 5).map(kw => `
                                <div class="keyword-row">
                                    <div class="keyword">${kw.termo || 'N/A'}</div>
                                    <div>${kw.volume_mensal || 'N/A'}</div>
                                    <div>${kw.cpc_estimado || 'N/A'}</div>
                                    <div class="difficulty ${(kw.dificuldade || '').toLowerCase()}">${kw.dificuldade || 'N/A'}</div>
                                    <div>${kw.intencao_busca || 'N/A'}</div>
                                    <div class="opportunity ${(kw.oportunidade || '').toLowerCase()}">${kw.oportunidade || 'N/A'}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${Object.keys(custos).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Custos por Plataforma</h4>
                        <div class="platform-costs">
                            ${Object.entries(custos).map(([platform, costs]) => `
                                <div class="platform-item">
                                    <h5>${platform.replace(/_/g, ' ')}</h5>
                                    <div class="platform-metrics">
                                        <span>CPC: ${costs.cpc_medio || 'N/A'}</span>
                                        <span>CPM: ${costs.cpm_medio || 'N/A'}</span>
                                        <span>CTR: ${costs.ctr_esperado || 'N/A'}</span>
                                        <span>CPA: ${costs.cpa_estimado || 'N/A'}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="chart-container">
                            <h4 class="chart-title">CPA por Plataforma</h4>
                            <canvas id="cpaChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createMetricsSection(analysis) {
    const metricas = analysis.metricas_performance_detalhadas || {};
    const benchmarks = metricas.benchmarks_segmento || {};
    const funil = metricas.funil_conversao_otimizado || {};
    const kpis = metricas.kpis_criticos || [];
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="neo-card-title">Métricas de Performance</h3>
                </div>
                <div class="neo-card-content">
                    ${Object.keys(benchmarks).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Benchmarks do Segmento</h4>
                        <div class="metrics-grid">
                            ${Object.entries(benchmarks).map(([key, value]) => `
                                <div class="metric-item">
                                    <div class="metric-value">${value}</div>
                                    <div class="metric-label">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${Object.keys(funil).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Funil de Conversão Otimizado</h4>
                        <div class="funnel-steps">
                            ${Object.entries(funil).map(([step, rate]) => `
                                <div class="funnel-step">
                                    ${step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${rate}
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="chart-container">
                            <h4 class="chart-title">Funil de Conversão</h4>
                            <canvas id="funnelChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${kpis.length > 0 ? `
                    <div class="avatar-section">
                        <h4>KPIs Críticos</h4>
                        ${kpis.map(kpi => `
                            <div class="kpi-item">
                                <h5>${kpi.metrica || 'KPI'}</h5>
                                <p><strong>Valor Ideal:</strong> ${kpi.valor_ideal || 'N/A'}</p>
                                <p><strong>Como Medir:</strong> ${kpi.como_medir || 'N/A'}</p>
                                <p><strong>Frequência:</strong> ${kpi.frequencia || 'N/A'}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createVoiceSection(analysis) {
    const voz = analysis.voz_mercado_linguagem || {};
    const linguagem = voz.linguagem_avatar || {};
    const objecoes = voz.objecoes_principais || [];
    const gatilhos = voz.gatilhos_mentais_efetivos || [];
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <h3 class="neo-card-title">Voz do Mercado</h3>
                </div>
                <div class="neo-card-content">
                    ${Object.keys(linguagem).length > 0 ? `
                    <div class="avatar-section">
                        <h4>Linguagem do Avatar</h4>
                        ${linguagem.termos_tecnicos ? `
                        <div class="detail-item">
                            <strong>Termos Técnicos:</strong>
                            <p>${linguagem.termos_tecnicos.join(', ')}</p>
                        </div>
                        ` : ''}
                        
                        ${linguagem.palavras_poder ? `
                        <div class="detail-item">
                            <strong>Palavras de Poder:</strong>
                            <p>${linguagem.palavras_poder.join(', ')}</p>
                        </div>
                        ` : ''}
                        
                        ${linguagem.palavras_evitar ? `
                        <div class="detail-item">
                            <strong>Palavras a Evitar:</strong>
                            <p>${linguagem.palavras_evitar.join(', ')}</p>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    ${objecoes.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Principais Objeções</h4>
                        ${objecoes.map((obj, index) => `
                            <div class="objecao-item">
                                <h5>Objeção ${index + 1}</h5>
                                <p><strong>Objeção:</strong> ${obj.objecao || 'N/A'}</p>
                                <p><strong>Estratégia:</strong> ${obj.estrategia_contorno || 'N/A'}</p>
                                <p><strong>Frequência:</strong> ${obj.frequencia || 'N/A'}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${gatilhos.length > 0 ? `
                    <div class="avatar-section">
                        <h4>Gatilhos Mentais Efetivos</h4>
                        ${gatilhos.map(gatilho => `
                            <div class="gatilho-item">
                                <h5>${gatilho.gatilho || 'Gatilho'}</h5>
                                <p><strong>Aplicação:</strong> ${gatilho.aplicacao || 'N/A'}</p>
                                <p><strong>Efetividade:</strong> ${gatilho.efetividade || 'N/A'}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createProjectionsSection(analysis) {
    const projecoes = analysis.projecoes_cenarios || {};
    const conservador = projecoes.cenario_conservador || {};
    const realista = projecoes.cenario_realista || {};
    const otimista = projecoes.cenario_otimista || {};
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <h3 class="neo-card-title">Projeções de Cenários</h3>
                </div>
                <div class="neo-card-content">
                    <div class="scenarios-grid">
                        ${Object.keys(conservador).length > 0 ? `
                        <div class="scenario-item conservador">
                            <h4>Cenário Conservador</h4>
                            <div class="scenario-metrics">
                                <p><strong>Taxa de Conversão:</strong> ${conservador.taxa_conversao || 'N/A'}</p>
                                <p><strong>Faturamento Mensal:</strong> ${conservador.faturamento_mensal || 'N/A'}</p>
                                <p><strong>ROI:</strong> ${conservador.roi || 'N/A'}</p>
                                <p><strong>Break Even:</strong> ${conservador.break_even || 'N/A'}</p>
                            </div>
                            ${conservador.premissas ? `
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${conservador.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                        
                        ${Object.keys(realista).length > 0 ? `
                        <div class="scenario-item realista">
                            <h4>Cenário Realista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Taxa de Conversão:</strong> ${realista.taxa_conversao || 'N/A'}</p>
                                <p><strong>Faturamento Mensal:</strong> ${realista.faturamento_mensal || 'N/A'}</p>
                                <p><strong>ROI:</strong> ${realista.roi || 'N/A'}</p>
                                <p><strong>Break Even:</strong> ${realista.break_even || 'N/A'}</p>
                            </div>
                            ${realista.premissas ? `
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${realista.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                        
                        ${Object.keys(otimista).length > 0 ? `
                        <div class="scenario-item otimista">
                            <h4>Cenário Otimista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Taxa de Conversão:</strong> ${otimista.taxa_conversao || 'N/A'}</p>
                                <p><strong>Faturamento Mensal:</strong> ${otimista.faturamento_mensal || 'N/A'}</p>
                                <p><strong>ROI:</strong> ${otimista.roi || 'N/A'}</p>
                                <p><strong>Break Even:</strong> ${otimista.break_even || 'N/A'}</p>
                            </div>
                            ${otimista.premissas ? `
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${otimista.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="chart-container">
                        <h4 class="chart-title">Comparação de ROI por Cenário</h4>
                        <canvas id="roiChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createActionPlanSection(analysis) {
    const plano = analysis.plano_acao_detalhado || [];
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-tasks"></i>
                    </div>
                    <h3 class="neo-card-title">Plano de Ação Detalhado</h3>
                </div>
                <div class="neo-card-content">
                    ${plano.length > 0 ? `
                    <div class="action-timeline">
                        ${plano.map((fase, index) => `
                            <div class="action-phase">
                                <div class="phase-header">
                                    <div class="phase-number">${index + 1}</div>
                                    <div class="phase-info">
                                        <h4>${fase.fase || `Fase ${index + 1}`}</h4>
                                        <p>Duração: ${fase.duracao || 'N/A'}</p>
                                    </div>
                                </div>
                                
                                ${fase.acoes ? `
                                <div class="phase-actions">
                                    ${fase.acoes.map((acao, aIndex) => `
                                        <div class="action-item-detailed">
                                            <h5>Ação ${aIndex + 1}: ${acao.acao || 'N/A'}</h5>
                                            <div class="action-details">
                                                <p><strong>Responsável:</strong> ${acao.responsavel || 'N/A'}</p>
                                                <p><strong>Prazo:</strong> ${acao.prazo || 'N/A'}</p>
                                                ${acao.recursos_necessarios ? `<p><strong>Recursos:</strong> ${acao.recursos_necessarios.join(', ')}</p>` : ''}
                                                ${acao.metricas_sucesso ? `<p><strong>Métricas:</strong> ${acao.metricas_sucesso.join(', ')}</p>` : ''}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                    ` : '<p>Nenhum plano de ação disponível.</p>'}
                </div>
            </div>
        </div>
    `;
}

function createInsightsSection(analysis) {
    const insights = analysis.insights_exclusivos || [];
    
    return `
        <div class="results-grid">
            <div class="neo-enhanced-card result-card full-width">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <h3 class="neo-card-title">Insights Exclusivos</h3>
                </div>
                <div class="neo-card-content">
                    ${insights.length > 0 ? `
                    <div class="insights-content">
                        <div class="insights-list">
                            ${insights.map((insight, index) => `
                                <div class="insight-item">
                                    <div class="insight-number">${index + 1}</div>
                                    <div class="insight-text">
                                        <p>${insight}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : '<p>Nenhum insight exclusivo disponível.</p>'}
                </div>
            </div>
        </div>
    `;
}

function initializeCharts(analysis) {
    console.log('🎨 Initializing interactive charts...');
    
    // Market Size Chart
    createMarketSizeChart(analysis);
    
    // Demographics Chart
    createDemographicsChart(analysis);
    
    // Pain Levels Chart
    createPainLevelsChart(analysis);
    
    // Competition Chart
    createCompetitionChart(analysis);
    
    // Seasonality Chart
    createSeasonalityChart(analysis);
    
    // CPA Chart
    createCPAChart(analysis);
    
    // Funnel Chart
    createFunnelChart(analysis);
    
    // ROI Chart
    createROIChart(analysis);
    
    console.log('✅ Charts initialized successfully');
}

function createMarketSizeChart(analysis) {
    const canvas = document.getElementById('marketSizeChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const escopo = analysis.escopo || {};
    const tamanho = escopo.tamanho_mercado || {};
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Chart data
    const data = [
        { label: 'TAM', value: parseFloat((tamanho.tam || '0').replace(/[^\d.]/g, '')) || 100 },
        { label: 'SAM', value: parseFloat((tamanho.sam || '0').replace(/[^\d.]/g, '')) || 50 },
        { label: 'SOM', value: parseFloat((tamanho.som || '0').replace(/[^\d.]/g, '')) || 10 }
    ];
    
    // Colors
    const colors = ['#00d4ff', '#ff6b00', '#ff3d71'];
    
    // Draw bars
    const barWidth = 80;
    const barSpacing = 40;
    const startX = 50;
    const maxValue = Math.max(...data.map(d => d.value));
    
    data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * 120;
        const x = startX + index * (barWidth + barSpacing);
        const y = 150 - barHeight;
        
        // Draw bar with gradient
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, colors[index]);
        gradient.addColorStop(1, colors[index] + '80');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Draw label
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, x + barWidth/2, 170);
        
        // Draw value
        ctx.fillStyle = colors[index];
        ctx.font = 'bold 10px Inter';
        ctx.fillText(item.value.toFixed(0), x + barWidth/2, y - 5);
    });
}

function createDemographicsChart(analysis) {
    const canvas = document.getElementById('demographicsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample demographics data
    const data = [
        { label: '25-35 anos', value: 35, color: '#00d4ff' },
        { label: '35-45 anos', value: 45, color: '#ff6b00' },
        { label: '45+ anos', value: 20, color: '#ff3d71' }
    ];
    
    drawPieChart(ctx, data, canvas.width/2, canvas.height/2, 80);
}

function createPainLevelsChart(analysis) {
    const canvas = document.getElementById('painLevelsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const dores = analysis.mapeamento_dores_ultra_detalhado || {};
    
    const data = [
        { label: 'Críticas', value: (dores.dores_nivel_1_criticas || []).length, color: '#ff3d71' },
        { label: 'Importantes', value: (dores.dores_nivel_2_importantes || []).length, color: '#ff6b00' },
        { label: 'Latentes', value: (dores.dores_nivel_3_latentes || []).length, color: '#00d4ff' }
    ];
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

function createCompetitionChart(analysis) {
    const canvas = document.getElementById('competitionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const concorrencia = analysis.analise_concorrencia_detalhada || {};
    const diretos = concorrencia.concorrentes_diretos || [];
    
    const data = diretos.slice(0, 4).map((comp, index) => ({
        label: comp.nome || `Concorrente ${index + 1}`,
        value: parseFloat((comp.share_mercado_estimado || '10').replace(/[^\d.]/g, '')) || 10,
        color: ['#00d4ff', '#ff6b00', '#ff3d71', '#10b981'][index]
    }));
    
    if (data.length > 0) {
        drawPieChart(ctx, data, canvas.width/2, canvas.height/2, 80);
    }
}

function createSeasonalityChart(analysis) {
    const canvas = document.getElementById('seasonalityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample seasonality data
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const values = [80, 85, 90, 95, 100, 85, 70, 75, 90, 95, 100, 85];
    
    drawLineChart(ctx, months, values, canvas.width, canvas.height);
}

function createCPAChart(analysis) {
    const canvas = document.getElementById('cpaChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const palavras = analysis.estrategia_palavras_chave || {};
    const custos = palavras.custos_aquisicao_canal || {};
    
    const data = Object.entries(custos).map(([platform, costs], index) => ({
        label: platform.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: parseFloat((costs.cpa_estimado || '0').replace(/[^\d.]/g, '')) || 100,
        color: ['#00d4ff', '#ff6b00', '#ff3d71', '#10b981', '#8b5cf6'][index]
    }));
    
    if (data.length > 0) {
        drawBarChart(ctx, data, canvas.width, canvas.height);
    }
}

function createFunnelChart(analysis) {
    const canvas = document.getElementById('funnelChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const metricas = analysis.metricas_performance_detalhadas || {};
    const funil = metricas.funil_conversao_otimizado || {};
    
    const steps = [
        { label: 'Visitantes', value: 100 },
        { label: 'Leads', value: parseFloat((funil.visitantes_leads || '18').replace(/[^\d.]/g, '')) || 18 },
        { label: 'Oportunidades', value: parseFloat((funil.leads_oportunidades || '25').replace(/[^\d.]/g, '')) || 25 },
        { label: 'Vendas', value: parseFloat((funil.oportunidades_vendas || '12').replace(/[^\d.]/g, '')) || 12 }
    ];
    
    drawFunnelChart(ctx, steps, canvas.width, canvas.height);
}

function createROIChart(analysis) {
    const canvas = document.getElementById('roiChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const projecoes = analysis.projecoes_cenarios || {};
    
    const data = [
        { 
            label: 'Conservador', 
            value: parseFloat((projecoes.cenario_conservador?.roi || '240').replace(/[^\d.]/g, '')) || 240,
            color: '#ff3d71'
        },
        { 
            label: 'Realista', 
            value: parseFloat((projecoes.cenario_realista?.roi || '380').replace(/[^\d.]/g, '')) || 380,
            color: '#00d4ff'
        },
        { 
            label: 'Otimista', 
            value: parseFloat((projecoes.cenario_otimista?.roi || '580').replace(/[^\d.]/g, '')) || 580,
            color: '#10b981'
        }
    ];
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

// Chart drawing functions
function drawPieChart(ctx, data, centerX, centerY, radius) {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = -Math.PI / 2;
    
    data.forEach(item => {
        const sliceAngle = (item.value / total) * 2 * Math.PI;
        
        // Draw slice
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();
        
        // Draw label
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius + 20);
        const labelY = centerY + Math.sin(labelAngle) * (radius + 20);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, labelX, labelY);
        
        currentAngle += sliceAngle;
    });
}

function drawBarChart(ctx, data, width, height) {
    const barWidth = (width - 100) / data.length - 20;
    const maxValue = Math.max(...data.map(d => d.value));
    const chartHeight = height - 60;
    
    data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * chartHeight;
        const x = 50 + index * (barWidth + 20);
        const y = height - 40 - barHeight;
        
        // Draw bar
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, item.color);
        gradient.addColorStop(1, item.color + '80');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Draw label
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, x + barWidth/2, height - 20);
        
        // Draw value
        ctx.fillStyle = item.color;
        ctx.font = 'bold 10px Inter';
        ctx.fillText(item.value.toFixed(0), x + barWidth/2, y - 5);
    });
}

function drawLineChart(ctx, labels, values, width, height) {
    const chartWidth = width - 100;
    const chartHeight = height - 60;
    const stepX = chartWidth / (labels.length - 1);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const valueRange = maxValue - minValue;
    
    // Draw line
    ctx.beginPath();
    ctx.strokeStyle = '#00d4ff';
    ctx.lineWidth = 3;
    
    values.forEach((value, index) => {
        const x = 50 + index * stepX;
        const y = 30 + (1 - (value - minValue) / valueRange) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        // Draw point
        ctx.fillStyle = '#00d4ff';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        
        // Draw label
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(labels[index], x, height - 20);
    });
    
    ctx.stroke();
}

function drawFunnelChart(ctx, steps, width, height) {
    const stepHeight = (height - 60) / steps.length;
    const maxWidth = width - 100;
    
    steps.forEach((step, index) => {
        const stepWidth = (step.value / 100) * maxWidth;
        const x = (width - stepWidth) / 2;
        const y = 30 + index * stepHeight;
        
        // Draw step
        const gradient = ctx.createLinearGradient(0, y, 0, y + stepHeight - 10);
        gradient.addColorStop(0, '#00d4ff');
        gradient.addColorStop(1, '#ff6b00');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, stepWidth, stepHeight - 10);
        
        // Draw label
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(`${step.label}: ${step.value}%`, width/2, y + stepHeight/2);
    });
}

function initializeResultsInteractions() {
    console.log('🎯 Results interactions initialized');
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.neo-enhanced-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

async function downloadPDFReport() {
    if (!currentAnalysis) {
        showNotification('Nenhuma análise disponível para download', 'error');
        return;
    }
    
    try {
        showNotification('Gerando relatório PDF...', 'info');
        
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAnalysis)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao gerar PDF');
        }
        
        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `analise-avatar-gemini-${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Relatório PDF baixado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        showNotification(`Erro ao gerar PDF: ${error.message}`, 'error');
    }
}

function shareResults() {
    if (!currentAnalysis) {
        showNotification('Nenhuma análise disponível para compartilhar', 'error');
        return;
    }
    
    const shareData = {
        title: 'Arqueologia do Avatar - Análise Ultra-Detalhada',
        text: `Análise completa do segmento ${currentAnalysis.escopo?.segmento_principal || 'N/A'} com IA`,
        url: window.location.href
    };
    
    if (navigator.share) {
        navigator.share(shareData);
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareData.url).then(() => {
            showNotification('Link copiado para a área de transferência!', 'success');
        });
    }
}

function initializeSearch() {
    const searchInput = document.querySelector('.neo-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            // Implement search functionality here
            console.log('Searching for:', query);
        });
    }
}

function initializeScrollEffects() {
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

function initializeFloatingAnimations() {
    const floatingCards = document.querySelectorAll('.neo-floating-card');
    
    floatingCards.forEach((card, index) => {
        // Add random floating animation
        const delay = index * 0.2;
        const duration = 3 + Math.random() * 2;
        
        card.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
    });
}

// Add floating animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        background: var(--neo-bg);
        border: 1px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        border-radius: var(--neo-border-radius);
        padding: 1rem 1.5rem;
        box-shadow: var(--neo-shadow-2);
        color: var(--text-primary);
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Export functions for global access
window.showAnalyzer = showAnalyzer;
window.downloadPDFReport = downloadPDFReport;
window.shareResults = shareResults;
