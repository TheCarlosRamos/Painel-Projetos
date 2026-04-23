// Chatbot PPI Integration
class PPIChatbot {
  constructor() {
    this.isOpen = false;
    this.history = [];
    this.chatbotApiUrl = 'http://localhost:5001/api/chat'; // Backend URL
    this.healthUrl = 'http://localhost:5001/api/health'; // Health check URL
    this.init();
  }

  init() {
    this.createChatbotHTML();
    this.bindEvents();
    this.loadHistory();
  }

  createChatbotHTML() {
    console.log('Criando HTML do chatbot...');
    
    const chatbotHTML = `
      <div class="chatbot-container">
        <button class="chatbot-toggle" id="chatbotToggle" title="Assistente PPI">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </button>
        
        <div class="chatbot-window" id="chatbotWindow">
          <div class="chatbot-header">
            <div>
              <h3> Assistente PPI</h3>
              <div class="subtitle">Programa de Parcerias de Investimentos</div>
            </div>
            <button class="chatbot-close" id="chatbotClose">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="chatbot-examples">
            <h4>Perguntas rápidas:</h4>
            <button class="chatbot-example-btn" data-question="Quais são os principais setores do PPI?"> Setores</button>
            <button class="chatbot-example-btn" data-question="Quantos projetos existem no PPI?"> Total</button>
            <button class="chatbot-example-btn" data-question="Me fale sobre projetos de infraestrutura"> Infraestrutura</button>
            <button class="chatbot-example-btn" data-question="Qual o status dos projetos?"> Status</button>
          </div>
          
          <div class="chatbot-messages" id="chatbotMessages"></div>
          <div class="chatbot-typing" id="chatbotTyping">🤔 Digitando...</div>
          
          <div class="chatbot-input-container">
            <input type="text" class="chatbot-input" id="chatbotInput" placeholder="Pergunte sobre os projetos do PPI...">
            <button class="chatbot-send" id="chatbotSend">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    console.log(' HTML do chatbot inserido no DOM');
  }

  bindEvents() {
    const toggle = document.getElementById('chatbotToggle');
    const close = document.getElementById('chatbotClose');
    const send = document.getElementById('chatbotSend');
    const input = document.getElementById('chatbotInput');
    const examples = document.querySelectorAll('.chatbot-example-btn');

    toggle.addEventListener('click', () => this.toggle());
    close.addEventListener('click', () => this.close());
    send.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });

    examples.forEach(btn => {
      btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        input.value = question;
        this.sendMessage();
      });
    });
  }

  toggle() {
    const window = document.getElementById('chatbotWindow');
    const toggle = document.getElementById('chatbotToggle');
    
    this.isOpen = !this.isOpen;
    
    if (this.isOpen) {
      window.classList.add('active');
      toggle.classList.add('active');
      if (this.history.length === 0) {
        this.addMessage('bot', ' Olá! Sou o assistente virtual do Programa de Parcerias de Investimentos (PPI). Posso ajudar com informações sobre projetos, setores, status e muito mais. Como posso ajudar você hoje?');
      }
      document.getElementById('chatbotInput').focus();
    } else {
      window.classList.remove('active');
      toggle.classList.remove('active');
    }
  }

  close() {
    const window = document.getElementById('chatbotWindow');
    const toggle = document.getElementById('chatbotToggle');
    
    this.isOpen = false;
    window.classList.remove('active');
    toggle.classList.remove('active');
  }

  addMessage(role, content) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${role}`;
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    this.saveHistory();
  }

