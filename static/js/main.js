/**
 * Chef Amin Pizzeria — Global Frontend Utilities
 * Handles navigation, cart badge sync, toast notifications, and Web Audio kitchen alerts.
 */

function toggleMobileNav() {
    const navLinks = document.getElementById('main-nav-links');
    if (navLinks) {
        navLinks.classList.toggle('open');
    }
}

function showToast(message, icon = '🍕') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        toast.style.transition = 'all 0.25s ease';
        setTimeout(() => toast.remove(), 260);
    }, 2600);
}

function syncGlobalCartBadge() {
    try {
        const cart = JSON.parse(localStorage.getItem('pizzeria_cart') || '[]');
        const totalQty = cart.reduce((acc, item) => acc + (parseInt(item.quantity, 10) || 0), 0);
        const floatingBtn = document.getElementById('floating-cart');
        const badge = document.getElementById('cart-badge-count');
        const navBadge = document.getElementById('nav-cart-count');

        if (badge) badge.textContent = totalQty;
        if (navBadge) navBadge.textContent = totalQty;

        if (floatingBtn) {
            const hasCartDrawer = !!document.getElementById('cart-overlay');
            if (totalQty > 0 && hasCartDrawer) {
                floatingBtn.style.display = 'flex';
            } else if (totalQty > 0 && !hasCartDrawer) {
                floatingBtn.style.display = 'flex';
                floatingBtn.onclick = function () {
                    window.location.href = '/checkout';
                };
            } else {
                floatingBtn.style.display = 'none';
            }
        }
    } catch (e) {
        console.error('Error syncing cart badge:', e);
    }
}

function playKitchenChime() {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const notes = [587.33, 880.0]; // D5 -> A5 chime
        notes.forEach((freq, idx) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.16);
            gain.gain.setValueAtTime(0.18, ctx.currentTime + idx * 0.16);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.16 + 0.45);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime + idx * 0.16);
            osc.stop(ctx.currentTime + idx * 0.16 + 0.45);
        });
    } catch (e) {
        // Ignore audio autoplay restrictions
    }
}

document.addEventListener('DOMContentLoaded', () => {
    syncGlobalCartBadge();

    // Auto-fade flash messages after 5 seconds
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.4s ease';
            setTimeout(() => flash.remove(), 400);
        }, 5000);
    });
});
