/**
 * Authentication Module
 * Manages user authentication, login state, and modal controls
 */

class AuthManager {
  static init() {
    this.setupEventListeners();
    this.checkAuthState();
  }
  
  static setupEventListeners() {
    document.getElementById('authActionBtn').addEventListener('click', () => this.showAuthModal());
    document.getElementById('authSubmitBtn').addEventListener('click', (e) => this.handleAuthSubmit(e));
    document.getElementById('closeAuthModalBtn').addEventListener('click', () => this.closeAuthModal());
    document.getElementById('authToggleBtn').addEventListener('click', (e) => this.toggleAuthMode(e));
    document.getElementById('demoAdminBtn').addEventListener('click', () => this.fillDemoAdmin());
    document.getElementById('demoStudentBtn').addEventListener('click', () => this.fillDemoStudent());
  }
  
  static showAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.add('active');
    this.setAuthMode('login');
  }
  
  static closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
  }
  
  static toggleAuthMode(e) {
    e.preventDefault();
    const currentMode = document.getElementById('authForm').dataset.mode || 'login';
    this.setAuthMode(currentMode === 'login' ? 'signup' : 'login');
  }
  
  static setAuthMode(mode) {
    const form = document.getElementById('authForm');
    const title = document.getElementById('authModalTitle');
    const toggleText = document.getElementById('authToggleText');
    const submitBtn = document.getElementById('authSubmitBtn');
    const fullNameGroup = document.getElementById('fullNameGroup');
    const roleSelectGroup = document.getElementById('roleSelectGroup');
    
    form.dataset.mode = mode;
    
    if (mode === 'login') {
      title.textContent = 'Sign In';
      toggleText.textContent = "Don't have an account?";
      submitBtn.textContent = 'Sign In';
      fullNameGroup.style.display = 'none';
      roleSelectGroup.style.display = 'none';
    } else {
      title.textContent = 'Create Account';
      toggleText.textContent = 'Already have an account?';
      submitBtn.textContent = 'Sign Up';
      fullNameGroup.style.display = 'flex';
      roleSelectGroup.style.display = 'flex';
    }
  }
  
  static fillDemoAdmin() {
    document.getElementById('authEmail').value = 'admin@college.edu';
    document.getElementById('authPassword').value = 'Admin@123';
  }
  
  static fillDemoStudent() {
    document.getElementById('authEmail').value = 'student@apex.edu';
    document.getElementById('authPassword').value = 'Student@123';
  }
  
  static async handleAuthSubmit(e) {
    e.preventDefault();
    const mode = document.getElementById('authForm').dataset.mode || 'login';
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    
    try {
      if (mode === 'login') {
        const response = await APIClient.login(email, password);
        this.setCurrentUser(response.user);
        ToastNotification.show('✅ Login successful!', 'success');
        this.closeAuthModal();
        this.updateUserProfile();
      } else {
        const fullName = document.getElementById('authFullName').value;
        const role = document.getElementById('authRole').value;
        const response = await APIClient.register(email, password, fullName, role);
        this.setCurrentUser(response.user);
        ToastNotification.show('✅ Account created successfully!', 'success');
        this.closeAuthModal();
        this.updateUserProfile();
      }
    } catch (error) {
      ToastNotification.show(`❌ ${error.message}`, 'error');
    }
  }
  
  static setCurrentUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
  }
  
  static getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
  }
  
  static isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }
  
  static checkAuthState() {
    const user = this.getCurrentUser();
    if (user) {
      this.updateUserProfile();
    }
  }
  
  static updateUserProfile() {
    const user = this.getCurrentUser();
    const userName = document.getElementById('userName');
    const userRoleBadge = document.getElementById('userRoleBadge');
    const authActionBtn = document.getElementById('authActionBtn');
    
    if (user) {
      userName.textContent = user.full_name || user.email;
      userRoleBadge.textContent = user.role === 'admin' ? 'Admin' : 'Student';
      authActionBtn.innerHTML = '<i class="fa-solid fa-right-from-bracket"></i>';
      authActionBtn.title = 'Logout';
      authActionBtn.onclick = () => this.logout();
    } else {
      userName.textContent = 'Guest Student';
      userRoleBadge.textContent = 'Guest Mode';
      authActionBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i>';
      authActionBtn.title = 'Account';
      authActionBtn.onclick = () => this.showAuthModal();
    }
  }
  
  static logout() {
    if (confirm('Are you sure you want to logout?')) {
      APIClient.logout();
      this.updateUserProfile();
      ToastNotification.show('✅ Logged out successfully', 'success');
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  AuthManager.init();
});