/**
 * Chat Module
 * Handles chat interface, message rendering, and RAG interactions
 */

class ChatManager {
  constructor() {
    this.currentSessionId = null;
    this.messages = [];
    this.isLoading = false;
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.loadChatHistory();
  }
  
  setupEventListeners() {
    document.getElementById('chatForm').addEventListener('submit', (e) => this.handleSendMessage(e));
    document.getElementById('newChatBtn').addEventListener('click', () => this.startNewChat());
    document.getElementById('seedDataQuickBtn').addEventListener('click', () => this.seedSampleData());
    document.getElementById('themeToggleBtn').addEventListener('click', () => this.toggleTheme());
    document.getElementById('deptFilterSelect').addEventListener('change', (e) => this.updateDepartmentScope(e));
    document.getElementById('tabChatBtn').addEventListener('click', () => this.switchView('chat'));
    document.getElementById('tabAdminBtn').addEventListener('click', () => this.switchView('admin'));
    document.getElementById('toggleSidebarBtn').addEventListener('click', () => this.toggleSidebar());
    document.getElementById('closeSidebarBtn').addEventListener('click', () => this.closeSidebar());
    
    // Starter cards
    document.querySelectorAll('.starter-card').forEach(card => {
      card.addEventListener('click', (e) => {
        const prompt = e.currentTarget.dataset.prompt;
        document.getElementById('chatInput').value = prompt;
      });
    });
  }
  
  async handleSendMessage(e) {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message || this.isLoading) return;
    
    this.isLoading = true;
    input.value = '';
    input.disabled = true;
    document.getElementById('sendBtn').disabled = true;
    
