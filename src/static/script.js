// Global variables
let currentAnalysis = null;
let analysisInProgress = false;

// DOM Elements
const sections = {
    home: document.getElementById('home'),
    analyzer: document.getElementById('analyzer'),
    dashboard: document.getElementById('dashboard')
};

const navLinks = document.querySelectorAll('.neo-nav-link');
const analyzerForm = document.getElementById('analyzerForm');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('resultsContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const loadingText = document.getElementById('loadingText');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeForm();
    initializeHeader();
    initializeSearch();
    addNeonGradientDefs();
});

// Add SVG gradient definitions for neon effects
function addNeonGradientDefs() {
    const svgDefs = document.createElement('div');
    svgDefs.className = 'neon-gradient-def';
    svgDefs.innerHTML = `
        <svg>
            <defs>
                <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:1" />
                    <stop offset="25%" style="stop-color:#0099cc;stop-opacity:1" />
                    <stop offset="75%" style="stop-color:#ff6b00;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#ff3d71;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
    `;
    document.body.appendChild(svgDefs);
}

// Navigation functionality
function initializeNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            showSection(targetId);
            updateActiveNav(this);
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    Object.values(sections).forEach(section => {
        if (section) section.style.display = 'none';
    });
    
    // Show target section
    if (sections[sectionId]) {
        sections[sectionId].style.display = 'block';
    }
}

function updateActiveNav(activeLink) {
    navLinks.forEach(link => link.classList.remove('active'));
    activeLink.classList.add('active');
}

function showAnalyzer() {
    showSection('analyzer');
    updateActiveNav(document.querySelector('a[href="#analyzer"]'));
}

// Header scroll effect
function initializeHeader() {
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Form functionality
function initializeForm() {
    if (analyzerForm) {
        analyzerForm.addEventListener('submit', handleFormSubmit);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (analysisInProgress) return;
    
    const formData = new FormData(analyzerForm);
    const data = Object.fromEntries(formData.entries());
    
    // Validate required fields
    if (!data.segmento.trim()) {
        showNotification('Por favor, informe o segmento de atuação.', 'error');
        return;
    }
    
    analysisInProgress = true;
    showDashboard();
    showLoading();
    
    try {
        await performAnalysis(data);
    } catch (error) {
        console.error('Erro na análise:', error);
        showNotification('Erro ao realizar análise. Tente novamente.', 'error');
        analysisInProgress = false;
        hideLoading();
    }
}

function showDashboard() {
    showSection('dashboard');
    updateActiveNav(document.querySelector('a[href="#dashboard"]'));
}

function showLoading() {
    loadingState.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Simulate progress with enhanced steps
    simulateProgress();
}

function simulateProgress() {
    const steps = [
        { progress: 5, text: 'Conectando com Gemini Pro 2.5...' },
        { progress: 15, text: 'Iniciando pesquisa na internet...' },
        { progress: 25, text: 'Coletando dados de mercado atualizados...' },
        { progress: 35, text: 'Analisando concorrência e tendências...' },
        { progress: 45, text: 'Mapeando avatar ultra-detalhado...' },
        { progress: 55, text: 'Processando psicografia e comportamento...' },
        { progress: 65, text: 'Calculando métricas e projeções...' },
        { progress: 75, text: 'Gerando estratégias de marketing...' },
        { progress: 85, text: 'Criando plano de ação detalhado...' },
        { progress: 95, text: 'Finalizando insights exclusivos...' },
        { progress: 100, text: 'Análise ultra-detalhada concluída!' }
    ];
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            updateProgress(step.progress, step.text);
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 2000); // 2 seconds per step = 22 seconds total
}

function updateProgress(percentage, text) {
    progressBar.style.width = percentage + '%';
    progressText.textContent = percentage + '%';
    loadingText.textContent = text;
}

async function performAnalysis(data) {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentAnalysis = result;
        
        // Wait for progress simulation to complete
        setTimeout(() => {
            hideLoading();
            displayResults(result);
            analysisInProgress = false;
        }, 22000); // 22 seconds total for progress simulation
        
    } catch (error) {
        console.error('Erro na análise:', error);
        hideLoading();
        showNotification('Erro ao realizar análise: ' + error.message, 'error');
        analysisInProgress = false;
    }
}

function hideLoading() {
    loadingState.style.display = 'none';
    resultsContainer.style.display = 'block';
}

function displayResults(analysis) {
    resultsContainer.innerHTML = generateResultsHTML(analysis);
    
    // Initialize interactive elements
    initializeResultsInteractions();
    initializeCharts(analysis);
}

