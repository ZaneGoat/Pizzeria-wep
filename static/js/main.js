/**
 * Pizza Time — Global Frontend Utilities
 * Handles navigation, cart badge sync, promo engine, order lookup, toast notifications, and Web Audio KDS alerts.
 */

const PROMO_RULES = {
    'PIZZATIME10': { type: 'percent', value: 10, minSubtotal: 0, label: '-10% (PIZZATIME10)' },
    'FIRSTORDER': { type: 'fixed', value: 15, minSubtotal: 70, label: '-15 DH (FIRSTORDER)' }
};

function computePromoDiscount(code, subtotal) {
    if (!code) return { discount: 0, valid: false, label: '', error: '' };
    const clean = code.trim().toUpperCase();
    const rule = PROMO_RULES[clean];
    if (!rule) {
        return { discount: 0, valid: false, label: '', error: 'Code promo invalide' };
    }
    if (subtotal < rule.minSubtotal) {
        return {
            discount: 0,
            valid: false,
            label: '',
            error: `Minimum ${rule.minSubtotal} DH requis pour ${clean}`
        };
    }
    const discount = rule.type === 'percent'
        ? +(subtotal * (rule.value / 100)).toFixed(2)
        : Math.min(subtotal, rule.value);
    return { discount, valid: true, code: clean, label: rule.label, error: '' };
}

function toggleMobileNav() {
    const navLinks = document.getElementById('main-nav-links');
    if (navLinks) {
        navLinks.classList.toggle('open');
    }
}

function showToast(message) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <svg class="icon icon-sm" style="color: var(--success);" viewBox="0 0 24 24">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(35px)';
        toast.style.transition = 'all 0.25s ease';
        setTimeout(() => toast.remove(), 260);
    }, 2400);
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

function openOrderLookupModal() {
    const modal = document.getElementById('order-lookup-modal');
    if (modal) modal.style.display = 'flex';
}

function closeOrderLookupModal() {
    const modal = document.getElementById('order-lookup-modal');
    if (modal) modal.style.display = 'none';
}

function searchCustomerOrders(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('lookup-phone-input');
    const resultsDiv = document.getElementById('lookup-orders-results');
    if (!input || !resultsDiv) return;

    const phone = input.value.trim();
    if (!phone) return;

    resultsDiv.innerHTML = '<p style="text-align: center; color: var(--text-muted);">Recherche en cours...</p>';

    fetch(`/api/client/orders?phone=${encodeURIComponent(phone)}`)
        .then(r => r.json())
        .then(data => {
            if (!data.orders || data.orders.length === 0) {
                resultsDiv.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 1rem;">Aucune commande trouvée pour ce numéro.</p>';
                return;
            }
            let html = `<div style="margin-bottom: 0.75rem; font-size: 0.85rem; color: var(--text-muted);">Client : <strong style="color: #fff;">${data.client_name}</strong></div>`;
            data.orders.forEach(order => {
                const itemsJson = encodeURIComponent(JSON.stringify(order.items || []));
                html += `
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 0.9rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem;">
                            <strong style="color: #fff;">Commande #${order.id}</strong>
                            <span class="status-badge status-${order.status}">${order.status}</span>
                        </div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.65rem;">
                            ${order.date} • <strong style="color: var(--accent-color);">${order.total_price.toFixed(2)} DH</strong>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <a href="${order.url}" class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.72rem; flex: 1;">Suivi en Direct</a>
                            <button type="button" onclick="reorderPastItems('${itemsJson}')" style="padding: 0.4rem 0.8rem; font-size: 0.72rem; flex: 1;">Re-commander</button>
                        </div>
                    </div>
                `;
            });
            resultsDiv.innerHTML = html;
        })
        .catch(() => {
            resultsDiv.innerHTML = '<p style="text-align: center; color: var(--danger);">Erreur lors de la recherche.</p>';
        });
}

function reorderPastItems(encodedItems) {
    try {
        const items = JSON.parse(decodeURIComponent(encodedItems));
        if (!Array.isArray(items) || items.length === 0) return;
        const formatted = items.map(it => ({
            id: it.id,
            name: it.name,
            price: it.price,
            extra_price: 0,
            quantity: it.quantity,
            customizations: it.customizations || ''
        }));
        localStorage.setItem('pizzeria_cart', JSON.stringify(formatted));
        closeOrderLookupModal();
        showToast('Panier rechargé avec votre commande');
        if (typeof updateCartUI === 'function') {
            cart = formatted;
            updateCartUI();
            if (typeof toggleCart === 'function') toggleCart();
        } else {
            window.location.href = '/checkout';
        }
    } catch (e) {
        console.error(e);
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
