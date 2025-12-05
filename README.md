# SmartExpenseBot - Bot de Telegram para Gestión de Gastos Compartidos

Bot de Telegram que permite registrar gastos y deudas compartidas utilizando lenguaje natural. Utiliza Google Gemini para procesar mensajes en lenguaje natural y extraer información estructurada.

## Características

- ✅ Registro de gastos mediante lenguaje natural
- ✅ Autorización de usuarios mediante base de datos
- ✅ Procesamiento de lenguaje natural con Google Gemini
- ✅ Base de datos PostgreSQL para persistencia
- ✅ Comandos de administración para gestión de usuarios

## Requisitos

- Python 3.10+
- PostgreSQL
- Token de bot de Telegram
- API Key de Google Gemini

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd chatbot-gastos
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```

Editar `.env` y agregar tus credenciales:
```
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
GOOGLE_API_KEY=tu_api_key_de_google
DATABASE_URL=postgresql://usuario:password@localhost:5432/smartexpensebot
SECRET_KEY=tu-secret-key-segura
```

5. Crear la base de datos PostgreSQL:
```sql
CREATE DATABASE smartexpensebot;
```

6. Ejecutar la aplicación:
```bash
python run.py
```

## Configuración del Webhook de Telegram

Para producción, configura el webhook de Telegram:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://tu-dominio.com/webhook"
```

Para desarrollo local, puedes usar ngrok:

```bash
ngrok http 5000
```

Luego configura el webhook con la URL de ngrok.

## Uso

### Comandos del Bot

- `/start` - Registra un nuevo usuario en el bot
- `/admin add <telegram_id> <nombre>` - Agrega un usuario manualmente
- `/admin list` - Lista todos los usuarios registrados
- `/admin authorize <telegram_id>` - Autoriza un usuario
- `/admin deauthorize <telegram_id>` - Desautoriza un usuario

### Registrar Gastos

Simplemente envía un mensaje con el gasto en lenguaje natural:

- "Gasté 50 USD en el supermercado"
- "Pagué 30 dólares por el taxi"
- "Compré comida por 25 USD"

El bot procesará el mensaje y registrará el gasto automáticamente.

## Estructura del Proyecto

```
chatbot-gastos/
├── app/
│   ├── __init__.py          # Inicialización de Flask
│   ├── config.py            # Configuración
│   ├── models.py            # Modelos SQLAlchemy
│   ├── routes.py            # Rutas Flask
│   ├── bot_services.py      # Servicios del bot
│   └── ai_services.py       # Servicios de IA (Gemini)
├── run.py                   # Punto de entrada
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

## Modelo de Datos

### Tabla `users`
- `id`: ID interno (Primary Key)
- `telegram_id`: ID único de Telegram
- `name`: Nombre del usuario
- `is_authorized`: Flag de autorización
- `created_at`: Fecha de creación

### Tabla `expenses`
- `id`: ID del gasto (Primary Key)
- `created_at`: Fecha de creación
- `description`: Descripción del gasto
- `amount`: Monto del gasto
- `currency`: Moneda
- `payer_id`: ID del usuario que pagó (Foreign Key)
- `debtor_id`: ID del usuario que debe (Foreign Key)
- `raw_text`: Mensaje original
- `is_settled`: Flag de deuda saldada
- `category`: Categoría del gasto

## Desarrollo

El proyecto sigue las mejores prácticas de Flask:

- Separación de responsabilidades (models, services, routes)
- Configuración mediante variables de entorno
- Logging estructurado
- Manejo de errores robusto
- Código modular y mantenible

## Licencia

Este proyecto es de código abierto.

