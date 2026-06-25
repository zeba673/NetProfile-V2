/**
 * clock.js — Reloj en vivo con fecha y hora
 * Actualiza el DOM cada segundo mediante setInterval nativo.
 */
(function () {
  'use strict';

  const DIAS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  const MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
  ];

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function updateClock() {
    const now = new Date();

    const hours   = pad(now.getHours());
    const minutes = pad(now.getMinutes());
    const seconds = pad(now.getSeconds());

    const dayName  = DIAS[now.getDay()];
    const day      = now.getDate();
    const month    = MESES[now.getMonth()];
    const year     = now.getFullYear();

    const timeEl = document.getElementById('clock-time');
    const dateEl = document.getElementById('clock-date');

    if (timeEl) timeEl.textContent = `${hours}:${minutes}:${seconds}`;
    if (dateEl) dateEl.textContent = `${dayName}, ${day} de ${month} de ${year}`;
  }

  // Ejecutar inmediatamente y luego cada segundo
  updateClock();
  setInterval(updateClock, 1000);

})();
