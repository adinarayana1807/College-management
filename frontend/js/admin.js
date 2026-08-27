/**
 * Admin Module
 * Handles admin dashboard, document management, and analytics
 */

class AdminManager {
  static init() {
    this.setupEventListeners();
  }
  
  static setupEventListeners() {
    document.getElementById('openUploadModalBtn').addEventListener('click', () => this.showUploadModal());
    document.getElementById('closeUploadModalBtn').addEventListener('click', () => this.closeUploadModal());
    document.getElementById('cancelUploadBtn').addEventListener('click', () => this.closeUploadModal());
    document.getElementById('uploadForm').addEventListener('submit', (e) => this.handleUpload(e));
    document.getElementById('refreshDocsBtn').addEventListener('click', () => this.loadDocuments());
    
    // File drop zone
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      fileInput.files = e.dataTransfer.files;
      this.updateSelectedFileName();
    });
    
    fileInput.addEventListener('change', () => this.updateSelectedFileName());
  }
  
  static async loadStats() {
    try {
      const stats = await APIClient.getAdminStats();
      
      document.getElementById('statTotalDocs').textContent = stats.total_documents || 0;
      document.getElementById('statTotalChunks').textContent = stats.total_chunks || 0;
      document.getElementById('statTotalQueries').textContent = stats.total_queries || 0;
      document.getElementById('statAvgLatency').textContent = (stats.avg_latency_ms || 0).toFixed(0) + ' ms';
      document.getElementById('statLLMProvider').textContent = `Engine: ${stats.llm_provider || 'Local'}`;
      
      this.loadDocuments();
      this.loadDepartmentDistribution(stats.department_distribution || []);
      this.loadAuditLog(stats.recent_queries || []);
    } catch (error) {
      console.error('Failed to load admin stats:', error);
    }
  }
  
  static async loadDocuments() {
    try {
      const documents = await APIClient.getDocuments();
      const tbody = document.getElementById('docsTableBody');
      
      if (!documents || documents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4">No documents uploaded yet</td></tr>';
        return;
      }
      
      tbody.innerHTML = documents.map(doc => `
        <tr>
          <td>${doc.title}</td>
          <td>${doc.department}</td>
          <td>${doc.file_format || 'TXT'}</td>
          <td>${doc.chunks_count || 0}</td>
          <td>${this.formatFileSize(doc.file_size || 0)}</td>
          <td><span class="status-badge indexed">✓ Indexed</span></td>
          <td>${new Date(doc.created_at).toLocaleDateString()}</td>
          <td class="text-right">
            <button class="btn btn-outline-sm" onclick="AdminManager.reindexDocument('${doc.id}')">Reindex</button>
            <button class="btn btn-outline-sm" onclick="AdminManager.deleteDocument('${doc.id}')" style="color: var(--accent-red);">Delete</button>
          </td>
        </tr>
      `).join('');
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  }
  
  static loadDepartmentDistribution(distribution) {
    const container = document.getElementById('deptDistributionList');
    
    if (!distribution || distribution.length === 0) {
      container.innerHTML = '<div style="text-align: center; color: var(--text-muted);">No data</div>';
      return;
    }
    
    const total = distribution.reduce((sum, d) => sum + d.count, 0);
    
    container.innerHTML = distribution.map(dept => `
      <div class="dept-row">
        <span>${dept.name}</span>
        <div class="dept-bar-bg">
          <div class="dept-bar-fill" style="width: ${(dept.count / total) * 100}%"></div>
        </div>
        <span>${dept.count}</span>
      </div>
    `).join('');
  }
  
  static loadAuditLog(queries) {
    const container = document.getElementById('auditLogList');
    
    if (!queries || queries.length === 0) {
      container.innerHTML = '<div style="text-align: center; color: var(--text-muted);">No queries yet</div>';
      return;
    }
    
    container.innerHTML = queries.slice(0, 10).map(query => `
      <div class="audit-row">
        <div class="audit-header">
          <strong>${query.student_name || 'Anonymous'}</strong>
          <span>${new Date(query.timestamp).toLocaleTimeString()}</span>
        </div>
        <p>${query.question}</p>
      </div>
    `).join('');
  }
  
  static showUploadModal() {
    const user = AuthManager.getCurrentUser();
    if (!user || user.role !== 'admin') {
      ToastNotification.show('Only admins can upload documents', 'error');
      return;
    }
    document.getElementById('uploadModal').classList.add('active');
  }
  
  static closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
    document.getElementById('uploadForm').reset();
    document.getElementById('selectedFileName').textContent = 'No file chosen';
  }
  
  static updateSelectedFileName() {
    const fileInput = document.getElementById('fileInput');
    const fileName = fileInput.files[0]?.name || 'No file chosen';
    document.getElementById('selectedFileName').textContent = fileName;
  }
  
  static async handleUpload(e) {
    e.preventDefault();
    
    const user = AuthManager.getCurrentUser();
    if (!user || user.role !== 'admin') {
      ToastNotification.show('Only admins can upload documents', 'error');
      return;
    }
    
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files[0]) {
      ToastNotification.show('Please select a file', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('title', document.getElementById('uploadDocTitle').value);
    formData.append('department', document.getElementById('uploadDocDept').value);
    
    try {
      await APIClient.uploadDocument(formData);
      ToastNotification.show('✅ Document uploaded successfully', 'success');
      this.closeUploadModal();
      this.loadDocuments();
    } catch (error) {
      ToastNotification.show(`Failed to upload: ${error.message}`, 'error');
    }
  }
  
  static async reindexDocument(docId) {
    if (!confirm('Reindex this document?')) return;
    
    try {
      await APIClient.reindexDocument(docId);
      ToastNotification.show('✅ Document reindexed', 'success');
      this.loadDocuments();
    } catch (error) {
      ToastNotification.show('Failed to reindex', 'error');
    }
  }
  
  static async deleteDocument(docId) {
    if (!confirm('Delete this document?')) return;
    
    try {
      await APIClient.deleteDocument(docId);
      ToastNotification.show('✅ Document deleted', 'success');
      this.loadDocuments();
    } catch (error) {
      ToastNotification.show('Failed to delete', 'error');
    }
  }
  
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
  }
}

// Initialize admin on page load
document.addEventListener('DOMContentLoaded', () => {
  AdminManager.init();
});