# Lexis Studio

Sistema de gestión jurídica profesional. Plataforma SPA (Single Page Application) 100% estática — sin backend, sin base de datos externa. Toda la persistencia se maneja en el navegador mediante `localStorage`.

## 🚀 Deploy en Vercel

Este proyecto se despliega automáticamente desde GitHub a Vercel.  
URL de producción: `https://tu-proyecto.vercel.app`

## 📁 Estructura del repositorio

```
/
├── index.html      ← Aplicación completa (HTML + CSS + JS en un solo archivo)
├── vercel.json     ← Configuración de rutas para Vercel
├── .gitignore
└── README.md
```

## 👥 Usuarios de acceso (demo)

| Usuario   | Contraseña | Rol         |
|-----------|------------|-------------|
| `jsmith`  | `demo123`  | Abogado     |
| `mgarcia` | `demo123`  | Secretaria  |
| `rlopez`  | `demo123`  | Abogado     |

## 🔧 Módulos incluidos

### Panel del Abogado
- **Dashboard** — KPIs en tiempo real: casos, honorarios, audiencias, clientes
- **Mis Casos** — Expedientes con nota estratégica privada (CRUD completo)
- **Mi Agenda** — Audiencias y reuniones con filtros
- **Clientes** — Cartera de clientes asignados
- **Documentos y Honorarios** — Biblioteca de escritos y control de cobros

### Panel de Secretaria
- **Dashboard Diario** — Checklist de tareas, sala de espera del día
- **Agenda General** — Calendario completo del estudio con filtros
- **Gestión de Casos** — Tabla de todos los expedientes, carga de documentos
- **Clientes** — Alta de nuevos clientes con asignación de abogado
- **Caja / Finanzas** — Ingresos, egresos y saldo recalculado en tiempo real

## 💾 Persistencia

Los datos se guardan en `localStorage` del navegador. Son permanentes entre sesiones en el mismo dispositivo/navegador. No se requiere servidor ni base de datos.

## 🎨 Stack técnico

- HTML5 + CSS3 Vanilla + JavaScript ES6+
- Google Fonts (Playfair Display + Inter)
- Sin frameworks, sin dependencias externas
- Diseño: Paleta Navy, sistema Bento Grid 12 columnas
