// Global variables
let currentUser = null;
let analysisResults = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showMainApp();
    } else {
        showLoginScreen();
    }
    
    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize results interactions
    initializeResultsInteractions();
}

// Google Sign-In Functions
function handleCredentialResponse(response) {
    try {
        // Decode JWT token
        const payload = JSON.parse(atob(response.credential.split('.')[1]));
        
        const user = {
            id: payload.sub,
            name: payload.name,
            email: payload.email,
            picture: payload.picture,
            loginTime: new Date().toISOString()
        };
        
        // Save user data
        currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        // Show main app
        showMainApp();
        
        console.log('Login successful:', user);
    } catch (error) {
        console.error('Error processing Google sign-in:', error);
        alert('Erro no login. Tente novamente.');
    }
}

function initiateGoogleSignIn() {
    // Fallback for when Google Sign-In button doesn't work
    // In production, you would implement proper Google OAuth flow
    const mockUser = {
        id: 'demo_user',
        name: 'Usuário Demo',
        email: 'demo@uplancamentos.com',
        picture: 'https://via.placeholder.com/40x40/00d4ff/ffffff?text=U',
        loginTime: new Date().toISOString()
    };
    
    currentUser = mockUser;
    localStorage.setItem('currentUser', JSON.stringify(mockUser));
    showMainApp();
}

function signOut() {
    // Clear user data
    currentUser = null;
    localStorage.removeItem('currentUser');
    
    // Hide user menu
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        userDropdown.classList.remove('show');
    }
    
    // Show login screen
    showLoginScreen();
    
    // Sign out from Google
    if (window.google && window.google.accounts) {
        google.accounts.id.disableAutoSelect();
    }
}

function showLoginScreen() {
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('header').style.display = 'none';
    document.getElementById('mainContent').style.display = 'none';
}

function showMainApp() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('header').style.display = 'block';
    document.getElementById('mainContent').style.display = 'block';
    
    // Update user info in header
    updateUserInfo();
    
    // Show home section by default
    showSection('home');
}

function updateUserInfo() {
    if (currentUser) {
        const userAvatar = document.getElementById('userAvatar');
        const userName = document.getElementById('userName');
        
        if (userAvatar) {
            userAvatar.src = currentUser.picture;
            userAvatar.alt = currentUser.name;
        }
        
        if (userName) {
            userName.textContent = currentUser.name;
        }
    }
}

function toggleUserMenu() {
    const userDropdown = document.getElementById('userDropdown');
    const userProfile = document.querySelector('.user-profile');
    
    if (userDropdown && userProfile) {
        const isVisible = userDropdown.classList.contains('show');
        
        if (isVisible) {
            userDropdown.classList.remove('show');
            userProfile.classList.remove('active');
        } else {
            userDropdown.classList.add('show');
            userProfile.classList.add('active');
        }
    }
}

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.querySelector('.user-menu');
    const userDropdown = document.getElementById('userDropdown');
    const userProfile = document.querySelector('.user-profile');
    
    if (userMenu && !userMenu.contains(event.target)) {
        if (userDropdown) userDropdown.classList.remove('show');
        if (userProfile) userProfile.classList.remove('active');
    }
});

