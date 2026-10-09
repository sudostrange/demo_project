function updateAuthStatus() {
  const t = localStorage.getItem('token');
  const el = document.getElementById('auth-status');
  if (!el) return;
  if (t) {
    try {
      const payload = JSON.parse(atob(t.split('.')[1]));
      el.textContent = 'logged in: ' + (payload.sub || payload.name || 'user');
    } catch {
      el.textContent = 'token saved';
    }
  } else {
    el.textContent = 'not logged in';
  }
}
document.getElementById('logout-btn')?.addEventListener('click', () => {
  localStorage.removeItem('token');
  updateAuthStatus();
});
updateAuthStatus();
