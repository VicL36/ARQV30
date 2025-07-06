document.addEventListener('DOMContentLoaded', () => {
    const supabaseUrl = '[https://your-supabase-url.supabase.co](https://your-supabase-url.supabase.co)'; // Substitua pela sua URL do Supabase
    const supabaseKey = 'your-supabase-anon-key'; // Substitua pela sua chave anônima do Supabase
    const supabase = supabase.createClient(supabaseUrl, supabaseKey);

    const loginPage = document.getElementById('login-page');
    const signupPage = document.getElementById('signup-page');
    const analysisPage = document.getElementById('analysis-page');
    const loadingPage = document.getElementById('loading-page');
    const resultsPage = document.getElementById('results-page');

    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const analysisForm = document.getElementById('analysis-form');

    const showSignup = document.getElementById('show-signup');
    const showLogin = document.getElementById('show-login');

    const loginError = document.getElementById('login-error');
    const signupError = document.getElementById('signup-error');
    
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const generateDashboardBtn = document.getElementById('generate-dashboard-btn');
    const dashboardView = document.getElementById('dashboard-view');
    const closeDashboardBtn = document.getElementById('close-dashboard-btn');
    const dashboardIframe = document.getElementById('dashboard-iframe');

    let currentUserId = null;
    let currentAnalysisId = null;
    let currentAnalysisData = null;

    // Navegação entre páginas
    const showPage = (page) => {
        [loginPage, signupPage, analysisPage, loadingPage, resultsPage].forEach(p => p.classList.add('hidden'));
        page.classList.remove('hidden');
    };

    showSignup.addEventListener('click', (e) => {
        e.preventDefault();
        showPage(signupPage);
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        showPage(loginPage);
    });

    // Lógica de Autenticação
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = e.target.email.value;
        const password = e.target.password.value;
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) {
            signupError.textContent = error.message;
        } else {
            alert('Cadastro realizado! Verifique seu e-mail para confirmação.');
            showPage(loginPage);
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = e.target.email.value;
        const password = e.target.password.value;
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) {
            loginError.textContent = error.message;
        } else {
            currentUserId = data.user.id;
            showPage(analysisPage);
        }
    });
    
    // Lógica da Análise
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const niche = e.target.niche.value;
        if (!currentUserId) {
            alert('Erro: Usuário não autenticado.');
            return;
        }
        showPage(loadingPage);
        
        try {
            const response = await fetch('/analysis/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ niche, user_id: currentUserId })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Falha na análise');
            }
            
            const data = await response.json();
            displayAnalysisResults(data);
            showPage(resultsPage);

        } catch (error) {
            console.error('Analysis error:', error);
            alert(`Erro ao realizar a análise: ${error.message}`);
            showPage(analysisPage);
        } finally {
            loadingPage.classList.add('hidden');
        }
    });

    function displayAnalysisResults(data) {
        const resultsContainer = document.getElementById('analysis-results');
        resultsContainer.innerHTML = data.analysis_html;
        currentAnalysisId = data.analysis_id;
        currentAnalysisData = data.analysis_data; // Armazena os dados brutos
        
        // Mostra o botão para gerar dashboard
        if (currentAnalysisData) {
            generateDashboardBtn.style.display = 'inline-block';
        }
    }

    // Lógica do PDF
    downloadPdfBtn.addEventListener('click', async () => {
        if (!currentAnalysisId) {
            alert('ID da análise não encontrado.');
            return;
        }
        try {
            const response = await fetch(`/pdf/generate/${currentAnalysisId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Falha ao gerar o PDF');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `relatorio_analise_${currentAnalysisId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF generation error:', error);
            alert(`Erro ao gerar o PDF: ${error.message}`);
        }
    });

    // Lógica do Dashboard
    generateDashboardBtn.addEventListener('click', async () => {
        if (!currentAnalysisData) {
            alert('Dados da análise não encontrados para gerar o dashboard.');
            return;
        }
        
        loadingPage.classList.remove('hidden'); // Reutiliza a página de loading
        
        try {
            const response = await fetch('/analysis/generate_dashboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentAnalysisData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Falha ao gerar o dashboard.');
            }

            const result = await response.json();
            displayDashboard(result.dashboard_html);

        } catch (error) {
            console.error('Dashboard generation error:', error);
            alert(`Erro ao gerar o dashboard: ${error.message}`);
        } finally {
            loadingPage.classList.add('hidden');
        }
    });

    function displayDashboard(dashboardHtml) {
        dashboardIframe.srcdoc = dashboardHtml;
        dashboardView.classList.remove('hidden');
    }

    closeDashboardBtn.addEventListener('click', () => {
        dashboardView.classList.add('hidden');
        dashboardIframe.srcdoc = ''; // Limpa o iframe para liberar memória
    });

});