// Navigation Functions
function initializeNavigation() {
    // Navigation links
    const navLinks = document.querySelectorAll('.neo-nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSection = this.getAttribute('href').substring(1);
            showSection(targetSection);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Header scroll effect
    window.addEventListener('scroll', function() {
        const header = document.getElementById('header');
        if (header) {
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    });
}

function showSection(sectionId) {
    // Hide all sections
    const sections = ['home', 'analyzer', 'dashboard'];
    sections.forEach(id => {
        const section = document.getElementById(id);
        if (section) {
            section.style.display = 'none';
        }
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
}

function showAnalyzer() {
    showSection('analyzer');
    
    // Update navigation
    const navLinks = document.querySelectorAll('.neo-nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#analyzer') {
            link.classList.add('active');
        }
    });
}

// Form Handlers
function initializeFormHandlers() {
    const analyzerForm = document.getElementById('analyzerForm');
    if (analyzerForm) {
        analyzerForm.addEventListener('submit', handleAnalysisSubmission);
    }
}

async function handleAnalysisSubmission(event) {
    event.preventDefault();
    
    if (!currentUser) {
        alert('Você precisa estar logado para realizar análises.');
        return;
    }
    
    const formData = new FormData(event.target);
    const analysisData = {
        segmento: formData.get('segmento'),
        produto: formData.get('produto'),
        descricao: formData.get('descricao'),
        preco: formData.get('preco'),
        publico: formData.get('publico'),
        objetivoReceita: formData.get('objetivoReceita'),
        orcamentoMarketing: formData.get('orcamentoMarketing'),
        prazoLancamento: formData.get('prazoLancamento'),
        concorrentes: formData.get('concorrentes'),
        dadosAdicionais: formData.get('dadosAdicionais'),
        userId: currentUser.id,
        userEmail: currentUser.email
    };
    
    // Validate required fields
    if (!analysisData.segmento) {
        alert('Por favor, informe o segmento de atuação.');
        return;
    }
    
    try {
        // Show loading state
        showLoadingState();
        
        // Switch to dashboard
        showSection('dashboard');
        updateNavigation('dashboard');
        
        // Start analysis
        await performAnalysis(analysisData);
        
    } catch (error) {
        console.error('Erro na análise:', error);
        hideLoadingState();
        alert('Erro ao realizar análise. Tente novamente.');
    }
}

function updateNavigation(activeSection) {
    const navLinks = document.querySelectorAll('.neo-nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${activeSection}`) {
            link.classList.add('active');
        }
    });
}

