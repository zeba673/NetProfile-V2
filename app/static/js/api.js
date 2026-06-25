/**
 * api.js — Wrapper centralizado para fetch() hacia la API Flask
 * Maneja JSON, errores y CSRF de forma uniforme.
 */
const Api = (function () {
  'use strict';

  const BASE = '/api';

  async function request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'same-origin',
    };

    if (body !== null) {
      opts.body = JSON.stringify(body);
    }

    const response = await fetch(BASE + path, opts);

    let data;
    try {
      data = await response.json();
    } catch {
      data = { error: 'Respuesta inválida del servidor.' };
    }

    if (!response.ok) {
      throw new Error(data.error || `Error ${response.status}`);
    }

    return data;
  }

  return {
    get:    (path)         => request('GET',    path),
    post:   (path, body)   => request('POST',   path, body),
    put:    (path, body)   => request('PUT',    path, body),
    delete: (path)         => request('DELETE', path),

    // Recursos específicos
    casos:       {
      list:   ()         => request('GET',    '/casos'),
      create: (data)     => request('POST',   '/casos', data),
      update: (id, data) => request('PUT',    `/casos/${id}`, data),
      delete: (id)       => request('DELETE', `/casos/${id}`),
    },
    clientes:    {
      list:   ()         => request('GET',    '/clientes'),
      create: (data)     => request('POST',   '/clientes', data),
      update: (id, data) => request('PUT',    `/clientes/${id}`, data),
      delete: (id)       => request('DELETE', `/clientes/${id}`),
    },
    audiencias:  {
      list:   ()         => request('GET',    '/audiencias'),
      create: (data)     => request('POST',   '/audiencias', data),
      update: (id, data) => request('PUT',    `/audiencias/${id}`, data),
      delete: (id)       => request('DELETE', `/audiencias/${id}`),
    },
    movimientos: {
      list:   ()         => request('GET',    '/movimientos'),
      create: (data)     => request('POST',   '/movimientos', data),
      delete: (id)       => request('DELETE', `/movimientos/${id}`),
    },
    tareas:      {
      list:   ()         => request('GET',    '/tareas'),
      create: (data)     => request('POST',   '/tareas', data),
      update: (id, data) => request('PUT',    `/tareas/${id}`, data),
      delete: (id)       => request('DELETE', `/tareas/${id}`),
    },
    documentos:  {
      list:   ()         => request('GET',    '/documentos'),
      create: (data)     => request('POST',   '/documentos', data),
      update: (id, data) => request('PUT',    `/documentos/${id}`, data),
      delete: (id)       => request('DELETE', `/documentos/${id}`),
    },
    dashboard:   {
      stats:  ()         => request('GET',    '/dashboard/stats'),
    },
    usuarios: {
      abogados: ()       => request('GET',    '/usuarios/abogados'),
    },
  };
})();
