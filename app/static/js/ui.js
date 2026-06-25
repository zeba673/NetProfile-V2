/**
 * ui.js — Interacciones de UI compartidas
 * Modal manager, caso card expansion, sidebar nav active state,
 * filtro de tabla, formateo de moneda y utilidades generales.
 */
(function () {
  'use strict';

  // ─── MODAL MANAGER ───────────────────────────────────────────
  window.Modal = {
    open(id) {
      const el = document.getElementById(id);
      if (el) {
        el.classList.add('open');
        document.body.style.overflow = 'hidden';
        // Foco en primer input
        setTimeout(() => {
          const first = el.querySelector('input, select, textarea');
          if (first) first.focus();
        }, 200);
      }
    },
    close(id) {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove('open');
        document.body.style.overflow = '';
      }
    },
    closeAll() {
      document.querySelectorAll('.modal-overlay.open').forEach(el => {
        el.classList.remove('open');
      });
      document.body.style.overflow = '';
    },
  };

  // Click fuera del modal lo cierra
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
      Modal.closeAll();
    }
  });

  // ESC cierra modales
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') Modal.closeAll();
  });

  // ─── CASO CARD EXPANSION ─────────────────────────────────────
  document.addEventListener('click', (e) => {
    const header = e.target.closest('.caso-card-header');
    if (header) {
      const card = header.closest('.caso-card');
      if (card) {
        card.classList.toggle('expanded');
      }
    }
  });

  // ─── SIDEBAR ACTIVE STATE ────────────────────────────────────
  function setSidebarActive() {
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-nav-item').forEach(item => {
      const href = item.getAttribute('href');
      if (href && path.startsWith(href)) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }
  setSidebarActive();

  // ─── TABLE FILTER / SEARCH ───────────────────────────────────
  window.filterTable = function (inputEl, tableBodyId) {
    const query = inputEl.value.toLowerCase();
    const tbody = document.getElementById(tableBodyId);
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    let visible = 0;
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const show = text.includes(query);
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Update count badge if present
    const countEl = document.getElementById(tableBodyId + '-count');
    if (countEl) countEl.textContent = visible;
  };

  // ─── FORMAT CURRENCY ─────────────────────────────────────────
  window.formatMoney = function (amount) {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // ─── FORMAT DATE ─────────────────────────────────────────────
  window.formatDate = function (dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr.replace(' ', 'T'));
    return d.toLocaleDateString('es-AR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  };

  window.formatDateTime = function (dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr.replace(' ', 'T'));
    return d.toLocaleDateString('es-AR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  // ─── BADGE HELPERS ───────────────────────────────────────────
  window.estadoBadge = function (estado) {
    const map = {
      activo:     '<span class="badge badge-activo">Activo</span>',
      en_curso:   '<span class="badge badge-en_curso">En Curso</span>',
      cerrado:    '<span class="badge badge-cerrado">Cerrado</span>',
      archivado:  '<span class="badge badge-archivado">Archivado</span>',
      pendiente:  '<span class="badge badge-pendiente">Pendiente</span>',
      confirmada: '<span class="badge badge-confirmada">Confirmada</span>',
      cancelada:  '<span class="badge badge-cancelada">Cancelada</span>',
      realizada:  '<span class="badge badge-realizada">Realizada</span>',
      completado: '<span class="badge badge-completado">Completed</span>',
      procesando: '<span class="badge badge-procesando">Processing</span>',
      fallido:    '<span class="badge badge-fallido">Failed</span>',
      pendiente_escaneo: '<span class="badge badge-amber">Pendiente escaneo</span>',
      digitalizado:      '<span class="badge badge-green">Digitalizado</span>',
    };
    return map[estado] || `<span class="badge badge-slate">${estado}</span>`;
  };

  window.tipoBadge = function (tipo) {
    const map = {
      audiencia: '<span class="badge badge-navy">Audiencia</span>',
      reunion:   '<span class="badge badge-blue">Reunión</span>',
      recepcion: '<span class="badge badge-amber">Recepción</span>',
      ingreso:   '<span class="badge badge-green">Ingreso</span>',
      egreso:    '<span class="badge badge-red">Egreso</span>',
    };
    return map[tipo] || `<span class="badge badge-slate">${tipo}</span>`;
  };

  window.prioridadBadge = function (prioridad) {
    const map = {
      baja:    '<span class="text-xs priority-baja">Baja</span>',
      normal:  '<span class="text-xs priority-normal">Normal</span>',
      alta:    '<span class="text-xs priority-alta font-semibold">Alta</span>',
      urgente: '<span class="text-xs priority-urgente font-bold">⚠ Urgente</span>',
    };
    return map[prioridad] || prioridad;
  };

  // ─── CONFIRM DELETE HELPER ───────────────────────────────────
  window.confirmDelete = function (message = '¿Eliminar este registro?') {
    return window.confirm(message);
    // Nota: Aunque confirmDelete usa confirm(), solo se usa como
    // un guard interno, nunca como flujo principal de UX.
  };

  // ─── RESET FORM ──────────────────────────────────────────────
  window.resetForm = function (formId) {
    const form = document.getElementById(formId);
    if (form) form.reset();
  };

  // ─── SET BUTTON LOADING ──────────────────────────────────────
  window.setBtnLoading = function (btn, loading, originalText) {
    if (loading) {
      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div>';
    } else {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  };

  // ─── GET FORM DATA ───────────────────────────────────────────
  window.getFormData = function (formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    const data = {};
    const formData = new FormData(form);
    formData.forEach((val, key) => { data[key] = val; });
    return data;
  };

  // ─── EMPTY STATE HTML ────────────────────────────────────────
  window.emptyStateHTML = function (message = 'No hay registros') {
    return `<tr><td colspan="99" class="empty-state" style="padding:2.5rem">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      <div class="empty-state-title">${message}</div>
      <div class="empty-state-desc">Usá el botón de arriba para agregar un registro.</div>
    </td></tr>`;
  };

})();