function generateResultsHTML(analysis) {
    return `
        <div class="results-header">
            <div class="neo-enhanced-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <h3 class="neo-card-title">Análise Ultra-Detalhada Concluída com Gemini Pro 2.5</h3>
                </div>
                <div class="neo-card-content">
                    <p>Sua análise de avatar foi processada pelo Gemini Pro 2.5 com pesquisa em tempo real na internet. Explore os insights profundos e gráficos interativos abaixo.</p>
                    <div class="results-actions">
                        <button class="neo-cta-button pdf-export-button" onclick="downloadPDFReport()">
                            <i class="fas fa-file-pdf"></i>
                            <span>Baixar Relatório PDF</span>
                        </button>
                        <button class="neo-cta-button" onclick="shareResults()" style="background: var(--neo-bg); color: var(--text-primary); box-shadow: var(--neo-shadow-1);">
                            <i class="fas fa-share"></i>
                            <span>Compartilhar</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Infográficos de Overview -->
        <div class="infographic-container">
            ${generateOverviewInfographics(analysis)}
        </div>
        
        <div class="results-grid">
            ${generateEscopoSection(analysis.escopo)}
            ${generateAvatarSection(analysis.avatar_ultra_detalhado)}
            ${generateDoresSection(analysis.mapeamento_dores_ultra_detalhado)}
            ${generateConcorrenciaSection(analysis.analise_concorrencia_detalhada)}
            ${generateMercadoSection(analysis.inteligencia_mercado)}
            ${generatePalavrasChaveSection(analysis.estrategia_palavras_chave)}
            ${generateMetricasSection(analysis.metricas_performance_detalhadas)}
            ${generateVozMercadoSection(analysis.voz_mercado_linguagem)}
            ${generateProjecoesSection(analysis.projecoes_cenarios)}
            ${generatePlanoAcaoSection(analysis.plano_acao_detalhado)}
            ${generateInsightsSection(analysis.insights_exclusivos)}
        </div>
    `;
}

function generateOverviewInfographics(analysis) {
    const escopo = analysis.escopo || {};
    const mercado = escopo.tamanho_mercado || {};
    const projecoes = analysis.projecoes_cenarios || {};
    const realista = projecoes.cenario_realista || {};
    
    return `
        <div class="infographic-item">
            <div class="infographic-icon">
                <i class="fas fa-bullseye"></i>
            </div>
            <div class="infographic-value">${mercado.som || 'R$ 24M'}</div>
            <div class="infographic-label">Mercado Obtível</div>
        </div>
        
        <div class="infographic-item">
            <div class="infographic-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="infographic-value">${realista.roi || '380%'}</div>
            <div class="infographic-label">ROI Projetado</div>
        </div>
        
        <div class="infographic-item">
            <div class="infographic-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="infographic-value">${realista.taxa_conversao || '3.2%'}</div>
            <div class="infographic-label">Taxa Conversão</div>
        </div>
        
        <div class="infographic-item">
            <div class="infographic-icon">
                <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="infographic-value">${realista.break_even || '4 meses'}</div>
            <div class="infographic-label">Break Even</div>
        </div>
    `;
}

