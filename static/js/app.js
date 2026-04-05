function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast' + (isError ? ' error' : '');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

function toggleNav() {
    document.getElementById('navLinks').classList.toggle('open');
}

function toggleDark() {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('darkMode', isDark ? '1' : '0');
    document.querySelector('.dark-toggle').textContent = isDark ? '☀️' : '🌙';
}

function updateOnlineStatus() {
    const bar = document.getElementById('offlineBar');
    if (navigator.onLine) {
        if (bar) bar.style.display = 'none';
    } else {
        if (!bar) {
            const nav = document.querySelector('.navbar');
            const div = document.createElement('div');
            div.id = 'offlineBar';
            div.style.cssText = 'background:#f59e0b;color:#000;text-align:center;padding:0.35rem;font-size:0.8rem;font-weight:600;';
            div.textContent = 'You are offline – cached data available';
            nav.after(div);
        } else {
            bar.style.display = 'block';
        }
    }
}

function apiFetch(url, options = {}) {
    if (!navigator.onLine && (!options.method || options.method === 'GET')) {
        return fetch(url, options).catch(() => {
            showToast('You are offline', true);
            return new Response(JSON.stringify([]), { status: 200, headers: { 'Content-Type': 'application/json' } });
        });
    }
    return fetch(url, options).catch((err) => {
        showToast('Connection error', true);
        throw err;
    });
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

(function () {
    if (localStorage.getItem('darkMode') === '1') {
        document.body.classList.add('dark');
        const btn = document.querySelector('.dark-toggle');
        if (btn) btn.textContent = '☀️';
    }
    updateOnlineStatus();
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
})();