    try {
      // Add user message to UI
      this.addMessageToUI(message, 'user');
      
      // Hide welcome hero if visible
      const welcomeHero = document.getElementById('welcomeHero');
      if (welcomeHero) welcomeHero.style.display = 'none';
      
      // Get department filter
      const department = document.getElementById('deptFilterSelect').value || 'All';
      
      // Call API
      const response = await APIClient.askQuestion(message, department);
      
      // Add assistant message
      this.addMessageToUI(response.answer, 'assistant', response.sources, response.latency_ms);
      
      ToastNotification.show('✅ Response received', 'success');
    } catch (error) {
      this.addMessageToUI('Sorry, an error occurred while processing your question.', 'assistant');
      console.error('Chat error:', error);
    } finally {
      this.isLoading = false;
      input.disabled = false;
      document.getElementById('sendBtn').disabled = false;
      input.focus();
    }
  }
  
  addMessageToUI(content, role = 'assistant', sources = [], latency = null) {
    const messageStream = document.getElementById('messageStream');
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user-graduate"></i>' : '<i class="fa-solid fa-robot"></i>';
    
    const body = document.createElement('div');
    body.className = 'message-body';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${this.escapeHtml(content)}</p>`;
    
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    
    if (latency) {
      const latencySpan = document.createElement('span');
      latencySpan.className = 'message-latency';
      latencySpan.textContent = `${latency}ms`;
      meta.appendChild(latencySpan);
    }
    
    body.appendChild(bubble);
    
    // Add citations if available
    if (sources && sources.length > 0) {
      const citationsContainer = document.createElement('div');
      citationsContainer.className = 'citations-container';
      
      sources.forEach(source => {
        const chip = document.createElement('div');
        chip.className = 'citation-chip';
        chip.innerHTML = `
          <span class="citation-score-dot"></span>
          <span>${source.document_title || 'Source'}</span>
        `;
        chip.style.cursor = 'pointer';
        chip.addEventListener('click', () => this.showCitationModal(source));
        citationsContainer.appendChild(chip);
      });
      
      body.appendChild(citationsContainer);
    }
    
    body.appendChild(meta);
    messageRow.appendChild(avatar);
    messageRow.appendChild(body);
    
    messageStream.appendChild(messageRow);
    messageStream.scrollTop = messageStream.scrollHeight;
  }
  
  showCitationModal(source) {
    const modal = document.getElementById('citationModal');
    document.getElementById('citationModalTitle').textContent = source.document_title || 'Source';
    document.getElementById('citationModalDept').textContent = source.department || 'General';
    document.getElementById('citationModalPage').textContent = `Page ${source.page_number || 1}`;
    document.getElementById('citationModalScore').textContent = `Similarity: ${(source.similarity_score || 0).toFixed(2)}`;
    document.getElementById('citationModalText').textContent = source.chunk_text || source.text || 'No text available';
    
    modal.classList.add('active');
    document.getElementById('closeCitationModalBtn').onclick = () => modal.classList.remove('active');
  }
  
  startNewChat() {
    const messageStream = document.getElementById('messageStream');
    messageStream.innerHTML = '';
    this.messages = [];
    this.currentSessionId = null;
    
    const welcomeHero = document.getElementById('welcomeHero');
    if (welcomeHero) welcomeHero.style.display = 'flex';
    
    document.getElementById('chatInput').focus();
  }
  
  async loadChatHistory() {
    try {
      const sessions = await APIClient.getChatSessions();
      const historyList = document.getElementById('historyList');
      
      if (!sessions || sessions.length === 0) {
        historyList.innerHTML = '<div class="history-empty">No conversations yet</div>';
        return;
      }
      
      historyList.innerHTML = '';
      sessions.forEach(session => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
          <span class="history-title" title="${session.title}">${session.title}</span>
          <button class="history-delete-btn" title="Delete"><i class="fa-solid fa-trash"></i></button>
        `;
        
        item.addEventListener('click', () => this.loadSession(session.id));
        item.querySelector('.history-delete-btn').addEventListener('click', (e) => {
          e.stopPropagation();
          this.deleteSession(session.id);
        });
        
        historyList.appendChild(item);
      });
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }
  
  async loadSession(sessionId) {
    try {
      const messages = await APIClient.getChatHistory(sessionId);
      const messageStream = document.getElementById('messageStream');
      messageStream.innerHTML = '';
      this.messages = messages;
      this.currentSessionId = sessionId;
      
      const welcomeHero = document.getElementById('welcomeHero');
      if (welcomeHero) welcomeHero.style.display = 'none';
      
      messages.forEach(msg => {
        this.addMessageToUI(msg.content, msg.role, msg.sources);
      });
    } catch (error) {
      ToastNotification.show('Failed to load conversation', 'error');
    }
  }
  
  async deleteSession(sessionId) {
    if (!confirm('Delete this conversation?')) return;
    
    try {
      await APIClient.deleteSession(sessionId);
      ToastNotification.show('✅ Conversation deleted', 'success');
      this.loadChatHistory();
      this.startNewChat();
    } catch (error) {
      ToastNotification.show('Failed to delete conversation', 'error');
    }
  }
  
  updateDepartmentScope(e) {
    const department = e.target.value;
    const badge = document.getElementById('currentScopeBadge');
    badge.querySelector('strong').textContent = department;
  }
  
  async seedSampleData() {
    if (!confirm('Load sample college documents?')) return;
    
    try {
      await APIClient.seedSampleData();
      ToastNotification.show('✅ Sample data loaded successfully', 'success');
    } catch (error) {
      ToastNotification.show('Failed to load sample data', 'error');
    }
  }
  
  toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  }
  
  switchView(view) {
    document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));
    document.getElementById(view + 'View').classList.add('active');
    
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById('tab' + (view === 'chat' ? 'Chat' : 'Admin') + 'Btn').classList.add('active');
    
    if (view === 'admin') {
      AdminManager.loadStats();
    }
  }
  
  toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
  }
  
  closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize chat on page load
let chatManager;
document.addEventListener('DOMContentLoaded', () => {
  chatManager = new ChatManager();
});