  async sendMessage() {
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSend');
    const typing = document.getElementById('chatbotTyping');
    const message = input.value.trim();
    if (!message) return;
    
    // Mostra mensagem do usuário
    this.addMessage('user', message);
    input.value = '';
    sendBtn.disabled = true;
    typing.classList.add('active');
    
    try {
      // Tenta a API direta primeiro
      const response = await fetch(this.chatbotApiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history: this.history })
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', [...response.headers.entries()]);
      
      const data = await response.json();
      console.log('Response data:', data);
      
      typing.classList.remove('active');
      
      if (data.error) {
        console.log('Backend retornou erro:', data.error);
        this.addMessage('bot', 'Desculpe, ocorreu um erro. Tente novamente mais tarde.');
      } else if (data.response) {
        console.log('Backend retornou resposta:', data.response);
        this.addMessage('bot', data.response);
        this.history.push([message, data.response]);
        if (this.history.length > 10) this.history.shift();
      } else {
        console.log('Resposta sem campo response ou error:', data);
        this.addMessage('bot', 'Resposta inesperada do servidor. Tente novamente.');
      }
      
    } catch (error) {
      console.error('CORS Error, tentando fallback:', error);
      
      // Fallback: usa proxy ou respostas pré-definidas
      try {
        const fallbackResponse = await this.getFallbackResponse(message);
        typing.classList.remove('active');
        this.addMessage('bot', fallbackResponse);
        this.history.push([message, fallbackResponse]);
        if (this.history.length > 10) this.history.shift();
      } catch (fallbackError) {
        typing.classList.remove('active');
        console.error('Fallback error:', fallbackError);
        this.addMessage('bot', '🔧 O assistente PPI está temporariamente indisponível. Por favor, tente novamente mais tarde ou contate o suporte técnico.\n\n💡 Enquanto o assistente estiver offline, você pode usar os filtros acima para explorar os projetos do PPI.');
      }
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  saveHistory() {
    try {
      localStorage.setItem('ppi_chatbot_history', JSON.stringify(this.history));
    } catch (e) {
      console.warn('Could not save chat history:', e);
    }
  }

  loadHistory() {
    try {
      const saved = localStorage.getItem('ppi_chatbot_history');
      if (saved) {
        this.history = JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Could not load chat history:', e);
    }
  }

  // Método para atualizar a URL da API (útil para diferentes ambientes)
  setApiUrl(url) {
    this.chatbotApiUrl = url;
    this.healthUrl = url.replace('/api/chat', '/api/health');
  }

  // Método para verificar se o backend está online
  async checkBackendHealth() {
    try {
      const response = await fetch(this.healthUrl);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Função fallback para quando a API não está disponível
  getFallbackResponse(message) {
    // Respostas simples baseadas em palavras-chave
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('projeto') && lowerMessage.includes('quantos')) {
      return "Existem 209 projetos no Programa de Parcerias de Investimentos (PPI). Os projetos abrangem diversos setores como infraestrutura, energia, transportes e telecomunicações.";
    }
    
    if (lowerMessage.includes('setor')) {
      return "Os principais setores do PPI incluem: Infraestrutura de Transportes, Energia, Telecomunicações, Saneamento Básico e Recursos Hídricos. Cada setor tem projetos específicos em diferentes fases de desenvolvimento.";
    }
    
    if (lowerMessage.includes('status') || lowerMessage.includes('andamento')) {
      return "Os projetos do PPI estão em diferentes fases: Em Estudo, Em Licitação, Em Execução e Concluídos. Cada projeto tem seu próprio cronograma e marcos específicos.";
    }
    
    if (lowerMessage.includes('infraestrutura')) {
      return "Os projetos de infraestrutura do PPI incluem rodovias, ferrovias, portos, aeroportos e sistemas de transporte urbano. São projetos estratégicos para o desenvolvimento do país.";
    }
    
    return "Sou o assistente do PPI! Posso ajudar com informações sobre projetos, setores, status e muito mais. Tente perguntar sobre 'quantos projetos existem', 'quais são os principais setores' ou 'status dos projetos'.";
  }
}

// Inicializa o chatbot quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  console.log('Inicializando Chatbot PPI...');
  
  try {
    window.ppiChatbot = new PPIChatbot();
    console.log('Chatbot PPI inicializado com sucesso');
    
    // Verifica saúde do backend periodicamente
    setInterval(async () => {
      const isHealthy = await window.ppiChatbot.checkBackendHealth();
      if (!isHealthy && window.ppiChatbot.isOpen) {
        console.warn('Chatbot backend is offline');
      }
    }, 30000); // Verifica a cada 30 segundos
  } catch (error) {
    console.error(' Erro ao inicializar chatbot:', error);
  }
});

// Exporta para uso global
window.PPIChatbot = PPIChatbot;