function generateEscopoSection(escopo) {
    if (!escopo) return '';
    
    const tamanhoMercado = escopo.tamanho_mercado || {};
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-bullseye"></i>
                </div>
                <h3 class="neo-card-title">Escopo Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="escopo-content">
                    <div class="detail-item">
                        <strong>Segmento Principal:</strong>
                        <p>${escopo.segmento_principal}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Subsegmentos Identificados:</strong>
                        <ul>
                            ${(escopo.subsegmentos || []).map(sub => `<li>${sub}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Produto Ideal:</strong>
                        <p>${escopo.produto_ideal}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Proposta de Valor:</strong>
                        <blockquote>${escopo.proposta_valor}</blockquote>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Tamanho do Mercado:</strong>
                        <div class="market-size-grid">
                            <div class="market-metric">
                                <span class="metric-label">TAM</span>
                                <span class="metric-value">${tamanhoMercado.tam || 'N/A'}</span>
                            </div>
                            <div class="market-metric">
                                <span class="metric-label">SAM</span>
                                <span class="metric-value">${tamanhoMercado.sam || 'N/A'}</span>
                            </div>
                            <div class="market-metric">
                                <span class="metric-label">SOM</span>
                                <span class="metric-value">${tamanhoMercado.som || 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateAvatarSection(avatar) {
    if (!avatar) return '';
    
    const persona = avatar.persona_principal || {};
    const demografia = avatar.demografia_detalhada || {};
    const psicografia = avatar.psicografia_profunda || {};
    const comportamento = avatar.comportamento_digital_avancado || {};
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-user-circle"></i>
                </div>
                <h3 class="neo-card-title">Avatar Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="avatar-profile">
                    <!-- Persona Principal -->
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
                    
                    <div class="avatar-section">
                        <h4>Demografia Detalhada</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <strong>Faixa Etária Primária:</strong>
                                <p>${demografia.faixa_etaria_primaria || 'N/A'}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Distribuição por Gênero:</strong>
                                <p>${demografia.distribuicao_genero || 'N/A'}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Distribuição Geográfica:</strong>
                                <p>${demografia.distribuicao_geografica || 'N/A'}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Classes Sociais:</strong>
                                <p>${demografia.classes_sociais || 'N/A'}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Nível Educacional:</strong>
                                <p>${demografia.nivel_educacional || 'N/A'}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Situação Profissional:</strong>
                                <p>${demografia.situacao_profissional || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="avatar-section">
                        <h4>Psicografia Profunda</h4>
                        <div class="detail-item">
                            <strong>Valores Fundamentais:</strong>
                            <ul>
                                ${(psicografia.valores_fundamentais || []).map(valor => `<li>${valor}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Estilo de Vida:</strong>
                            <p>${psicografia.estilo_vida_detalhado || 'N/A'}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Personalidade Dominante:</strong>
                            <p>${psicografia.personalidade_dominante || 'N/A'}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Aspirações Profissionais:</strong>
                            <ul>
                                ${(psicografia.aspiracoes_profissionais || []).map(asp => `<li>${asp}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Medos Profundos:</strong>
                            <ul>
                                ${(psicografia.medos_profundos || []).map(medo => `<li>${medo}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Motivadores Principais:</strong>
                            <ul>
                                ${(psicografia.motivadores_principais || []).map(mot => `<li>${mot}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    
                    <div class="avatar-section">
                        <h4>Comportamento Digital Avançado</h4>
                        <div class="detail-item">
                            <strong>Plataformas Primárias:</strong>
                            <ul>
                                ${(comportamento.plataformas_primarias || []).map(plat => `<li>${plat}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Horários de Pico:</strong>
                            <p><strong>Segunda a Sexta:</strong> ${comportamento.horarios_pico_detalhados?.segunda_sexta || 'N/A'}</p>
                            <p><strong>Fins de Semana:</strong> ${comportamento.horarios_pico_detalhados?.fins_semana || 'N/A'}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Conteúdo Consumido:</strong>
                            <p><strong>Formatos:</strong> ${comportamento.conteudo_consumido?.formatos_preferidos?.join(', ') || 'N/A'}</p>
                            <p><strong>Temas:</strong> ${comportamento.conteudo_consumido?.temas_interesse?.join(', ') || 'N/A'}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Comportamento de Compra:</strong>
                            <p><strong>Frequência:</strong> ${comportamento.comportamento_compra_online?.frequencia_compras || 'N/A'}</p>
                            <p><strong>Ticket Médio:</strong> ${comportamento.comportamento_compra_online?.ticket_medio || 'N/A'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Chart Container for Avatar Demographics -->
                <div class="chart-container">
                    <div class="chart-title">Distribuição Demográfica</div>
                    <canvas id="demographicsChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generateDoresSection(dores) {
    if (!dores) return '';
    
    const nivel1 = dores.dores_nivel_1_criticas || [];
    const nivel2 = dores.dores_nivel_2_importantes || [];
    const nivel3 = dores.dores_nivel_3_latentes || [];
    const jornada = dores.jornada_dor || {};
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-heart-broken"></i>
                </div>
                <h3 class="neo-card-title">Mapeamento Ultra-Detalhado de Dores</h3>
            </div>
            <div class="neo-card-content">
                <div class="dores-content">
                    <div class="detail-item">
                        <strong>Dores Críticas (Nível 1):</strong>
                        <div class="dores-list">
                            ${nivel1.map(dor => `
                                <div class="dor-item nivel-1">
                                    <h5>Intensidade: ${dor.intensidade} | Frequência: ${dor.frequencia}</h5>
                                    <p><strong>Dor:</strong> ${dor.dor}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida}</p>
                                    <p><strong>Consciência:</strong> ${dor.nivel_consciencia}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Dores Importantes (Nível 2):</strong>
                        <div class="dores-list">
                            ${nivel2.map(dor => `
                                <div class="dor-item nivel-2">
                                    <h5>Intensidade: ${dor.intensidade} | Frequência: ${dor.frequencia}</h5>
                                    <p><strong>Dor:</strong> ${dor.dor}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Dores Latentes (Nível 3):</strong>
                        <div class="dores-list">
                            ${nivel3.map(dor => `
                                <div class="dor-item nivel-3">
                                    <h5>Intensidade: ${dor.intensidade} | Frequência: ${dor.frequencia}</h5>
                                    <p><strong>Dor:</strong> ${dor.dor}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Jornada da Dor:</strong>
                        <div class="jornada-dor">
                            <p><strong>Gatilho Inicial:</strong> ${jornada.gatilho_inicial || 'N/A'}</p>
                            <p><strong>Evolução:</strong> ${jornada.evolucao_dor || 'N/A'}</p>
                            <p><strong>Ponto Insuportável:</strong> ${jornada.ponto_insuportavel || 'N/A'}</p>
                            <p><strong>Busca por Solução:</strong> ${jornada.busca_solucao || 'N/A'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Chart Container for Pain Levels -->
                <div class="chart-container">
                    <div class="chart-title">Distribuição de Dores por Nível</div>
                    <canvas id="painLevelsChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generateConcorrenciaSection(concorrencia) {
    if (!concorrencia) return '';
    
    const diretos = concorrencia.concorrentes_diretos || [];
    const indiretos = concorrencia.concorrentes_indiretos || [];
    const gaps = concorrencia.gaps_oportunidades || [];
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chess"></i>
                </div>
                <h3 class="neo-card-title">Análise Competitiva Detalhada</h3>
            </div>
            <div class="neo-card-content">
                <div class="concorrencia-content">
                    <div class="detail-item">
                        <strong>Concorrentes Diretos:</strong>
                        ${diretos.map(conc => `
                            <div class="competitor-item">
                                <h5>${conc.nome} - ${conc.preco_range}</h5>
                                <p><strong>Proposta:</strong> ${conc.proposta_valor}</p>
                                <p><strong>Posicionamento:</strong> ${conc.posicionamento}</p>
                                <p><strong>Share de Mercado:</strong> ${conc.share_mercado_estimado}</p>
                                <p><strong>Forças:</strong> ${conc.pontos_fortes?.join(', ')}</p>
                                <p><strong>Fraquezas:</strong> ${conc.pontos_fracos?.join(', ')}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-item">
                        <strong>Concorrentes Indiretos:</strong>
                        ${indiretos.map(ind => `
                            <div class="competitor-item">
                                <h5>${ind.categoria}</h5>
                                <p><strong>Exemplos:</strong> ${ind.exemplos?.join(', ')}</p>
                                <p><strong>Nível de Ameaça:</strong> ${ind.ameaca_nivel}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-item">
                        <strong>Gaps e Oportunidades:</strong>
                        <ul>
                            ${gaps.map(gap => `<li>${gap}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <!-- Chart Container for Market Share -->
                <div class="chart-container">
                    <div class="chart-title">Share de Mercado Estimado</div>
                    <canvas id="marketShareChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generateMercadoSection(mercado) {
    if (!mercado) return '';
    
    const tendenciasCrescimento = mercado.tendencias_crescimento || [];
    const sazonalidade = mercado.sazonalidade_detalhada || {};
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-pie"></i>
                </div>
                <h3 class="neo-card-title">Inteligência de Mercado</h3>
            </div>
            <div class="neo-card-content">
                <div class="mercado-content">
                    <div class="detail-item">
                        <strong>Tendências em Crescimento:</strong>
                        ${tendenciasCrescimento.map(tend => `
                            <div class="tendencia-item crescimento">
                                <h5>${tend.tendencia}</h5>
                                <p><strong>Impacto:</strong> ${tend.impacto}</p>
                                <p><strong>Timeline:</strong> ${tend.timeline}</p>
                                <p><strong>Oportunidade:</strong> ${tend.oportunidade}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-item">
                        <strong>Sazonalidade:</strong>
                        <div class="sazonalidade-grid">
                            <div class="sazonalidade-item">
                                <h6>Picos de Demanda</h6>
                                <p>${sazonalidade.picos_demanda?.join(', ') || 'N/A'}</p>
                            </div>
                            <div class="sazonalidade-item">
                                <h6>Baixas de Demanda</h6>
                                <p>${sazonalidade.baixas_demanda?.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Tecnologias Emergentes:</strong>
                        <ul>
                            ${(mercado.tecnologias_emergentes || []).map(tech => `<li>${tech}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <!-- Chart Container for Seasonality -->
                <div class="chart-container">
                    <div class="chart-title">Sazonalidade do Mercado</div>
                    <canvas id="seasonalityChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generatePalavrasChaveSection(palavras) {
    if (!palavras) return '';
    
    const primarias = palavras.palavras_primarias || [];
    const secundarias = palavras.palavras_secundarias || [];
    const custos = palavras.custos_aquisicao_canal || {};
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3 class="neo-card-title">Estratégia de Palavras-Chave</h3>
            </div>
            <div class="neo-card-content">
                <div class="palavras-content">
                    <div class="detail-item">
                        <strong>Palavras-Chave Primárias:</strong>
                        <div class="keywords-table">
                            ${primarias.map(kw => `
                                <div class="keyword-row">
                                    <span class="keyword">${kw.termo}</span>
                                    <span class="volume">${kw.volume_mensal}/mês</span>
                                    <span class="cpc">${kw.cpc_estimado}</span>
                                    <span class="difficulty ${kw.dificuldade?.toLowerCase()}">${kw.dificuldade}</span>
                                    <span class="intent">${kw.intencao_busca}</span>
                                    <span class="opportunity ${kw.oportunidade?.toLowerCase()}">${kw.oportunidade}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Palavras-Chave Secundárias:</strong>
                        <div class="keywords-table">
                            ${secundarias.map(kw => `
                                <div class="keyword-row">
                                    <span class="keyword">${kw.termo}</span>
                                    <span class="volume">${kw.volume_mensal}/mês</span>
                                    <span class="cpc">${kw.cpc_estimado}</span>
                                    <span class="difficulty ${kw.dificuldade?.toLowerCase()}">${kw.dificuldade}</span>
                                    <span class="intent">${kw.intencao_busca}</span>
                                    <span class="opportunity ${kw.oportunidade?.toLowerCase()}">${kw.oportunidade}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Custos por Plataforma:</strong>
                        <div class="platform-costs">
                            ${Object.entries(custos).map(([platform, costs]) => `
                                <div class="platform-item">
                                    <h5>${platform.charAt(0).toUpperCase() + platform.slice(1)}</h5>
                                    <div class="platform-metrics">
                                        <span>CPC: ${costs.cpc_medio}</span>
                                        <span>CPM: ${costs.cpm_medio}</span>
                                        <span>CTR: ${costs.ctr_esperado}</span>
                                        <span>Conv: ${costs.conversao_esperada}</span>
                                        <span>CPA: ${costs.cpa_estimado}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <!-- Chart Container for CPA by Platform -->
                <div class="chart-container">
                    <div class="chart-title">CPA por Plataforma</div>
                    <canvas id="cpaChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generateMetricasSection(metricas) {
    if (!metricas) return '';
    
    const benchmarks = metricas.benchmarks_segmento || {};
    const funil = metricas.funil_conversao_otimizado || {};
    const kpis = metricas.kpis_criticos || [];
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 class="neo-card-title">Métricas de Performance</h3>
            </div>
            <div class="neo-card-content">
                <div class="metricas-content">
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-value">${benchmarks.cac_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">CAC Médio</div>
                        </div>
                        
                        <div class="metric-item">
                            <div class="metric-value">${benchmarks.ltv_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">LTV Médio</div>
                        </div>
                        
                        <div class="metric-item">
                            <div class="metric-value">${benchmarks.churn_rate_medio || 'N/A'}</div>
                            <div class="metric-label">Churn Rate</div>
                        </div>
                        
                        <div class="metric-item">
                            <div class="metric-value">${benchmarks.ticket_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">Ticket Médio</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Funil de Conversão Otimizado:</strong>
                        <div class="funnel-steps">
                            <div class="funnel-step">Visitantes → Leads: ${funil.visitantes_leads || 'N/A'}</div>
                            <div class="funnel-step">Leads → Oportunidades: ${funil.leads_oportunidades || 'N/A'}</div>
                            <div class="funnel-step">Oportunidades → Vendas: ${funil.oportunidades_vendas || 'N/A'}</div>
                            <div class="funnel-step">Vendas → Clientes: ${funil.vendas_clientes || 'N/A'}</div>
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <strong>KPIs Críticos:</strong>
                        ${kpis.map(kpi => `
                            <div class="kpi-item">
                                <h5>${kpi.metrica}</h5>
                                <p><strong>Valor Ideal:</strong> ${kpi.valor_ideal}</p>
                                <p><strong>Como Medir:</strong> ${kpi.como_medir}</p>
                                <p><strong>Frequência:</strong> ${kpi.frequencia}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Chart Container for Conversion Funnel -->
                <div class="chart-container">
                    <div class="chart-title">Funil de Conversão</div>
                    <canvas id="funnelChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generateVozMercadoSection(voz) {
    if (!voz) return '';
    
    const linguagem = voz.linguagem_avatar || {};
    const objecoes = voz.objecoes_principais || [];
    const gatilhos = voz.gatilhos_mentais_efetivos || [];
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-comments"></i>
                </div>
                <h3 class="neo-card-title">Voz do Mercado</h3>
            </div>
            <div class="neo-card-content">
                <div class="voz-content">
                    <div class="detail-item">
                        <strong>Linguagem do Avatar:</strong>
                        <p><strong>Termos Técnicos:</strong> ${linguagem.termos_tecnicos?.join(', ') || 'N/A'}</p>
                        <p><strong>Gírias:</strong> ${linguagem.girias_expressoes?.join(', ') || 'N/A'}</p>
                        <p><strong>Palavras de Poder:</strong> ${linguagem.palavras_poder?.join(', ') || 'N/A'}</p>
                        <p><strong>Palavras a Evitar:</strong> ${linguagem.palavras_evitar?.join(', ') || 'N/A'}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Principais Objeções:</strong>
                        ${objecoes.map(obj => `
                            <div class="objecao-item">
                                <h5>Objeção: "${obj.objecao}"</h5>
                                <p><strong>Frequência:</strong> ${obj.frequencia}</p>
                                <p><strong>Momento:</strong> ${obj.momento_surgimento}</p>
                                <p><strong>Estratégia:</strong> ${obj.estrategia_contorno}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-item">
                        <strong>Gatilhos Mentais Efetivos:</strong>
                        ${gatilhos.map(gatilho => `
                            <div class="gatilho-item">
                                <h5>${gatilho.gatilho}</h5>
                                <p><strong>Aplicação:</strong> ${gatilho.aplicacao}</p>
                                <p><strong>Efetividade:</strong> ${gatilho.efetividade}</p>
                                <p><strong>Exemplos:</strong> ${gatilho.exemplos?.join(', ')}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateProjecoesSection(projecoes) {
    if (!projecoes) return '';
    
    const conservador = projecoes.cenario_conservador || {};
    const realista = projecoes.cenario_realista || {};
    const otimista = projecoes.cenario_otimista || {};
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h3 class="neo-card-title">Projeções de Cenários</h3>
            </div>
            <div class="neo-card-content">
                <div class="projecoes-content">
                    <div class="scenarios-grid">
                        <div class="scenario-item conservador">
                            <h4>Cenário Conservador</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${conservador.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${conservador.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${conservador.cac}</p>
                                <p><strong>LTV:</strong> ${conservador.ltv}</p>
                                <p><strong>Faturamento:</strong> ${conservador.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${conservador.roi}</p>
                                <p><strong>Break Even:</strong> ${conservador.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${(conservador.premissas || []).map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        
                        <div class="scenario-item realista">
                            <h4>Cenário Realista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${realista.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${realista.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${realista.cac}</p>
                                <p><strong>LTV:</strong> ${realista.ltv}</p>
                                <p><strong>Faturamento:</strong> ${realista.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${realista.roi}</p>
                                <p><strong>Break Even:</strong> ${realista.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${(realista.premissas || []).map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        
                        <div class="scenario-item otimista">
                            <h4>Cenário Otimista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${otimista.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${otimista.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${otimista.cac}</p>
                                <p><strong>LTV:</strong> ${otimista.ltv}</p>
                                <p><strong>Faturamento:</strong> ${otimista.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${otimista.roi}</p>
                                <p><strong>Break Even:</strong> ${otimista.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${(otimista.premissas || []).map(premissa => `<li>${premissa}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Chart Container for ROI Comparison -->
                <div class="chart-container">
                    <div class="chart-title">Comparação de ROI por Cenário</div>
                    <canvas id="roiComparisonChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    `;
}

function generatePlanoAcaoSection(plano) {
    if (!plano || !Array.isArray(plano)) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-tasks"></i>
                </div>
                <h3 class="neo-card-title">Plano de Ação Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="plano-content">
                    <div class="action-timeline">
                        ${plano.map((fase, index) => `
                            <div class="action-phase">
                                <div class="phase-header">
                                    <div class="phase-number">${index + 1}</div>
                                    <div class="phase-info">
                                        <h4>${fase.fase}</h4>
                                        <p>Duração: ${fase.duracao}</p>
                                    </div>
                                </div>
                                <div class="phase-actions">
                                    ${(fase.acoes || []).map(acao => `
                                        <div class="action-item-detailed">
                                            <h5>${acao.acao}</h5>
                                            <div class="action-details">
                                                <p><strong>Responsável:</strong> ${acao.responsavel}</p>
                                                <p><strong>Prazo:</strong> ${acao.prazo}</p>
                                                <p><strong>Recursos:</strong> ${acao.recursos_necessarios?.join(', ')}</p>
                                                <p><strong>Entregáveis:</strong> ${acao.entregaveis?.join(', ')}</p>
                                                <p><strong>Métricas:</strong> ${acao.metricas_sucesso?.join(', ')}</p>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateInsightsSection(insights) {
    if (!insights || !Array.isArray(insights)) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <h3 class="neo-card-title">Insights Exclusivos</h3>
            </div>
            <div class="neo-card-content">
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
            </div>
        </div>
    `;
}

function initializeResultsInteractions() {
    // Add any interactive functionality for results
    console.log('Results interactions initialized');
}

function initializeCharts(analysis) {
    // Initialize all charts with the analysis data
    setTimeout(() => {
        try {
            initializeDemographicsChart(analysis);
            initializePainLevelsChart(analysis);
            initializeMarketShareChart(analysis);
            initializeSeasonalityChart(analysis);
            initializeCPAChart(analysis);
            initializeFunnelChart(analysis);
            initializeROIComparisonChart(analysis);
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }, 500);
}

function initializeDemographicsChart(analysis) {
    const canvas = document.getElementById('demographicsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample data - in real implementation, extract from analysis
    const data = {
        labels: ['25-32 anos', '32-45 anos', '45-55 anos'],
        datasets: [{
            data: [25, 65, 10],
            backgroundColor: [
                'rgba(0, 212, 255, 0.8)',
                'rgba(255, 107, 0, 0.8)',
                'rgba(255, 61, 113, 0.8)'
            ],
            borderColor: [
                '#00d4ff',
                '#ff6b00',
                '#ff3d71'
            ],
            borderWidth: 2
        }]
    };
    
    // Simple pie chart implementation
    drawPieChart(ctx, data, canvas.width, canvas.height);
}

function initializePainLevelsChart(analysis) {
    const canvas = document.getElementById('painLevelsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const dores = analysis.mapeamento_dores_ultra_detalhado || {};
    const nivel1 = (dores.dores_nivel_1_criticas || []).length;
    const nivel2 = (dores.dores_nivel_2_importantes || []).length;
    const nivel3 = (dores.dores_nivel_3_latentes || []).length;
    
    const data = {
        labels: ['Críticas', 'Importantes', 'Latentes'],
        datasets: [{
            data: [nivel1, nivel2, nivel3],
            backgroundColor: [
                'rgba(255, 61, 113, 0.8)',
                'rgba(255, 107, 0, 0.8)',
                'rgba(0, 212, 255, 0.8)'
            ]
        }]
    };
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

function initializeMarketShareChart(analysis) {
    const canvas = document.getElementById('marketShareChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample market share data
    const data = {
        labels: ['Líder', 'Concorrente A', 'Concorrente B', 'Outros', 'Oportunidade'],
        datasets: [{
            data: [30, 20, 15, 25, 10],
            backgroundColor: [
                'rgba(255, 61, 113, 0.8)',
                'rgba(255, 107, 0, 0.8)',
                'rgba(0, 212, 255, 0.8)',
                'rgba(153, 153, 153, 0.8)',
                'rgba(0, 255, 127, 0.8)'
            ]
        }]
    };
    
    drawPieChart(ctx, data, canvas.width, canvas.height);
}

function initializeSeasonalityChart(analysis) {
    const canvas = document.getElementById('seasonalityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample seasonality data
    const data = {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        datasets: [{
            data: [100, 85, 120, 95, 90, 75, 60, 80, 110, 105, 90, 70],
            backgroundColor: 'rgba(0, 212, 255, 0.3)',
            borderColor: '#00d4ff',
            borderWidth: 2
        }]
    };
    
    drawLineChart(ctx, data, canvas.width, canvas.height);
}

function initializeCPAChart(analysis) {
    const canvas = document.getElementById('cpaChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const palavras = analysis.estrategia_palavras_chave || {};
    const custos = palavras.custos_aquisicao_canal || {};
    
    const platforms = Object.keys(custos);
    const cpaValues = platforms.map(platform => {
        const cpa = custos[platform]?.cpa_estimado || 'R$ 0';
        return parseFloat(cpa.replace('R$ ', '').replace(',', '.')) || 0;
    });
    
    const data = {
        labels: platforms.map(p => p.charAt(0).toUpperCase() + p.slice(1)),
        datasets: [{
            data: cpaValues,
            backgroundColor: [
                'rgba(0, 212, 255, 0.8)',
                'rgba(255, 107, 0, 0.8)',
                'rgba(255, 61, 113, 0.8)',
                'rgba(0, 255, 127, 0.8)',
                'rgba(255, 255, 0, 0.8)'
            ]
        }]
    };
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

function initializeFunnelChart(analysis) {
    const canvas = document.getElementById('funnelChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const metricas = analysis.metricas_performance_detalhadas || {};
    const funil = metricas.funil_conversao_otimizado || {};
    
    const data = {
        labels: ['Visitantes', 'Leads', 'Oportunidades', 'Vendas'],
        datasets: [{
            data: [
                100,
                parseFloat(funil.visitantes_leads?.replace('%', '')) || 18,
                parseFloat(funil.leads_oportunidades?.replace('%', '')) || 25,
                parseFloat(funil.oportunidades_vendas?.replace('%', '')) || 12
            ],
            backgroundColor: [
                'rgba(0, 212, 255, 0.8)',
                'rgba(255, 107, 0, 0.8)',
                'rgba(255, 61, 113, 0.8)',
                'rgba(0, 255, 127, 0.8)'
            ]
        }]
    };
    
    drawFunnelChart(ctx, data, canvas.width, canvas.height);
}

function initializeROIComparisonChart(analysis) {
    const canvas = document.getElementById('roiComparisonChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const projecoes = analysis.projecoes_cenarios || {};
    const conservador = parseFloat(projecoes.cenario_conservador?.roi?.replace('%', '')) || 240;
    const realista = parseFloat(projecoes.cenario_realista?.roi?.replace('%', '')) || 380;
    const otimista = parseFloat(projecoes.cenario_otimista?.roi?.replace('%', '')) || 580;
    
    const data = {
        labels: ['Conservador', 'Realista', 'Otimista'],
        datasets: [{
            data: [conservador, realista, otimista],
            backgroundColor: [
                'rgba(255, 61, 113, 0.8)',
                'rgba(0, 212, 255, 0.8)',
                'rgba(0, 255, 127, 0.8)'
            ]
        }]
    };
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

// Simple chart drawing functions
function drawPieChart(ctx, data, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 20;
    
    let total = data.datasets[0].data.reduce((sum, value) => sum + value, 0);
    let currentAngle = -Math.PI / 2;
    
    data.datasets[0].data.forEach((value, index) => {
        const sliceAngle = (value / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = data.datasets[0].backgroundColor[index];
        ctx.fill();
        ctx.strokeStyle = '#0a0a0f';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Add labels
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
        const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(data.labels[index], labelX, labelY);
        
        currentAngle += sliceAngle;
    });
}

function drawBarChart(ctx, data, width, height) {
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const barWidth = chartWidth / data.labels.length - 10;
    const maxValue = Math.max(...data.datasets[0].data);
    
    data.datasets[0].data.forEach((value, index) => {
        const barHeight = (value / maxValue) * chartHeight;
        const x = padding + index * (barWidth + 10);
        const y = height - padding - barHeight;
        
        ctx.fillStyle = data.datasets[0].backgroundColor[index];
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Add value labels
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(value.toString(), x + barWidth / 2, y - 5);
        
        // Add category labels
        ctx.fillText(data.labels[index], x + barWidth / 2, height - 10);
    });
}

function drawLineChart(ctx, data, width, height) {
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const pointSpacing = chartWidth / (data.labels.length - 1);
    const maxValue = Math.max(...data.datasets[0].data);
    
    ctx.beginPath();
    ctx.strokeStyle = data.datasets[0].borderColor;
    ctx.lineWidth = data.datasets[0].borderWidth;
    
    data.datasets[0].data.forEach((value, index) => {
        const x = padding + index * pointSpacing;
        const y = height - padding - (value / maxValue) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        // Draw points
        ctx.fillStyle = data.datasets[0].borderColor;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        
        // Add labels
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(data.labels[index], x, height - 10);
    });
    
    ctx.stroke();
}

function drawFunnelChart(ctx, data, width, height) {
    const padding = 40;
    const chartHeight = height - padding * 2;
    const maxValue = Math.max(...data.datasets[0].data);
    
    data.datasets[0].data.forEach((value, index) => {
        const barWidth = (value / maxValue) * (width - padding * 2);
        const barHeight = chartHeight / data.labels.length - 10;
        const x = padding + (width - padding * 2 - barWidth) / 2;
        const y = padding + index * (barHeight + 10);
        
        ctx.fillStyle = data.datasets[0].backgroundColor[index];
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Add labels
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'left';
        ctx.fillText(`${data.labels[index]}: ${value}%`, padding, y + barHeight / 2 + 4);
    });
}

async function downloadPDFReport() {
    if (!currentAnalysis) {
        showNotification('Nenhuma análise disponível para download.', 'error');
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
            throw new Error('Erro ao gerar PDF');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `analise-avatar-gemini-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Relatório PDF baixado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        showNotification('Erro ao gerar PDF. Tente novamente.', 'error');
    }
}

function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'Análise de Avatar com Gemini Pro 2.5 - UP Lançamentos',
            text: 'Confira minha análise ultra-detalhada de avatar!',
            url: window.location.href
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Link copiado para a área de transferência!', 'success');
        });
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: var(--neo-border-radius);
        color: var(--text-light);
        font-weight: 600;
        z-index: 10000;
        box-shadow: var(--neo-shadow-2);
        transition: var(--neo-transition);
        transform: translateX(100%);
        max-width: 400px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #00ff7f, #00d4ff)';
            notification.style.boxShadow = 'var(--neo-shadow-2), 0 0 20px rgba(0, 255, 127, 0.5)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #ff3d71, #ff6b00)';
            notification.style.boxShadow = 'var(--neo-shadow-2), 0 0 20px rgba(255, 61, 113, 0.5)';
            break;
        default:
            notification.style.background = 'var(--brand-gradient-neon)';
            notification.style.boxShadow = 'var(--neo-shadow-2), var(--neon-blue-glow)';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('.neo-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            if (query.length > 2) {
                searchSegmentos(query);
            }
        });
    }
}

async function searchSegmentos(query) {
    try {
        const response = await fetch(`/api/segmentos?search=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        // Display search suggestions
        displaySearchSuggestions(data.segmentos);
        
    } catch (error) {
        console.error('Erro na busca:', error);
    }
}

function displaySearchSuggestions(segmentos) {
    // Implementation for search suggestions dropdown
    console.log('Segmentos encontrados:', segmentos);
}