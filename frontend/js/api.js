/**
 * API Client Module
 * Handles all REST API calls to the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

// Toast notification system
class ToastNotification {
  static show(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = '🔔';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    if (type === 'info') icon = 'ℹ️';
    
    toast.innerHTML = `
      <i class="fa-solid fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      <span>${message}</span>
    `;
    
    container.appendChild(toast);
    toast.style.animation = 'toastIn 0.25s ease-out both';
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
}

// API Client
class APIClient {
  static async request(endpoint, options = {}) {
    try {
      const token = localStorage.getItem('authToken');
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('authToken');
          window.location.reload();
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      ToastNotification.show(`Error: ${error.message}`, 'error');
      throw error;
    }
  }
  
  // Chat endpoints
  static async askQuestion(question, department = 'All') {
    return this.request('/chat/ask', {
      method: 'POST',
      body: JSON.stringify({ question, department }),
    });
  }
  
  static async getChatSessions() {
    return this.request('/chat/sessions');
  }
  
  static async getChatHistory(sessionId) {
    return this.request(`/chat/sessions/${sessionId}/messages`);
  }
  
  static async deleteSession(sessionId) {
    return this.request(`/chat/sessions/${sessionId}`, { method: 'DELETE' });
  }
  
  // Document endpoints
  static async getDocuments(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/documents?${params}`);
  }
  
  static async getDepartments() {
    return this.request('/documents/departments');
  }
  
  static async uploadDocument(formData) {
    const token = localStorage.getItem('authToken');
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`);
    return await response.json();
  }
  
  static async deleteDocument(docId) {
    return this.request(`/documents/${docId}`, { method: 'DELETE' });
  }
  
  static async reindexDocument(docId) {
    return this.request(`/documents/${docId}/reindex`, { method: 'POST' });
  }
  
  // Admin endpoints
  static async getAdminStats() {
    return this.request('/admin/stats');
  }
  
  static async seedSampleData() {
    return this.request('/admin/seed-sample-data', { method: 'POST' });
  }
  
  // Auth endpoints
  static async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (response.access_token) {
      localStorage.setItem('authToken', response.access_token);
    }
    return response;
  }
  
  static async register(email, password, full_name, role = 'student') {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, role }),
    });
    
    if (response.access_token) {
      localStorage.setItem('authToken', response.access_token);
    }
    return response;
  }
  
  static logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
  }
}