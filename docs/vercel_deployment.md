# 🚀 Guía de Despliegue en Vercel

Para desplegar este chatbot en Vercel, necesitas seguir estos pasos. Vercel es excelente para aplicaciones Python, pero hay una consideración importante: **no soporta bases de datos locales (SQLite) de forma persistente**.

## 1. Requisitos Previos

*   Una cuenta en [Vercel](https://vercel.com/).
*   Tener instalado Vercel CLI (`npm i -g vercel`) o conectar tu repositorio de GitHub a Vercel.

## 2. Configuración del Proyecto

### Archivo `vercel.json`
Ya se ha creado el archivo `vercel.json` en la raíz del proyecto. Este archivo le dice a Vercel que use Python y redirija todo el tráfico a `run.py`.

```json
{
  "version": 2,
  "builds": [
    {
      "src": "run.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "run.py"
    }
  ]
}
```

### Base de Datos (¡IMPORTANTE!)
**SQLite NO funcionará correctamente en Vercel** porque el sistema de archivos es efímero (se borra). Necesitas una base de datos en la nube (PostgreSQL).

1.  **Opción recomendada:** Usa **Vercel Postgres** (puedes añadirlo desde el dashboard de Vercel en la pestaña "Storage") o servicios como **Neon**, **Supabase** o **ElephantSQL**.
2.  Obtén la URL de conexión de tu base de datos (ej: `postgres://usuario:pass@host:port/dbname`).
3.  Configura esta URL en las variables de entorno.

## 3. Variables de Entorno

En el dashboard de tu proyecto en Vercel (Settings > Environment Variables), debes agregar las siguientes variables (las mismas que en tu `.env` local, pero adaptadas):

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Tu token del bot de Telegram. |
| `GOOGLE_API_KEY` | Tu API Key de Google Gemini. |
| `GEMINI_MODEL` | `models/gemini-2.5-flash` (o el que uses). |
| `GEMINI_API_URL` | `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent` |
| `SQLALCHEMY_DATABASE_URI` | **AQUÍ VA TU URL DE POSTGRES** (no uses sqlite). |
| `LOG_LEVEL` | `INFO` |

> **Nota:** Si usas Vercel Postgres, las variables se configuran automáticamente al conectar la base de datos, pero asegúrate de que tu código use `SQLALCHEMY_DATABASE_URI`.

## 4. Despliegue

### Opción A: Desde GitHub (Recomendado)
1.  Sube tu código a un repositorio de GitHub.
2.  En Vercel, haz clic en "Add New Project" e importa tu repositorio.
3.  Configura las variables de entorno antes de desplegar.
4.  Haz clic en "Deploy".

### Opción B: Vercel CLI
En la terminal de tu proyecto:
```bash
vercel
```
Sigue las instrucciones en pantalla.

## 5. Webhook de Telegram

Una vez desplegado, obtendrás una URL (ej: `https://chatbot-gastos.vercel.app`). Necesitas decirle a Telegram que envíe los mensajes a esa nueva URL.

Abre tu navegador y visita:
`https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://<TU_PROYECTO>.vercel.app/webhook`

Recibirás un JSON confirmando: `{"ok":true, "result":true, "description":"Webhook was set"}`.

## Consideraciones Adicionales

*   **Librerías:** Asegúrate de que `requirements.txt` tenga `psycopg2-binary` (ya está incluido) para poder conectar con PostgreSQL.
*   **Logs:** En Vercel, los logs se ven en la pestaña "Logs" del dashboard.

