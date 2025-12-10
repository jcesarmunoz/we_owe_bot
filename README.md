# SmartExpenseBot - Bot de Telegram para Gestión de Gastos Compartidos

Bot de Telegram inteligente que permite registrar gastos y deudas compartidas utilizando lenguaje natural. Utiliza la IA de Google Gemini para procesar mensajes, extraer información estructurada (montos, monedas, personas, fechas) y gestionar automáticamente quién debe a quién.

## Características Principales 🌟

- **🗣️ Procesamiento de Lenguaje Natural:** Entiende mensajes como "Gasté 50000 con Julieth en el cine" o "Le debo 20000 a Carlos para el lunes".
- **🧠 Lógica Inteligente de Deudas:**
  - **"Gasté..."**: Tú eres el cobrador, la otra persona te debe.
  - **"Debo..."**: Tú eres el deudor, la otra persona es el cobrador.
- **📅 Detección de Fechas:** Identifica automáticamente referencias temporales como "mañana", "el próximo viernes" o "en 3 días" para establecer fechas de vencimiento.
- **💳 Pagos Interactivos:** Flujo sencillo para registrar pagos mediante botones en el chat y generación automática de comprobantes.
- **🛡️ Seguridad Robusta:** Validación estricta de entradas para prevenir inyecciones y manejo seguro de datos.
- **📊 Resúmenes de Cuenta:** Consulta rápida de "Qué debo", "Quién me debe" y balance general.
- **☁️ Listo para la Nube:** Configurado para despliegue fácil en Vercel con soporte para PostgreSQL.
- **📝 Logs Estructurados:** Sistema de logging detallado para auditoría y depuración.

## Requisitos 📋

- Python 3.10+
- Base de datos PostgreSQL (recomendado para producción) o SQLite (dev)
- Token de bot de Telegram (@BotFather)
- API Key de Google Gemini (AI Studio)

## Instalación y Configuración ⚙️

1. **Clonar el repositorio:**
   ```bash
   git clone <repository-url>
   cd chatbot-gastos
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` basado en `.env.example`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_telegram
   GOOGLE_API_KEY=tu_api_key_gemini
   GEMINI_MODEL=models/gemini-2.5-flash
   GEMINI_API_URL=https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent
   SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host:port/dbname
   LOG_LEVEL=INFO
   ```

5. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

## Guía de Uso Rápido 🚀

### Comandos Básicos
- `/start` - Registro inicial.
- `Ver mis gastos` / `Resumen` - Ver estado de cuenta global.
- `Pagar` / `Mis deudas` - Ver lista de deudas pendientes para pagar.
- `Cobrar` / `Quién me debe` - Ver quién te debe dinero.

### Registrando Movimientos
El bot interpreta tu intención según cómo escribas:

1.  **Gastos Compartidos ("Gasté")**
    *   *Mensaje:* "Gasté 200.000 en el asado con Pedro"
    *   *Resultado:* Tú pagaste, Pedro te debe.

2.  **Deudas Personales ("Debo")**
    *   *Mensaje:* "Le debo 50.000 a María por el taxi de ayer"
    *   *Resultado:* Tú debes, María espera el pago.

Para más detalles, consulta la [Guía de Usuario](docs/user_guide.md).

## Documentación 📚

En la carpeta `docs/` encontrarás documentación detallada:

*   [📖 Guía de Usuario](docs/user_guide.md): Manual completo de uso.
*   [🔒 Seguridad](docs/security.md): Políticas de seguridad y validación de datos.
*   [🚀 Despliegue en Vercel](docs/vercel_deployment.md): Pasos para publicar el bot en Vercel.
*   [🔌 API Endpoints](docs/api-endpoints.md): Detalles técnicos de los endpoints.

## Seguridad 🔒

El proyecto implementa "Security by Design":
- **Validación de Entrada:** Solo se permiten caracteres alfanuméricos y signos de puntuación básicos (`$`, `,`, `.`). Cualquier carácter especial sospechoso bloquea el procesamiento del mensaje.
- **Gestión de Secretos:** Uso estricto de variables de entorno.
- **Logs:** Registro de intentos fallidos y errores de validación.

## Estructura del Proyecto 📂

```
chatbot-gastos/
├── app/
│   ├── __init__.py          # Factory de la app Flask
│   ├── routes.py            # Webhook y lógica de ruteo
│   ├── models.py            # Modelos DB (User, Expense)
│   ├── ai_services.py       # Integración con Google Gemini
│   ├── bot_services.py      # Lógica de Telegram y negocio
│   ├── logger_config.py     # Configuración de logging estructurado
│   └── config.py            # Configuración de entorno
├── docs/                    # Documentación del proyecto
├── api/
│   └── index.py             # Punto de entrada para Vercel
├── vercel.json              # Configuración para Vercel
├── requirements.txt         # Dependencias
└── README.md                # Este archivo
```

## Despliegue en Vercel

El proyecto incluye configuración nativa para Vercel (`vercel.json`).
**Nota importante:** Para Vercel es obligatorio usar una base de datos externa (como Vercel Postgres o Neon), ya que SQLite no persiste datos en entornos serverless.

Ver [Guía de Despliegue](docs/vercel_deployment.md).

## Licencia

Este proyecto es de código abierto.