// Analysis Functions
async function performAnalysis(data) {
    const loadingMessages = [
        'Iniciando análise ultra-detalhada...',
        'Pesquisando dados na internet...',
        'Analisando concorrência...',
        'Mapeando dores do avatar...',
        'Calculando métricas de performance...',
        'Gerando insights exclusivos...',
        'Criando plano de ação...',
        'Finalizando análise...'
    ];
    
    let progress = 0;
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const loadingText = document.getElementById('loadingText');
    
    // Simulate progress
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) progress = 95;
        
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${Math.round(progress)}%`;
        
        // Update loading message
        const messageIndex = Math.floor((progress / 100) * loadingMessages.length);
        if (loadingText && loadingMessages[messageIndex]) {
            loadingText.textContent = loadingMessages[messageIndex];
        }
    }, 800);
    
    try {
        // Make API call
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const results = await response.json();
        
        // Complete progress
        clearInterval(progressInterval);
        if (progressBar) progressBar.style.width = '100%';
        if (progressText) progressText.textContent = '100%';
        if (loadingText) loadingText.textContent = 'Análise concluída!';
        
        // Wait a moment then show results
        setTimeout(() => {
            hideLoadingState();
            displayResults(results);
        }, 1000);
        
    } catch (error) {
        clearInterval(progressInterval);
        throw error;
    }
}

function showLoadingState() {
    const loadingState = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loadingState) loadingState.style.display = 'flex';
    if (resultsContainer) resultsContainer.style.display = 'none';
    
    // Reset progress
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    if (progressBar) progressBar.style.width = '0%';
    if (progressText) progressText.textContent = '0%';
}

function hideLoadingState() {
    const loadingState = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loadingState) loadingState.style.display = 'none';
    if (resultsContainer) resultsContainer.style.display = 'block';
}

// Results Display Functions
function displayResults(results) {
    analysisResults = results;
    const container = document.getElementById('resultsContainer');
    
    if (!container) return;
    
    container.innerHTML = `
        <div class="results-header">
            <div class="neo-enhanced-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="neo-card-title">Análise Ultra-Detalhada Concluída</h3>
                </div>
                <div class="neo-card-content">
                    <p>Sua análise de avatar foi processada com sucesso usando IA avançada e pesquisa em tempo real na internet.</p>
                    <div class="results-actions">
                        <button class="neo-cta-button" onclick="downloadPDFReport()">
                            <i class="fas fa-file-pdf"></i>
                            <span>Baixar Relatório PDF</span>
                        </button>
                        <button class="neo-cta-button" onclick="shareResults()" style="background: linear-gradient(135deg, #ff6b00 0%, #ff3d71 100%);">
                            <i class="fas fa-share-alt"></i>
                            <span>Compartilhar</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="results-grid">
            ${generateScopeCard(results.escopo)}
            ${generateAvatarCard(results.avatar_ultra_detalhado)}
            ${generatePainCard(results.mapeamento_dores_ultra_detalhado)}
            ${generateCompetitionCard(results.analise_concorrencia_detalhada)}
            ${generateMarketCard(results.inteligencia_mercado)}
            ${generateKeywordsCard(results.estrategia_palavras_chave)}
            ${generateMetricsCard(results.metricas_performance_detalhadas)}
            ${generateVoiceCard(results.voz_mercado_linguagem)}
            ${generateProjectionsCard(results.projecoes_cenarios)}
            ${generateActionPlanCard(results.plano_acao_detalhado)}
            ${generateInsightsCard(results.insights_exclusivos)}
        </div>
    `;
    
    // Initialize charts and interactions
    setTimeout(() => {
        initializeCharts();
        initializeResultsInteractions();
    }, 100);
}

function generateScopeCard(escopo) {
    if (!escopo) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-bullseye"></i>
                </div>
                <h3 class="neo-card-title">Escopo Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="detail-item">
                    <strong>Segmento Principal:</strong>
                    <blockquote>${escopo.segmento_principal || 'N/A'}</blockquote>
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
                <div class="detail-item">
                    <strong>Tamanho do Mercado:</strong>
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
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function generateAvatarCard(avatar) {
    if (!avatar) return '';
    
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
                    ${avatar.persona_principal ? `
                    <div class="avatar-section">
                        <h4>Persona Principal</h4>
                        <div class="persona-card">
                            <div class="persona-info">
                                <h5>${avatar.persona_principal.nome || 'Avatar Principal'}</h5>
                                <p><strong>Idade:</strong> ${avatar.persona_principal.idade || 'N/A'}</p>
                                <p><strong>Profissão:</strong> ${avatar.persona_principal.profissao || 'N/A'}</p>
                                <p><strong>Renda:</strong> ${avatar.persona_principal.renda_mensal || 'N/A'}</p>
                                <p><strong>Localização:</strong> ${avatar.persona_principal.localizacao || 'N/A'}</p>
                                <p><strong>Estado Civil:</strong> ${avatar.persona_principal.estado_civil || 'N/A'}</p>
                                <p><strong>Escolaridade:</strong> ${avatar.persona_principal.escolaridade || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.demografia_detalhada ? `
                    <div class="avatar-section">
                        <h4>Demografia Detalhada</h4>
                        <div class="detail-grid">
                            ${Object.entries(avatar.demografia_detalhada).map(([key, value]) => `
                                <div class="detail-item">
                                    <strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                                    <p>${value}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.psicografia_profunda ? `
                    <div class="avatar-section">
                        <h4>Psicografia Profunda</h4>
                        <div class="detail-grid">
                            ${avatar.psicografia_profunda.valores_fundamentais ? `
                            <div class="detail-item">
                                <strong>Valores Fundamentais:</strong>
                                <ul>
                                    ${avatar.psicografia_profunda.valores_fundamentais.map(valor => `<li>${valor}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            
                            ${avatar.psicografia_profunda.estilo_vida_detalhado ? `
                            <div class="detail-item">
                                <strong>Estilo de Vida:</strong>
                                <p>${avatar.psicografia_profunda.estilo_vida_detalhado}</p>
                            </div>
                            ` : ''}
                            
                            ${avatar.psicografia_profunda.aspiracoes_profissionais ? `
                            <div class="detail-item">
                                <strong>Aspirações Profissionais:</strong>
                                <ul>
                                    ${avatar.psicografia_profunda.aspiracoes_profissionais.map(asp => `<li>${asp}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            
                            ${avatar.psicografia_profunda.medos_profundos ? `
                            <div class="detail-item">
                                <strong>Medos Profundos:</strong>
                                <ul>
                                    ${avatar.psicografia_profunda.medos_profundos.map(medo => `<li>${medo}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.comportamento_digital_avancado ? `
                    <div class="avatar-section">
                        <h4>Comportamento Digital</h4>
                        <div class="detail-grid">
                            ${avatar.comportamento_digital_avancado.plataformas_primarias ? `
                            <div class="detail-item">
                                <strong>Plataformas Primárias:</strong>
                                <ul>
                                    ${avatar.comportamento_digital_avancado.plataformas_primarias.map(plat => `<li>${plat}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            
                            ${avatar.comportamento_digital_avancado.conteudo_consumido ? `
                            <div class="detail-item">
                                <strong>Conteúdo Consumido:</strong>
                                <p><strong>Formatos:</strong> ${avatar.comportamento_digital_avancado.conteudo_consumido.formatos_preferidos?.join(', ') || 'N/A'}</p>
                                <p><strong>Temas:</strong> ${avatar.comportamento_digital_avancado.conteudo_consumido.temas_interesse?.join(', ') || 'N/A'}</p>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generatePainCard(dores) {
    if (!dores) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-heart-broken"></i>
                </div>
                <h3 class="neo-card-title">Mapeamento de Dores Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                ${dores.dores_nivel_1_criticas ? `
                <div class="detail-item">
                    <strong>Dores Críticas (Nível 1):</strong>
                    <div class="dores-list">
                        ${dores.dores_nivel_1_criticas.map((dor, index) => `
                            <div class="dor-item nivel-1">
                                <h5>Dor ${index + 1}</h5>
                                <p><strong>Dor:</strong> ${typeof dor === 'object' ? dor.dor : dor}</p>
                                ${typeof dor === 'object' ? `
                                    <p><strong>Intensidade:</strong> ${dor.intensidade || 'N/A'}</p>
                                    <p><strong>Frequência:</strong> ${dor.frequencia || 'N/A'}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida || 'N/A'}</p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${dores.dores_nivel_2_importantes ? `
                <div class="detail-item">
                    <strong>Dores Importantes (Nível 2):</strong>
                    <div class="dores-list">
                        ${dores.dores_nivel_2_importantes.map((dor, index) => `
                            <div class="dor-item nivel-2">
                                <h5>Dor ${index + 1}</h5>
                                <p><strong>Dor:</strong> ${typeof dor === 'object' ? dor.dor : dor}</p>
                                ${typeof dor === 'object' ? `
                                    <p><strong>Intensidade:</strong> ${dor.intensidade || 'N/A'}</p>
                                    <p><strong>Frequência:</strong> ${dor.frequencia || 'N/A'}</p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${dores.dores_nivel_3_latentes ? `
                <div class="detail-item">
                    <strong>Dores Latentes (Nível 3):</strong>
                    <div class="dores-list">
                        ${dores.dores_nivel_3_latentes.map((dor, index) => `
                            <div class="dor-item nivel-3">
                                <h5>Dor ${index + 1}</h5>
                                <p><strong>Dor:</strong> ${typeof dor === 'object' ? dor.dor : dor}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${dores.jornada_dor ? `
                <div class="detail-item">
                    <strong>Jornada da Dor:</strong>
                    <div class="jornada-dor">
                        <p><strong>Gatilho Inicial:</strong> ${dores.jornada_dor.gatilho_inicial || 'N/A'}</p>
                        <p><strong>Evolução:</strong> ${dores.jornada_dor.evolucao_dor || 'N/A'}</p>
                        <p><strong>Ponto Insuportável:</strong> ${dores.jornada_dor.ponto_insuportavel || 'N/A'}</p>
                        <p><strong>Busca por Solução:</strong> ${dores.jornada_dor.busca_solucao || 'N/A'}</p>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function generateCompetitionCard(concorrencia) {
    if (!concorrencia) return '';
    
    return `
        <div class="neo-enhanced-card result-card half-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chess"></i>
                </div>
                <h3 class="neo-card-title">Análise da Concorrência</h3>
            </div>
            <div class="neo-card-content">
                ${concorrencia.concorrentes_diretos ? `
                <div class="detail-item">
                    <strong>Concorrentes Diretos:</strong>
                    ${concorrencia.concorrentes_diretos.map(comp => `
                        <div class="competitor-item">
                            <h5>${comp.nome || 'Concorrente'}</h5>
                            <p><strong>Preço:</strong> ${comp.preco_range || 'N/A'}</p>
                            <p><strong>Proposta:</strong> ${comp.proposta_valor || 'N/A'}</p>
                            <p><strong>Share de Mercado:</strong> ${comp.share_mercado_estimado || 'N/A'}</p>
                            ${comp.pontos_fortes ? `
                                <p><strong>Pontos Fortes:</strong></p>
                                <ul>
                                    ${comp.pontos_fortes.map(ponto => `<li>${ponto}</li>`).join('')}
                                </ul>
                            ` : ''}
                            ${comp.pontos_fracos ? `
                                <p><strong>Pontos Fracos:</strong></p>
                                <ul>
                                    ${comp.pontos_fracos.map(ponto => `<li>${ponto}</li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
                ` : ''}
                
                ${concorrencia.gaps_oportunidades ? `
                <div class="detail-item">
                    <strong>Gaps e Oportunidades:</strong>
                    <ul>
                        ${concorrencia.gaps_oportunidades.map(gap => `<li>${gap}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${concorrencia.fatores_diferenciacao ? `
                <div class="detail-item">
                    <strong>Fatores de Diferenciação:</strong>
                    <ul>
                        ${concorrencia.fatores_diferenciacao.map(fator => `<li>${fator}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function generateMarketCard(mercado) {
    if (!mercado) return '';
    
    return `
        <div class="neo-enhanced-card result-card half-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-pie"></i>
                </div>
                <h3 class="neo-card-title">Inteligência de Mercado</h3>
            </div>
            <div class="neo-card-content">
                ${mercado.tendencias_crescimento ? `
                <div class="detail-item">
                    <strong>Tendências em Crescimento:</strong>
                    ${mercado.tendencias_crescimento.map(tend => `
                        <div class="tendencia-item crescimento">
                            <h5>${tend.tendencia || 'Tendência'}</h5>
                            <p><strong>Impacto:</strong> ${tend.impacto || 'N/A'}</p>
                            <p><strong>Timeline:</strong> ${tend.timeline || 'N/A'}</p>
                            <p><strong>Oportunidade:</strong> ${tend.oportunidade || 'N/A'}</p>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
                
                ${mercado.sazonalidade_detalhada ? `
                <div class="detail-item">
                    <strong>Sazonalidade:</strong>
                    <div class="sazonalidade-grid">
                        <div class="sazonalidade-item">
                            <h6>Picos de Demanda</h6>
                            <p>${mercado.sazonalidade_detalhada.picos_demanda?.join(', ') || 'N/A'}</p>
                        </div>
                        <div class="sazonalidade-item">
                            <h6>Baixas de Demanda</h6>
                            <p>${mercado.sazonalidade_detalhada.baixas_demanda?.join(', ') || 'N/A'}</p>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${mercado.tecnologias_emergentes ? `
                <div class="detail-item">
                    <strong>Tecnologias Emergentes:</strong>
                    <ul>
                        ${mercado.tecnologias_emergentes.map(tech => `<li>${tech}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function generateKeywordsCard(palavras) {
    if (!palavras) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3 class="neo-card-title">Estratégia de Palavras-Chave</h3>
            </div>
            <div class="neo-card-content">
                ${palavras.palavras_primarias ? `
                <div class="detail-item">
                    <strong>Palavras-Chave Primárias:</strong>
                    <div class="keywords-table">
                        ${palavras.palavras_primarias.slice(0, 5).map(kw => `
                            <div class="keyword-row">
                                <span class="keyword">${kw.termo || 'N/A'}</span>
                                <span>${kw.volume_mensal || 'N/A'}</span>
                                <span>${kw.cpc_estimado || 'N/A'}</span>
                                <span class="difficulty ${(kw.dificuldade || '').toLowerCase()}">${kw.dificuldade || 'N/A'}</span>
                                <span class="opportunity ${(kw.oportunidade || '').toLowerCase()}">${kw.oportunidade || 'N/A'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${palavras.palavras_long_tail ? `
                <div class="detail-item">
                    <strong>Palavras Long Tail:</strong>
                    <ul>
                        ${palavras.palavras_long_tail.map(kw => `<li>${kw}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${palavras.custos_aquisicao_canal ? `
                <div class="detail-item">
                    <strong>Custos por Plataforma:</strong>
                    <div class="platform-costs">
                        ${Object.entries(palavras.custos_aquisicao_canal).map(([platform, costs]) => `
                            <div class="platform-item">
                                <h5>${platform.replace('_', ' ')}</h5>
                                <div class="platform-metrics">
                                    <span>CPC: ${costs.cpc_medio || 'N/A'}</span>
                                    <span>CPM: ${costs.cpm_medio || 'N/A'}</span>
                                    <span>CPA: ${costs.cpa_estimado || 'N/A'}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function generateMetricsCard(metricas) {
    if (!metricas) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 class="neo-card-title">Métricas de Performance</h3>
            </div>
            <div class="neo-card-content">
                ${metricas.benchmarks_segmento ? `
                <div class="detail-item">
                    <strong>Benchmarks do Segmento:</strong>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-value">${metricas.benchmarks_segmento.cac_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">CAC Médio</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${metricas.benchmarks_segmento.ltv_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">LTV Médio</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${metricas.benchmarks_segmento.churn_rate_medio || 'N/A'}</div>
                            <div class="metric-label">Churn Rate</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${metricas.benchmarks_segmento.ticket_medio_segmento || 'N/A'}</div>
                            <div class="metric-label">Ticket Médio</div>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${metricas.funil_conversao_otimizado ? `
                <div class="detail-item">
                    <strong>Funil de Conversão Otimizado:</strong>
                    <div class="funnel-steps">
                        <div class="funnel-step">Visitantes → Leads: ${metricas.funil_conversao_otimizado.visitantes_leads || 'N/A'}</div>
                        <div class="funnel-step">Leads → Oportunidades: ${metricas.funil_conversao_otimizado.leads_oportunidades || 'N/A'}</div>
                        <div class="funnel-step">Oportunidades → Vendas: ${metricas.funil_conversao_otimizado.oportunidades_vendas || 'N/A'}</div>
                        <div class="funnel-step">Vendas → Clientes: ${metricas.funil_conversao_otimizado.vendas_clientes || 'N/A'}</div>
                    </div>
                </div>
                ` : ''}
                
                ${metricas.kpis_criticos ? `
                <div class="detail-item">
                    <strong>KPIs Críticos:</strong>
                    ${metricas.kpis_criticos.map(kpi => `
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
    `;
}

function generateVoiceCard(voz) {
    if (!voz) return '';
    
    return `
        <div class="neo-enhanced-card result-card half-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-comments"></i>
                </div>
                <h3 class="neo-card-title">Voz do Mercado</h3>
            </div>
            <div class="neo-card-content">
                ${voz.linguagem_avatar ? `
                <div class="detail-item">
                    <strong>Linguagem do Avatar:</strong>
                    ${voz.linguagem_avatar.termos_tecnicos ? `
                        <p><strong>Termos Técnicos:</strong> ${voz.linguagem_avatar.termos_tecnicos.join(', ')}</p>
                    ` : ''}
                    ${voz.linguagem_avatar.palavras_poder ? `
                        <p><strong>Palavras de Poder:</strong> ${voz.linguagem_avatar.palavras_poder.join(', ')}</p>
                    ` : ''}
                    ${voz.linguagem_avatar.palavras_evitar ? `
                        <p><strong>Palavras a Evitar:</strong> ${voz.linguagem_avatar.palavras_evitar.join(', ')}</p>
                    ` : ''}
                </div>
                ` : ''}
                
                ${voz.objecoes_principais ? `
                <div class="detail-item">
                    <strong>Principais Objeções:</strong>
                    ${voz.objecoes_principais.map(obj => `
                        <div class="objecao-item">
                            <h5>Objeção</h5>
                            <p><strong>Objeção:</strong> ${obj.objecao || 'N/A'}</p>
                            <p><strong>Estratégia:</strong> ${obj.estrategia_contorno || 'N/A'}</p>
                            <p><strong>Frequência:</strong> ${obj.frequencia || 'N/A'}</p>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
                
                ${voz.gatilhos_mentais_efetivos ? `
                <div class="detail-item">
                    <strong>Gatilhos Mentais Efetivos:</strong>
                    ${voz.gatilhos_mentais_efetivos.map(gatilho => `
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
    `;
}

function generateProjectionsCard(projecoes) {
    if (!projecoes) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h3 class="neo-card-title">Projeções de Cenários</h3>
            </div>
            <div class="neo-card-content">
                <div class="scenarios-grid">
                    ${projecoes.cenario_conservador ? `
                    <div class="scenario-item conservador">
                        <h4>Cenário Conservador</h4>
                        <div class="scenario-metrics">
                            <p><strong>Taxa de Conversão:</strong> ${projecoes.cenario_conservador.taxa_conversao || 'N/A'}</p>
                            <p><strong>Faturamento Mensal:</strong> ${projecoes.cenario_conservador.faturamento_mensal || 'N/A'}</p>
                            <p><strong>ROI:</strong> ${projecoes.cenario_conservador.roi || 'N/A'}</p>
                            <p><strong>Break Even:</strong> ${projecoes.cenario_conservador.break_even || 'N/A'}</p>
                        </div>
                        ${projecoes.cenario_conservador.premissas ? `
                        <div class="scenario-assumptions">
                            <strong>Premissas:</strong>
                            <ul>
                                ${projecoes.cenario_conservador.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    ${projecoes.cenario_realista ? `
                    <div class="scenario-item realista">
                        <h4>Cenário Realista</h4>
                        <div class="scenario-metrics">
                            <p><strong>Taxa de Conversão:</strong> ${projecoes.cenario_realista.taxa_conversao || 'N/A'}</p>
                            <p><strong>Faturamento Mensal:</strong> ${projecoes.cenario_realista.faturamento_mensal || 'N/A'}</p>
                            <p><strong>ROI:</strong> ${projecoes.cenario_realista.roi || 'N/A'}</p>
                            <p><strong>Break Even:</strong> ${projecoes.cenario_realista.break_even || 'N/A'}</p>
                        </div>
                        ${projecoes.cenario_realista.premissas ? `
                        <div class="scenario-assumptions">
                            <strong>Premissas:</strong>
                            <ul>
                                ${projecoes.cenario_realista.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    ${projecoes.cenario_otimista ? `
                    <div class="scenario-item otimista">
                        <h4>Cenário Otimista</h4>
                        <div class="scenario-metrics">
                            <p><strong>Taxa de Conversão:</strong> ${projecoes.cenario_otimista.taxa_conversao || 'N/A'}</p>
                            <p><strong>Faturamento Mensal:</strong> ${projecoes.cenario_otimista.faturamento_mensal || 'N/A'}</p>
                            <p><strong>ROI:</strong> ${projecoes.cenario_otimista.roi || 'N/A'}</p>
                            <p><strong>Break Even:</strong> ${projecoes.cenario_otimista.break_even || 'N/A'}</p>
                        </div>
                        ${projecoes.cenario_otimista.premissas ? `
                        <div class="scenario-assumptions">
                            <strong>Premissas:</strong>
                            <ul>
                                ${projecoes.cenario_otimista.premissas.map(premissa => `<li>${premissa}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateActionPlanCard(plano) {
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
                                ${fase.acoes.map(acao => `
                                    <div class="action-item-detailed">
                                        <h5>${acao.acao || 'Ação'}</h5>
                                        <div class="action-details">
                                            <p><strong>Responsável:</strong> ${acao.responsavel || 'N/A'}</p>
                                            <p><strong>Prazo:</strong> ${acao.prazo || 'N/A'}</p>
                                            ${acao.recursos_necessarios ? `
                                                <p><strong>Recursos:</strong> ${acao.recursos_necessarios.join(', ')}</p>
                                            ` : ''}
                                            ${acao.metricas_sucesso ? `
                                                <p><strong>Métricas:</strong> ${acao.metricas_sucesso.join(', ')}</p>
                                            ` : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function generateInsightsCard(insights) {
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

// Chart Functions
function initializeCharts() {
    // Initialize any charts here
    console.log('Charts initialized');
}

// Results Interactions
function initializeResultsInteractions() {
    // Add any interactive elements here
    console.log('Results interactions initialized');
}

// PDF Download Function
async function downloadPDFReport() {
    if (!analysisResults) {
        alert('Nenhuma análise disponível para download.');
        return;
    }
    
    try {
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisResults)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao gerar PDF');
        }
        
        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `analise-avatar-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        alert('Erro ao gerar PDF. Tente novamente.');
    }
}

// Share Results Function
function shareResults() {
    if (!analysisResults) {
        alert('Nenhuma análise disponível para compartilhar.');
        return;
    }
    
    const shareData = {
        title: 'Análise de Avatar - UP Lançamentos',
        text: `Confira minha análise ultra-detalhada de avatar para o segmento ${analysisResults.escopo?.segmento_principal || 'N/A'}`,
        url: window.location.href
    };
    
    if (navigator.share) {
        navigator.share(shareData);
    } else {
        // Fallback for browsers that don't support Web Share API
        const url = encodeURIComponent(shareData.url);
        const text = encodeURIComponent(shareData.text);
        const whatsappUrl = `https://wa.me/?text=${text}%20${url}`;
        window.open(whatsappUrl, '_blank');
    }
}

// Utility Functions
function formatCurrency(value) {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatPercentage(value) {
    if (!value) return 'N/A';
    return `${value}%`;
}

// Error Handling
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled Promise Rejection:', event.reason);
});